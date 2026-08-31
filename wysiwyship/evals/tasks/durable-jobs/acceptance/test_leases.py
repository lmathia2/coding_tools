import jobservice

from acceptance_support import QueueCase


class LeaseContractTests(QueueCase):
    def test_claim_has_live_capability_and_stable_attempt(self):
        job = self.claimed()
        self.assertEqual(job.state, "running")
        self.assertEqual(job.attempts, 1)
        self.assertEqual(job.lease_owner, "worker-a")
        self.assertIsInstance(job.lease_token, str)
        self.assertTrue(job.lease_token)
        self.assertEqual(job.lease_expires_at, 1010)
        self.assertIsNone(self.other().claim("worker-b"))
        self.assertEqual(self.store.get(job.id).to_dict(), job.to_dict())

    def test_heartbeat_renews_from_now_not_old_expiry(self):
        job = self.claimed()
        self.clock.advance(3)
        renewed = self.other().heartbeat(job.id, job.lease_token, lease_seconds=20)
        self.assertEqual(renewed.lease_expires_at, 1023)
        self.assertEqual(renewed.lease_token, job.lease_token)
        self.assertEqual(renewed.attempts, 1)
        self.clock.advance(7)
        self.assertEqual(self.store.reap_expired(), 0)
        done = self.store.complete(job.id, job.lease_token, {"ok": True})
        self.assertEqual(done.state, "succeeded")
        self.no_lease(done)

    def test_expiry_equality_fences_all_writes_before_reaping(self):
        job = self.claimed()
        self.clock.advance(10)
        for operation in (
            lambda: self.store.complete(job.id, job.lease_token, "stale"),
            lambda: self.store.fail(job.id, job.lease_token, "stale failure"),
            lambda: self.store.heartbeat(job.id, job.lease_token),
        ):
            with self.subTest(operation=operation):
                self.assert_lost_unchanged(job.id, operation)
        self.assertEqual(self.store.get(job.id).state, "running")

    def test_wrong_missing_and_terminal_tokens_never_write(self):
        job = self.claimed()
        for token in (None, "", "different-token", 123):
            self.assert_lost_unchanged(job.id, lambda: self.store.complete(job.id, token, "x"))
        self.store.complete(job.id, job.lease_token, "committed")
        self.assert_lost_unchanged(job.id, lambda: self.store.fail(job.id, job.lease_token, "late"))
        self.assert_lost_unchanged(job.id, lambda: self.store.complete(job.id, job.lease_token, "twice"))

    def test_reclaimed_token_changes_even_for_same_worker(self):
        first = self.claimed()
        self.clock.advance(10)
        self.assertEqual(self.store.reap_expired(), 1)
        self.clock.advance(1)
        second = self.store.claim("worker-a", lease_seconds=10)
        self.assertNotEqual(second.lease_token, first.lease_token)
        self.assertEqual(second.attempts, 2)
        self.assert_lost_unchanged(first.id, lambda: self.other().complete(first.id, first.lease_token, "old"))
        self.assertEqual(self.other().complete(second.id, second.lease_token, "new").result, "new")

    def test_invalid_claim_does_not_recover_expired_work(self):
        job = self.claimed()
        self.clock.advance(10)
        before = self.history(job.id)
        for duration in (0, -1, True, float("inf"), float("nan"), "30"):
            with self.assertRaises(jobservice.ValidationError):
                self.store.claim("worker-b", lease_seconds=duration)
        for kinds in ("echo", [""], 3):
            with self.assertRaises(jobservice.ValidationError):
                self.store.claim("worker-b", kinds=kinds)
        self.assertEqual(self.store.get(job.id).state, "running")
        self.assertEqual(self.history(job.id), before)

    def test_empty_and_unmatched_filters_still_recover(self):
        job = self.claimed()
        self.clock.advance(10)
        self.assertIsNone(self.store.claim("worker-b", kinds=[]))
        self.assertEqual(self.store.get(job.id).state, "queued")
        self.assertEqual(self.store.get(job.id).available_at, 1011)
        self.assertIsNone(self.store.claim("worker-b", kinds=["unconfigured"]))

    def test_reads_do_not_recover_or_change_history(self):
        job = self.claimed()
        self.clock.advance(20)
        self.assertEqual(self.store.get(job.id).state, "running")
        self.assertEqual(self.store.list_jobs(state="running")[0].id, job.id)
        self.assertEqual(self.store.stats()["running"], 1)
        self.assertEqual([event["type"] for event in self.history(job.id)], ["enqueued", "claimed"])
