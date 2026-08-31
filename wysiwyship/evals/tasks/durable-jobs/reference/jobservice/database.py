"""Atomic schema migration and connection-per-operation SQLite persistence."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path


BASE_TABLE = """CREATE TABLE IF NOT EXISTS jobs (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL UNIQUE,
    kind TEXT NOT NULL,
    payload TEXT NOT NULL,
    state TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL,
    result TEXT,
    error TEXT
)"""

ADDITIONS = {
    "available_at": "REAL NOT NULL DEFAULT 0",
    "idempotency_key": "TEXT",
    "cancel_requested": "INTEGER NOT NULL DEFAULT 0",
    "lease_owner": "TEXT",
    "lease_token": "TEXT",
    "lease_expires_at": "REAL",
}


class Database:
    def __init__(self, path):
        self.path = str(Path(path))
        if self.path == ":memory:":
            raise ValueError("use a file database; operations open separate connections")
        with self.connect() as connection:
            connection.execute("PRAGMA journal_mode=WAL")
        with self.transaction() as connection:
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            if version > 2:
                raise ValueError("database was created by a newer jobservice")
            connection.execute(BASE_TABLE)
            columns = {row["name"] for row in connection.execute("PRAGMA table_info(jobs)")}
            migrating = "available_at" not in columns
            for name, declaration in ADDITIONS.items():
                if name not in columns:
                    connection.execute("ALTER TABLE jobs ADD COLUMN " + name + " " + declaration)
            connection.execute("CREATE INDEX IF NOT EXISTS jobs_queue ON jobs(state,created_at,seq)")
            connection.execute("CREATE INDEX IF NOT EXISTS jobs_ready ON jobs(state,available_at,created_at,seq)")
            connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS jobs_idempotency ON jobs(idempotency_key) WHERE idempotency_key IS NOT NULL")
            connection.execute("""CREATE TABLE IF NOT EXISTS job_events (
                seq INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL REFERENCES jobs(id),
                type TEXT NOT NULL,
                at REAL NOT NULL,
                attempt INTEGER NOT NULL,
                details TEXT NOT NULL
            )""")
            connection.execute("CREATE INDEX IF NOT EXISTS events_job ON job_events(job_id,seq)")
            if migrating:
                connection.execute("UPDATE jobs SET available_at=created_at")
                # An old running attempt has no fencing capability and must be recovered.
                connection.execute("UPDATE jobs SET lease_expires_at=0 WHERE state='running'")
                connection.execute("""INSERT INTO job_events(job_id,type,at,attempt,details)
                    SELECT id,'imported',updated_at,attempts,'{}' FROM jobs ORDER BY seq""")
            connection.execute("PRAGMA user_version=2")

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        try:
            yield connection
        finally:
            connection.close()

    @contextmanager
    def transaction(self):
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                yield connection
            except BaseException:
                connection.rollback()
                raise
            else:
                connection.commit()
