"""Detached records: callers never hold live SQLite cursors."""

import json
from dataclasses import asdict, dataclass
from typing import Any, Optional


STATES = ("queued", "running", "succeeded", "failed", "cancelled")
TERMINAL_STATES = frozenset(("succeeded", "failed", "cancelled"))


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
    available_at: float = 0.0
    idempotency_key: Optional[str] = None
    cancel_requested: bool = False
    lease_owner: Optional[str] = None
    lease_token: Optional[str] = None
    lease_expires_at: Optional[float] = None

    def to_dict(self):
        return asdict(self)


def decode_job(row):
    values = dict(row)
    values.pop("seq", None)
    values["payload"] = json.loads(values["payload"])
    values["result"] = json.loads(values["result"]) if values["result"] is not None else None
    values["cancel_requested"] = bool(values["cancel_requested"])
    return Job(**values)
