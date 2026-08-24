---
description: Self-contained smart development workflow: plan first, use bundled parallel Pi children for independent work, apply the local Superpowers/Ponytail methodology, update documentation with code, and verify completely.
argument-hint: <coding task>
---

Task: $ARGUMENTS

Use the repository-local `plan-first`, `parallel-work`, `engineering-core`, `documentation-sync`, `superpowers-methodology`, and `ponytail` skills.

## Mandatory plan

Before any edit, produce a proportional plan containing acceptance criteria, implementation/test/docs steps, Documentation Impact, parallel lanes, and sequential dependencies.

For independent read-only exploration, hypotheses, architecture challenges, test mapping, or documentation impact, create a JSON task list and run `.pi/tools/parallel-pi.py`. The bundled runner uses Pi print-mode children and Python standard library only; do not install an extension.

For non-trivial work, follow `superpowers-methodology`. Use Ponytail after understanding the full path to choose the smallest correct design. Ponytail never overrides documentation, tests, security, accessibility, compatibility, migration, data safety, or explicit requirements.

Parallel writers require isolated worktrees and disjoint ownership; otherwise write sequentially.

## Execution and documentation

Implement only after the plan is accepted. Update code, tests, and required function/API/architecture/configuration/migration/operational documentation in the same pass. Documentation explains function, intent, goals, contracts, boundaries, and relevant failure/operational behavior.

## Verification

Run targeted tests and broader feasible unit/integration/e2e/build/type/lint/static/documentation checks according to blast radius. Never report an unexecuted check as passing.

Return Result, Verification, Documentation Impact/paths/checks, Decisions, and Residual Risk.
