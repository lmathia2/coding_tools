# Architecture and current scope

## Purpose and flow

The application deliberately keeps a service boundary separate from transport.
`api.py` maps HTTP-like method/path/body/query values to `Service` and `Exports`;
it catches domain errors and does not run a server. Code may call services
directly using an immutable `RequestContext`. Synthetic actor IDs stand in for
identity selected by a trusted caller, not for a production login mechanism.

`Service` owns input validation and business operations. `Authorizer` wraps its
public entry points. `Repository` maps records to SQL; `Database` owns the
connection, versioned schema, and explicit transactions. A service response
cache copies values on both read and write so callers cannot mutate stored
responses. This original cache is one process-local namespace.

## Durable state

Users and tenants are fixture data. Memberships record each user's role and
active flag per tenant. Projects contain tenant metadata. Issues point at
projects; comments point at issues. Export jobs persist request metadata, state,
CSV bytes, and an error. Audit rows record actor, tenant metadata, action,
resource ID, and JSON details. `database.py` is the complete v1 schema source.

Single-record service writes and their audit event share a transaction. The
legacy bulk endpoint delegates to the single-update flow for each ID. Cache
invalidation follows individual successful issue writes. Background execution is
explicit: `run_next()` takes the oldest queued job, renders CSV from current SQL
rows, and commits bytes/state/audit. There are no timed jobs or worker threads.

## Current deployment assumptions

One App owns one SQLite connection and in-memory cache. It is used serially, and
resource mutations flow through the service. The original behavior assumed one
workspace. Tenant labels and role records are preparation for a multi-tenant
change, not evidence that isolation is already enforced.

The maintenance SQL port allows deterministic fixtures and membership changes;
it is trusted and not remotely exposed. No concurrent requests, external
resource edits, cross-App cache coherence, external authentication, public
network transport, or distributed worker guarantees are supplied. App restart
preserves only SQLite state, never process-local cached values.
