# Runtime contracts

## Identity, authorization, errors

Every public Service/Exports operation takes immutable RequestContext first.
Known positive-integer actor IDs are required; missing, unknown, bool, or string
actors receive 401 unauthenticated (`Known identity required`). A missing or
malformed tenant receives 400 invalid_request. A positive tenant without current
active membership or an insufficient tenant role receives 403 forbidden
(`Operation not permitted`). No implicit tenant or cross-tenant superuser exists.

Roles are viewer < editor < admin. Viewer reads projects/issues/comments and
owns exports; editor also creates/updates issues/comments and performs bulk;
admin also creates projects and reads audit. Role checks precede resource lookup.
Foreign resources, absent resources, and another member's export all return
404 not_found (`Resource not found`) without resource metadata. Direct calls
raise DomainError; App.request converts it into `{error: {code, message}}` with
the corresponding Response status. Unsupported route/method pairs are 404.

## API compatibility

The adapter supports `/projects` GET/POST, `/issues` GET/POST,
`/issues/{id}` GET/PATCH, `/issues/{id}/comments` GET/POST,
`/issues/bulk` POST, `/exports` POST, `/exports/{id}` GET,
`/exports/{id}/download` GET, and `/audit` GET. Methods are case-insensitive;
body/query are dictionaries or None. The create statuses are 201 for resource
creation, 202 for export enqueue, and 200 for reads/updates/batches.

Payload fields are unchanged: projects id/tenant_id/name; issues
id/project_id/title/status/created_by; comments id/issue_id/author_id/text;
job metadata id/tenant_id/requested_by/project_id/state/error. Audit includes
id/tenant_id/actor_id/action/resource_id/details with decoded details. Issue and
comment payloads intentionally omit the new durable tenant_id column.

Search q is case-insensitive literal substring, status is open/closed, and
project_id is a positive int. IDs exclude booleans. Text is stripped/nonempty.
PATCH allows title/status/project_id only. Issues/comments use the context actor
as creator/author. Ordered lists use increasing IDs; batches preserve input order.
Moving an issue within a tenant remains valid; changing its tenant does not.

## Batch/cache/audit

Bulk accepts 1–100 unique positive IDs. Every target and optional destination
must be in the tenant. Invalid input is 400; missing/foreign resources are 404.
All writes and one `issues.bulk_updated` event (NULL resource, `{count: N}`)
commit atomically. Single writes retain their `*.created`/`issue.updated` events
with resource IDs and empty details. Audit failure rolls back business writes.

Tenant cache keys include complete resource/query identity and data is copied.
Authorization is checked before cache hits. Successful issue mutation invalidates
only its tenant after commit. `cache.get(tenant,kind,key)` returns None on miss;
`put` stores a copy; `invalidate(tenant)` retains other partitions.

Failed role/resource calls by active tenant members append one `access.denied`,
NULL resource, `{code: forbidden}` or `{code: not_found}`; no request data or
foreign identifiers. Nonmembers/revoked actors cannot append. Reads, 400s, 409s,
and unsupported routes need no audit. Audit reads require tenant admin.

## Exports

Only the original owner with current same-tenant membership can get/download a
job; admin does not override ownership. Metadata never contains content.
Worker run_next returns one oldest queued job's metadata or None. It reauthorizes
the stored owner and filter, uses scoped execution-time SQL rows, and atomically
commits bytes/state/audit. CSV columns are id/project_id/title/status, rows by ID,
with stdlib escaping and a header for empty results.

Authorized jobs become ready/error NULL. Revocation or deleted membership makes
jobs denied/content NULL/error authorization_revoked. Worker denial emits
`export.denied` with job ID and `{reason: authorization_revoked}` in the job
tenant even when the owner is no longer a member; it emits no ready event.
Denied jobs are terminal. Authorized owners downloading non-ready jobs receive
409 export_unavailable (`Export is not ready`). Ready-job downloads check fresh
membership; restoration restores access to ready bytes, not to denied jobs.

## Durable schema and trusted maintenance ports

Database v2 preserves existing table names, payload columns, IDs and allocation
high-water marks. Issues/comments have required tenant_id. SQL enforces
tenant-consistent issue/project, comment/issue, export/project relations, with
tenant-leading indexes for issues/comments/export_jobs/audit. Foreign keys are
enabled. Migration fails atomically on invalid legacy relations. Legacy content
is cleared and ready jobs requeued; queued jobs remain queued; denied state/error
is retained. Reopening v2 leaves safely produced ready jobs alone.

app.db.connection and transaction(), app.repo scoped lookup methods, and app.cache
remain trusted local maintenance ports. Repository calls accept a tenant and do
not authenticate an actor; callers at that level must already be trusted.
Maintenance membership changes are visible on the next serial service/worker
call without flushing cache. Concurrent use, resource writes outside Service,
cross-App cache coherence, authentication infrastructure, public networking, and
spreadsheet formula safety are not promised.
