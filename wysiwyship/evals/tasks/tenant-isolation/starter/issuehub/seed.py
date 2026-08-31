"""Synthetic local fixtures. Not an identity provider or a production auth scheme."""


def seed_demo(app):
    """Initialize exactly one workspace in an empty database, idempotently."""
    if app.db.connection.execute("SELECT 1 FROM tenants LIMIT 1").fetchone():
        return
    with app.db.transaction():
        app.db.connection.execute("INSERT INTO tenants(id,name) VALUES(1,'Atlas')")
        app.db.connection.executemany("INSERT INTO users(id,name) VALUES(?,?)", [
            (1, 'Ada Admin'), (2, 'Eli Editor'), (3, 'Val Viewer'),
        ])
        app.db.connection.executemany(
            "INSERT INTO memberships(tenant_id,user_id,role) VALUES(1,?,?)",
            [(1, 'admin'), (2, 'editor'), (3, 'viewer')],
        )
        app.repo.create_project(1, 'Launch')
        app.repo.create_issue(1, 1, 1, 'Write release notes')
