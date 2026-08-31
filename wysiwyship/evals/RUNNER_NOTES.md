# Local runner: contracts and limits

The runner uses Python 3.9+ and its standard library. Fixture validation and
grading are offline. Git is required for preparation; Codex is required only
for an explicitly authorized `run --execute`.

## Lifecycle

`list` reads `catalog.json`. `validate` verifies each pilot's original regression
tests pass, at least two acceptance assertions or per-test runtime checks fail
on its starter, and both groups pass after applying the reference overlay.
Discovery/import collapse, zero tests, skips, expected failures, timeouts and
malformed grader output are not passes. Planned entries are shown as skipped;
an all-planned catalog is not a successful validation. Counts are unittest test
counts, not independent assertions or requirement-coverage percentages.

`prepare TASK --condition baseline|workflow --output NEW_ABSOLUTE_DIRECTORY
--model EXACT_MODEL --reasoning low|medium|high|xhigh` creates one trial. The
timeout defaults to 7200 seconds and must be positive. `--harness-root` overrides
the default harness (the parent of the runner directory). Global `--suite-root`
overrides the fixture directory, which defaults to the runner directory.

Only starter files and the task brief are copied from the fixture into the
candidate workspace. Reference and acceptance files are not copied there.
Existing destinations, reserved runtime paths in starters, unsafe nesting and
symlinks are rejected. The only symlink-path exceptions are macOS's standard
`/tmp` and `/var` aliases. Partial preparations remain inspectable and are never
silently overwritten; use a new destination after an error.

The workflow arm runs the project Codex installer with the current interpreter
and `--no-model-discovery`. It pins every active-profile Codex role and workflow,
rewrites all native agent TOMLs using the harness adapter, and writes a named
`argv` regression check. Installer stdout/stderr are retained. Installation is
completed before the initial Git commit. That commit uses fixed local identity,
disabled signing/hooks/templates and no global Git configuration changes.

Both prompts contain identical task, documentation, ELI5 and verification
requirements. The workflow prompt additionally starts with
`$engineering-workflow auto`. This assignment and the installed configuration
are **not proof of actual workflow invocation**; audit the execution trace.
The task brief controls ordinary implementation/commit behavior for both arms.

## One attempt, separate grading

`run TRIAL` prints a JSON command preview and never launches a process or makes
a network call. `run TRIAL --execute` launches one bounded `codex exec` using
the saved CLI login. There is no credential-file access/copying or API-key
fallback in the runner. The argv uses JSON output, an ephemeral session,
`--ignore-user-config`, workspace-write sandboxing, exact requested model and
reasoning effort, and a final-message output file. The optional
`--codex-executable` exists for offline fake-executable testing.

An exclusive, fsynced `STARTED.json` marker is written before launch. Receipts
are atomically replaced and fsynced. A started, failed, interrupted or completed
trial cannot be relaunched; prepare a new trial. `run.json` distinguishes
completed, nonzero, timeout, interrupted, launch_error and event_error outcomes.
Elapsed time is monotonic. JSONL/stdout and stderr are retained on failures.
Timeout/interruption cleanup terminates the POSIX process group, escalates to
KILL even if its leader has exited, and waits for the direct child. Processes
that deliberately escape the group are outside this local runner's boundary.
On non-POSIX systems only direct-process cleanup is available.

Token observations are summed from nested `turn.completed.usage` records. A
missing field remains null, never zero. Invalid JSON lines are counted without
crashing. `turn.failed`/`error` events prevent a successful run receipt even if
the CLI exits zero. A zero-turn trace is not evidence of model execution.
Requested model is configuration; effective model is always `UNVERIFIED`, and
child-agent usage coverage and host-global instruction/skill contamination
remain unknown. `--ignore-user-config` is not full host isolation.

`grade TRIAL` runs canonical regression and acceptance groups in separate fresh
candidate copies with separate processes. Copies exclude agent tests, Git,
runtime state, installed harness/skills/config and caches. The full canonical
test directory (including helper modules and SQL fixtures) is copied separately.
The candidate is both cwd and PYTHONPATH for tests and their CLI subprocesses.
Structured grader reports must be well-formed and agree with an exit-zero run;
stdout is diagnostic, not a result channel. Unexecuted workspaces may be graded
for diagnostics, but cannot produce a comparative win.

## Revision and comparison rules

Preparation freezes suite/task versions, fixture contents (excluding caches),
runner/grader source hashes, the exact treatment configuration, and relevant
Codex installer inputs. The installed workflow snapshot is hashed separately.
The whole surrounding repository is never hashed. Launch, grading and comparison
recheck these pins. Grades also pin candidate contents; later changes make them
stale. These checks detect accidental drift, not malicious receipt rewriting by
another process under the same user account.

`compare TRIAL...` requires exactly one baseline and one workflow per matching
task, fixture/evaluator/harness revision, requested model, reasoning effort,
run timeout and grading timeout. Duplicates, missing pairs, mismatches, missing
grades and stale revisions fail closed without printing a bogus delta. Matching
trials with infrastructure failure or no completed-turn evidence remain visible
as diagnostic pairs with null deltas and nonzero exit status. Valid pairs show
correctness and elapsed-time deltas plus per-arm run status, token observations
and source/documentation metrics. They are observations, not causal claims.

Source LOC and file changes exclude tests, docs and installed/runtime harness
content, and include added and deleted source files. Python function complexity
uses the existing stdlib harness analyzer's `analyze_code` and `attach_baseline`
functions. Only changed functions are reported, with before/after scores and
matched-function deltas. Added/deleted baselines and unavailable metrics are
null, not zero. Source syntax errors are reported as analyzer errors. README,
docs and HTML presence is an artifact check, not documentation accuracy.

## Verification

Run `python3 -m unittest discover -s tests -v` from the evals directory. Installer,
pair and analyzer integration tests use its parent harness; for an isolated
runner checkout, set `EVAL_TEST_HARNESS_ROOT` to a real harness source directory.
Tests never launch a model, inspect credentials or contact services. They use
temporary fixtures, fake Codex executables and mocked interruption only.

The completed offline verification includes actual installer/native pinning,
canonical-test tampering, fresh-copy isolation, helper/SQL preservation,
symlink/no-overwrite checks, planned tasks, malformed/zero/skipped/discovery
grading, matched and rejected comparisons, stale grades, nested/missing tokens,
failure receipts, and a TERM-ignoring descendant whose heartbeat stops on timeout.
The local grader executes trusted evaluation code under the same account as the
candidate. It is not a security sandbox or anti-cheating isolation.

## Simplicity review

The runner/grader remain two standard-library modules: no plugin architecture,
generic task execution framework, scheduler, dashboard or external service.
The complexity check passes at a ceiling of 20, but that is a guardrail, not an
assertion that every function is simple. Current runner hotspots are `metrics`
(20), `complexity_delta` (16), `validate` (14), and `trace_summary` (13).

These functions each traverse one bounded report or comparison. File matching,
added/deleted cases, missing evidence and validation failures explain their
branches. The concrete next simplification, if these contracts grow, is extracting
a per-file diff result from `metrics` and a per-function record from
`complexity_delta`; keep missing baselines explicit. Do not replace these short
loops with a report framework just to reduce the score. Fixture CLI dispatch
(maximum 18) and acceptance-process cleanup (12) are also bounded and tested;
retain behavior-first checks when extracting command handlers.
