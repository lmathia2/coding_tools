---
description: Default development command. Plans before editing, uses the cheapest capable model, parallelizes only useful independent work, keeps authoritative docs synchronized, and verifies before completion.
argument-hint: <coding task>
model: sonnet[1m]
effort: high
---
<!-- harness-role: coordinator -->

# /dev

Task: $ARGUMENTS

Use `engineering-workflow`. The user should not have to choose a model or sub-workflow.

## Route with a simple default

1. Understand the task and write the proportional plan required by `engineering-workflow`.
2. For targeted independent repository/test/docs discovery, launch `smart-fast` EXPLORE lanes in parallel only when this will materially reduce latency or uncertainty.
3. Route implementation:
   - mechanical/local/deterministic → `smart-fast` IMPLEMENT_MECHANICAL;
   - normal engineering → implement in this Sonnet conversation;
   - complex state/algorithm/integration/refactor → `smart-deep-implementer`;
   - ambiguous bug → `smart-deep-reasoner` DEBUG before editing;
   - architecture/high-risk → one `smart-top-reviewer` ARCHITECT and/or one independent `smart-deep-reasoner` challenge only when the decision warrants it.
4. Parallel writers require disjoint ownership and isolated worktrees; otherwise use one writer.
5. Run deterministic verification with `smart-fast` when command output would be verbose or separable.
6. Add a top-model final review only for the risk dimension that caused high-risk escalation.

## Specialist documentation

Use `product-behavior-spec` only when the user explicitly asks for an outside-in product behavior specification. If one already exists and this task changes documented user-visible behavior, update the affected artifacts as normal authoritative documentation; do not invoke the full specification workflow.

## Completion

Return Result, Verification, Documentation impact/changed paths, Important decisions only when non-obvious, and Residual risk/blocked checks.
