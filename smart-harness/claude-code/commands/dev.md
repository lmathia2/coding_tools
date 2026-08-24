---
description: Default smart Claude Code development workflow. Always plans first, parallelizes independent work, and escalates from Haiku to Sonnet/Opus only as task complexity requires.
argument-hint: <coding task>
model: sonnet[1m]
effort: high
---
<!-- harness-role: coordinator -->

# /dev

Task: $ARGUMENTS

Apply `plan-first`, `parallel-work`, and `engineering-core`.

## 1. Always plan before edits

No source edit before an explicit accepted plan exists.

- mechanical: 1–3 step micro-plan;
- normal: acceptance criteria + implementation + verification plan;
- complex/high risk: repository evidence + alternatives/invariants + independent challenge.

Use `smart-fast-executor` subagents for independent repository exploration. Launch separate independent explorations in parallel rather than serially.

## 2. Route intelligently

### MECHANICAL
After the micro-plan, delegate implementation to `smart-fast-worker` (Haiku).

### NORMAL
Implement in this main Sonnet conversation after the plan. Keep planning, implementation, and testing together because they share context.

### COMPLEX
Delegate implementation to `smart-deep-worker` in IMPLEMENT mode after the plan.

### DEBUG_AMBIGUOUS
Before edits, launch `smart-deep-worker` in DEBUG mode. If there are genuinely independent plausible causes, launch multiple investigations in parallel with distinct hypotheses. Implement only after an evidence-backed root cause or discriminating experiment exists.

### ARCHITECTURE_OR_HIGH_RISK
Triggers include multiple credible designs, shared/public contracts, persistence/schema migration, auth/permissions, distributed state/transactions, rollback-sensitive infrastructure, critical calculations, or broad cross-layer refactors.

Launch in parallel:
- `smart-top-reviewer` in ARCHITECTURE mode;
- `smart-deep-worker` in INDEPENDENT_PLAN_CHALLENGE mode;
- independent `smart-fast-executor` repository investigations where useful.

Synthesize once and resolve material disagreement using repository evidence. Avoid repeated debate unless new evidence invalidates the plan.

## 3. Parallel implementation only when clearly partitioned

If the accepted plan has independent components with agreed interfaces and no overlapping files/state, create isolated worktrees/branches and run writers in parallel. Otherwise implement sequentially.

Do not use Agent Teams by default. Use them only for a large feature where peers own independent components and need sustained direct coordination.

## 4. Verify

Run targeted tests and the relevant broader unit/integration/build/type/static checks. Use `smart-fast-executor` for verbose/deterministic verification when that keeps the main context clean.

Do not claim completion without fresh executable evidence.

Return Result, Verification, Important Decisions, Residual Risk.
