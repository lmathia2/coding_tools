# Jobservice: durable leased queue

A standard-library-only Python 3.9+ SQLite queue for local automation. No server,
installation step, network dependency or daemon is required. Run from this
directory, or put it on `PYTHONPATH`. Commands emit JSON lines.

```sh
python3 -m jobservice --db demo.sqlite submit summary '{"values":[2,4,6]}' --idempotency-key report-7
python3 -m jobservice --db demo.sqlite work --once --lease-seconds 30
python3 -m jobservice --db demo.sqlite list --state succeeded
python3 -m jobservice --db demo.sqlite stats
python3 -m unittest discover -s tests -v
```

The [developer explainer](docs/explainer.html) covers what/how/why with source
links. [Architecture](docs/architecture.md) explains transactions and crash
boundaries. [Contracts](docs/contracts.md) specifies the public Python API.

## Working with jobs

`submit KIND -` reads JSON from stdin; `show ID` reads a record. `list` supports
state/kind filters and limit/offset pagination. `work --kind echo` restricts
execution (repeat for several kinds). `work --max-jobs N` stops at the first
empty poll or N processed attempts. Future retries do not make it sleep.

Built-ins: `echo` (any JSON), `summary` (`{"values":[1,2]}`), `render`
(`{"template":"Hi {name}","values":{"name":"Ada"}}`), `fail`
(`{"message":"demonstration"}`). Custom callables have `(payload, context)`
arguments and are registered with `HandlerRegistry().register(kind, handler)`.

```sh
python3 -m jobservice --db demo.sqlite cancel JOB_ID
python3 -m jobservice --db demo.sqlite events JOB_ID --after-seq 0 --limit 100
python3 -m jobservice --db demo.sqlite reap
```

## Guarantees and operating limits

Independent local workers claim atomically. Each attempt receives an expiring,
opaque token. Only its live owner can commit a result, error, or heartbeat.
Expired attempts recover on the next claim or explicit reap. Backoff defaults to
1, 2, 4, ... seconds, capped at 60; attempt exhaustion is terminal. Claim counts
include crashed attempts. Cancellation is immediate for queued work and
cooperative for running work: the owner or reaper resolves the terminal state.

Handlers running longer than their lease must explicitly call
`context.heartbeat()` or `context.check_cancelled()`. Neither a daemon nor an
automatic renewal thread is provided. A supervisor chooses when to poll again.
Use one consistent retry policy and a nondecreasing clock across workers. Use a
local filesystem, not multi-host/network-mounted SQLite.

State transitions and their audit events commit atomically. External handler
effects are **at-least-once**, not exactly-once: a crashed or expired handler may
have sent an email or written a file before another attempt repeats it. The queue
token fences queue writes only. Use downstream idempotency for such effects.
An enqueue idempotency key deduplicates submissions, not handler executions.

Existing database files migrate in place on open. Unowned legacy running attempts
are recoverable; terminal records retain their data. Back up the SQLite database
with SQLite's backup facilities before upgrading important workloads. Do not
copy just the main database file while WAL writers are active. There is no
pruning/TTL for jobs, keys or events in this version.
