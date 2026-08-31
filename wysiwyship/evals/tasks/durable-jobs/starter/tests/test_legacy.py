import io
import json
import tempfile
import unittest
from pathlib import Path

from jobservice import HandlerRegistry, JobNotFound, JobStore, ManualClock, ValidationError, Worker
from jobservice.cli import main


class LegacyApplicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "queue.sqlite"
        self.clock = ManualClock()
        self.store = JobStore(self.path, clock=self.clock)

    def test_persistence_and_detached_payload(self):
        payload = {"items": [1, 2], "unicode": "café"}
        job = self.store.enqueue("echo", payload)
        payload["items"].append(3)
        job.payload["items"].append(4)
        reopened = JobStore(self.path, clock=self.clock)
        self.assertEqual(reopened.get(job.id).payload["items"], [1, 2])
        self.assertEqual(job.attempts, 0)

    def test_fifo_filters_and_pagination(self):
        jobs = [self.store.enqueue(kind, index) for index, kind in enumerate(("echo", "render", "echo"))]
        self.assertEqual([j.id for j in self.store.list_jobs()], [j.id for j in jobs])
        self.assertEqual(self.store.list_jobs(limit=1, offset=1)[0].id, jobs[1].id)
        self.assertEqual(len(self.store.list_jobs(kind="echo")), 2)
        self.assertEqual(self.store.list_jobs(state="succeeded"), [])

    def test_default_handlers(self):
        a = self.store.enqueue("echo", [1, {"ok": True}])
        b = self.store.enqueue("summary", {"values": [2, 4, 6]})
        c = self.store.enqueue("render", {"template": "Hi {name}", "values": {"name": "Ada"}})
        outcomes = Worker(self.store).run_until_idle()
        self.assertEqual([j.id for j in outcomes], [a.id, b.id, c.id])
        self.assertTrue(all(j.state == "succeeded" for j in outcomes))
        self.assertEqual(outcomes[1].result, {"count": 3, "sum": 12, "mean": 4, "min": 2, "max": 6})
        self.assertEqual(outcomes[2].result, {"text": "Hi Ada"})

    def test_empty_summary(self):
        self.store.enqueue("summary", {"values": []})
        self.assertEqual(Worker(self.store).run_one().result["mean"], None)

    def test_max_jobs_and_kind_selection(self):
        a = self.store.enqueue("echo", "a")
        b = self.store.enqueue("summary", {"values": [3]})
        c = self.store.enqueue("echo", "c")
        outcomes = Worker(self.store).run_until_idle(max_jobs=1, kinds=["summary"])
        self.assertEqual([j.id for j in outcomes], [b.id])
        self.assertEqual(self.store.get(a.id).state, "queued")
        self.assertEqual(self.store.get(c.id).attempts, 0)

    def test_failure_and_unknown_handler_exhaust_single_attempt(self):
        for kind in ("fail", "not-configured"):
            job = self.store.enqueue(kind, {"message": "broken"}, max_attempts=1)
            result = Worker(self.store).run_one()
            self.assertEqual(result.id, job.id)
            self.assertEqual(result.state, "failed")
            self.assertEqual(result.attempts, 1)
            self.assertTrue(result.error)

    def test_custom_handler_and_correlated_logs(self):
        logs = []
        def handler(payload, context):
            context.log("custom", value=payload)
            return {"attempt": context.attempt, "worker": context.worker_id}
        registry = HandlerRegistry().register("custom", handler)
        job = self.store.enqueue("custom", 42)
        outcome = Worker(self.store, registry, worker_id="test-worker", logger=logs.append).run_one()
        self.assertEqual(outcome.result, {"attempt": 1, "worker": "test-worker"})
        self.assertEqual(logs[0]["job_id"], job.id)

    def test_process_control_exception_leaves_attempt_running(self):
        def interrupt(payload, context):
            raise KeyboardInterrupt()
        registry = HandlerRegistry().register("interrupt", interrupt)
        job = self.store.enqueue("interrupt", None)
        with self.assertRaises(KeyboardInterrupt):
            Worker(self.store, registry).run_one()
        self.assertEqual(self.store.get(job.id).state, "running")

    def test_empty_worker_and_state_counts(self):
        self.assertIsNone(Worker(self.store).run_one())
        for state in ("queued", "running", "succeeded", "failed"):
            self.assertEqual(self.store.stats()[state], 0)

    def test_validation_does_not_insert(self):
        for kind, payload, attempts in (("", {}, 1), ("echo", float("nan"), 1), ("echo", {}, 0), ("echo", {}, True)):
            with self.assertRaises(ValidationError):
                self.store.enqueue(kind, payload, max_attempts=attempts)
        self.assertEqual(self.store.list_jobs(), [])
        with self.assertRaises(JobNotFound):
            self.store.get("absent")
        with self.assertRaises(ValidationError):
            self.store.list_jobs(limit=1001)

    def test_registry_validation(self):
        registry = HandlerRegistry().register("x", lambda p, c: p)
        with self.assertRaises(ValidationError):
            registry.register("x", lambda p, c: p)
        with self.assertRaises(ValidationError):
            registry.register("y", None)
        self.assertEqual(registry.kinds(), ("x",))

    def test_cli_json_stdin_and_work(self):
        output, error = io.StringIO(), io.StringIO()
        self.assertEqual(main(["--db", str(self.path), "submit", "echo", "-"], stdin=io.StringIO('{"x":2}'), stdout=output, stderr=error), 0)
        job = json.loads(output.getvalue())
        output = io.StringIO()
        self.assertEqual(main(["--db", str(self.path), "work", "--once"], stdout=output, stderr=error), 0)
        self.assertEqual(json.loads(output.getvalue())["id"], job["id"])
        self.assertEqual(error.getvalue(), "")

    def test_cli_application_errors(self):
        for arguments in (["submit", "echo", "{"], ["show", "missing"]):
            output, error = io.StringIO(), io.StringIO()
            self.assertEqual(main(["--db", str(self.path)] + arguments, stdout=output, stderr=error), 2)
            self.assertEqual(output.getvalue(), "")
            self.assertIn("error", json.loads(error.getvalue()))


if __name__ == "__main__":
    unittest.main()
