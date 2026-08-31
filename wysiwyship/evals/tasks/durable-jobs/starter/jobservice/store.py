"""Persistent submission, query, and immediate-retry queue operations."""

import uuid

from .clock import SystemClock
from .database import Database
from .errors import JobNotFound, ValidationError
from .model import STATES, decode_job
from .validation import json_text, page, positive_integer, text


class JobStore:
    def __init__(self, path, *, clock=None):
        self.database = Database(path)
        self.clock = clock if clock is not None else SystemClock()

    def _get(self, connection, job_id):
        row = connection.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        if row is None:
            raise JobNotFound(job_id)
        return decode_job(row)

    def enqueue(self, kind, payload, *, max_attempts=3):
        text(kind, "kind")
        positive_integer(max_attempts, "max_attempts")
        encoded = json_text(payload)
        now = self.clock()
        job_id = uuid.uuid4().hex
        with self.database.transaction() as connection:
            connection.execute(
                "INSERT INTO jobs(id,kind,payload,state,max_attempts,created_at,updated_at) "
                "VALUES(?,?,?,'queued',?,?,?)",
                (job_id, kind, encoded, max_attempts, now, now),
            )
            return self._get(connection, job_id)

    def get(self, job_id):
        with self.database.connect() as connection:
            return self._get(connection, job_id)

    def list_jobs(self, *, state=None, kind=None, limit=100, offset=0):
        page(limit, offset)
        if state is not None and state not in STATES:
            raise ValidationError("unknown state: " + str(state))
        clauses, values = [], []
        if state is not None:
            clauses.append("state=?")
            values.append(state)
        if kind is not None:
            text(kind, "kind")
            clauses.append("kind=?")
            values.append(kind)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM jobs" + where + " ORDER BY created_at,seq LIMIT ? OFFSET ?",
                values + [limit, offset],
            ).fetchall()
            return [decode_job(row) for row in rows]

    def stats(self):
        counts = {state: 0 for state in STATES}
        with self.database.connect() as connection:
            for row in connection.execute("SELECT state,COUNT(*) AS n FROM jobs GROUP BY state"):
                counts[row["state"]] = row["n"]
        return counts

    def claim(self, worker_id, *, kinds=None):
        text(worker_id, "worker_id")
        values = []
        where = "state='queued'"
        if kinds is not None:
            kinds = tuple(kinds)
            if not kinds:
                return None
            for kind in kinds:
                text(kind, "kind")
            where += " AND kind IN (" + ",".join("?" for _ in kinds) + ")"
            values.extend(kinds)
        with self.database.transaction() as connection:
            row = connection.execute(
                "SELECT id FROM jobs WHERE " + where + " ORDER BY created_at,seq LIMIT 1",
                values,
            ).fetchone()
            if row is None:
                return None
            connection.execute(
                "UPDATE jobs SET state='running',attempts=attempts+1,updated_at=? WHERE id=?",
                (self.clock(), row["id"]),
            )
            return self._get(connection, row["id"])

    def complete(self, job_id, result):
        encoded = json_text(result)
        with self.database.transaction() as connection:
            job = self._get(connection, job_id)
            if job.state != "running":
                raise ValidationError("only running jobs can complete")
            connection.execute(
                "UPDATE jobs SET state='succeeded',result=?,error=NULL,updated_at=? WHERE id=?",
                (encoded, self.clock(), job_id),
            )
            return self._get(connection, job_id)

    def fail(self, job_id, error):
        text(error, "error")
        with self.database.transaction() as connection:
            job = self._get(connection, job_id)
            if job.state != "running":
                raise ValidationError("only running jobs can fail")
            state = "queued" if job.attempts < job.max_attempts else "failed"
            connection.execute(
                "UPDATE jobs SET state=?,error=?,updated_at=? WHERE id=?",
                (state, error, self.clock(), job_id),
            )
            return self._get(connection, job_id)
