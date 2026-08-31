"""Durable state machine. Every writer and its audit event share one transaction."""

import json
import math
import uuid

from .clock import SystemClock
from .database import Database
from .errors import IdempotencyConflict, JobNotFound, LeaseLost, ValidationError
from .model import STATES, TERMINAL_STATES, decode_job
from .validation import json_text, kind_filter, page, positive_integer, positive_seconds, text


class JobStore:
    def __init__(self, path, *, clock=None, retry_base_seconds=1.0, retry_cap_seconds=60.0):
        self.retry_base_seconds = positive_seconds(retry_base_seconds, "retry_base_seconds")
        self.retry_cap_seconds = positive_seconds(retry_cap_seconds, "retry_cap_seconds")
        if self.retry_cap_seconds < self.retry_base_seconds:
            raise ValidationError("retry cap must be at least retry base")
        self.clock = clock if clock is not None else SystemClock()
        self.database = Database(path)

    def _now(self):
        now = float(self.clock())
        if not math.isfinite(now):
            raise ValidationError("clock must return finite seconds")
        return now

    def _get(self, connection, job_id):
        row = connection.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        if row is None:
            raise JobNotFound(job_id)
        return decode_job(row)

    def _event(self, connection, job, event_type, now, details=None):
        connection.execute(
            "INSERT INTO job_events(job_id,type,at,attempt,details) VALUES(?,?,?,?,?)",
            (job.id, event_type, now, job.attempts, json_text(details or {})),
        )

    def _change(self, connection, job_id, event_type, now, *, details=None, **fields):
        fields["updated_at"] = now
        connection.execute(
            "UPDATE jobs SET " + ",".join(name + "=?" for name in fields) + " WHERE id=?",
            list(fields.values()) + [job_id],
        )
        job = self._get(connection, job_id)
        self._event(connection, job, event_type, now, details)
        return job

    def enqueue(self, kind, payload, *, max_attempts=3, idempotency_key=None):
        text(kind, "kind")
        positive_integer(max_attempts, "max_attempts")
        encoded = json_text(payload)
        if idempotency_key is not None:
            text(idempotency_key, "idempotency_key")
        with self.database.transaction() as connection:
            if idempotency_key is not None:
                row = connection.execute("SELECT * FROM jobs WHERE idempotency_key=?", (idempotency_key,)).fetchone()
                if row is not None:
                    if (row["kind"], row["payload"], row["max_attempts"]) != (kind, encoded, max_attempts):
                        raise IdempotencyConflict("key already bound: " + idempotency_key)
                    return decode_job(row)
            now, job_id = self._now(), uuid.uuid4().hex
            connection.execute(
                "INSERT INTO jobs(id,kind,payload,state,max_attempts,created_at,updated_at,available_at,idempotency_key) "
                "VALUES(?,?,?,'queued',?,?,?,?,?)",
                (job_id, kind, encoded, max_attempts, now, now, now, idempotency_key),
            )
            job = self._get(connection, job_id)
            self._event(connection, job, "enqueued", now)
            return job

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

    def _delay(self, attempts):
        exponent = attempts - 1
        # Compare logarithms before exponentiation: safe even after huge counts.
        if exponent >= math.log2(self.retry_cap_seconds) - math.log2(self.retry_base_seconds):
            return self.retry_cap_seconds
        return min(self.retry_cap_seconds, math.ldexp(self.retry_base_seconds, exponent))

    def _released(self):
        return dict(lease_owner=None, lease_token=None, lease_expires_at=None, result=None)

    def _failure(self, connection, job, error, now):
        fields = self._released()
        if job.cancel_requested:
            state, event_type = "cancelled", "cancelled"
        elif job.attempts < job.max_attempts:
            state, event_type = "queued", "retry_scheduled"
            fields["available_at"] = now + self._delay(job.attempts)
        else:
            state, event_type = "failed", "failed"
        return self._change(connection, job.id, event_type, now,
                            state=state, error=error, **fields)

    def _recover(self, connection, now):
        rows = connection.execute(
            "SELECT * FROM jobs WHERE state='running' AND (lease_expires_at<=? OR lease_token IS NULL) ORDER BY seq", (now,),
        ).fetchall()
        for row in rows:
            self._failure(connection, decode_job(row), "lease expired", now)
        return len(rows)

    def reap_expired(self):
        with self.database.transaction() as connection:
            return self._recover(connection, self._now())

    def claim(self, worker_id, *, lease_seconds=30.0, kinds=None):
        text(worker_id, "worker_id")
        lease_seconds = positive_seconds(lease_seconds, "lease_seconds")
        kinds = kind_filter(kinds)
        with self.database.transaction() as connection:
            now = self._now()
            self._recover(connection, now)
            if kinds == ():
                return None
            values = [now]
            where = "state='queued' AND available_at<=?"
            if kinds is not None:
                where += " AND kind IN (" + ",".join("?" for _ in kinds) + ")"
                values.extend(kinds)
            row = connection.execute(
                "SELECT * FROM jobs WHERE " + where + " ORDER BY available_at,created_at,seq LIMIT 1",
                values,
            ).fetchone()
            if row is None:
                return None
            return self._change(
                connection, row["id"], "claimed", now,
                state="running", attempts=row["attempts"] + 1, lease_owner=worker_id,
                lease_token=uuid.uuid4().hex, lease_expires_at=now + lease_seconds,
                details={"worker_id": worker_id, "lease_expires_at": now + lease_seconds},
            )

    def _owned(self, connection, job_id, token, now):
        job = self._get(connection, job_id)
        if (job.state != "running" or not isinstance(token, str) or not token
                or token != job.lease_token or job.lease_expires_at is None
                or now >= job.lease_expires_at):
            raise LeaseLost("lease no longer owned for " + job_id)
        return job

    def heartbeat(self, job_id, token, *, lease_seconds=30.0):
        lease_seconds = positive_seconds(lease_seconds, "lease_seconds")
        with self.database.transaction() as connection:
            now = self._now()
            self._owned(connection, job_id, token, now)
            return self._change(connection, job_id, "heartbeat", now,
                                lease_expires_at=now + lease_seconds)

    def complete(self, job_id, token, result):
        with self.database.transaction() as connection:
            now = self._now()
            job = self._owned(connection, job_id, token, now)
            if job.cancel_requested:
                return self._change(connection, job_id, "cancelled", now,
                                    state="cancelled", **self._released())
            encoded = json_text(result)
            fields = self._released()
            fields["result"] = encoded
            return self._change(connection, job_id, "succeeded", now,
                                state="succeeded", error=None, **fields)

    def fail(self, job_id, token, error):
        with self.database.transaction() as connection:
            now = self._now()
            job = self._owned(connection, job_id, token, now)
            text(error, "error")
            return self._failure(connection, job, error, now)

    def cancel(self, job_id):
        with self.database.transaction() as connection:
            job = self._get(connection, job_id)
            if job.state in TERMINAL_STATES or job.cancel_requested:
                return job
            now = self._now()
            if job.state == "running":
                return self._change(connection, job_id, "cancel_requested", now,
                                    cancel_requested=True)
            return self._change(connection, job_id, "cancelled", now,
                                state="cancelled", cancel_requested=True, **self._released())

    def events(self, job_id, *, after_seq=0, limit=100):
        page(limit, after_seq)
        with self.database.connect() as connection:
            self._get(connection, job_id)
            rows = connection.execute(
                "SELECT * FROM job_events WHERE job_id=? AND seq>? ORDER BY seq LIMIT ?",
                (job_id, after_seq, limit),
            ).fetchall()
            return [dict(row, details=json.loads(row["details"])) for row in rows]
