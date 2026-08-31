# IssueHub

IssueHub is a runnable local issue tracker used to explore changes to a persistent
service. It combines projects, issues, comments, audit events, and explicit CSV
jobs without requiring a web framework, account, network, or third-party package.

Python 3.9+ is sufficient. From this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m issuehub
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

The demo seeds one synthetic workspace and prints its issue list and CSV export.
`App(path)` persists data in SQLite; `App()` uses memory. `seed_demo(app)` is
idempotent but intended only for an empty demo database. Always close an App.

The current application originated as a single-workspace service. Its tenant
metadata is not a guarantee of access isolation, and membership role records are
not yet a production authorization system. Never expose this adapter as public
authentication. The accompanying engineering task defines the required change.

```python
from issuehub import App, RequestContext
from issuehub.seed import seed_demo

app = App()
try:
    seed_demo(app)
    issue = app.service.create_issue(RequestContext(2, 1), 1, "Verify release")
    job = app.exports.enqueue(RequestContext(1, 1), project_id=1)
    app.exports.run_next()
    print(app.exports.download(RequestContext(1, 1), job["id"]))
finally:
    app.close()
```

Read [architecture](docs/architecture.md) for the existing ownership and data flow,
and [contracts](docs/contracts.md) for the adapter, maintenance ports, and legacy
compatibility surface. The regression suite exercises legitimate original
single-workspace workflows; passing it alone says nothing about tenant isolation.
