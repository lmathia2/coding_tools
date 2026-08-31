# Existing application contracts

`JobStore(path, clock=callable)` accepts a SQLite file path and optional callable
returning wall-clock seconds. A connection is never retained on the store object.

- `enqueue(kind, payload, max_attempts=3) -> Job`: nonempty kind, finite JSON,
  positive integer attempt limit. Submission is independent of handler registry.
- `get(id) -> Job`: raises `JobNotFound` for absent ids.
- `list_jobs(state=None, kind=None, limit=100, offset=0) -> list[Job]`: ascending
  created timestamp/insertion order. Limit is 1..1000, offset is nonnegative.
- `stats() -> dict`: all known state names, including zero counts.
- `claim(worker_id, kinds=None) -> Job|None`: oldest queued job, atomically moves
  to running and increments attempts. Empty kinds claims nothing.
- `complete(id, result)` and `fail(id, error)` are worker-internal transitions.
  Only running jobs accept them. Failure retries immediately until exhausted.

`Job` is a frozen dataclass; `to_dict()` gives a detached JSON-ready dictionary.
Mutating decoded payloads cannot mutate stored records. Fields: id, kind, payload,
state, attempts, max_attempts, created_at, updated_at, result, error.

`Worker(store, registry=None, worker_id=None, logger=None)` defaults to built-ins.
`run_one(kinds=None)` returns the resulting job or None on an empty poll.
`run_until_idle(max_jobs=100, kinds=None)` returns outcomes, one per processed
attempt, and stops at empty or its limit. Ordinary exceptions become persisted
`TypeName: message` errors; process-control exceptions propagate. A handler is a
callable `(payload, context) -> finite JSON`. Context fields are job_id, attempt,
worker_id; `context.log(message, **fields)` sends a structured dict to the logger.

CLI commands are `submit`, `show`, `list`, `work`, `stats`. Successful commands
return zero. Application and JSON-input errors return 2 with one diagnostic JSON
object on stderr; no traceback or stdout error records. Argument errors use
argparse diagnostics and code 2. Jobs which fail inside work are still outcomes,
not command errors. With no eligible work, work emits no records and returns 0.
