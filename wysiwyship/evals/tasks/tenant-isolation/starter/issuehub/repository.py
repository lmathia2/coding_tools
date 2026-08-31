"""SQL mapping for projects, issues, comments, exports, and audit history."""

import json

from .errors import missing


class Repository:
    def __init__(self, database):
        self.db = database

    def projects(self, tenant_id):
        return [dict(row) for row in self.db.connection.execute(
            "SELECT id,tenant_id,name FROM projects ORDER BY id"
        )]

    def project(self, tenant_id, project_id):
        row = self.db.connection.execute(
            "SELECT id,tenant_id,name FROM projects WHERE id=?", (project_id,)
        ).fetchone()
        if row is None:
            raise missing()
        return dict(row)

    def create_project(self, tenant_id, name):
        cursor = self.db.connection.execute(
            "INSERT INTO projects(tenant_id,name) VALUES(?,?)", (tenant_id or 1, name)
        )
        return self.project(tenant_id, cursor.lastrowid)

    def issue(self, tenant_id, issue_id):
        row = self.db.connection.execute(
            "SELECT id,project_id,title,status,created_by FROM issues WHERE id=?",
            (issue_id,),
        ).fetchone()
        if row is None:
            raise missing()
        return dict(row)

    def issues(self, tenant_id, query="", status=None, project_id=None):
        clauses, values = ["1=1"], []
        if query:
            clauses.append("instr(lower(title),lower(?))>0")
            values.append(query)
        if status is not None:
            clauses.append("status=?")
            values.append(status)
        if project_id is not None:
            clauses.append("project_id=?")
            values.append(project_id)
        return [dict(row) for row in self.db.connection.execute(
            "SELECT id,project_id,title,status,created_by FROM issues WHERE "
            + " AND ".join(clauses) + " ORDER BY id", values
        )]

    def create_issue(self, tenant_id, actor_id, project_id, title):
        cursor = self.db.connection.execute(
            "INSERT INTO issues(project_id,title,status,created_by) VALUES(?,?,'open',?)",
            (project_id, title, actor_id),
        )
        return self.issue(tenant_id, cursor.lastrowid)

    def update_issue(self, tenant_id, issue_id, changes):
        columns = sorted(changes)
        self.db.connection.execute(
            "UPDATE issues SET " + ",".join(column + "=?" for column in columns)
            + " WHERE id=?", [changes[column] for column in columns] + [issue_id]
        )
        return self.issue(tenant_id, issue_id)

    def comments(self, tenant_id, issue_id):
        return [dict(row) for row in self.db.connection.execute(
            "SELECT id,issue_id,author_id,text FROM comments WHERE issue_id=? ORDER BY id",
            (issue_id,),
        )]

    def create_comment(self, tenant_id, actor_id, issue_id, text):
        cursor = self.db.connection.execute(
            "INSERT INTO comments(issue_id,author_id,text) VALUES(?,?,?)",
            (issue_id, actor_id, text),
        )
        return {"id": cursor.lastrowid, "issue_id": issue_id,
                "author_id": actor_id, "text": text}

    def export(self, tenant_id, export_id):
        row = self.db.connection.execute(
            "SELECT * FROM export_jobs WHERE id=?", (export_id,)
        ).fetchone()
        if row is None:
            raise missing()
        return dict(row)

    def audit(self, tenant_id):
        rows = self.db.connection.execute("SELECT * FROM audit ORDER BY id")
        return [dict(row, details=json.loads(row["details"])) for row in rows]
