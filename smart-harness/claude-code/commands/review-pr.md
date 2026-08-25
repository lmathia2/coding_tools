---
description: Self-contained execution-based PR review. Plans first, creates an isolated PR-head worktree, runs semantic/executable/documentation/complexity lanes in parallel, runs full feasible unit/integration/static checks, and verifies serious findings.
argument-hint: [base-ref] [PR intent/details]
model: sonnet[1m]
effort: high
---
<!-- harness-role: coordinator -->

# /review-pr

Review request: $ARGUMENTS

Apply `plan-first`, `parallel-work`, `context-snapshot`, `pr-review`, `documentation-sync`, and `ponytail-review`.

## 1. Plan before review execution

Establish base ref, committed PR HEAD SHA, intent/acceptance criteria, changed runtime/contracts/docs, expected test/static/docs commands, risk, and parallel lanes.

If an outside-in product behavior specification exists, map the changed behavior to affected feature/foundation/cross-cutting docs, glossary, coverage rows, verification items, source commit, and triage.

## 2. Create the review worktree

Create a detached worktree at exact PR HEAD under `.agent-worktrees/`. All reviewers and commands use that path. Never mutate the developer's primary checkout.

## 3. Parallel default lanes

Launch together:

- `smart-deep-reasoner` in PR_CORE mode against the worktree, including behavior-spec semantics when present;
- `smart-fast-executor` in PR_EXEC mode against the worktree;
- a complexity-only `ponytail-review` pass against the same snapshot/diff.

The execution lane runs the complete feasible configured unit suite and complete feasible configured integration suite, plus relevant e2e/runtime, build/type/lint/static-analysis, documentation, and applicable behavior-spec checklist/probe checks. Independent suites may run concurrently only when resources do not conflict.

## 4. High-risk lanes

For security/trust boundaries, migration/persistence, distributed state/concurrency, retries/idempotency/transactions, external contracts, deployment/rollback, or critical business logic, launch in parallel:

- fresh `smart-deep-reasoner` in PR_ADVERSARIAL mode;
- `smart-top-reviewer` in SECURITY_RESILIENCE mode.

## 5. Baseline and finding verification

When PR-head failures have unclear causality, run the failing subset against a temporary base worktree. Attempt to falsify every BLOCKER/MAJOR in a fresh independent context before publishing it.

## 6. Report and cleanup

Return recommendation, evidence-backed architecture/correctness/wiring/docs findings, stale or missing behavior-spec artifacts, safe complexity reductions, exact unit/integration/e2e/static/docs results, security/resilience findings, missing behavior tests/docs, NOT EXECUTED blockers, and GitHub-ready serious comments. Then remove/prune the worktree unless intentionally preserved.

Ponytail review never replaces correctness, security, testing, accessibility, compatibility, or documentation review.
