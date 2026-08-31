"""JSON-lines CLI. Diagnostics go to stderr, records go to stdout."""

import argparse
import json
import sys

from .errors import JobServiceError
from .store import JobStore
from .worker import Worker


def parser():
    root = argparse.ArgumentParser(prog="python -m jobservice")
    root.add_argument("--db", required=True, help="path to SQLite database")
    commands = root.add_subparsers(dest="command", required=True)
    submit = commands.add_parser("submit", help="persist a JSON job")
    submit.add_argument("kind")
    submit.add_argument("payload", help="JSON value, or - to read stdin")
    submit.add_argument("--max-attempts", type=int, default=3)
    submit.add_argument("--idempotency-key")
    show = commands.add_parser("show", help="read one job")
    show.add_argument("job_id")
    listing = commands.add_parser("list", help="oldest-first paginated records")
    listing.add_argument("--state")
    listing.add_argument("--kind")
    listing.add_argument("--limit", type=int, default=100)
    listing.add_argument("--offset", type=int, default=0)
    work = commands.add_parser("work", help="process jobs without waiting")
    work.add_argument("--once", action="store_true")
    work.add_argument("--max-jobs", type=int, default=100)
    work.add_argument("--kind", action="append", dest="kinds")
    work.add_argument("--worker-id")
    work.add_argument("--lease-seconds", type=float, default=30.0)
    commands.add_parser("stats", help="counts by state")
    cancel = commands.add_parser("cancel", help="request cooperative cancellation")
    cancel.add_argument("job_id")
    events = commands.add_parser("events", help="read committed transition history")
    events.add_argument("job_id")
    events.add_argument("--after-seq", type=int, default=0)
    events.add_argument("--limit", type=int, default=100)
    commands.add_parser("reap", help="recover expired attempts")
    return root


def emit(record, stream):
    if hasattr(record, "to_dict"):
        record = record.to_dict()
    stream.write(json.dumps(record, sort_keys=True, allow_nan=False) + "\n")


def main(argv=None, *, stdin=None, stdout=None, stderr=None):
    stdin = stdin if stdin is not None else sys.stdin
    stdout = stdout if stdout is not None else sys.stdout
    stderr = stderr if stderr is not None else sys.stderr
    args = parser().parse_args(argv)
    try:
        store = JobStore(args.db)
        if args.command == "submit":
            raw = stdin.read() if args.payload == "-" else args.payload
            job = store.enqueue(args.kind, json.loads(raw), max_attempts=args.max_attempts,
                                idempotency_key=args.idempotency_key)
            emit(job, stdout)
        elif args.command == "show":
            emit(store.get(args.job_id), stdout)
        elif args.command == "list":
            for job in store.list_jobs(state=args.state, kind=args.kind,
                                       limit=args.limit, offset=args.offset):
                emit(job, stdout)
        elif args.command == "work":
            worker = Worker(store, worker_id=args.worker_id, lease_seconds=args.lease_seconds)
            count = 1 if args.once else args.max_jobs
            for job in worker.run_until_idle(max_jobs=count, kinds=args.kinds):
                emit(job, stdout)
        elif args.command == "stats":
            emit(store.stats(), stdout)
        elif args.command == "cancel":
            emit(store.cancel(args.job_id), stdout)
        elif args.command == "events":
            for event in store.events(args.job_id, after_seq=args.after_seq, limit=args.limit):
                emit(event, stdout)
        elif args.command == "reap":
            emit({"recovered": store.reap_expired()}, stdout)
        return 0
    except (JobServiceError, ValueError) as exc:
        emit({"error": str(exc), "type": type(exc).__name__}, stderr)
        return 2
