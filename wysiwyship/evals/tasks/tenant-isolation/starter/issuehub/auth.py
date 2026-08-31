"""Central service boundary for identity checks and denied-access audit events."""

import functools
import json

from .errors import DomainError


class Authorizer:
    def __init__(self, database):
        self.db = database

    def require(self, context, minimum_role="viewer"):
        user = self.db.connection.execute(
            "SELECT id FROM users WHERE id=?", (context.actor_id,)
        ).fetchone()
        if user is None:
            raise DomainError(401, "unauthenticated", "Known identity required")

    def record_denial(self, context, code):
        # Single-workspace deployments have no tenant audit partition.
        return None

    def event(self, context, action, resource_id=None, details=None):
        self.db.connection.execute(
            "INSERT INTO audit(tenant_id,actor_id,action,resource_id,details) "
            "VALUES(?,?,?,?,?)",
            (context.tenant_id or 1, context.actor_id, action, resource_id,
             json.dumps(details or {}, sort_keys=True)),
        )


def operation(role="viewer"):
    """Apply checks on every service invocation, including non-API callers."""
    def decorate(function):
        @functools.wraps(function)
        def checked(self, context, *args, **kwargs):
            try:
                self.auth.require(context, role)
                return function(self, context, *args, **kwargs)
            except DomainError as error:
                if error.status in (403, 404):
                    self.auth.record_denial(context, error.code)
                raise
        return checked
    return decorate
