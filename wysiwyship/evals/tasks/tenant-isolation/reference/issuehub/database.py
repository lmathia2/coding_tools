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
            version = 1
        if version == 1:
            self._upgrade_v2()
        elif version != 2:
            self.connection.close()
            raise ValueError("Unsupported database schema version")
    def _upgrade_v2(self):
        """Backfill ownership and enforce it at the durable relation boundary.

        DDL and backfill are one transaction: invalid legacy relations fail
        without advancing user_version or discarding the original tables.
        """
        statements = [
            "CREATE UNIQUE INDEX projects_tenant_id ON projects(tenant_id,id)",
            """CREATE TABLE issues_v2(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL REFERENCES tenants(id),
                project_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('open','closed')),
                created_by INTEGER NOT NULL REFERENCES users(id),
                UNIQUE(tenant_id,id),
                FOREIGN KEY(tenant_id,project_id) REFERENCES projects(tenant_id,id)
            )""",
            """INSERT INTO issues_v2(id,tenant_id,project_id,title,status,created_by)
               SELECT i.id,p.tenant_id,i.project_id,i.title,i.status,i.created_by
               FROM issues i JOIN projects p ON p.id=i.project_id""",
            """CREATE TABLE comments_v2(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL REFERENCES tenants(id),
                issue_id INTEGER NOT NULL,
                author_id INTEGER NOT NULL REFERENCES users(id),
                text TEXT NOT NULL,
                FOREIGN KEY(tenant_id,issue_id) REFERENCES issues_v2(tenant_id,id)
            )""",
            """INSERT INTO comments_v2(id,tenant_id,issue_id,author_id,text)
               SELECT c.id,i.tenant_id,c.issue_id,c.author_id,c.text
               FROM comments c JOIN issues_v2 i ON i.id=c.issue_id""",
            """CREATE TABLE export_jobs_v2(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL REFERENCES tenants(id),
                requested_by INTEGER NOT NULL REFERENCES users(id),
                project_id INTEGER,
                state TEXT NOT NULL CHECK(state IN ('queued','ready','denied')),
                content TEXT,
                error TEXT,
                FOREIGN KEY(tenant_id,project_id) REFERENCES projects(tenant_id,id)
            )""",
            """INSERT INTO export_jobs_v2
               SELECT id,tenant_id,requested_by,project_id,
                      CASE WHEN state='ready' THEN 'queued' ELSE state END,
                      NULL, CASE WHEN state='denied' THEN error ELSE NULL END
               FROM export_jobs""",
        ]
        try:
            with self.transaction():
                # A legacy database might have been written with FK checks off.
                if self.connection.execute("PRAGMA foreign_key_check").fetchone():
                    raise sqlite3.IntegrityError("Invalid legacy foreign keys")
                sequences = dict(self.connection.execute(
                    "SELECT name,seq FROM sqlite_sequence WHERE name IN ('issues','comments','export_jobs')"
                ))
                for statement in statements:
                    self.connection.execute(statement)
                for statement in [
                    "DROP TABLE comments",
                    "DROP TABLE issues",
                    "DROP TABLE export_jobs",
                    "ALTER TABLE issues_v2 RENAME TO issues",
                    "ALTER TABLE comments_v2 RENAME TO comments",
                    "ALTER TABLE export_jobs_v2 RENAME TO export_jobs",
                    "CREATE INDEX issues_tenant_status ON issues(tenant_id,status,id)",
                    "CREATE INDEX issues_project_status ON issues(tenant_id,project_id,status,id)",
                    "CREATE INDEX comments_tenant_issue ON comments(tenant_id,issue_id,id)",
                    "CREATE INDEX exports_tenant_owner ON export_jobs(tenant_id,requested_by,id)",
                    "CREATE INDEX audit_tenant_id ON audit(tenant_id,id)",
                    "PRAGMA user_version=2",
                ]:
                    self.connection.execute(statement)
                for name, sequence in sequences.items():
                    self.connection.execute(
                        "UPDATE sqlite_sequence SET seq=MAX(seq,?) WHERE name=?", (sequence, name)
                    )
                if self.connection.execute("PRAGMA foreign_key_check").fetchone():
                    raise sqlite3.IntegrityError("Invalid upgraded foreign keys")
        except BaseException:
            self.close()
            raise

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
