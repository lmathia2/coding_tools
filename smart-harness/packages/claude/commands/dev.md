---
description: Default development command. Plans before editing, uses the cheapest capable model, parallelizes only useful independent work, keeps authoritative docs synchronized, and verifies before completion.
argument-hint: <coding task>
model: sonnet[1m]
effort: high
---
<!-- harness-role: coordinator -->
<!-- harness-workflow: dev -->

# /dev

Task: $ARGUMENTS

Use `smart-harness:engineering-workflow`. The user should not have to choose a model or sub-workflow.

## Route with a simple default

Every implementation unit follows `plan -> implement -> document -> simplify -> verify`.

1. Understand the task and decompose it into coherent, independently committable work units with dependencies, ownership, acceptance criteria, documentation impact, complexity scope, and verification.
2. For targeted independent repository/test/docs discovery, launch `smart-harness:smart-fast` EXPLORE lanes in parallel only when this will materially reduce latency or uncertainty.
3. Route implementation:
   - mechanical/local/deterministic or normal engineering → one `smart-harness:smart-worker` per independent work unit;
   - complex state/algorithm/integration/refactor → `smart-harness:smart-deep-implementer`;
   - ambiguous bug → `smart-harness:smart-deep-reasoner` DEBUG before editing;
   - architecture/high-risk → one `smart-harness:smart-top-reviewer` ARCHITECT and/or one independent `smart-harness:smart-deep-reasoner` challenge only when the decision warrants it.
4. Give each implementation context one complete work-unit contract. Launch independent `smart-harness:smart-worker` units concurrently only with disjoint ownership and isolated worktrees; integrate their commit-ready changes in dependency order.
5. For every unit, update live authoritative documentation in the same logical commit, including implementation, APIs/contracts, purpose, intent, and invariants; otherwise record `Docs-Impact: none — <reason>`.
6. After documentation, use `smart-harness:smart-fast` COMPLEXITY or the repository-native analyzer to score changed functions against the unit start ref, then simplify without gaming the score.
7. Run deterministic verification with `smart-harness:smart-fast` when command output would be verbose or separable.
8. For a committed unit, run `${CLAUDE_PLUGIN_ROOT}/tools/check.py <unit-start-ref> --head HEAD` (or `--active`) as the composed lifecycle gate; before commit, report that range gate as `NOT EXECUTED` and run its applicable components.
9. Add a top-model final review only for the risk dimension that caused high-risk escalation.

## Specialist documentation

Use `smart-harness:product-behavior-spec` only when the user explicitly asks for an outside-in product behavior specification. If one already exists and this task changes documented user-visible behavior, update the affected artifacts as normal authoritative documentation; do not invoke the full specification workflow.

## Completion

Return Result, work units/commits, Verification, Documentation impact/changed paths, Complexity scores/deltas, Important decisions only when non-obvious, and Residual risk/blocked checks.
