---
description: Default self-contained development workflow: plan before editing, use the cheapest capable path, parallelize only useful independent work, keep authoritative docs synchronized, and verify before completion.
argument-hint: <coding task>
---

Task: $ARGUMENTS

Use `engineering-workflow`.

Every implementation unit follows `plan -> implement -> document -> simplify -> verify`.

1. Decompose non-trivial work into coherent, independently committable units with dependencies, ownership, acceptance criteria, documentation impact, complexity scope, and verification.
2. For genuinely independent repository/test/docs questions, use `.pi/tools/parallel-pi.py` only when parallel children materially reduce latency or uncertainty; otherwise stay in the main context.
3. Use the simplest correct implementation. For ambiguous bugs, establish root cause before editing. For complex/high-risk decisions, use at most one independent challenge unless new evidence requires more.
4. Give each implementation context a complete work-unit contract. Parallel writers require isolated worktrees and disjoint ownership; invoke the helper with `--capability write --auto-approve` only from those worktrees, and integrate commit-ready changes in dependency order.
5. Update live authoritative documentation in the same logical commit, including implementation, APIs/contracts, purpose, intent, and invariants; otherwise record `Docs-Impact: none — <reason>`.
6. After documentation, score changed functions with `.smart-harness/tools/complexity.py --compare-ref <unit-start-ref>` or the repository-native analyzer, and simplify without gaming the score.
7. Run targeted then broader feasible unit/integration/e2e/build/type/lint/static/docs checks according to blast radius.

Use `product-behavior-spec` only when the user explicitly asks for an outside-in product behavior specification. If one already exists and the task changes behavior it covers, update only the affected artifacts as normal documentation.

Return Result, work units/commits, Verification, Documentation impact/changed paths, Complexity scores/deltas, Important decisions only when non-obvious, and Residual risk/blocked checks.
