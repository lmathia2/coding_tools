import sqlite3

import jobservice

from acceptance_support import QueueCase


class RetryAndRecoveryTests(QueueCase):
    def test_worker_failures_are_delayed_not_immediate(self):
        job = self.store.enqueue("fail", {"message": "transient"}, max_attempts=3)
        worker = jobservice.Worker(self.store)
        outcomes = worker.run_until_idle()
        self.assertEqual(len(outcomes), 1, "one poll cycle must not burn through delayed retries")
        self.assertEqual(outcomes[0].state, "queued")
        self.assertEqual(self.store.get(job.id).attempts, 1)
        self.assertIsNone(worker.run_one())
        self.clock.advance(1)
        self.assertEqual(worker.run_one().attempts, 2)

    def test_backoff_cap_exact_boundaries_and_exhaustion(self):
        store = self.other(retry_base_seconds=2, retry_cap_seconds=5)
        job = store.enqueue("echo", 1, max_attempts=4)
        for attempt, delay in ((1, 2), (2, 4), (3, 5)):
            claimed = store.claim("worker", lease_seconds=20)
            self.assertEqual(claimed.attempts, attempt)
            failed_at = self.clock()
            queued = store.fail(job.id, claimed.lease_token, "try again")
            self.assertEqual(queued.available_at, failed_at + delay)
            self.no_lease(queued)
            self.clock.advance(delay - 0.25)
            self.assertIsNone(store.claim("early"))
            self.clock.advance(0.25)
        last = store.claim("worker")
        terminal = store.fail(job.id, last.lease_token, "last failure")
        self.assertEqual((terminal.state, terminal.attempts, terminal.error), ("failed", 4, "last failure"))
        self.no_lease(terminal)
        self.clock.advance(10000)
        self.assertIsNone(store.claim("later"))

    def test_recovery_anchors_delay_at_recovery_time(self):
        job = self.claimed()
        self.clock.advance(100)
        self.assertEqual(self.other().reap_expired(), 1)
        recovered = self.store.get(job.id)
        self.assertEqual(recovered.available_at, 1101)
        self.assertEqual(recovered.error, "lease expired")
        self.assertEqual(recovered.attempts, 1)
        self.no_lease(recovered)
        history = self.history(job.id)
        self.assertEqual(self.store.reap_expired(), 0)
        self.assertEqual(history, self.history(job.id))

    def test_expired_last_attempt_is_failed(self):
        job = self.claimed(attempts=1)
        self.clock.advance(10)
        self.assertIsNone(self.other().claim("replacement"))
        terminal = self.store.get(job.id)
        self.assertEqual((terminal.state, terminal.error, terminal.attempts), ("failed", "lease expired", 1))
        self.no_lease(terminal)

    def test_claim_order_uses_availability_then_original_insertion(self):
        first = self.store.enqueue("echo", "first")
        second = self.store.enqueue("echo", "second")
        lease = self.store.claim("one", lease_seconds=20)
        self.assertEqual(lease.id, first.id)
        self.store.fail(first.id, lease.lease_token, "retry")
        self.clock.advance(1)
        third = self.store.enqueue("echo", "third")
        selected = self.store.claim("two", lease_seconds=20)
        self.assertEqual(selected.id, second.id)
        self.store.complete(selected.id, selected.lease_token, None)
        selected = self.store.claim("three")
        self.assertEqual(selected.id, first.id)
        self.assertNotEqual(selected.id, third.id)

    def test_large_existing_attempt_count_caps_without_overflow(self):
        job = self.store.enqueue("echo", None, max_attempts=1000001)
        # Existing schema is a public migration input, not a prescribed new design.
        with sqlite3.connect(self.path) as connection:
            connection.execute("UPDATE jobs SET attempts=999999 WHERE id=?", (job.id,))
        lease = self.store.claim("worker", lease_seconds=30)
        queued = self.store.fail(job.id, lease.lease_token, "still retryable")
        self.assertEqual(queued.available_at, 1060)
        self.assertEqual(queued.attempts, 1000000)

    def test_policy_validation(self):
        for base, cap in ((0, 1), (2, 1), (True, 2), (1, float("inf")), (float("nan"), 2)):
            with self.assertRaises(jobservice.ValidationError):
                self.other(retry_base_seconds=base, retry_cap_seconds=cap)
