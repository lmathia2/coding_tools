---
description: Default self-contained development workflow: plan before editing, use the cheapest capable path, parallelize only useful independent work, keep authoritative docs synchronized, and verify before completion.
argument-hint: <coding task>
---

<!-- harness-role: coordinator -->
<!-- harness-workflow: dev -->

Task: $ARGUMENTS

Use `engineering-workflow`.

Every implementation unit follows `plan -> implement -> document -> simplify -> verify`.

Before decomposition or source edits, run the planning grill defined by `engineering-workflow`. Default to an interactive, evidence-first interview that resolves goals, acceptance, in/out scope, alternatives, assumptions, and relevant constraints; include a recommendation and tradeoff with each material question and iterate until the user locks the plan. If the first task argument is exactly `auto` or `--auto`, remove it, pose and answer the same questions yourself from evidence or the smallest reversible assumptions, record them, and lock without routine user input. Record mode, iterations, gate, key decisions, scope, assumptions, open questions, ambiguity assessment, and the plan lock. After lock, execute rapidly and autonomously; reopen only an invalidated decision when evidence breaks the plan, scope/contracts must materially change, or new authority is required, then relock and resume.

1. Use the locked decision record to decompose non-trivial work into coherent, independently committable units with dependencies, ownership, acceptance criteria, documentation impact, complexity scope, and verification.
2. For genuinely independent repository/test/docs questions, use `.pi/tools/parallel-pi.py --workflow dev` only when parallel children materially reduce latency or uncertainty; otherwise stay in the main context. Give every child a semantic `role` (`fast`, `normal`, `deep`, or `top`) so the active model profile supplies its model and thinking strength. Explicit per-task `model` or `thinking` values are experiment overrides.
3. Use the simplest correct implementation. For ambiguous bugs, establish root cause before editing. For complex/high-risk decisions, use at most one independent challenge unless new evidence requires more.
4. Give each implementation context a complete work-unit contract. Parallel writers require isolated worktrees and disjoint ownership; invoke the helper with `--workflow dev --capability write --auto-approve` only from those worktrees, and integrate commit-ready changes in dependency order.
5. Update live authoritative documentation in the same logical commit, including implementation, APIs/contracts, purpose, intent, and invariants; otherwise record `Docs-Impact: none — <reason>`.
6. After documentation, score changed functions with `.wysiwyship/tools/complexity.py --compare-ref <unit-start-ref>` or the repository-native analyzer, and simplify without gaming the score.
7. Run targeted then broader feasible unit/integration/e2e/build/type/lint/static/docs checks according to blast radius.
8. For a committed unit, run `.wysiwyship/tools/check.py <unit-start-ref> --head HEAD` (or `--active`) as the composed lifecycle gate; before commit, report that range gate as `NOT EXECUTED` and run its applicable components.
9. After all units are integrated and the range gate passes, invoke `eli5` and generate its checked visual explainer under `.agent-state/eli5/`. A successful development run is not complete without the artifact path and audience in the handoff.

Use `product-behavior-spec` only when the user explicitly asks for an outside-in product behavior specification. If one already exists and the task changes behavior it covers, update only the affected artifacts as normal documentation.

Return Result, planning grill mode/iterations/key decisions/assumptions/boundaries and any re-entry, work units/commits, Verification, Documentation impact/changed paths, Complexity scores/deltas, ELI5 artifact/audience, and Residual risk/blocked checks.
