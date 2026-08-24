---
description: Deep execution-based PR review in an isolated worktree with parallel semantic, test/static, documentation, adversarial, and security lanes.
argument-hint: [base-ref] [PR details]
---

Review request: $ARGUMENTS

Use `plan-first`, `parallel-work`, `pr-review`, and `documentation-sync`.

## Plan and isolate

Establish base ref, exact committed PR HEAD, intent/acceptance criteria, changed code/contracts/data/operations/docs, expected checks, risk, and parallel lanes.

Create a detached worktree at exact PR HEAD under `.agent-worktrees/`. All review reads and execution must target it. Never mutate the primary checkout.

## Parallel review

When Pi subagent tools are available, launch independent lanes for:

- architecture/correctness/wiring/compatibility/documentation semantics;
- complete feasible configured unit/integration suites, relevant e2e/runtime checks, build/type/lint/static analysis, docs build/doctests/examples/links/generated-reference checks;
- adversarial behavior for meaningful semantic risk;
- security/resilience for high-risk boundaries.

Use the main agent as coordinator and synthesizer. Parallelize test/check processes only when resources do not conflict.

If Ponytail is installed, use `ponytail-review` only as an additional over-engineering lane; it cannot replace correctness, security, test, or documentation review.

If a PR-head failure may be pre-existing, run the failing subset in a temporary base worktree when practical.

Attempt to falsify every candidate BLOCKER/MAJOR in an independent context.

Report recommendation, verified findings, exact code/docs checks and results, missing tests/docs, NOT EXECUTED blockers, and GitHub-ready serious comments. Remove/prune worktrees after capture unless preserving one is explicitly useful.
