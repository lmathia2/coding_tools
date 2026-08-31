import json
import sqlite3

import jobservice

from acceptance_support import QueueCase


class MigrationTests(QueueCase):
    def test_legacy_database_migrates_without_loss_and_reopens_idempotently(self):
        legacy_path = self.path.with_name("legacy.sqlite")
        with sqlite3.connect(legacy_path) as connection:
            connection.execute("""CREATE TABLE jobs (
                seq INTEGER PRIMARY KEY AUTOINCREMENT, id TEXT NOT NULL UNIQUE,
                kind TEXT NOT NULL, payload TEXT NOT NULL, state TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0, max_attempts INTEGER NOT NULL,
                created_at REAL NOT NULL, updated_at REAL NOT NULL, result TEXT, error TEXT)""")
            for job_id, state, attempts, result, error in (
                ("old-queued", "queued", 0, None, None),
                ("old-running", "running", 1, None, "earlier failure"),
                ("old-success", "succeeded", 2, '{"kept":true}', None),
                ("old-failed", "failed", 3, None, "permanent"),
            ):
                connection.execute("INSERT INTO jobs(id,kind,payload,state,attempts,max_attempts,created_at,updated_at,result,error) VALUES(?,?,?,?,?,3,500,600,?,?)", (job_id, "echo", '{"original":7}', state, attempts, result, error))
        store = jobservice.JobStore(legacy_path, clock=self.clock)
        self.assertEqual([j.id for j in store.list_jobs()], ["old-queued", "old-running", "old-success", "old-failed"])
        self.assertEqual(store.get("old-success").result, {"kept": True})
        self.assertEqual(store.get("old-failed").error, "permanent")
        self.assertEqual(store.get("old-running").attempts, 1)
        self.assertEqual(store.get("old-queued").created_at, 500)
        self.assertEqual(store.get("old-queued").payload, {"original": 7})
        self.assertIsNone(store.get("old-running").lease_token)
        self.assertEqual(store.reap_expired(), 1)
        recovered = store.get("old-running")
        self.assertEqual((recovered.state, recovered.attempts, recovered.available_at), ("queued", 1, 1001))
        first = store.claim("new-worker")
        self.assertEqual(first.id, "old-queued")
        store.complete(first.id, first.lease_token, "first")
        self.clock.advance(1)
        second = store.claim("new-worker")
        self.assertEqual((second.id, second.attempts), ("old-running", 2))
        store.complete(second.id, second.lease_token, "recovered")
        snapshot = [j.to_dict() for j in store.list_jobs()]
        events = {j["id"]: store.events(j["id"]) for j in snapshot}
        reopened = jobservice.JobStore(legacy_path, clock=self.clock)
        self.assertEqual([j.to_dict() for j in reopened.list_jobs()], snapshot)
        self.assertEqual({j["id"]: reopened.events(j["id"]) for j in snapshot}, events)

    def test_migration_failure_is_atomic_and_can_retry(self):
        legacy_path = self.path.with_name("migration-fault.sqlite")
        with sqlite3.connect(legacy_path) as connection:
            connection.execute("""CREATE TABLE jobs (
                seq INTEGER PRIMARY KEY AUTOINCREMENT, id TEXT NOT NULL UNIQUE,
                kind TEXT NOT NULL, payload TEXT NOT NULL, state TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0, max_attempts INTEGER NOT NULL,
                created_at REAL NOT NULL, updated_at REAL NOT NULL, result TEXT, error TEXT)""")
            connection.execute("INSERT INTO jobs(id,kind,payload,state,max_attempts,created_at,updated_at) VALUES('old','echo','1','queued',3,500,500)")
            connection.execute("CREATE TRIGGER refuse_migration BEFORE UPDATE ON jobs BEGIN SELECT RAISE(ABORT,'migration interrupted'); END")
            schema_before = connection.execute("SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name").fetchall()
            version_before = connection.execute("PRAGMA user_version").fetchone()[0]
        # Schema-default migrations may legitimately avoid touching old rows.
        try:
            jobservice.JobStore(legacy_path, clock=self.clock)
        except Exception:
            with sqlite3.connect(legacy_path) as connection:
                self.assertEqual(connection.execute("SELECT id,payload,state FROM jobs").fetchall(), [("old", "1", "queued")])
                self.assertEqual(connection.execute("SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name").fetchall(), schema_before)
                self.assertEqual(connection.execute("PRAGMA user_version").fetchone()[0], version_before)
        finally:
            with sqlite3.connect(legacy_path) as connection:
                connection.execute("DROP TRIGGER refuse_migration")
        reopened = jobservice.JobStore(legacy_path, clock=self.clock)
        job = reopened.claim("worker", lease_seconds=5)
        self.assertEqual(job.id, "old")
        self.assertEqual(reopened.complete(job.id, job.lease_token, "works").state, "succeeded")


class CliIntegrationTests(QueueCase):
    def test_cli_idempotency_work_events_and_legacy_show(self):
        args = ("submit", "echo", '{"x":1}', "--idempotency-key", "cli-request")
        first = json.loads(self.cli(*args).stdout)
        second = json.loads(self.cli(*args).stdout)
        self.assertEqual(first["id"], second["id"])
        result = json.loads(self.cli("work", "--once", "--worker-id", "cli", "--lease-seconds", "15").stdout)
        self.assertEqual(result["state"], "succeeded")
        shown = json.loads(self.cli("show", first["id"]).stdout)
        self.assertEqual(shown["result"], {"x": 1})
        events = [json.loads(line) for line in self.cli("events", first["id"], "--limit", "100").stdout.splitlines()]
        self.assertEqual([e["type"] for e in events], ["enqueued", "claimed", "succeeded"])
        page = self.cli("events", first["id"], "--after-seq", str(events[0]["seq"]), "--limit", "1")
        self.assertEqual(json.loads(page.stdout)["type"], "claimed")
        self.assertEqual(self.cli("work", "--once").stdout, "")

    def test_cli_cancel_reap_and_stats(self):
        job = json.loads(self.cli("submit", "echo", "null").stdout)
        cancelled = json.loads(self.cli("cancel", job["id"]).stdout)
        self.assertEqual(cancelled["state"], "cancelled")
        self.assertEqual(json.loads(self.cli("reap").stdout), {"recovered": 0})
        self.assertEqual(json.loads(self.cli("stats").stdout)["cancelled"], 1)
        self.assertEqual(json.loads(self.cli("list", "--state", "cancelled").stdout)["id"], job["id"])

    def test_cli_conflicts_and_missing_cancel_are_json_errors(self):
        self.cli("submit", "echo", "1", "--idempotency-key", "key")
        for args, error_type in (
            (("submit", "echo", "2", "--idempotency-key", "key"), "IdempotencyConflict"),
            (("cancel", "missing"), "JobNotFound"),
            (("work", "--once", "--lease-seconds", "0"), "ValidationError"),
        ):
            result = self.cli(*args, expected=2)
            self.assertEqual(result.stdout, "")
            self.assertEqual(json.loads(result.stderr)["type"], error_type)
