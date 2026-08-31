"""Candidate-owned durability regressions, separate from evaluator acceptance."""

import tempfile
import unittest
from pathlib import Path

from jobservice import HandlerRegistry, IdempotencyConflict, JobStore, LeaseLost, ManualClock, Worker


class DurableLocalTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.clock = ManualClock()
        self.store = JobStore(Path(temp.name) / "queue.sqlite", clock=self.clock)

    def test_durable_key_survives_success(self):
        job = self.store.enqueue("echo", {"x": 1}, idempotency_key="request")
        Worker(self.store).run_one()
        repeated = self.store.enqueue("echo", {"x": 1}, idempotency_key="request")
        self.assertEqual((repeated.id, repeated.state), (job.id, "succeeded"))
        with self.assertRaises(IdempotencyConflict):
            self.store.enqueue("echo", {"x": 2}, idempotency_key="request")

    def test_expiry_is_exclusive_and_recovery_is_delayed(self):
        job = self.store.enqueue("echo", None)
        claim = self.store.claim("owner", lease_seconds=5)
        self.clock.advance(5)
        with self.assertRaises(LeaseLost):
            self.store.complete(job.id, claim.lease_token, "late")
        self.assertEqual(self.store.reap_expired(), 1)
        self.assertIsNone(self.store.claim("replacement"))
        self.clock.advance(1)
        replacement = self.store.claim("replacement")
        self.assertEqual(replacement.attempts, 2)
        self.assertNotEqual(replacement.lease_token, claim.lease_token)

    def test_cancel_request_discards_result(self):
        job = self.store.enqueue("echo", None)
        claim = self.store.claim("owner")
        self.store.cancel(job.id)
        done = self.store.complete(job.id, claim.lease_token, "not committed")
        self.assertEqual(done.state, "cancelled")
        self.assertIsNone(done.result)

    def test_non_json_result_uses_failure_path(self):
        self.store.enqueue("invalid", None, max_attempts=1)
        registry = HandlerRegistry().register("invalid", lambda payload, context: object())
        self.assertEqual(Worker(self.store, registry).run_one().state, "failed")

    def test_read_and_noop_operations_do_not_emit_events(self):
        job = self.store.enqueue("echo", 1)
        self.store.cancel(job.id)
        events = self.store.events(job.id)
        self.clock.advance(1)
        self.store.cancel(job.id)
        self.store.get(job.id)
        self.store.list_jobs()
        self.store.stats()
        self.store.reap_expired()
        self.assertEqual(self.store.events(job.id), events)

    def test_process_control_still_leaves_recoverable_attempt(self):
        def stop(payload, context):
            raise SystemExit(7)
        self.store.enqueue("stop", None, max_attempts=1)
        registry = HandlerRegistry().register("stop", stop)
        with self.assertRaises(SystemExit):
            Worker(self.store, registry, lease_seconds=2).run_one()
        self.clock.advance(2)
        self.assertEqual(self.store.reap_expired(), 1)
        self.assertEqual(self.store.list_jobs()[0].state, "failed")
