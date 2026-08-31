"""Request identity supplied by an in-process adapter, never production auth."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RequestContext:
    actor_id: int
    tenant_id: Optional[int] = None
