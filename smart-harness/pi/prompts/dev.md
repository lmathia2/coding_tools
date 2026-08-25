---
description: Default self-contained development workflow: plan before editing, use the cheapest capable path, parallelize only useful independent work, keep authoritative docs synchronized, and verify before completion.
argument-hint: <coding task>
---

Task: $ARGUMENTS

Use `engineering-workflow`.

1. Write the proportional plan before edits.
2. For genuinely independent repository/test/docs questions, use `.pi/tools/parallel-pi.py` only when parallel children materially reduce latency or uncertainty; otherwise stay in the main context.
3. Use the simplest correct implementation. For ambiguous bugs, establish root cause before editing. For complex/high-risk decisions, use at most one independent challenge unless new evidence requires more.
4. Parallel writers require isolated worktrees and disjoint ownership; otherwise use one writer.
5. Update affected authoritative documentation in the same pass.
6. Run targeted then broader feasible unit/integration/e2e/build/type/lint/static/docs checks according to blast radius.

Use `product-behavior-spec` only when the user explicitly asks for an outside-in product behavior specification. If one already exists and the task changes behavior it covers, update only the affected artifacts as normal documentation.

Return Result, Verification, Documentation impact/changed paths, Important decisions only when non-obvious, and Residual risk/blocked checks.
