# Local engineering evaluation: locked scope

Planning mode: interactive. Iterations: 2 (initial scope, then the user's correction
from small exercises to substantial engineering). Gate: pass. Locked at the user's
`yes` on 2026-08-31. No source fixtures existed before approval.

## Decisions

- **Goal:** compare ordinary coding-agent execution with WYSIWYShip on substantial,
  coordinated changes, not function-completion puzzles.
- **Acceptance:** ten original task specifications; first deliver two complete
  pilots plus a standard-library runner. Each starter must work and pass its
  existing tests; each reference must pass both regression and new acceptance
  tests. Starter acceptance failures must represent missing requested behavior.
- **Boundaries:** no Harbor, containers, external evaluation packages, downloaded
  repositories, hosted services, paid evaluations, publication, or git push in the
  build milestone. The agent executable is optional until an explicit model run.
- **Alternatives:** use original backend applications instead of copying large
  upstream environments. Tradeoff: reproducible offline tests, but less ecological
  validity than genuine maintenance in mature upstream projects.
- **Fairness:** identical task briefs, deliverables, evaluator tests, model/effort,
  and time caps in both conditions. The workflow condition adds the installed
  workflow and its invocation. Multi-model routing is a later separate experiment.
- **Calibration:** 45–120 minutes per task is an unmeasured difficulty target, not
  a runtime promise. Pilot before finishing eight more fixtures; never add delays,
  boilerplate, or arbitrary complexity to consume time.

Goals, acceptance, boundaries, and alternatives are clear. Assumptions are
mostly clear: Python standard-library backend tasks satisfy the agreed initial
scope. Whether they meaningfully discriminate agent behavior remains open and
requires actual runs. Local directories are not a security boundary against a
same-user process. Prepared workspaces omit answers but cannot hide their source
repository from an adversarial local agent.

## Work units and integration

| Unit | Exclusive ownership | Acceptance and documentation | Dependencies |
|---|---|---|---|
| Durable jobs pilot | `tasks/durable-jobs/` | Runnable starter, exhaustive brief, reference overlay, regression/acceptance tests, architecture/contracts/rubric | None |
| Tenant isolation pilot | `tasks/tenant-isolation/` | Same artifact contract; cross-tenant state and authorization tested | None |
| Local runner | `runner.py`, grader helpers, `tests/` | Prepare, explicit launch, authoritative grading, paired reports, runner tests and notes | Shared fixture layout locked before dispatch |
| Integration | Catalog, guide, provenance, explainer | Validate both pilots end-to-end, inspect correctness and scoring limits | All three units |

The implementation units run in separate temporary workspaces; the coordinator
integrates only their owned files. Each follows plan → implement → document →
simplify → verify. Routing uses configured Codex normal/deep lanes via actual
subagent dispatch; local build receipts retain requested settings and invocation
references, without claiming host-confirmed effective settings. No commits are
authorized; this milestone produces commit-ready changes, not a committed-range
verification claim.

## Next gate

After local validation, explicitly approve a bounded pilot experiment: two tasks,
two conditions, one attempt per condition, an agreed exact model/effort and a
two-hour maximum per attempt. Then inspect solve rates, failure families, elapsed
time, available usage, and blind review. Amend weak or ambiguous tasks before
freezing the suite and constructing the remaining eight. Do not tune tasks just
to manufacture a workflow win. Preserve failed/timed-out runs in reporting.

Reopen only for invalid requirements, inability to keep the suite dependency-free,
material difficulty/fairness failures, or new execution authority. Ordinary code
structure and test details remain autonomous within this scope.
