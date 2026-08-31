"""Small framework-free HTTP-like adapter. It does not open a network socket."""

import re
from dataclasses import dataclass
from typing import Any

from .auth import Authorizer
from .cache import QueryCache
from .context import RequestContext
from .database import Database
from .errors import DomainError, invalid, missing
from .exports import Exports
from .repository import Repository
from .service import Service


@dataclass
class Response:
    status: int
    body: Any


class App:
    def __init__(self, database_path=":memory:"):
        self.db = Database(database_path)
        self.repo = Repository(self.db)
        self.auth = Authorizer(self.db)
        self.cache = QueryCache()
        self.service = Service(self.db, self.repo, self.auth, self.cache)
        self.exports = Exports(self.db, self.repo, self.auth)

    def close(self):
        self.db.close()

    def request(self, method, path, *, actor_id=None, tenant_id=None, body=None, query=None):
        context = RequestContext(actor_id, tenant_id)
        body = {} if body is None else body
        query = {} if query is None else query
        try:
            if not isinstance(body, dict) or not isinstance(query, dict):
                raise invalid("body and query must be objects")
            return self._dispatch(method.upper(), path, context, body, query)
        except DomainError as error:
            return Response(error.status, error.payload())

    def _dispatch(self, method, path, context, body, query):
        if path == "/projects":
            return self._projects(method, context, body)
        if path == "/issues":
            return self._issues(method, context, body, query)
        if path == "/issues/bulk" and method == "POST":
            return Response(200, self.service.bulk_update(context, body.get("ids"), body.get("changes")))
        match = re.fullmatch(r"/issues/(\d+)(/comments)?", path)
        if match:
            return self._issue_resource(method, context, int(match.group(1)), bool(match.group(2)), body)
        if path == "/exports" and method == "POST":
            return Response(202, self.exports.enqueue(context, body.get("project_id")))
        match = re.fullmatch(r"/exports/(\d+)(/download)?", path)
        if match and method == "GET":
            export_id = int(match.group(1))
            if match.group(2):
                return Response(200, self.exports.download(context, export_id))
            return Response(200, self.exports.get(context, export_id))
        if path == "/audit" and method == "GET":
            return Response(200, self.service.list_audit(context))
        raise missing()

    def _projects(self, method, context, body):
        if method == "GET":
            return Response(200, self.service.list_projects(context))
        if method == "POST":
            return Response(201, self.service.create_project(context, body.get("name")))
        raise missing()

    def _issues(self, method, context, body, query):
        if method == "GET":
            return Response(200, self.service.list_issues(
                context, query.get("q", ""), query.get("status"), query.get("project_id")))
        if method == "POST":
            return Response(201, self.service.create_issue(
                context, body.get("project_id"), body.get("title")))
        raise missing()

    def _issue_resource(self, method, context, issue_id, comments, body):
        if comments:
            if method == "GET":
                return Response(200, self.service.list_comments(context, issue_id))
            if method == "POST":
                return Response(201, self.service.add_comment(context, issue_id, body.get("text")))
            raise missing()
        if method == "GET":
            return Response(200, self.service.get_issue(context, issue_id))
        if method == "PATCH":
            return Response(200, self.service.update_issue(context, issue_id, body))
        raise missing()
