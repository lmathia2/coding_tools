# Architecture: tenant ownership is a cross-layer contract

## What each boundary protects

`App.request` constructs an immutable `RequestContext` and delegates to services.
The adapter does not authenticate an Internet user; its actor is synthetic data
selected by a trusted caller. The `operation` wrapper in `auth.py` applies to
both adapter and direct-service callers, so switching transports cannot bypass
authorization. `Authorizer.require` looks up the active membership and minimum
role for the exact requested tenant on every call.

`Repository` scopes SQL with the tenant before loading a resource. This avoids
passing foreign records through validation, cache, or serialization and ensures
foreign/absent records produce the same domain error. The storage boundary is
still trusted: it accepts a tenant but does not establish an actor's right to
use that tenant. Role checking belongs to service/export entry points.

V2 also stores tenant identity on issues/comments. Composite SQLite foreign keys
bind `(tenant_id, parent_id)` to the parent's tenant and ID. Thus a future writer
cannot silently attach an Atlas comment to a Boreal issue. Tenant-leading
indexes support scoped lookup without requiring per-tenant ID sequences. The
HTTP-like payload shapes remain unchanged despite the extra durable columns.

## Mutations, cache, and audit

`Service` validates fields and relationship targets. For bulk, all issue IDs and
the destination project are resolved within one transaction before any update.
Business mutations and their success audit share the transaction. If SQL/audit
fails, rollback preserves durable state; only after commit is the tenant's cache
partition invalidated. Batch failures are not partial successes.

`QueryCache` keys tenant, kind, and resource/query identity. Copying on put/get
prevents caller mutation. The cache stores data, not membership grants: the
authorization wrapper always runs before cache lookup. Invalidating one tenant
retains another tenant's data. Broad invalidation within the changed tenant keeps
the implementation simple while covering all search/status/project variants.

Resource 404s and role 403s generate one sanitized `access.denied` only if the
caller is a current member of the requested tenant. That event is emitted after
the operation has unwound and any mutation transaction has rolled back. It omits
resource IDs and request bodies. Nonmembers cannot write to tenant audit streams.
Successful reads and validation failures do not generate audit noise.

## Export state and fresh authorization

`Exports.enqueue` records tenant, owner, filter, and queued state. `run_next`
selects one oldest queued job inside a transaction, reconstructs its original
context, and reauthorizes against current membership before reading current SQL
rows. It bypasses the query cache. Rows, ready bytes, and success audit are one
transaction; revoked access instead yields terminal denied state, no content,
and a job-tenant denial audit. The worker can advance the next job on its next
call. There are no retries, timing heuristics, threads, or leases.

Inspection and download are owner-only and also require current membership.
Neither a ready artifact nor tenant administrator status grants ownership.
Revocation blocks access to existing bytes. Restoration permits a ready job to
be downloaded again, but does not regenerate a terminal denied job.

## Migration and recovery intent

`Database._upgrade_v2` rebuilds issues/comments/exports inside an explicit SQLite
transaction. Ownership is backfilled through existing relations, allocation
high-water marks are retained, and invalid legacy keys or export filters abort
without a partial schema. Ready legacy bytes are untrusted: content is cleared
and ready jobs become queued. The worker will apply the new authorization and
scope checks before those jobs regain bytes. Existing denied jobs stay denied;
the migration itself adds no audit events.

## Limits

The supported unit is one serial App with one SQLite connection and one cache.
Membership revocation becomes visible at the next operation, not retroactively
inside an already executing call. The implementation does not promise concurrent
request/worker safety, multi-process cache invalidation, external resource-write
coherence, production identity proof, network security, or constant-time errors.
SQLite exceptions remain visible to callers for diagnosis; they are not silently
converted into successful writes. This is behaviorally tested isolation within
a bounded application, not a comprehensive security certification.
