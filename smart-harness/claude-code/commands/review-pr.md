---
description: Execution-based PR review: plan first, create an isolated PR-head worktree, run semantic and full executable/documentation checks in parallel, and verify serious findings.
argument-hint: [base-ref] [PR intent/details]
model: sonnet[1m]
effort: high
---
<!-- harness-role: coordinator -->

# /review-pr

Review request: $ARGUMENTS

Apply `plan-first`, `parallel-work`, `pr-review`, and `documentation-sync`.

## 1. Plan

Establish base ref, exact PR HEAD SHA, intent/acceptance criteria, changed runtime/contracts/data/operations/docs, expected unit/integration/e2e/static/docs commands, risk, and parallel lanes.

## 2. Create review worktree

Create a detached worktree at exact PR HEAD under `.agent-worktrees/`. Record its absolute path.

All reviewers and Bash commands must target that path. Never mutate the primary checkout.

## 3. Parallel default lanes

Launch together:

- `smart-deep-reasoner` in PR_CORE mode with worktree/base/head;
- `smart-fast-executor` in PR_EXEC mode with the worktree.

PR_EXEC runs the complete feasible configured unit and integration suites, relevant e2e/runtime checks, build/type/lint/static analysis, and documentation build/doctest/example/link/generated-reference checks.

Independent suites may run concurrently only when resources do not conflict.

If `ponytail-review` is installed, it may run as an additional complexity-only lane.

## 4. High-risk lanes

For security/trust boundaries, persistence/migrations, distributed state/concurrency, retries/idempotency/transactions, external contracts, deployment/rollback, or critical logic, launch in parallel:

- `smart-deep-reasoner` in PR_ADVERSARIAL mode;
- `smart-top-reviewer` in SECURITY_RESILIENCE mode.

## 5. Baseline and high-severity verification

When PR-head failures may be pre-existing, run the failing subset in a temporary base worktree when practical.

Attempt to falsify every BLOCKER/MAJOR in a fresh independent context before publishing it.

## 6. Report and cleanup

Return risk/recommendation, verified findings, exact test/static/docs commands/results, missing behavior/docs, NOT EXECUTED blockers, and GitHub-ready serious comments.

Remove/prune the worktree after capturing the report unless preserving it is explicitly useful.
