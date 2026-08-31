"""Detached records: callers never hold live SQLite cursors."""

import json
from dataclasses import asdict, dataclass
from typing import Any, Optional


STATES = ("queued", "running", "succeeded", "failed")
TERMINAL_STATES = frozenset(("succeeded", "failed"))


@dataclass(frozen=True)
class Job:
    id: str
    kind: str
    payload: Any
    state: str
    attempts: int
    max_attempts: int
    created_at: float
    updated_at: float
    result: Any = None
    error: Optional[str] = None

    def to_dict(self):
        return asdict(self)


def decode_job(row):
    return Job(
        id=row["id"], kind=row["kind"], payload=json.loads(row["payload"]),
        state=row["state"], attempts=row["attempts"],
        max_attempts=row["max_attempts"], created_at=row["created_at"],
        updated_at=row["updated_at"],
        result=json.loads(row["result"]) if row["result"] is not None else None,
        error=row["error"],
    )
