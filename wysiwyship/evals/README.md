# Local engineering evaluations

Test whether WYSIWYShip improves a substantial coding change over ordinary Codex
execution. This is a small repository-owned evaluation suite, not another agent
framework. The runner, applications, and verifiers use Python's standard library.
No Harbor, Docker, package installation, external service, or downloaded benchmark
checkout is required. Codex is needed only when you explicitly launch an agent.

**Current milestone: two runnable pilots; eight tasks planned. Difficulty is not
yet calibrated and no improvement claim has been established.** See
[catalog.json](catalog.json) for status and [PLAN.md](PLAN.md) for the approved
pilot-first rollout. The 45–120 minute task target is unmeasured, not a minimum
runtime or a delay imposed by the runner.

## What the agent works on

| Pilot | Existing application | Requested engineering change |
|---|---|---|
| [Durable jobs](tasks/durable-jobs/task.md) | SQLite job service, worker, handlers, CLI, persisted history | Coordinate leases, stale-worker fencing, retries, recovery, cancellation, and idempotency |
| [Tenant isolation](tasks/tenant-isolation/task.md) | Project/issue service, memberships, cache, API boundary, exports | Carry tenant authorization through every read/write, cached result, relationship, and export lifecycle |

These start from working applications, not empty repositories or isolated TODO
functions. Existing behavior must remain intact. Correctness spans multiple
modules, persistence boundaries, and failure paths. Both conditions must deliver
updated tests, purpose/architecture/API documentation, and a developer explainer;
the baseline is not deliberately given a weaker task.

## First five minutes: no model usage

From the `coding_tools` repository root, use Python 3.9+ (Python 3.12 recommended
for consistency with local validation) and Git:

```bash
python3 wysiwyship/evals/runner.py list
python3 wysiwyship/evals/runner.py validate
python3 -m unittest discover -s wysiwyship/evals/tests -v
```

`validate` runs the starter's original regression suite and verifies the separate
reference solution against regression plus acceptance tests. It also checks that
the starter does not already solve the task. An incomplete starter failing new
acceptance tests is expected; a broken starter regression suite or failing
reference solution is not. These commands never invoke Codex.

The same runner tests and fixture validation are included in repository CI and
`config/checks.wysiwyship.json`. They are not added to installed projects' default
checks or distributed in the native workflow packages.

## Prepare a fair pair

Choose an exact model available in your Codex account. Use the same model,
reasoning effort, and timeout in both commands. Each destination must be new and
outside this repository's evaluation suite.

```bash
export EVAL_MODEL="your-exact-model-id"
python3 wysiwyship/evals/runner.py prepare durable-jobs \
  --condition baseline --output /tmp/wysiwyship-evals/jobs-baseline \
  --model "$EVAL_MODEL" --reasoning high --timeout-seconds 7200
python3 wysiwyship/evals/runner.py prepare durable-jobs \
  --condition workflow --output /tmp/wysiwyship-evals/jobs-workflow \
  --model "$EVAL_MODEL" --reasoning high --timeout-seconds 7200
```

Each trial gets a fresh working project and Git baseline. The workflow trial
additionally installs the real Codex adapter and skills using the repository's
installer with model discovery disabled. Its coordinator and every configured
specialist are pinned to the chosen model/effort. This isolates the workflow from
the benefit of using different models. The baseline gets no project-installed
WYSIWYShip instructions. Neither workspace contains the acceptance tests or
reference solution.

The task brief and outcome requirements are identical. The workflow prompt
explicitly invokes `engineering-workflow` in auto mode; it does not merely install
configuration and assume the skill ran. Trace review must still establish actual
workflow/agent use. Interactive clarification is a separate future experiment:
these tasks provide explicit contracts and use recorded assumptions without
human answers during execution.

## Preview, then explicitly run

```bash
python3 wysiwyship/evals/runner.py run /tmp/wysiwyship-evals/jobs-baseline
python3 wysiwyship/evals/runner.py run /tmp/wysiwyship-evals/jobs-workflow
```

Preview does not call the model. Add `--execute` to each command only when ready
to use your Codex allowance. Start with one attempt at a time; change which
condition runs first on the next task. Avoid unrelated host activity during a
timing comparison. A two-hour cap is a maximum, not the expected duration.

The runner launches `codex exec` with the workspace-write sandbox and captures
JSON events. It does not copy credentials, bypass the sandbox, or fall back to
an API key. Existing Codex authentication is reused. Confirm the account/auth
mode yourself before a run; a subscription is not a guarantee of remaining quota.
See [official non-interactive Codex documentation](https://learn.chatgpt.com/docs/non-interactive-mode).

`--ignore-user-config` reduces configuration drift, but does **not** promise to
disable every globally installed skill, plugin, instruction, or memory. Review
the actual host setup and traces. Requested settings are not effective-model
attestation, and parent usage events may not include all child usage.

## Grade and compare

```bash
python3 wysiwyship/evals/runner.py grade /tmp/wysiwyship-evals/jobs-baseline
python3 wysiwyship/evals/runner.py grade /tmp/wysiwyship-evals/jobs-workflow
python3 wysiwyship/evals/runner.py compare \
  /tmp/wysiwyship-evals/jobs-baseline /tmp/wysiwyship-evals/jobs-workflow
```

Grading uses evaluator-owned original regression tests and acceptance tests
against a fresh copy of candidate code. Editing or deleting the workspace's
tests does not change that canonical suite. A process exiting successfully does
not mean the task is solved. Discovery failures, zero tests, skipped requirements,
and timeouts must not be presented as passing acceptance.

| Dimension | Evidence | Interpretation |
|---|---|---|
| Functional completion | Canonical regression and acceptance results | Primary outcome; examine failed requirement groups, not only pass fractions |
| Efficiency | Observed elapsed time and available token events | Missing usage stays unknown; compare efficiency alongside correctness |
| Simplicity | Changed-source function complexity and diff size | Review cohesion and scope; smaller numbers alone do not establish better design |
| Documentation | Artifact inventory plus task-specific blind rubric | Presence is automatic; factual accuracy, intent, and usability need review |
| Workflow execution | Trace and routing receipts | Diagnostic only; configuration or self-report alone is not confirmed execution |
| Human involvement | Record interventions alongside a run | Noninteractive attempts should normally need none; do not silently repair the submission |

Reports should preserve failed and timed-out attempts. Grade their final state
where possible, but do not count a timeout as successful autonomous completion
merely because some tests pass. Never cherry-pick the better attempt or silently
exclude a broken run. Distinguish infrastructure failures from code failures.

## Under the hood

```text
catalog.json + task.md + starter/
              │ prepare: copy starter, install workflow only in that condition
              ▼
     trial/workspace/ ── explicit codex exec ──► modified candidate + trace
              │ grade: copy candidate into a fresh evaluation directory
              ▼
 canonical starter/tests/ + acceptance/ ── unittest ──► behavioral results
              │
              └── source measurements + run observations ──► paired report

starter/ + reference/ overlay ── validate only ──► fixture sanity check
```

- `catalog.json` is the inventory, not a claim that planned tasks exist.
- `tasks/<id>/starter/` is agent-visible code and documentation.
- `tasks/<id>/reference/` is a maintainer-only solution overlay, never a grading
  target or a patch-similarity criterion.
- `tasks/<id>/acceptance/` contains evaluator-owned behavioral checks.
- `tasks/<id>/rubric.md` guides blind human review beyond executable behavior.
- `runner.py` owns trial preparation, explicit execution, grading and comparison;
  its companion grader runs unittest in a separate process.
- `.agent-state/` inside a trial holds workflow state, not canonical acceptance.

## Difficulty calibration and expansion

First run two pilots × two conditions × one attempt = **four attempts**, capped
at eight aggregate execution hours. Actual duration and allowance consumption are
unknown before running. Inspect task clarity, meaningful failure modes, code
quality, and effort. A very fast solve does not automatically invalidate a task,
but if both agents trivially finish the pilots, they do not discriminate the
workflow sufficiently. Do not add artificial delays to fix that.

Audit weak tests and ambiguous specifications using reference and deliberately
incomplete solutions. Freeze revisions and grading rules before confirmatory
runs. Calibrated-on tasks are development data; reserve follow-on tasks for a
less biased comparison. Build the remaining eight only after that gate.

Ten tasks × two conditions gives twenty attempts and useful directional evidence,
not a statistically reliable universal improvement claim. Report task-level
paired outcomes. Repeats should be planned in advance and counted in full.

## Safety and scope

Run only trusted local submissions. Separate directories and fresh processes are
**not security isolation**: an agent with local file access may be able to read
the original suite, and candidate Python executes with the evaluator's privileges.
Do not grade downloaded or adversarial code with this runner. Network-free task
requirements do not constitute host-enforced network isolation.

The applications are synthetic engineering fixtures, not production queue or
authentication libraries. Their value is controlled contracts and observable
failure paths. See [provenance and validity limits](PROVENANCE.md) and
[runner details](RUNNER_NOTES.md). No public benchmark score is implied.

Use the [calibration protocol](CALIBRATION.md) to freeze the first four attempts
and record outcomes without silently dropping failed runs.

See [local verification evidence](VERIFICATION.md) for what has actually passed
and what remains unmeasured.
