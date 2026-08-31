"""Central service boundary for identity checks and denied-access audit events."""

import functools
import json

from .context import RequestContext
from .errors import DomainError, forbidden, invalid


class Authorizer:
    def __init__(self, database):
        self.db = database

    def require(self, context, minimum_role="viewer"):
        if (not isinstance(context, RequestContext)
                or type(context.actor_id) is not int or context.actor_id < 1):
            raise DomainError(401, "unauthenticated", "Known identity required")
        user = self.db.connection.execute(
            "SELECT id FROM users WHERE id=?", (context.actor_id,)
        ).fetchone()
        if user is None:
            raise DomainError(401, "unauthenticated", "Known identity required")
        if type(context.tenant_id) is not int or context.tenant_id < 1:
            raise invalid("tenant_id must be a positive integer")
        membership = self.db.connection.execute(
            "SELECT role FROM memberships WHERE tenant_id=? AND user_id=? AND active=1",
            (context.tenant_id, context.actor_id),
        ).fetchone()
        ranks = {"viewer": 0, "editor": 1, "admin": 2}
        if membership is None or ranks[membership["role"]] < ranks[minimum_role]:
            raise forbidden()

    def record_denial(self, context, code):
        # Never let unaffiliated callers append to another tenant's audit stream.
        if not isinstance(context, RequestContext):
            return
        membership = self.db.connection.execute(
            "SELECT 1 FROM memberships WHERE tenant_id=? AND user_id=? AND active=1",
            (context.tenant_id, context.actor_id),
        ).fetchone()
        if membership:
            self.event(context, "access.denied", details={"code": code})

    def event(self, context, action, resource_id=None, details=None):
        self.db.connection.execute(
            "INSERT INTO audit(tenant_id,actor_id,action,resource_id,details) "
            "VALUES(?,?,?,?,?)",
            (context.tenant_id, context.actor_id, action, resource_id,
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
