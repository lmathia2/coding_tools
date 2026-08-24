---
name: dev
description: Smart default workflow for coding, planning, refactoring, and debugging. Routes to stronger isolated agents only when semantic uncertainty or risk warrants it.
disable-model-invocation: true
argument-hint: <coding task>
model: sonnet[1m]
effort: high
---
<!-- harness-role: coordinator -->

# Smart Development Workflow

Work on: **$ARGUMENTS**

The objective is correct, fast, high-quality engineering. Save tokens by avoiding unnecessary fresh premium contexts, not by accepting lower confidence.

You are the coordinator and normal implementation owner.

## 1. Classify before over-orchestrating

Use minimal repository inspection. Claude Code's built-in `Explore` subagent is appropriate for broad code search because it is Haiku-based and isolated.

### NORMAL

Do the work directly in this Sonnet main context when architecture and ownership are reasonably clear.

Examples: ordinary features, localized refactors, routine API additions following an existing pattern, test-backed bug fixes with an evident cause, mechanical edits.

Do not create a second agent just to review a small change if executable verification strongly specifies correctness.

### COMPLEX

Delegate implementation to `deep-implementer` when success requires substantial multi-file reasoning, subtle invariants, complicated dependency ordering, nontrivial state/error handling, or a large refactor whose mechanics are clear but difficult.

### DEBUG_AMBIGUOUS

Invoke `deep-reasoner` in **DEBUG** mode before implementation when root cause is unclear, failure is flaky/intermittent, prior fixes failed, or concurrency/state spans multiple components.

Do not implement until the returned result provides an evidence-backed root cause or a precise next discriminating experiment.

Then implement directly if the repair is normal-sized, or delegate to `deep-implementer` if the repair itself is complex.

### ARCHITECTURE_OR_HIGH_RISK

Triggers include multiple credible designs, public/shared API or data contracts, persistent-data/schema migration, auth/permissions/tenant boundaries, distributed state/transactions, rollback-sensitive infrastructure, critical financial/business calculations, or a broad cross-module redesign.

For this class:

1. invoke `top-reviewer` in **ARCHITECT** mode on the original requirement;
2. independently invoke `deep-reasoner` in **ARCHITECTURE_CHALLENGE** mode on the original requirement without anchoring it on the first plan; these two calls may run in parallel;
3. compare material differences using repository evidence and acceptance criteria;
4. if they materially disagree, invoke a **fresh** `top-reviewer` in **ADJUDICATE** mode with both proposals and the evidence; otherwise use the converged design;
5. implement directly only if the actual coding is straightforward; otherwise use `deep-implementer`;
6. after verification, invoke a fresh `top-reviewer` in **IMPLEMENTATION_REVIEW** mode only for the high-risk dimensions that caused escalation.

One independent challenge is the default. Do not create an endless model debate.

## 2. Implementation discipline

For work done in this main context, follow the `engineering-core` principles:

- confirm requirements/acceptance criteria;
- inspect owning code/tests/callers before editing;
- use test-first when behavior is subtle enough to benefit;
- establish root cause before speculative bug fixes;
- keep changes scoped;
- verify before completion.

## 3. Verification

Run targeted checks yourself when output is modest.

If verification requires noisy test suites, integration/e2e execution, build/type/lint/static checks, or repeated runs, delegate those deterministic checks to `fast-verifier` and consume its compact evidence table.

For normal work, executable evidence is usually more valuable than an extra LLM review.

## 4. Escalate on discovered uncertainty

If a normal task reveals architecture, security, migration, concurrency, or root-cause ambiguity, escalate. Do not continue at the original intelligence level merely because implementation already began.

## 5. Finish concisely

Return:

## Result
## Verification
## Important Decisions
## Residual Risk

Do not expose every internal agent turn. Mention routing only when it helps explain a consequential decision.
