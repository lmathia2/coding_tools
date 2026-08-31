# Maintainer notes — durable-jobs pilot

## Packaging and isolation

`starter/` is the entire candidate application. Copy it into a disposable project,
then provide the identical `task.md` to either arm. `reference/` is an overlay:
copy only its contents on top of starter for a golden candidate. It contains
changed implementation/docs and one added local test module, not unchanged
handlers/clock/entrypoint/legacy tests. Never expose reference, rubric, maintainer
notes or evaluator acceptance tests inside the candidate task workspace.

`acceptance/` is evaluator-owned unittest discovery, separate from candidate
`tests/`. Candidate modules are resolved through `PYTHONPATH`. Acceptance support
imports only legacy package symbols at module scope: every test family discovers
against the starter, rather than disappearing after a new-symbol import failure.
No network, third-party packages, model calls, commits or pushes are required to
author or verify this pilot. Both evaluation arms have identical deliverables,
including an offline developer HTML explainer; process instructions belong in
the runner's arm prompt, not the shared task. Optional disposable local commits
are allowed to both arms; pushing/remotes are not.

## Reproduction commands

From this pilot directory, with a Python 3.9+ interpreter:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/starter" python3 -m unittest discover -s starter/tests -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/starter" python3 -m unittest discover -s acceptance -v
EVAL_GOLDEN="$(mktemp -d)"
cp -R starter/. "$EVAL_GOLDEN/"
cp -R reference/. "$EVAL_GOLDEN/"
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$EVAL_GOLDEN" python3 -m unittest discover -s "$EVAL_GOLDEN/tests" -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$EVAL_GOLDEN" python3 -m unittest discover -s acceptance -v
```

Each reproduction uses a fresh temporary golden directory to avoid stale files.
The second command is intentionally nonzero: the starter is the deliberately
incomplete candidate. Its legacy behavior works, but its queue has no leases,
recovery, audit events, cancellation or idempotency and retries immediately.
Do not turn this negative control into an expected passing score.

## Observed verification

Author verification on 2026-08-31, Python 3.9.6 / SQLite 3.51.0 (confirm exact
runtime in the accompanying run output if using a different host):

- Starter legacy: 13 tests pass.
- Starter acceptance: all 47 tests discover; expected nonzero with failures in
  leases, retries, cancellation, idempotency/events, concurrency/worker, migration
  and CLI (8 failure records, 40 error records, zero skips). unittest records
  multiple subtest errors in some failing cases, so
  failures+errors can exceed testsRun; do not treat those as extra cases.
- Golden legacy + added local tests: 19 tests pass.
- Golden evaluator acceptance: 47 tests pass (the initial 46-test suite took
  1.814 seconds; later one storage-failure propagation check was added).
- A separately staged almost-complete mutant removed only the expiry comparison
  in `_owned`, retaining the full API and all other durability features. Its
  eight lease tests discovered and failed at the exact-expiry boundary (two
  failure records from one case/subtest). This verifies a behavioral defect is
  rejected independently of starter missing-API failures. Reproduction: overlay
  reference on a separate copy, remove `or now >= job.lease_expires_at` only, then
  run `PYTHONPATH=/absolute/mutant python3 -m unittest discover -s acceptance -p test_leases.py -v`.
- Python 3.9 AST parsing succeeded for all 30 application/test source files;
  overlay audit found no unchanged source/doc copies; all 12 HTML source/docs
  links resolve in the overlay-composed application.

Wall-clock verification duration is not engineering-task difficulty. The proposed
45–120 minute agent duration remains UNMEASURED pending actual Codex pilot runs.
No effective model identity is inferred. Author route:
`3a0e3cf1-2d0d-440c-b6b1-10c9e6184280` (`wysiwyship_deep` native work unit).

## What the checks cover

- Live tokens and renewal, equality-at-expiry fencing before any reaper,
  same-worker token rotation, no stale mutation/history, read-only observability.
- Exact exponential retry boundaries and cap, exhaustion, huge attempt counts,
  crash recovery anchored at recovery time, empty/unmatched filters recovering.
- Queued/running/terminal cancellation, failure/expiry precedence, no-op history,
  actual cancellation/completion races and explicit handler heartbeats.
- Canonical-key replay/conflict across terminal state and concurrent enqueue,
  event cursor isolation/ordering/attempts, full zero-inclusive state counts.
- Independent SQLite connections with barriers; six competing child processes;
  a child that commits its claim and abruptly exits with `os._exit(17)`.
- Duplicate handler execution with fenced final state; stale handler errors;
  non-JSON result handling; old CLI behavior plus new CLI commands.
- Handwritten original schema migration with queued/running/succeeded/failed
  records, preservation and reopen idempotence, injected migration failure.
- SQLite trigger fault injection on discovered auxiliary event tables (or jobs
  for embedded history) verifies audit failure cannot commit state; a separate
  jobs-update fault verifies no event can precede a failed transition commit.

No sleep-based lease waiting is used. ManualClock drives lease/retry boundaries;
thread barriers and pipe start gates coordinate concurrency; subprocess waits
have safety deadlines. Trigger injection uses the existing jobs table and
discovers auxiliary tables without prescribing a new audit schema.

## Design decisions and known limits

The starter contains 12 meaningful application modules, 507 source lines, 13
legacy tests, and existing documentation. It is deliberately compact, not padded
to a line target: queue persistence, validated queries, registries, built-ins,
logging, worker polling, and JSON CLI are working functionality. Completing the
contract coordinates nine implementation files, persistence migration, API/CLI
integration, deterministic tests and documentation. It is not a TODO skeleton.

Reference keeps connection-per-operation SQLite and one writer transaction per
mutation. Mutation/event recording and failure/recovery decisions are shared,
not duplicate implementations. Handlers execute outside SQLite transactions.
Token authority checks are centralized and cancellation is cooperative. Retry
base/cap is configuration on each store, not persisted per job; operators must
use a consistent policy across workers. No jitter or background heartbeat.

The local complexity tool measured maximum production function scores of 14 in
starter CLI main and 18 in reference CLI main; all other application functions
are <=10. These are straightforward command dispatchers with injected streams and
shared error behavior. Splitting them into a framework would hide the CLI's small
public surface without improving the state-machine invariants. No function is
above the proposed <=20 gate. Reference local tests also remain below the gate.
The complexity tool is only a maintainer convenience, not a runtime
or candidate dependency.

The acceptance suite is not exhaustive model checking. It does not simulate disk
power loss, every SQLite filesystem/lock failure, adversarial clock regressions,
multiple hosts, or handler external APIs. It checks committed database behavior,
not exactly-once external effects. Python syntax is kept 3.9-compatible; no newer
language feature is required. Neither timing claims nor effect guarantees should
be inferred from these deterministic checks. Human review remains necessary for
purpose/intent, documentation accuracy, complexity and scope.
