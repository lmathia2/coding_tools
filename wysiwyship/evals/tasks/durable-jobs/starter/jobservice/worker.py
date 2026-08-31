"""Synchronous worker; a supervisor decides when another poll is appropriate."""

import os
import socket
import uuid

from .context import ExecutionContext, discard_log
from .handlers import default_registry
from .validation import positive_integer, text


class Worker:
    def __init__(self, store, registry=None, *, worker_id=None, logger=None):
        self.store = store
        self.registry = registry if registry is not None else default_registry()
        self.worker_id = worker_id or "%s:%s:%s" % (socket.gethostname(), os.getpid(), uuid.uuid4().hex[:8])
        text(self.worker_id, "worker_id")
        self.logger = logger if logger is not None else discard_log

    def run_one(self, *, kinds=None):
        job = self.store.claim(self.worker_id, kinds=kinds)
        if job is None:
            return None
        context = ExecutionContext(job.id, job.attempts, self.worker_id, self.logger)
        try:
            result = self.registry.resolve(job.kind)(job.payload, context)
        except Exception as exc:
            return self.store.fail(job.id, "%s: %s" % (type(exc).__name__, exc))
        return self.store.complete(job.id, result)

    def run_until_idle(self, *, max_jobs=100, kinds=None):
        positive_integer(max_jobs, "max_jobs")
        outcomes = []
        for _ in range(max_jobs):
            result = self.run_one(kinds=kinds)
            if result is None:
                break
            outcomes.append(result)
        return outcomes
