# IssueHub — tenant-isolated local service

IssueHub tracks projects, issues, and comments and generates durable CSV exports.
This implementation isolates synthetic workspaces at service, SQL relation,
cache, export, and audit boundaries. It is a local engineering example, not a
production identity or public networking system.

Python 3.9+ and its standard library are sufficient. Run from the application root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m issuehub
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

The demo uses only synthetic users and prints an issue list and CSV. No sleeps,
network, external packages, model calls, or credentials are needed.

```python
from issuehub import App, RequestContext
from issuehub.seed import seed_demo

app = App("issues.sqlite")
try:
    seed_demo(app)
    editor = RequestContext(actor_id=2, tenant_id=1)
    issue = app.service.create_issue(editor, 1, "Verify release")
    viewer = RequestContext(actor_id=3, tenant_id=1)
    job = app.exports.enqueue(viewer, project_id=1)
    app.exports.run_next()
    print(app.exports.download(viewer, job["id"]))
finally:
    app.close()
```

Supply an explicit tenant on every operation. Membership and role are looked up
fresh, including before cache hits and before export execution/download. An
actor's role in another tenant confers no privilege. Jobs are owner-only, even
for administrators. Do not accept caller-supplied actor IDs as public proof of
identity; a real deployment would need a trusted authentication adapter.

## Existing database upgrade

Opening a v1 database automatically upgrades it transactionally to v2. Back up
valuable local data before any software migration. Existing issues/comments gain
tenant ownership from their parents; IDs and allocation high-water marks remain
stable. Inconsistent legacy relations fail without changing the original schema.
Legacy CSV content is discarded and old ready jobs are requeued, because those
bytes were not produced under the new isolation contract. Run the worker to
regenerate authorized exports. Reopening v2 does not reset fresh ready jobs.

Only one serial App is supported per active resource/cache workflow. Trusted
maintenance membership changes take effect on the next call; externally editing
resource rows and cross-App cache coherence are outside the contract. Read
[architecture](docs/architecture.md), [contracts](docs/contracts.md), or the offline
[developer explainer](docs/explainer.html) for the boundaries and failure cases.
