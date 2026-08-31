# Pilot protocol and review record

This is a protocol, not a report of executed Codex evaluations. Complete it before
authorizing the first four attempts. The task briefs and reference tests are local;
the target difficulty has not been established by an agent run.

## Freeze before launch

Record the suite revision/hashes, exact requested model, reasoning effort, Codex
CLI version, Python version, hardware, operating system, and timeout. Record
global host instructions, skills/plugins and any concurrency settings that may
affect the comparison. Verify all native specialist settings match the chosen
fixed-model profile in the workflow trial. Do not change configuration mid-pair.

Initial budget: two tasks, two conditions, one attempt each, at most 7,200 seconds
per attempt (eight aggregate hours at the cap). This is a wall-clock bound, not a
token or monetary ceiling. Stop further launches if quota, authentication, or
environment failures prevent a meaningful comparison. No API-key fallback.

Use a fresh trial and agent session for each attempt. Suggested order:

1. Durable jobs — baseline.
2. Durable jobs — workflow.
3. Tenant isolation — workflow.
4. Tenant isolation — baseline.

Do not run paired attempts against the same database or working directory. Avoid
concurrent attempts for the initial timing calibration. A restarted or repeated
attempt is another attempt, not a replacement for unfavorable evidence.

## Outcomes

Keep three separate judgments:

- **Execution:** completed, nonzero exit, timeout, interrupted, or launch failure.
- **Behavior:** canonical regression and acceptance results for the submitted
  state. Preserve partial results and list failed requirement families.
- **Reviewability:** blind task-specific rubric assessment of code, contracts,
  documentation, tests, and explanation. Do not expose arm labels to the reviewer
  where practical; exclude installed workflow scaffolding from review diffs.

An execution timeout with passing tests is not automatically autonomous success.
A completed agent with failing tests is not functional success. A test-passing
patch with a serious uncovered defect is not reviewable. Report each distinction
instead of blending them into an opaque overall number.

## Per-attempt record

Copy this block into the local experiment notes (never store credentials):

```text
Trial path / ID:
Task and frozen revision:
Condition (conceal for blind review):
Requested model and effort:
Observed effective model/effort and evidence, or UNVERIFIED:
Codex/Python/OS versions:
Host global configuration exceptions:
Started / ended / elapsed / execution status:
Canonical regression passed / total:
Canonical acceptance passed / total / failed families:
Recorded parent tokens; child coverage known or unknown:
Interventions (count, reason, transcript reference):
Complexity and source-diff measurements:
Blind reviewer / rubric evidence:
Source-grounded docs / explainer findings:
Workflow invocation / delegation / lifecycle evidence, or unverified:
Environment failures and recovery attempts:
```

Use `unknown` rather than `0` when something was not observed. Keep human review
outside the automatic behavioral score. Review references and evaluator code
only after each agent attempt has finished, not inside its context.

## Admission to the expanded suite

The first pilots are development/calibration data. Before adding eight more:

- A clean starter runs and passes legacy behavior; reference overlays satisfy all
  required behavior without depending on exact internal implementation choices.
- Missing behavior is caught in multiple meaningful families, not just a missing
  method import or an assertion about a particular class layout.
- Deterministic failure injection or synchronization exercises important boundaries;
  tests do not manufacture long runtime through sleeps or huge inputs.
- Briefs resolve product-level ambiguities. Tests enforce stated requirements,
  not undisclosed preferences or reference-specific behavior.
- Observed agents perform material cross-module reasoning and integration. If
  both solve trivially, strengthen the engineering scenario, not the prompt size.
- Inconvenient workflow losses are retained. Choose diversity and realistic
  failure modes, not tasks selected because WYSIWYShip happens to win them.

Freeze task versions, record why any revision changed, and reserve later tasks
for evaluation rather than repeatedly tuning every task on the same agent.
For the full ten, report paired task outcomes and usage/quality distributions.
Do not treat fifty assertions in one task as fifty independent experiments.
