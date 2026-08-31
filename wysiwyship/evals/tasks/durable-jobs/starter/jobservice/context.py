"""Per-invocation metadata and structured, injectable handler logging."""

from dataclasses import dataclass
from typing import Callable


def discard_log(record):
    pass


@dataclass(frozen=True)
class ExecutionContext:
    job_id: str
    attempt: int
    worker_id: str
    logger: Callable = discard_log

    def log(self, message, **fields):
        self.logger(dict(fields, job_id=self.job_id, attempt=self.attempt,
                         worker_id=self.worker_id, message=message))
