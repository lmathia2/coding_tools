import sqlite3
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import jobservice

from acceptance_support import QueueCase


class IdempotencyTests(QueueCase):
    def test_canonical_payload_reuses_key_across_terminal_state(self):
        first = self.store.enqueue("echo", {"b": 2, "a": [1]}, idempotency_key="request")
        self.clock.advance(1)
        repeated = self.other().enqueue("echo", {"a": [1], "b": 2}, idempotency_key="request")
        self.assertEqual(repeated.to_dict(), first.to_dict())
        done = jobservice.Worker(self.store).run_one()
        events = self.history(first.id)
        self.assertEqual(self.store.enqueue("echo", {"a": [1], "b": 2}, idempotency_key="request"), done)
        self.assertEqual(events, self.history(first.id))
        self.assertEqual(sum(e["type"] == "enqueued" for e in events), 1)

    def test_conflicting_kind_payload_or_attempt_limit_does_not_mutate(self):
        job = self.store.enqueue("echo", {"n": 1}, max_attempts=3, idempotency_key="shared")
        before = self.history(job.id)
        for kind, payload, attempts in (("summary", {"n": 1}, 3), ("echo", {"n": 1.0}, 3), ("echo", {"n": 1}, 4)):
            with self.assertRaises(jobservice.IdempotencyConflict):
                self.store.enqueue(kind, payload, max_attempts=attempts, idempotency_key="shared")
        self.assertEqual(self.store.get(job.id), job)
        self.assertEqual(self.history(job.id), before)

    def test_concurrent_submissions_share_one_record_and_event(self):
        gate = Barrier(10)
        def submit(index):
            store = self.other()
            gate.wait(timeout=10)
            payload = {"a": 1, "b": 2} if index % 2 else {"b": 2, "a": 1}
            return store.enqueue("echo", payload, idempotency_key="concurrent").id
        with ThreadPoolExecutor(max_workers=10) as executor:
            ids = list(executor.map(submit, range(10)))
        self.assertEqual(len(set(ids)), 1)
        self.assertEqual(len(self.store.list_jobs()), 1)
        self.assertEqual([e["type"] for e in self.history(ids[0])], ["enqueued"])

    def test_key_validation_and_no_key_are_distinct(self):
        for key in ("", "   ", 3, False):
            with self.assertRaises(jobservice.ValidationError):
                self.store.enqueue("echo", 1, idempotency_key=key)
        first = self.store.enqueue("echo", 1)
        second = self.store.enqueue("echo", 1)
        self.assertNotEqual(first.id, second.id)
        exact = self.store.enqueue("echo", 1, idempotency_key=" x ")
        separate = self.store.enqueue("echo", 1, idempotency_key="x")
        self.assertNotEqual(exact.id, separate.id)


class EventAndAtomicityTests(QueueCase):
    def test_event_cursor_order_attempts_and_job_isolation(self):
        job = self.claimed()
        other = self.store.enqueue("echo", "other")
        self.clock.advance(1)
        self.store.heartbeat(job.id, job.lease_token, lease_seconds=20)
        self.store.fail(job.id, job.lease_token, "retry")
        events = self.history(job.id)
        self.assertEqual([e["type"] for e in events], ["enqueued", "claimed", "heartbeat", "retry_scheduled"])
        self.assertEqual([e["attempt"] for e in events], [0, 1, 1, 1])
        self.assertEqual([e["at"] for e in events], [1000, 1000, 1001, 1001])
        seqs = [e["seq"] for e in events]
        self.assertEqual(seqs, sorted(set(seqs)))
        self.assertTrue(all(e["job_id"] == job.id and isinstance(e["details"], dict) for e in events))
        self.assertEqual(self.store.events(job.id, after_seq=seqs[1], limit=1), events[2:3])
        self.assertEqual(self.store.events(job.id, after_seq=seqs[-1]), [])
        self.assertNotIn(self.history(other.id)[0]["seq"], seqs)

    def test_event_write_failure_rolls_back_state_and_reopens_cleanly(self):
        job = self.claimed()
        before, history = self.store.get(job.id), self.history(job.id)
        # Fault injection discovers auxiliary tables; it does not prescribe their
        # names/columns. An implementation embedding history in jobs is already
        # single-row atomic and receives an UPDATE failure instead.
        with sqlite3.connect(self.path) as connection:
            tables = [r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
                      if r[0] != "jobs" and not r[0].startswith("sqlite_")]
            targets = [(name, "INSERT") for name in tables] or [("jobs", "UPDATE")]
            for index, (table, operation) in enumerate(targets):
                quoted = '"' + table.replace('"', '""') + '"'
                connection.execute('CREATE TRIGGER reject_audit_%d BEFORE %s ON %s BEGIN SELECT RAISE(ABORT, \'audit unavailable\'); END' % (index, operation, quoted))
        try:
            with self.assertRaises(Exception):
                self.store.complete(job.id, job.lease_token, "cannot commit")
            self.assertEqual(self.store.get(job.id), before)
            self.assertEqual(self.history(job.id), history)
        finally:
            with sqlite3.connect(self.path) as connection:
                for index in range(len(targets)):
                    connection.execute("DROP TRIGGER reject_audit_%d" % index)
        reopened = self.other()
        self.assertEqual(reopened.get(job.id), before)
        self.assertEqual(reopened.complete(job.id, job.lease_token, "committed").state, "succeeded")

    def test_failed_job_update_cannot_leave_a_committed_event(self):
        job = self.claimed()
        before, history = self.store.get(job.id), self.history(job.id)
        with sqlite3.connect(self.path) as connection:
            connection.execute("CREATE TRIGGER reject_job BEFORE UPDATE ON jobs BEGIN SELECT RAISE(ABORT,'job unavailable'); END")
        try:
            with self.assertRaises(Exception):
                self.store.fail(job.id, job.lease_token, "not committed")
            self.assertEqual(self.store.get(job.id), before)
            self.assertEqual(self.history(job.id), history)
        finally:
            with sqlite3.connect(self.path) as connection:
                connection.execute("DROP TRIGGER reject_job")

    def test_invalid_completion_is_atomic_then_owner_can_retry(self):
        job = self.claimed()
        before, history = self.store.get(job.id), self.history(job.id)
        with self.assertRaises(jobservice.ValidationError):
            self.store.complete(job.id, job.lease_token, {"bad": float("nan")})
        self.assertEqual(self.store.get(job.id), before)
        self.assertEqual(self.history(job.id), history)
        self.assertEqual(self.store.complete(job.id, job.lease_token, 7).result, 7)

    def test_event_query_validation_and_complete_stats(self):
        job = self.store.enqueue("echo", None)
        for cursor, limit in ((-1, 1), (True, 1), (0, 0), (0, 1001)):
            with self.assertRaises(jobservice.ValidationError):
                self.store.events(job.id, after_seq=cursor, limit=limit)
        with self.assertRaises(jobservice.JobNotFound):
            self.store.events("missing")
        self.assertEqual(self.store.stats(), {"queued": 1, "running": 0, "succeeded": 0, "failed": 0, "cancelled": 0})
