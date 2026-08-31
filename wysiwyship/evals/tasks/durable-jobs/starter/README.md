# Jobservice

A standard-library-only Python 3.9+ SQLite job queue for local automation. There
is no server, installation step, network service, or daemon required. Run commands
from this directory (or put it on `PYTHONPATH`). Each command emits JSON lines.

```sh
python3 -m jobservice --db demo.sqlite submit summary '{"values":[2,4,6]}'
python3 -m jobservice --db demo.sqlite work --once
python3 -m jobservice --db demo.sqlite list --state succeeded
python3 -m jobservice --db demo.sqlite stats
python3 -m unittest discover -s tests -v
```

`submit KIND -` reads one JSON value from stdin. `show ID` reads a record. `list`
accepts state/kind filters and limit/offset pagination. `work --kind echo` restricts
execution to one kind (repeat the flag for several). `work --max-jobs N` stops at
the first empty poll or N processed attempts; it never sleeps.

Built-ins are `echo` (any JSON value), `summary` (`{"values":[1,2]}`), `render`
(`{"template":"Hi {name}","values":{"name":"Ada"}}`), and `fail`
(`{"message":"demonstration"}`). Register custom callables using
`HandlerRegistry().register("kind", handler)`, then pass the registry to `Worker`.

Python entry points and behavior are described in [contracts](docs/contracts.md).
Storage and execution boundaries are in [architecture](docs/architecture.md).

## Operational limitations

Jobs persist across normal restarts, but a worker killed after claiming a job
leaves it running indefinitely. Errors are retried immediately; there is no
delayed scheduling, lease renewal, cancellation, deduplication or transition
history. Do not use this version for unattended crash-sensitive workloads.
