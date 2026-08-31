# Tenant isolation for IssueHub

## The change

IssueHub is a working local SQLite-backed issue tracker. Its original deployment
had one workspace; tenant columns and membership records now exist, but the
application still behaves like a single-workspace installation. Make tenant
isolation a property of the whole application, not only selected API routes.
Preserve legitimate same-tenant workflows and the public interfaces below.

Work in the candidate copy of `starter/`. Use Python 3.9+ standard library only.
Do not read evaluator-owned acceptance tests or a reference implementation when
performing the task. Do not replace the application with test-specific responses.
Implement the contract for arbitrary valid tenant IDs, resource IDs, and
synthetic identities, not just the demo seed values.

This change spans request/service authorization, storage/migration, cache
behavior, relationships/batches, exports, and operational documentation.

## Deliverables — identical in both experimental conditions

1. A functioning implementation in the candidate application, preserving all
   original passing regression tests.
2. New candidate-owned regression tests for the new behavior and failure paths.
   They must run through ordinary `unittest` discovery separately from the grader.
3. Updated `README.md`, `docs/architecture.md`, and `docs/contracts.md`. Explain
   purpose and intent, ownership boundaries, transaction/cache decisions,
   migration and export recovery, and limitations. Do not merely enumerate files.
4. An offline `docs/explainer.html` for a new developer: what the application does,
   how to use it, how tenant ownership flows through it, why the important
   boundaries exist, and what its limits are. Ground explanations in source
   modules/symbols and executable examples; no external scripts or assets.
5. A concise final report of changes, exact verification commands/results, and
   remaining limitations. Never claim production authentication or unmeasured
   model/runtime/difficulty outcomes.

The feature contract, available host tools, and grading criteria do not change
with orchestration condition. Delegation and local commits in the disposable
candidate project are allowed. Do not push, contact remotes, modify evaluator
artifacts, or write outside the candidate project. Any condition-specific
workflow instructions are supplied separately by the experiment runner.

## Execution and threat model

There is no HTTP server, external identity provider, network dependency, clock,
thread pool, or background daemon. `App.request` is a framework-free HTTP-like
adapter; `Exports.run_next()` explicitly advances one durable job. `actor_id`
represents a synthetic identity that a trusted adapter has already selected. It
must not be described as authenticated proof supplied safely by an Internet user.

One `App` owns one SQLite connection and one process-local cache. Operations,
including trusted maintenance changes to memberships, execute serially. A
membership change must affect the next service/API call or worker invocation.
Reopen tests use independent App instances for persistence. Concurrent requests,
cross-App resource-cache coherence, and linearizable revocation during an already
executing call are out of scope. Out-of-band resource edits are not supported;
maintenance membership edits are explicitly supported and must not need cache
flushes. SQL integrity checks and migrations may use the documented DB port.

## Public interfaces and compatibility

Keep these names/signatures callable. Internal decomposition may change.

```python
from issuehub import App, RequestContext

app = App(database_path=":memory:")  # path-like objects also work
context = RequestContext(actor_id=1, tenant_id=1)
response = app.request("GET", "/issues", actor_id=1, tenant_id=1,
                       body=None, query=None)
response.status  # integer HTTP-like status
response.body    # dict/list, or CSV text for successful downloads
app.close()
```

`RequestContext` remains immutable. Every public service/export operation takes
context as its first argument; no ambient/global current tenant. The required
service calls are `list_projects`, `create_project(name)`, `get_issue(issue_id)`,
`list_issues(query="", status=None, project_id=None)`,
`create_issue(project_id, title)`, `update_issue(issue_id, changes)`,
`bulk_update(ids, changes)`, `list_comments(issue_id)`,
`add_comment(issue_id, text)`, and `list_audit`. Required export calls are
`enqueue(project_id=None)`, `get(export_id)`, `download(export_id)`, plus the
trusted context-free worker `run_next()`.

Direct service/export calls enforce the same checks and raise
`issuehub.errors.DomainError` with `status`, `code`, `message`, and `payload()`.
The adapter turns those errors into a Response. Do not swallow unexpected storage
failures as successful responses; storage exceptions may propagate to the caller.

Supported routes and minimum roles:

| Method and path | Input | Success | Role |
| --- | --- | --- | --- |
| GET `/projects` | — | 200 project list | viewer |
| POST `/projects` | `name` | 201 project | admin |
| GET `/issues` | query `q`, `status`, `project_id` | 200 issue list | viewer |
| POST `/issues` | `project_id`, `title` | 201 issue | editor |
| GET `/issues/{id}` | — | 200 issue | viewer |
| PATCH `/issues/{id}` | nonempty changes object | 200 issue | editor |
| POST `/issues/bulk` | `ids`, `changes` | 200 ordered issue list | editor |
| GET `/issues/{id}/comments` | — | 200 comment list | viewer |
| POST `/issues/{id}/comments` | `text` | 201 comment | editor |
| POST `/exports` | optional `project_id` | 202 job metadata | viewer |
| GET `/exports/{id}` | — | 200 own job metadata | viewer |
| GET `/exports/{id}/download` | — | 200 own CSV text | viewer |
| GET `/audit` | — | 200 event list | admin |

Roles form `viewer < editor < admin` within the requested tenant only. There is
no cross-tenant superuser. For exports, admin does **not** override ownership.
Unknown route/method pairs return 404; they need no resource-authorization audit.
Methods are case insensitive. Body and query must be dicts or None; malformed
containers return 400 before dispatch. Query IDs are integers, not URL strings.

Existing success representations stay exactly shaped as follows; do not add
durable tenant columns to issue/comment response payloads:

- Project: `id, tenant_id, name`.
- Issue: `id, project_id, title, status, created_by`.
- Comment: `id, issue_id, author_id, text`.
- Job metadata: `id, tenant_id, requested_by, project_id, state, error`.
- Audit: `id, tenant_id, actor_id, action, resource_id, details`, where `details`
  is a decoded object, not a JSON string.

Lists are ordered by increasing resource ID, except bulk results preserve input
order. Title/name/comment text is nonempty after stripping; whitespace is
stripped on writes. Search is case-insensitive literal substring search, so `%`
is not a wildcard. Status is `open` or `closed`. New issues start `open` and use
the context actor as `created_by`; comment author also comes from context.
PATCH accepts only `title`, `status`, and `project_id`; reject unknown fields.
Other routes may continue ignoring extra body/query fields as the starter does.
IDs are positive integers (not booleans). Keep existing validation behavior.

## Boundary and error contract

For a recognized service operation, validate in this order:

1. A missing, unknown, or malformed actor is 401, code `unauthenticated`, message
   `Known identity required`. In particular bool/string actor IDs are invalid.
2. A missing/malformed tenant is 400 `invalid_request`; a tenant ID must be a
   positive int, not bool. There is no implicit default tenant.
3. A known actor without an active membership in that tenant is 403 `forbidden`,
   message `Operation not permitted`; an unknown positive tenant is also 403.
4. Insufficient role in that tenant is the same 403, even if the actor is an
   admin in another tenant. Role/membership checks precede resource lookups.
5. Validate operation inputs, then resolve resources in the requested tenant.

Foreign resources and nonexistent resources must be indistinguishable to an
otherwise authorized caller: same 404 and exactly this body (no foreign title,
tenant, ownership hint, different error code, or resource identifier):

```json
{"error": {"code": "not_found", "message": "Resource not found"}}
```

This applies to detail reads, updates, comment parents, list project filters,
issue/project relationships, batches, and export lookup/filter/ownership.
Timing/constant-time lookup is not a requirement. Validation error messages other
than the stable errors above may be descriptive; code remains `invalid_request`.

## Storage, relationships, and migration

Tenant ownership must constrain SQL resource queries, not merely be filtered from
an unscoped response after loading everything. A project owns issues; an issue
owns comments. Tenant identity of existing issues cannot be changed by PATCH.
Moving an issue between two projects in its tenant remains supported. All
relationship targets must be resolved in the same tenant before mutation.

The documented maintenance ports are `app.db.connection` (sqlite3 connection),
`app.db.transaction()` (transaction context manager), `app.repo`, and `app.cache`.
They are trusted internal/testing ports, not new public network endpoints.
`app.repo.projects(tenant_id)`, `project(tenant_id, project_id)`,
`issue(tenant_id, issue_id)`, and
`issues(tenant_id, query="", status=None, project_id=None)` remain callable,
return existing payload shapes, and scope by the supplied tenant independently
of the adapter. These low-level storage calls do not perform actor authorization.

Upgrade the existing documented SQLite v1 schema to `PRAGMA user_version=2`:

- Keep table names and original columns. Add required durable `tenant_id` columns
  to `issues` and `comments`, backfilled through their existing parents.
- Enforce issue→project, comment→issue, and optional export→project tenant
  agreement in SQLite, not only in service code. Foreign-key enforcement stays
  enabled. An attempted mismatched relation using the maintenance SQL connection
  must raise `sqlite3.IntegrityError`. Composite FKs or equivalent durable
  constraints are acceptable; no particular helper/class/index names are graded.
- Add tenant-leading indexed lookup paths for issues, comments, export jobs, and
  audit. Preserve valid records, IDs, relationships, audit history, and
  AUTOINCREMENT high-water marks (including deleted maximum IDs).
- Upgrade is atomic. Invalid legacy foreign keys or cross-tenant export filters
  must fail with `sqlite3.IntegrityError` without advancing version, dropping
  original data, or leaving half-created schema objects.
- Queued legacy jobs remain queued and become safe to execute. Discard *all*
  persisted legacy CSV content. Requeue legacy `ready` jobs with NULL content and
  NULL error; their bytes were produced without tenant guarantees. Preserve
  terminal `denied` state/error. Reopening v2 is idempotent and must not requeue
  exports generated safely under v2. No migration audit events are required.

Global unique numeric resource IDs remain supported; per-tenant ID sequences are
not required. The v1 schema is fully available in `issuehub/database.py`.

## Cache and atomic updates

Cache partitions include tenant identity plus complete resource/query identity.
The same actor can switch tenants, and two tenants can issue identical searches.
Authorization must run before a cached response is returned. Never cache a role
or membership grant across service calls. Returned cached objects must be copies
so caller mutation cannot poison future responses.

The public low-level cache contract stays `get(tenant_id, kind, key)`,
`put(tenant_id, kind, key, value)`, `invalidate(tenant_id)`. Missing entries return
None. Tenant invalidation removes that tenant only. Successful issue changes
invalidate all affected issue-detail and query variants after commit; failures
must not publish changed data to the cache. Mutating one tenant must not evict or
overwrite another tenant's partition. This is intentionally stronger than simply
clearing a global cache after every write.

Bulk accepts 1–100 unique positive issue IDs and one validated changes object.
It is all-or-nothing: validate every ID and optional destination project, perform
updates plus success audit in one transaction, preserve input order in the
response, and invalidate only after commit. A foreign/missing later ID must not
leave an earlier issue changed or a misleading success audit event. Duplicate,
empty, excessive, malformed ID lists and invalid changes return 400 without
business writes. Audit persistence failure must roll back the associated write.

## Durable export lifecycle

Enqueue stores tenant, requesting actor, and optional same-tenant project filter.
Only the requesting actor with a currently active membership in that same tenant
may inspect or download the job. A different member/admin sees the generic 404.
No content is included in job metadata, in any state.

`run_next()` processes at most the oldest queued ID and returns its public
metadata; returns None if none remain. Jobs persist across App restart. On each
execution, reauthorize the original actor in the stored tenant and revalidate
the filter before reading rows. Read execution-time data, not an enqueue-time
snapshot or another tenant's cached list.

- Authorized: scoped CSV bytes and state `ready`, error NULL, committed together.
- Revoked/deleted membership or invalid authorization: terminal state `denied`,
  content NULL, error exactly `authorization_revoked`. Return that metadata and
  let a later call process the next job. Do not throw for expected revocation.
- A denied job does not retry automatically, even if membership is restored.
- Download/get reauthorize again; already-ready bytes do not grant access after
  revocation. Restoring active membership allows the owner to download a
  previously ready v2 job; restoration does not regenerate a denied job.
- A currently authorized owner of any non-ready job receives 409,
  `export_unavailable`, message `Export is not ready` when downloading.

CSV header is `id,project_id,title,status`, rows are ordered by issue ID, commas,
quotes, and embedded newlines round-trip through Python's csv reader. Empty
results still have a header. Do not make claims about spreadsheet formula safety.

## Audit behavior

Audit reads are admin-only and scoped to their tenant. Successful single writes
emit exactly one existing event in the same transaction as their business write:
`project.created`, `issue.created`, `issue.updated`, `comment.created`,
`export.queued`, or worker `export.ready`, with that resource/job ID and `{}`
details. Successful bulk emits one `issues.bulk_updated`, resource_id NULL,
details `{"count": N}` instead of per-item success events.

An authorized member's failed 403 or resource 404 emits exactly one
`access.denied` in the *requested* tenant, actor from context, resource_id NULL,
details exactly `{"code": "forbidden"}` or `{"code": "not_found"}`. Do not log
foreign identifiers, titles, bodies, or ownership information. Direct service
calls have the same behavior. Validation errors, non-ready 409s, unsupported
route/method pairs, and successful reads need no audit. An unaffiliated or
revoked actor must not append to a tenant's audit stream.

The trusted worker is different: it records `export.denied` against the stored
job's tenant and original actor even after membership revocation, with job ID and
details exactly `{"reason": "authorization_revoked"}`. There must be no
`export.ready` event for that denied execution. Batch rollback must leave no
success audit; the sanitized denial event may be committed after rollback.

## Examples

Ada is admin in Atlas and viewer in Boreal. Reading a Boreal issue with Boreal
context succeeds, updating it returns 403, and reading it with Atlas context
returns the same 404 as an absent issue. Warm either cache first; the results
must not change.

An Atlas editor submits `[atlas_issue, boreal_issue]` with status `closed`.
The entire batch returns 404, neither issue changes, and Atlas receives one
sanitized denial audit. Boreal receives no event from this request.

A viewer enqueues an Atlas export and is removed before execution. The worker
marks it denied without bytes, records the job-tenant denial, and can process
the next queued job on its next invocation. A ready export is also inaccessible
to its owner after membership revocation.

## Verification and non-goals

Run from the candidate root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m issuehub
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

The evaluator separately runs `unittest discover` against evaluator-owned tests
with the candidate root on PYTHONPATH. Do not copy evaluator/reference artifacts
into candidate tests or change their discovery. Behavioral tests may use the
public maintenance ports above, but do not grade internal helper names.

Non-goals: OAuth/JWT/passwords, public networking, UI, real users or production
credentials, attachment storage, new delete/membership-management routes,
distributed caches/queues, concurrent workers, multi-process transaction
coordination, pagination, full-text ranking, encryption, CSV formula sanitizing,
or claims that passing this exercise constitutes a security audit.
