import jobservice

from acceptance_support import QueueCase


class CancellationTests(QueueCase):
    def test_queued_cancel_is_terminal_and_repeat_is_noop(self):
        job = self.store.enqueue("echo", "never run")
        cancelled = self.other().cancel(job.id)
        self.assertEqual(cancelled.state, "cancelled")
        self.assertTrue(cancelled.cancel_requested)
        self.assertEqual(cancelled.attempts, 0)
        self.no_lease(cancelled)
        self.clock.advance(3)
        events = self.history(job.id)
        self.assertEqual(self.store.cancel(job.id), cancelled)
        self.assertEqual(self.history(job.id), events)
        self.assertIsNone(self.store.claim("worker"))
        self.assertEqual(self.store.stats()["cancelled"], 1)

    def test_running_cancel_keeps_lease_and_completion_cannot_win_later(self):
        job = self.claimed()
        requested = self.other().cancel(job.id)
        self.assertEqual(requested.state, "running")
        self.assertEqual(requested.lease_token, job.lease_token)
        self.assertEqual(requested.attempts, 1)
        self.assertTrue(self.store.heartbeat(job.id, job.lease_token).cancel_requested)
        finished = self.store.complete(job.id, job.lease_token, "must not commit")
        self.assertEqual(finished.state, "cancelled")
        self.assertIsNone(finished.result)
        self.no_lease(finished)

    def test_running_cancel_failure_and_expiry_do_not_retry(self):
        for finish_by in ("failure", "expiry"):
            with self.subTest(finish_by=finish_by):
                job = self.claimed()
                self.store.cancel(job.id)
                if finish_by == "failure":
                    terminal = self.store.fail(job.id, job.lease_token, "stopping")
                else:
                    self.clock.advance(10)
                    self.assertEqual(self.store.reap_expired(), 1)
                    terminal = self.store.get(job.id)
                self.assertEqual(terminal.state, "cancelled")
                self.assertIsNone(terminal.result)
                self.no_lease(terminal)
        self.assertIsNone(self.store.claim("worker"))

    def test_cancel_terminal_success_and_failure_preserves_records(self):
        for fail in (False, True):
            job = self.claimed(attempts=1)
            terminal = self.store.fail(job.id, job.lease_token, "finished") if fail else self.store.complete(job.id, job.lease_token, "committed")
            before = self.history(job.id)
            self.clock.advance(1)
            self.assertEqual(self.store.cancel(job.id), terminal)
            self.assertEqual(self.history(job.id), before)
            self.assertFalse(self.store.get(job.id).cancel_requested)

    def test_duplicate_running_request_adds_no_event_or_timestamp(self):
        job = self.claimed()
        first = self.store.cancel(job.id)
        before = self.history(job.id)
        self.clock.advance(1)
        self.assertEqual(self.other().cancel(job.id), first)
        self.assertEqual(self.history(job.id), before)

    def test_cooperative_handler_context_observes_cancel(self):
        saw = []
        def handler(payload, context):
            self.assertFalse(context.heartbeat())
            self.other().cancel(context.job_id)
            saw.append(context.heartbeat())
            context.check_cancelled()
            self.fail("cancelled handler continued")
        registry = jobservice.HandlerRegistry().register("cooperative", handler)
        job = self.store.enqueue("cooperative", None)
        result = jobservice.Worker(self.store, registry, lease_seconds=7).run_one()
        self.assertEqual(result.state, "cancelled")
        self.assertEqual(saw, [True])
        self.assertEqual(self.store.get(job.id).attempts, 1)

    def test_unsolicited_job_cancelled_exception_is_a_normal_failure(self):
        def handler(payload, context):
            raise jobservice.JobCancelled("no durable request")
        registry = jobservice.HandlerRegistry().register("self-cancel", handler)
        self.store.enqueue("self-cancel", None, max_attempts=1)
        result = jobservice.Worker(self.store, registry).run_one()
        self.assertEqual(result.state, "failed")
        self.assertFalse(result.cancel_requested)

    def test_missing_cancel_is_explicit(self):
        with self.assertRaises(jobservice.JobNotFound):
            self.store.cancel("absent")
