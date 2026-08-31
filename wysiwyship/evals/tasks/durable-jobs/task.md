# Durable leased jobs

## Purpose and work unit

You own the existing, runnable `jobservice` application in the workspace root.
Extend its SQLite queue so several independent workers can share it safely and
abandoned attempts recover after worker crashes. Preserve useful existing CLI,
handler, submission, query and logging behavior. This is coordinated persistence,
execution, API, operational-documentation and test work, not a replacement demo.

The same deliverables, constraints and acceptance contract apply to every
evaluation arm. Work in the supplied candidate workspace only. Do not access an
evaluator reference solution, modify evaluator tests, use network services, add
dependencies, push to remotes, or change files outside this disposable project.
Optional local commits inside this project are allowed. Python 3.9+ and standard
library only. Expected duration is a hypothesis to calibrate, not a measured claim.

## Deliverables

Provide functioning durable application code, meaningful local regression tests,
updated README, architecture and API/operational contract documents, and a concise
verification handoff with commands, outcomes, decisions and limits. Include an
offline `docs/explainer.html` developer explainer: what the service does, how the
durable behavior works, why its safety boundaries matter, concrete usage, and
links to the source implementing the explanation. Make it understandable to a
new maintainer without substituting slogans for the actual guarantees. Do not
remove legacy functionality or replace its tests. No particular workflow,
internal class decomposition, HTML styling or SQL formulation is required.

## Existing compatibility

`from jobservice import JobStore, Worker, HandlerRegistry, ManualClock,
JobNotFound, ValidationError` remains supported. Keep `enqueue`, `get`,
`list_jobs`, `stats`, all four built-ins, custom handler registration, structured
handler logs and JSON-lines CLI behavior. Existing Job fields and `to_dict()`
remain; additions are allowed. FIFO is insertion order for equal timestamps.
Existing persisted databases must migrate in place without losing ids, payloads,
results, errors, attempt counts, or insertion order. Existing queued work becomes
immediately eligible. Existing running work has no valid owner and must become
recoverable immediately; never pretend that its old process has a valid lease.
Do not reset a database to migrate it. Migration is atomic and repeatable.

The internal completion/failure protocol intentionally changes to require a
lease token. Immediate retries intentionally become delayed. `run_until_idle`
still never sleeps: it stops when no work is eligible now, even if future retries
exist. Legacy tests do not promise immediate retry timing.

## Public target API

Keyword arguments below are keyword-only. Store methods are synchronous.

```python
JobStore(path, *, clock=None, retry_base_seconds=1.0, retry_cap_seconds=60.0)
store.enqueue(kind, payload, *, max_attempts=3, idempotency_key=None) -> Job
store.get(job_id) -> Job
store.list_jobs(*, state=None, kind=None, limit=100, offset=0) -> list[Job]
store.stats() -> dict[str, int]
store.claim(worker_id, *, lease_seconds=30.0, kinds=None) -> Job | None
store.heartbeat(job_id, token, *, lease_seconds=30.0) -> Job
store.complete(job_id, token, result) -> Job
store.fail(job_id, token, error) -> Job
store.cancel(job_id) -> Job
store.reap_expired() -> int
store.events(job_id, *, after_seq=0, limit=100) -> list[dict]
```

Export `LeaseLost` and `IdempotencyConflict` from `jobservice`; both must derive
from `JobServiceError` (defined in `jobservice.errors`). Unknown job ids raise
`JobNotFound`; malformed inputs raise `ValidationError`. A missing/non-current/
expired token on an existing job raises `LeaseLost`, even before a reaper runs.
The token may be `None` as input, but must never authorize a transition.

Jobs add `available_at: float`, `idempotency_key: str | None`,
`cancel_requested: bool`, `lease_owner: str | None`, `lease_token: str | None`,
`lease_expires_at: float | None`. JSON dictionaries expose these fields too.
Valid states are `queued`, `running`, `succeeded`, `failed`, `cancelled`.
All non-running records have all three lease fields cleared. Terminal states
never become runnable again. A succeeded job has its committed result and no
error; failed/cancelled jobs have result None. Job records remain detached.

### Enqueue and idempotency

Validate nonblank string kind, JSON-serializable finite payload, integer (not
bool) max_attempts >=1, and optional nonblank string key. Empty/whitespace keys
are invalid; key whitespace otherwise has no normalization. Key scope is the
whole database, across kinds and terminal states, without TTL. Under concurrent
submissions, one key creates at most one job and one `enqueued` event. Repeating
the same key returns the existing job iff kind, canonical JSON payload and
max_attempts match. Object key order is ignored; JSON values such as `1` and
`1.0` are not interchangeable. Conflict raises `IdempotencyConflict` with no
mutation. No key means each submission creates a distinct job.

### Claim, clocks, leases and fencing

Clock is an injected callable returning finite epoch seconds; omitted means
wall time. Assume it is nondecreasing for one database. Tests use deterministic
clocks; implementation must not sleep to meet correctness. Lease lengths, retry
base/cap must be finite positive numbers, not bool; cap >= base. `kinds` is None
or an iterable of nonblank strings; empty means claim nothing. A bare string is
invalid. `claim` validates first, recovers *all* expired running attempts, then
atomically selects one eligible queued job. Eligibility: available_at <= now.
Order: available_at, then created_at, then original insertion order. Kind filters
only affect selection, not expiry recovery. An empty filter still recovers.

A successful claim increments attempts exactly once, records worker_id, returns
a fresh opaque nonempty string token, sets expiry to now + lease_seconds, and
emits `claimed`. Tokens must change even when the same worker reclaims a job.
One job can have at most one current claim across threads/processes/store
instances. No handler code runs inside a SQLite write transaction.

The validity interval is half-open: a lease is valid only while now < expiry.
At equality it is expired. heartbeat, complete and fail atomically verify state,
token and expiry before changing anything. Stale/wrong/None tokens never change
job state, result, error, attempts, timestamps or event history. A current
heartbeat resets expiry to now + lease_seconds (not old expiry + duration),
preserves token/attempt count, and emits `heartbeat`. There is no global worker
identity authority: token + live lease is the fencing capability.

### Failure, recovery and retries

On an authorized `fail`, persist the nonblank error string. If attempts is below
max_attempts, return to queued and schedule at
`now + min(retry_cap_seconds, retry_base_seconds * 2**(attempts - 1))`.
Otherwise transition to failed. Retry arithmetic must stay safe for very large
attempt counts; cap it without constructing an enormous integer exponent.
No jitter. Attempts count claims, including abandoned attempts, not failures.

`reap_expired()` atomically resolves every expired running record and returns
the number resolved. It uses the same retry/exhaustion policy, with exact error
text `lease expired`, except cancellation takes precedence. Recovery backoff is
anchored at recovery time, not historical expiry. Clear lease fields. Repeating
reap at the same time makes no extra transitions/events. `claim` invokes this
same recovery behavior before selection. `get`, `list_jobs`, `stats` and `events`
are read-only and never secretly recover work.

### Cancellation and terminal behavior

`cancel` on queued work immediately produces cancelled with cancel_requested
true. On running work it records cancel_requested true, retaining the live lease
and running state, so the owner can cooperatively stop. A current completion or
failure after that request transitions to cancelled, never succeeded or retry.
A heartbeat remains allowed and returns cancel_requested so the handler can
notice it. Expiry recovery also resolves a cancelled-requested attempt directly
to cancelled. Repeated cancel requests are no-ops (including events/timestamps).
On any terminal state, cancel is a no-op, including a succeeded result. Missing
ids still raise JobNotFound. Cancellation does not kill threads/processes.

### Worker and handler integration

Keep existing Worker arguments and add `lease_seconds=30.0`. Worker claims with
that duration and passes its current token on completion/failure. Add
`context.heartbeat() -> bool`: renews using the worker's lease duration and
returns cancel_requested. Add `context.check_cancelled() -> None`: renews and
raises exported `JobCancelled` (a JobServiceError) if cancellation is requested.
The context's existing fields/logging stay compatible. Handlers explicitly call
these methods; no background heartbeat thread is required or desired.

Ordinary handler errors (including non-JSON/nonfinite return values) go through
the retry/failure path. Process-control BaseExceptions propagate and leave the
attempt for recovery. If a worker loses its lease during a handler, it must not
persist that handler's result/error or crash its polling caller with LeaseLost;
`run_one` returns the current durable job snapshot instead. Do not mask unrelated
storage errors as success. A JobCancelled raised by a handler without a durable
cancel request is just an ordinary handler failure. Delayed retries mean
run_until_idle may return a queued outcome then stop.

### Atomic observability

Each successful mutation writes an event in the same SQLite transaction as the
job change; failed writes roll back both. Event dictionaries have `seq` (globally
increasing positive integer), `job_id`, `type`, `at` (clock timestamp), `attempt`
(resulting attempt count), `details` (JSON object). Event types:
`enqueued`, `claimed`, `heartbeat`, `retry_scheduled`, `succeeded`, `failed`,
`cancel_requested`, `cancelled`. One event per mutation; do not emit a separate
failure event when retrying. Details may include operational context; their
exact content is not graded. Do not put executable handler objects in storage.

`events(id, after_seq=0, limit=100)` returns ascending sequence, strictly after
the cursor, for that job only. Validate integer nonnegative cursor and limit
1..1000. It raises JobNotFound for absent ids. Legacy migrated jobs may have one
`imported` baseline event; no invented history is required. No-op cancellation,
idempotent enqueue, idle polls, stale attempts and repeat reaping add no events.
`stats()` includes all five state names with zeros, counting durable state only.

### CLI additions

Preserve old commands and JSON-lines/error behavior. Add:

```sh
python3 -m jobservice --db q.sqlite submit echo '{"x":1}' --idempotency-key request-7
python3 -m jobservice --db q.sqlite cancel JOB_ID
python3 -m jobservice --db q.sqlite events JOB_ID --after-seq 0 --limit 100
python3 -m jobservice --db q.sqlite reap
python3 -m jobservice --db q.sqlite work --once --lease-seconds 20
```

cancel emits a Job, events emits one JSON object per event, reap emits exactly
`{"recovered": N}`. CLI input/application errors use code 2 and stderr; an empty
worker poll succeeds without stdout. CLI uses the real clock; deterministic
lease/retry boundary tests use the Python API.

## Verification and operational intent

Test independent store connections, deterministic race coordination, fencing at
and beyond expiry, recovery after an abruptly exiting worker process, bounded
retry/exhaustion, cancellation boundaries, concurrent idempotency, migration,
transaction rollback, CLI, and existing regressions. Do not rely on long sleeps.

Document the exact delivery guarantee: database attempt transitions and event
commits are fenced/atomic, but handlers may execute more than once after crash
or lease expiry. External effects are at-least-once, NOT exactly-once. A token
fences this queue's writes, not arbitrary external APIs/files. Callers needing
effect deduplication must use their own downstream idempotency mechanism.

Non-goals: distributed clock consensus, brokers/network servers, auth, UI,
multi-host network-filesystem SQLite, priorities, cron, retry jitter, pruning,
forced process termination, exactly-once external effects, async frameworks,
automatic heartbeat threads or a permanently polling daemon.
