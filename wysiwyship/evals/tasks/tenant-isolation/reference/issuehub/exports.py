"""Durable, explicitly driven CSV jobs; no threads or wall-clock dependencies."""

import csv
import io

from .auth import operation
from .context import RequestContext
from .errors import DomainError, missing
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
                (context.tenant_id, context.actor_id, project_id),
            )
            self.auth.event(context, "export.queued", cursor.lastrowid)
        return public_job(self.repo.export(context.tenant_id, cursor.lastrowid))

    def _owned_job(self, context, export_id):
        positive_id(export_id)
        job = self.repo.export(context.tenant_id, export_id)
        if job["requested_by"] != context.actor_id:
            raise missing()
        return job

    @operation()
    def get(self, context, export_id):
        return public_job(self._owned_job(context, export_id))

    @operation()
    def download(self, context, export_id):
        job = self._owned_job(context, export_id)
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
            try:
                # Job arguments are not an authorization grant. Read current
                # membership under the same transaction used to produce bytes.
                self.auth.require(context)
                if job["project_id"] is not None:
                    self.repo.project(context.tenant_id, job["project_id"])
            except DomainError:
                self.db.connection.execute(
                    "UPDATE export_jobs SET state='denied',content=NULL,error=? WHERE id=?",
                    ("authorization_revoked", job["id"]),
                )
                self.auth.event(context, "export.denied", job["id"],
                                {"reason": "authorization_revoked"})
                job.update(state="denied", error="authorization_revoked")
                return public_job(job)
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
