"""SQLite lifetime, transactions, and versioned on-disk schema."""

import sqlite3
from contextlib import contextmanager


SCHEMA_V1 = """
CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE tenants(id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE memberships(
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    role TEXT NOT NULL CHECK(role IN ('viewer','editor','admin')),
    active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1)),
    PRIMARY KEY(tenant_id,user_id)
);
CREATE TABLE projects(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    name TEXT NOT NULL
);
CREATE TABLE issues(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    title TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('open','closed')),
    created_by INTEGER NOT NULL REFERENCES users(id)
);
CREATE TABLE comments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_id INTEGER NOT NULL REFERENCES issues(id),
    author_id INTEGER NOT NULL REFERENCES users(id),
    text TEXT NOT NULL
);
CREATE TABLE export_jobs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    requested_by INTEGER NOT NULL REFERENCES users(id),
    project_id INTEGER REFERENCES projects(id),
    state TEXT NOT NULL CHECK(state IN ('queued','ready','denied')),
    content TEXT,
    error TEXT
);
CREATE TABLE audit(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    actor_id INTEGER NOT NULL REFERENCES users(id),
    action TEXT NOT NULL,
    resource_id INTEGER,
    details TEXT NOT NULL
);
CREATE INDEX issues_project_status ON issues(project_id,status,id);
PRAGMA user_version=1;
"""


class Database:
    def __init__(self, path=":memory:"):
        self.connection = sqlite3.connect(str(path), isolation_level=None)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys=ON")
        version = self.connection.execute("PRAGMA user_version").fetchone()[0]
        if version == 0:
            self.connection.executescript(SCHEMA_V1)
        elif version != 1:
            self.connection.close()
            raise ValueError("Unsupported database schema version")

    @contextmanager
    def transaction(self):
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            yield
        except BaseException:
            self.connection.rollback()
            raise
        else:
            self.connection.commit()

    def close(self):
        self.connection.close()
