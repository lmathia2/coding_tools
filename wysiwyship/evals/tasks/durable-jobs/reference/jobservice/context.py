"""Per-invocation metadata, correlated logs and cooperative lease/cancel checks."""

from dataclasses import dataclass
from typing import Callable, Optional

from .errors import JobCancelled


def discard_log(record):
    pass


@dataclass(frozen=True)
class ExecutionContext:
    job_id: str
    attempt: int
    worker_id: str
    logger: Callable = discard_log
    renew: Optional[Callable] = None

    def log(self, message, **fields):
        self.logger(dict(fields, job_id=self.job_id, attempt=self.attempt,
                         worker_id=self.worker_id, message=message))

    def heartbeat(self):
        if self.renew is None:
            raise RuntimeError("context has no live lease")
        return self.renew().cancel_requested

    def check_cancelled(self):
        if self.heartbeat():
            raise JobCancelled("cancellation requested")
