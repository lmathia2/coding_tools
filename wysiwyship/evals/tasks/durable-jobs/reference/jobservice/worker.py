"""Synchronous leased worker; handlers run outside database transactions."""

import os
import socket
import uuid

from .context import ExecutionContext, discard_log
from .errors import LeaseLost, ValidationError
from .handlers import default_registry
from .validation import kind_filter, positive_integer, positive_seconds, text


class Worker:
    def __init__(self, store, registry=None, *, worker_id=None, logger=None, lease_seconds=30.0):
        self.store = store
        self.registry = registry if registry is not None else default_registry()
        self.worker_id = worker_id or "%s:%s:%s" % (socket.gethostname(), os.getpid(), uuid.uuid4().hex[:8])
        text(self.worker_id, "worker_id")
        self.logger = logger if logger is not None else discard_log
        self.lease_seconds = positive_seconds(lease_seconds, "lease_seconds")

    def run_one(self, *, kinds=None):
        job = self.store.claim(self.worker_id, kinds=kinds, lease_seconds=self.lease_seconds)
        if job is None:
            return None
        context = ExecutionContext(
            job.id, job.attempts, self.worker_id, self.logger,
            lambda: self.store.heartbeat(job.id, job.lease_token, lease_seconds=self.lease_seconds),
        )
        try:
            try:
                result = self.registry.resolve(job.kind)(job.payload, context)
            except LeaseLost:
                raise
            except Exception as exc:
                return self.store.fail(job.id, job.lease_token, "%s: %s" % (type(exc).__name__, exc))
            try:
                return self.store.complete(job.id, job.lease_token, result)
            except ValidationError as exc:
                # Only an invalid result is a handler error; storage errors escape.
                return self.store.fail(job.id, job.lease_token, "%s: %s" % (type(exc).__name__, exc))
        except LeaseLost:
            return self.store.get(job.id)

    def run_until_idle(self, *, max_jobs=100, kinds=None):
        positive_integer(max_jobs, "max_jobs")
        kinds = kind_filter(kinds)
        outcomes = []
        for _ in range(max_jobs):
            result = self.run_one(kinds=kinds)
            if result is None:
                break
            outcomes.append(result)
        return outcomes
