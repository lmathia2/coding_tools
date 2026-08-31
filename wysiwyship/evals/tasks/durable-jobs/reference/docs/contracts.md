# Public contracts

Python 3.9+, standard library only. All optional parameters shown after `*` are
keyword-only. Timestamps are epoch seconds from a shared nondecreasing callable
clock; default is wall time. Path must name a local SQLite file in an existing
directory. Connections are operation-scoped; `:memory:` is unsupported.

```python
JobStore(path, *, clock=None, retry_base_seconds=1.0, retry_cap_seconds=60.0)
store.enqueue(kind, payload, *, max_attempts=3, idempotency_key=None)
store.get(job_id)
store.list_jobs(*, state=None, kind=None, limit=100, offset=0)
store.stats()
store.claim(worker_id, *, lease_seconds=30.0, kinds=None)
store.heartbeat(job_id, token, *, lease_seconds=30.0)
store.complete(job_id, token, result)
store.fail(job_id, token, error)
store.cancel(job_id)
store.reap_expired()
store.events(job_id, *, after_seq=0, limit=100)
```

The store returns frozen detached Job records except: list_jobs returns a list;
stats returns state counts; claim may return None; reap_expired returns a count;
events returns event dictionaries. `to_dict()` is JSON-ready. Existing fields:
id, kind, payload, state, attempts, max_attempts, created_at, updated_at, result,
error. New fields: available_at, idempotency_key, cancel_requested (bool),
lease_owner, lease_token, lease_expires_at. The three lease fields are None
outside running. States: queued, running, succeeded, failed, cancelled.

## Inputs and queries

Kind, worker_id, supplied idempotency key and error are nonblank strings. Payload
and result must be finite JSON. max_attempts is a positive integer, not bool.
Durations/base/cap are finite positive numbers, not bool, and cap >= base.
`kinds` is None or an iterable of nonblank strings; a bare string is invalid.
Limit is 1..1000 and offset/after_seq is an integer >=0; bool is not an integer
for validation. Unknown states are invalid. Query lists order by created_at and
original insertion sequence. Claims order by available_at, created_at, sequence.
Read APIs are non-mutating even when a lease has expired. Counts include zeros.

An idempotency key is global and permanent: kind, canonical payload and attempt
limit must match its original submission, including after terminal completion.
Object key order is ignored; numeric JSON encodings 1 and 1.0 remain distinct.
Absent keys always create new records. Replays and conflicts add no events.

## Attempts and cancellation

Claim first recovers all expired attempts (even with an empty kind filter), then
selects eligible queued work with available_at <= now. Claim increments attempts
and supplies a fresh token. Its lease is valid only before expiry, not at it.
Heartbeat resets expiry to now + duration, retaining attempts and token. All
owned writes require a live matching token; None, stale, expired, wrong-token,
and terminal writes raise LeaseLost without modifying records or history.

Failure persists the error, clears the lease and either fails terminally or
queues at `now + min(cap, base * 2**(attempts-1))`. Recovery uses that same policy
with error `lease expired` and its observation timestamp. Claimed abandoned
attempts count toward exhaustion. Repeated reaping makes no extra transitions.

Cancel on queued work is immediately terminal. Cancel on running work records
cancel_requested while retaining ownership. A later live complete/fail or expiry
recovery resolves it to cancelled, discarding any result and not retrying.
Heartbeat can still renew and report the flag. Repeated cancellation and cancel
on a terminal record are exact no-ops. Successful results are never discarded by
a later cancel. Cancellation does not interrupt a thread or kill a process.

## Events and exceptions

Event fields: seq (global increasing positive integer), job_id, type, at, attempt
(resulting claim count), details (JSON object). Types: enqueued, claimed,
heartbeat, retry_scheduled, succeeded, failed, cancel_requested, cancelled, and
optional imported migration baseline. Exactly one event per successful mutation;
no event for a no-op or rejected attempt. Cursor queries are exclusive and
ascending, filtered to the requested job. Job and event writes share a transaction.

`JobNotFound` means absent id. `ValidationError` means malformed input.
`IdempotencyConflict` means a key is bound to different submission inputs.
`LeaseLost` means the caller cannot mutate this attempt. `JobCancelled` supports
cooperative handler interruption. All derive from `JobServiceError` and are
exported with the original package API. Storage errors
propagate rather than silently becoming successful commands.

## Worker and CLI

`Worker(store, registry=None, *, worker_id=None, logger=None, lease_seconds=30.0)`
keeps the original fields and adds duration. `run_one(kinds=None)` returns an
outcome/snapshot or None. `run_until_idle(max_jobs=100, kinds=None)` returns one
outcome per processed attempt, stopping at the first currently empty poll or
its bound; it never waits for future retries. Handlers are `(payload, context)`
callables returning finite JSON. Context keeps job_id, attempt, worker_id and
log(message, **fields), and adds heartbeat() -> cancel_requested and
check_cancelled() -> None (raises JobCancelled after renewal when requested).
Explicit checks are the only automatic work a handler opts into; there is no
background renewal thread. Spurious JobCancelled without a persisted request is
an ordinary handler error. Non-JSON results enter the ordinary failure path.
Stale handler results/errors cannot overwrite durable state; worker returns its
current snapshot. Process-control BaseExceptions propagate for recovery.

Existing CLI commands and flags remain. Add submit --idempotency-key KEY,
work --lease-seconds N, cancel ID, events ID --after-seq N --limit N, reap.
cancel emits a Job; events emits one object per event; reap emits {"recovered": N}.
stdout is JSON lines, stderr diagnostics. Application/JSON errors return code 2
with one diagnostic JSON object; argparse errors also use code 2. Handler failures
are job outcomes, not command failures. An empty work poll returns 0 with no output.

## Delivery guarantee

Only one authorized completion commits for an attempt, and its history is atomic.
Handlers can run again after expiry/crash, including after an external effect.
External effects are at-least-once; lease fencing and submission idempotency do
not confer exactly-once effects on an email, file or downstream API.
