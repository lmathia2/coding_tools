---
description: Smart development workflow: plan first, parallelize independent evidence/work, execute code and documentation together, and verify completely.
argument-hint: <coding task>
---

Task: $ARGUMENTS

Use the shared `plan-first`, `parallel-work`, `engineering-core`, and `documentation-sync` skills.

## Mandatory plan

Before any source edit, write a proportional plan containing:

- goal and acceptance criteria;
- repository evidence and affected boundaries;
- implementation steps;
- verification commands;
- Documentation Impact;
- parallel lanes and sequential dependencies.

Use Pi subagents for independent read-only discovery or hypotheses when the `pi-subagents` tools are available. Prefer async `subagent_spawn` for work that can overlap useful main-agent work; use bounded consultation for critical read-only advice. Wait for required completions before synthesis.

For high-risk architecture, launch independent architecture/challenge and repository-evidence lanes in parallel, then resolve material disagreement once.

Parallel writers require disjoint ownership and isolated worktrees; otherwise write sequentially.

## Execution

Implement only after the plan is accepted. Update code, tests, and required API/function/architecture/configuration/migration/operational documentation in the same pass.

Documentation must explain function, intent, goals, contract, constraints, and relevant failure/operational behavior.

## Verification

Run targeted tests and broader feasible unit/integration/e2e/build/type/lint/static/documentation checks according to blast radius. Never report an unexecuted check as passing.

Return Result, Verification, Documentation Impact/paths/checks, Decisions, and Residual Risk.
