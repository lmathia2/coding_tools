# Architecture and failure boundaries

`cli` translates JSON-lines commands into `JobStore`/`Worker`. `JobStore` owns
state, persistence and audit events. `Worker` invokes registered handlers outside
transactions. `ExecutionContext` provides correlated logging and explicit lease
renewal/cancellation checks. Clock injection makes boundaries deterministic.

## Serialization and transactions

`Database` opens a fresh SQLite connection for each operation. Each writer uses
`BEGIN IMMEDIATE`, acquiring the write reservation before reading the record that
determines a transition. This serializes independent connections/processes, not
just threads sharing a Python object. WAL supports concurrent readers; a ten
second busy timeout bounds temporary contention. Handler code never holds that
write reservation. SQL parameters carry user inputs; dynamic column names come
only from implementation-owned update fields.

`JobStore._change` writes the record and its event within that same transaction.
`enqueue` does likewise for the initial event. An event insert failure rolls back
the state change, and a state write failure cannot leave a committed event.
The `job_events` sequence is global, while reads filter by job and exclusive
cursor. Idle polls, idempotent reads/submissions, stale writes and no-op cancels
do not add events. Handler logs are an independent injectable diagnostic channel,
not the committed transition history.

## State machine

| Input | State before | Committed outcome |
| --- | --- | --- |
| Claim eligible | queued | running, attempts +1, fresh owner/token/expiry |
| Live heartbeat | running | same attempt/token, expiry = now + duration |
| Live completion | running | succeeded and result, unless cancel requested |
| Live failure | running | delayed queued retry, or failed if exhausted |
| Cancel | queued | cancelled immediately |
| Cancel | running | same lease plus cancel_requested |
| Owner finishes or reaper resolves cancelled attempt | running | cancelled |
| Expiry/recovery | running | delayed queued retry or failed, error = lease expired |
| Stale token / terminal mutation | any | rejected or documented cancel no-op |

Expiry is exact: validity is `now < lease_expires_at`. A stale worker cannot win
merely because the reaper has not run. Every owned write verifies state, current
token and timestamp inside its write transaction. Reusing a worker_id gives no
authority; a reclaimed attempt receives a different token. Non-running records
clear lease fields. Terminal states are never requeued.

`_recover` and ordinary failure share `_failure`, keeping cancellation precedence,
retry exhaustion and lease cleanup consistent. Retry delay is based on claim
count, uses bounded exponential arithmetic, and is anchored at the recovery or
failure observation time. `claim` recovers every expired attempt before applying
kind filters. Read APIs never trigger recovery, so monitoring does not change
queue behavior. A supervisor must keep issuing claim or reap operations.

## Idempotency and migration

An optional global idempotency key binds kind, canonical finite JSON payload and
max_attempts. Under one write transaction, matching inputs return the original
record; conflicts change nothing. A partial unique index provides an additional
database-level safeguard. Null keys are not deduplicated. JSON object order is
ignored, but `1` and `1.0` have distinct canonical encodings.

Startup migration uses transactional DDL and data updates under one write lock.
Existing base fields and insertion sequence are preserved. Added nullable lease
fields leave legacy running records unowned; recovery detects that condition.
Queued records use their created timestamp for immediate eligibility. One
`imported` baseline event captures a legacy record, without inventing historical
transitions. Reopening does not repeat import events. Version 2 is recorded with
SQLite user_version; newer versions are refused rather than downgraded.

## What is not atomic

A handler can produce an external effect, then crash before completion; recovery
will execute another attempt. It can also keep running after its lease expires.
Fencing prevents both attempts from committing conflicting queue state, not from
performing external effects. Exactly-once database transition acceptance is not
exactly-once execution or delivery. Pass business idempotency keys to downstream
systems if repeated external effects are unacceptable. Cancel does not kill a
handler; explicit context checks let cooperative code stop early.

Worker catches LeaseLost and returns the current durable snapshot. It retries
ordinary handler errors and invalid result serialization, but propagates storage
failures. KeyboardInterrupt/SystemExit still escape for supervisor recovery.
