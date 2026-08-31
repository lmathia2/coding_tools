# Existing contracts

## Adapter and services

`App.request(method, path, actor_id=..., tenant_id=..., body=..., query=...)`
returns a `Response(status, body)`. No socket is opened. Unknown route/method
pairs return a generic 404. Domain errors have `status`, `code`, `message`, and
`payload()`; direct service calls raise them rather than returning Response.

The routes are projects GET/POST, issues GET/POST, issue GET/PATCH, issue comments
GET/POST, issues/bulk POST, exports POST, export GET, export/download GET, and
audit GET. Path IDs are decimal numbers. Query `project_id` uses an integer.
`q` is literal case-insensitive substring search, not SQL wildcard syntax.

Project payloads contain id/tenant_id/name; issue payloads contain
id/project_id/title/status/created_by; comments contain id/issue_id/author_id/text.
Lists use ascending ID order. Bulk results follow input order. Titles, project
names, and comment text are stripped and nonempty. Status is open/closed.
PATCH allows only title/status/project_id. Batch IDs must be 1–100 distinct
positive ints. Returned cache values are independent copies.

`App.service` exposes all project/issue/comment/audit operations, each with
RequestContext first. `App.exports` exposes enqueue/get/download with context,
and trusted context-free run_next. Job metadata contains
id/tenant_id/requested_by/project_id/state/error, never CSV content. States are
queued, ready, and denied. A non-ready download is 409 export_unavailable. CSV
columns are id/project_id/title/status and quotes/newlines use stdlib csv rules.

## Maintenance and persistence

`App.db.connection` is a sqlite3 connection with foreign keys enabled;
`App.db.transaction()` opens a BEGIN IMMEDIATE transaction. The schema version is
PRAGMA user_version=1. All schema definitions are in database.py. `App.repo`
provides typed dictionary mappings and `App.cache` offers get/put/invalidate
using the tenant/kind/key calling convention. These ports are trusted local
maintenance/testing surfaces, not authentication or remote APIs.

Synthetic fixtures may insert users, tenants, and memberships directly. Tests
must not need clocks, sleeps, services, or packages. The original regression
suite assumes a known actor and a single tenant; the engineering task specifies
the new isolation, audit, and migration requirements separately.
