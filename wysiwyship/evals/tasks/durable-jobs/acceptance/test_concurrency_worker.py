import json
import os
import select
import sqlite3
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest.mock import patch

import jobservice

from acceptance_support import QueueCase


class ConcurrencyTests(QueueCase):
    def test_distinct_connections_claim_each_job_once(self):
        jobs = [self.store.enqueue("echo", index) for index in range(8)]
        barrier = Barrier(12)
        def claim(index):
            store = self.other()
            barrier.wait(timeout=10)
            return store.claim("worker-%d" % index, lease_seconds=30)
        with ThreadPoolExecutor(max_workers=12) as executor:
            claimed = [j for j in executor.map(claim, range(12)) if j is not None]
        self.assertEqual({j.id for j in claimed}, {j.id for j in jobs})
        self.assertEqual(len(claimed), 8)
        self.assertTrue(all(j.attempts == 1 for j in claimed))
        self.assertEqual(len({j.lease_token for j in claimed}), 8)
        for job in jobs:
            self.assertEqual(sum(e["type"] == "claimed" for e in self.history(job.id)), 1)

    def test_competing_processes_do_not_double_claim(self):
        jobs = [self.store.enqueue("echo", index) for index in range(4)]
        script = """
import json, sys
from jobservice import JobStore
store = JobStore(sys.argv[1], clock=lambda: 1000.0)
print('ready', flush=True)
sys.stdin.readline()
job = store.claim(sys.argv[2], lease_seconds=30)
print(json.dumps(job.to_dict() if job else None), flush=True)
"""
        processes = []
        try:
            for index in range(6):
                processes.append(subprocess.Popen([sys.executable, "-c", script, str(self.path), "process-%d" % index], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=os.environ.copy()))
            for process in processes:
                self.assertTrue(select.select([process.stdout], [], [], 10)[0], "child never reached start gate")
                self.assertEqual(process.stdout.readline().strip(), "ready")
            for process in processes:
                process.stdin.write("go\n")
                process.stdin.flush()
            outputs = []
            for process in processes:
                stdout, stderr = process.communicate(timeout=15)
                self.assertEqual(process.returncode, 0, stderr)
                value = json.loads(stdout)
                if value is not None:
                    outputs.append(value)
            self.assertEqual({j["id"] for j in outputs}, {j.id for j in jobs})
            self.assertEqual(len(outputs), 4)
            self.assertTrue(all(j["attempts"] == 1 for j in outputs))
        finally:
            for process in processes:
                if process.poll() is None:
                    process.kill()
                process.communicate(timeout=5)

    def test_crashed_process_claim_is_recoverable_and_old_token_fenced(self):
        job = self.store.enqueue("echo", "survives")
        script = """
import json, os, sys
from jobservice import JobStore
store = JobStore(sys.argv[1], clock=lambda: 1000.0)
job = store.claim('crashing-process', lease_seconds=5)
os.write(1, (json.dumps(job.to_dict()) + '\\n').encode())
os._exit(17)
"""
        process = subprocess.run([sys.executable, "-c", script, str(self.path)], capture_output=True, text=True, timeout=10, env=os.environ.copy())
        self.assertEqual(process.returncode, 17, process.stderr)
        abandoned = json.loads(process.stdout)
        self.assertEqual(self.other().get(job.id).state, "running")
        self.clock.advance(5)
        self.assertEqual(self.other().reap_expired(), 1)
        self.clock.advance(1)
        replacement = self.other().claim("replacement")
        self.assertEqual(replacement.id, job.id)
        self.assertEqual(replacement.attempts, 2)
        self.assert_lost_unchanged(job.id, lambda: self.store.complete(job.id, abandoned["lease_token"], "stale"))
        self.assertEqual(self.other().complete(job.id, replacement.lease_token, "durable").result, "durable")

    def test_cancel_completion_race_has_only_serializable_outcomes(self):
        for index in range(6):
            job = self.claimed()
            barrier = Barrier(2)
            def cancel():
                store = self.other()
                barrier.wait(timeout=10)
                return store.cancel(job.id)
            def complete():
                store = self.other()
                barrier.wait(timeout=10)
                return store.complete(job.id, job.lease_token, "finished")
            with ThreadPoolExecutor(max_workers=2) as executor:
                a, b = executor.submit(cancel), executor.submit(complete)
                a.result(timeout=15)
                b.result(timeout=15)
            result = self.store.get(job.id)
            types = [e["type"] for e in self.history(job.id)]
            if result.state == "succeeded":
                self.assertEqual(result.result, "finished")
                self.assertEqual(types, ["enqueued", "claimed", "succeeded"])
            else:
                self.assertEqual(result.state, "cancelled")
                self.assertIsNone(result.result)
                self.assertEqual(types, ["enqueued", "claimed", "cancel_requested", "cancelled"])


class WorkerLeaseTests(QueueCase):
    def test_storage_failure_is_not_reported_as_a_job_outcome(self):
        job = self.store.enqueue("echo", "result")
        with patch.object(self.store, "complete", side_effect=sqlite3.OperationalError("disk unavailable")):
            with self.assertRaises(sqlite3.OperationalError):
                jobservice.Worker(self.store).run_one()
        self.assertEqual(self.store.get(job.id).state, "running")

    def test_stale_worker_return_does_not_overwrite_replacement(self):
        effects = []
        def handler(payload, context):
            effects.append(context.attempt)
            if context.attempt == 2:
                return "winner"
            self.clock.advance(5)
            self.other().reap_expired()
            self.clock.advance(1)
            replacement = jobservice.Worker(self.other(), registry, worker_id="replacement", lease_seconds=10).run_one()
            self.assertEqual(replacement.result, "winner")
            return "stale result"
        registry = jobservice.HandlerRegistry().register("effect", handler)
        job = self.store.enqueue("effect", None)
        result = jobservice.Worker(self.store, registry, lease_seconds=5).run_one()
        self.assertEqual(result.result, "winner")
        self.assertEqual(self.store.get(job.id).attempts, 2)
        self.assertEqual(effects, [1, 2], "effects can repeat while only one result is authoritative")
        self.assertEqual(sum(e["type"] == "succeeded" for e in self.history(job.id)), 1)

    def test_stale_handler_exception_returns_durable_snapshot(self):
        def handler(payload, context):
            self.clock.advance(5)
            self.other().reap_expired()
            raise RuntimeError("late failure must not replace lease-expired error")
        registry = jobservice.HandlerRegistry().register("slow", handler)
        job = self.store.enqueue("slow", None)
        result = jobservice.Worker(self.store, registry, lease_seconds=5).run_one()
        self.assertEqual((result.id, result.state, result.error), (job.id, "queued", "lease expired"))

    def test_non_json_handler_result_enters_retry_path(self):
        registry = jobservice.HandlerRegistry().register("bad-result", lambda p, c: {"x": object()})
        job = self.store.enqueue("bad-result", None, max_attempts=1)
        result = jobservice.Worker(self.store, registry).run_one()
        self.assertEqual(result.state, "failed")
        self.assertIn("ValidationError", result.error)
        self.assertIsNone(self.store.get(job.id).result)

    def test_explicit_heartbeat_extends_handler_lifetime(self):
        def handler(payload, context):
            self.clock.advance(4)
            self.assertFalse(context.heartbeat())
            self.assertEqual(self.store.get(context.job_id).lease_expires_at, 1009)
            self.clock.advance(4)
            return "still live"
        registry = jobservice.HandlerRegistry().register("long", handler)
        self.store.enqueue("long", None)
        result = jobservice.Worker(self.store, registry, lease_seconds=5).run_one()
        self.assertEqual(result.state, "succeeded")

    def test_generator_kind_filter_is_reusable_over_a_poll_cycle(self):
        self.store.enqueue("echo", 1)
        self.store.enqueue("echo", 2)
        self.store.enqueue("summary", {"values": [3]})
        outcomes = jobservice.Worker(self.store).run_until_idle(kinds=(x for x in ["echo"]))
        self.assertEqual([job.result for job in outcomes], [1, 2])
