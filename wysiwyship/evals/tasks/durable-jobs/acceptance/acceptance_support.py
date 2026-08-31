"""Evaluator-owned fixtures; import only legacy symbols at module scope."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import jobservice


class QueueCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "queue.sqlite"
        self.clock = jobservice.ManualClock(1000)
        self.store = jobservice.JobStore(self.path, clock=self.clock)

    def other(self, **kwargs):
        return jobservice.JobStore(self.path, clock=self.clock, **kwargs)

    def claimed(self, *, attempts=3, duration=10, kind="echo"):
        job = self.store.enqueue(kind, {"value": 7}, max_attempts=attempts)
        claim = self.store.claim("worker-a", lease_seconds=duration, kinds=[kind])
        self.assertEqual(claim.id, job.id)
        return claim

    def no_lease(self, job):
        self.assertIsNone(job.lease_owner)
        self.assertIsNone(job.lease_token)
        self.assertIsNone(job.lease_expires_at)

    def history(self, job_id):
        return self.store.events(job_id, limit=1000)

    def assert_lost_unchanged(self, job_id, operation):
        before = self.store.get(job_id).to_dict()
        history = self.history(job_id)
        with self.assertRaises(jobservice.LeaseLost):
            operation()
        self.assertEqual(self.store.get(job_id).to_dict(), before)
        self.assertEqual(self.history(job_id), history)

    def cli(self, *arguments, expected=0, stdin=None):
        result = subprocess.run(
            [sys.executable, "-m", "jobservice", "--db", str(self.path)] + list(arguments),
            input=stdin, text=True, capture_output=True, timeout=10, env=os.environ.copy(),
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        if expected == 0:
            self.assertEqual(result.stderr, "")
        return result
