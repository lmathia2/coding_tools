"""Durable, explicitly driven CSV jobs; no threads or wall-clock dependencies."""

import csv
import io

from .auth import operation
from .context import RequestContext
from .errors import DomainError
from .service import positive_id


def public_job(job):
    return {key: job[key] for key in
            ("id", "tenant_id", "requested_by", "project_id", "state", "error")}


class Exports:
    def __init__(self, database, repository, authorizer):
        self.db = database
        self.repo = repository
        self.auth = authorizer

    @operation()
    def enqueue(self, context, project_id=None):
        if project_id is not None:
            positive_id(project_id, "project_id")
            self.repo.project(context.tenant_id, project_id)
        with self.db.transaction():
            cursor = self.db.connection.execute(
                "INSERT INTO export_jobs(tenant_id,requested_by,project_id,state) "
                "VALUES(?,?,?,'queued')",
                (context.tenant_id or 1, context.actor_id, project_id),
            )
            self.auth.event(context, "export.queued", cursor.lastrowid)
        return public_job(self.repo.export(context.tenant_id, cursor.lastrowid))

    @operation()
    def get(self, context, export_id):
        positive_id(export_id)
        return public_job(self.repo.export(context.tenant_id, export_id))

    @operation()
    def download(self, context, export_id):
        positive_id(export_id)
        job = self.repo.export(context.tenant_id, export_id)
        if job["state"] != "ready":
            raise DomainError(409, "export_unavailable", "Export is not ready")
        return job["content"]

    def run_next(self):
        """Run one oldest queued job; return public metadata or None."""
        with self.db.transaction():
            row = self.db.connection.execute(
                "SELECT * FROM export_jobs WHERE state='queued' ORDER BY id LIMIT 1"
            ).fetchone()
            if row is None:
                return None
            job = dict(row)
            context = RequestContext(job["requested_by"], job["tenant_id"])
            issues = self.repo.issues(job["tenant_id"], project_id=job["project_id"])
            output = io.StringIO(newline="")
            writer = csv.writer(output, lineterminator="\n")
            writer.writerow(["id", "project_id", "title", "status"])
            for issue in issues:
                writer.writerow([issue[key] for key in ("id", "project_id", "title", "status")])
            self.db.connection.execute(
                "UPDATE export_jobs SET state='ready',content=?,error=NULL WHERE id=?",
                (output.getvalue(), job["id"]),
            )
            self.auth.event(context, "export.ready", job["id"])
            job.update(state="ready", error=None)
            return public_job(job)
