"""Business operations and validation, usable without the API adapter."""

from .auth import operation
from .errors import invalid


def positive_id(value, name="id"):
    if type(value) is not int or value < 1:
        raise invalid(name + " must be a positive integer")
    return value


def nonempty(value, name):
    if not isinstance(value, str) or not value.strip():
        raise invalid(name + " must be non-empty text")
    return value.strip()


def issue_changes(changes):
    if not isinstance(changes, dict) or not changes:
        raise invalid("changes must be a non-empty object")
    if set(changes) - {"title", "status", "project_id"}:
        raise invalid("Unknown issue field")
    result = dict(changes)
    if "title" in result:
        result["title"] = nonempty(result["title"], "title")
    if "status" in result and result["status"] not in ("open", "closed"):
        raise invalid("status must be open or closed")
    if "project_id" in result:
        positive_id(result["project_id"], "project_id")
    return result


class Service:
    def __init__(self, database, repository, authorizer, cache):
        self.db = database
        self.repo = repository
        self.auth = authorizer
        self.cache = cache

    @operation()
    def list_projects(self, context):
        return self.repo.projects(context.tenant_id)

    @operation("admin")
    def create_project(self, context, name):
        name = nonempty(name, "name")
        with self.db.transaction():
            project = self.repo.create_project(context.tenant_id, name)
            self.auth.event(context, "project.created", project["id"])
        return project

    @operation()
    def get_issue(self, context, issue_id):
        positive_id(issue_id)
        cached = self.cache.get(context.tenant_id, "issue", issue_id)
        if cached is not None:
            return cached
        issue = self.repo.issue(context.tenant_id, issue_id)
        self.cache.put(context.tenant_id, "issue", issue_id, issue)
        return issue

    @operation()
    def list_issues(self, context, query="", status=None, project_id=None):
        if not isinstance(query, str):
            raise invalid("q must be text")
        if status is not None and status not in ("open", "closed"):
            raise invalid("status must be open or closed")
        if project_id is not None:
            positive_id(project_id, "project_id")
            self.repo.project(context.tenant_id, project_id)
        key = (query, status, project_id)
        cached = self.cache.get(context.tenant_id, "list", key)
        if cached is not None:
            return cached
        issues = self.repo.issues(context.tenant_id, query, status, project_id)
        self.cache.put(context.tenant_id, "list", key, issues)
        return issues

    @operation("editor")
    def create_issue(self, context, project_id, title):
        positive_id(project_id, "project_id")
        title = nonempty(title, "title")
        self.repo.project(context.tenant_id, project_id)
        with self.db.transaction():
            issue = self.repo.create_issue(context.tenant_id, context.actor_id, project_id, title)
            self.auth.event(context, "issue.created", issue["id"])
        self.cache.invalidate(context.tenant_id)
        return issue

    @operation("editor")
    def update_issue(self, context, issue_id, changes):
        positive_id(issue_id)
        changes = issue_changes(changes)
        self.repo.issue(context.tenant_id, issue_id)
        if "project_id" in changes:
            self.repo.project(context.tenant_id, changes["project_id"])
        with self.db.transaction():
            issue = self.repo.update_issue(context.tenant_id, issue_id, changes)
            self.auth.event(context, "issue.updated", issue_id)
        self.cache.invalidate(context.tenant_id)
        return issue

    @operation("editor")
    def bulk_update(self, context, ids, changes):
        if not isinstance(ids, list) or not ids or len(ids) > 100:
            raise invalid("ids must contain between 1 and 100 issue IDs")
        for issue_id in ids:
            positive_id(issue_id)
        if len(set(ids)) != len(ids):
            raise invalid("ids must be unique")
        changes = issue_changes(changes)
        with self.db.transaction():
            # Validate the complete batch before writing; the lock also prevents
            # another connection from changing these relations mid-transaction.
            for issue_id in ids:
                self.repo.issue(context.tenant_id, issue_id)
            if "project_id" in changes:
                self.repo.project(context.tenant_id, changes["project_id"])
            issues = [self.repo.update_issue(context.tenant_id, issue_id, changes)
                      for issue_id in ids]
            self.auth.event(context, "issues.bulk_updated", details={"count": len(ids)})
        self.cache.invalidate(context.tenant_id)
        return issues

    @operation()
    def list_comments(self, context, issue_id):
        positive_id(issue_id)
        self.repo.issue(context.tenant_id, issue_id)
        return self.repo.comments(context.tenant_id, issue_id)

    @operation("editor")
    def add_comment(self, context, issue_id, text):
        positive_id(issue_id)
        text = nonempty(text, "text")
        self.repo.issue(context.tenant_id, issue_id)
        with self.db.transaction():
            comment = self.repo.create_comment(context.tenant_id, context.actor_id, issue_id, text)
            self.auth.event(context, "comment.created", comment["id"])
        return comment

    @operation("admin")
    def list_audit(self, context):
        return self.repo.audit(context.tenant_id)
