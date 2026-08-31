# Architecture

`cli` translates JSON-lines commands into `JobStore` and `Worker` calls. The
store owns persistence and validation; the worker owns invoking handlers.
`HandlerRegistry` decouples application code from execution, and immutable
`ExecutionContext` attaches correlation metadata to an injectable logger.

`Database` opens a new connection for each operation. Writes use explicit
transactions with `BEGIN IMMEDIATE`; reads return detached dataclass records.
WAL allows readers while a writer is active. SQLite's busy timeout handles short
writer contention. The file path's parent must already exist. In-memory databases
are deliberately unsupported because connections are operation-scoped.

The jobs table has a monotonic insertion sequence and a public UUID id. Selection
uses timestamp and insertion sequence, so simultaneous submissions have stable
FIFO order. Payloads/results are canonical finite JSON. Handler code runs outside
database transactions and can call back into the store without holding its lock.

The state machine is queued -> running -> succeeded. A handler exception moves a
running record to queued if attempts remain, otherwise failed. Claims increment
attempts, not submissions. Completed results and last error text are persisted.
The store does not register handlers: unknown kinds can be submitted, and fail
normally when an unconfigured worker tries to execute them.

Known failure boundary: after claim commit, a process crash has no recovery
mechanism. Database atomicity does not make a handler's external effects atomic.
`KeyboardInterrupt`/`SystemExit` intentionally escape the worker. Supervisors must
currently reconcile abandoned jobs manually.
