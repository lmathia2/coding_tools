---
name: review-pr
description: Execution-based Claude Code PR review. Plans first, creates an isolated PR-head worktree, runs semantic review and full unit/integration/static checks in parallel, and verifies serious findings.
argument-hint: [base-ref] [PR intent/details]
disable-model-invocation: true
model: sonnet[1m]
effort: high
---
<!-- harness-role: coordinator -->

# /review-pr

Review request: $ARGUMENTS

Apply `plan-first`, `parallel-work`, and `pr-review`.

## 1. Plan before review execution

Establish the base ref, committed PR HEAD SHA, intent/acceptance criteria, changed runtime/contracts, expected test/static commands, and NORMAL/HIGH_RISK classification.

If a PR number is provided and `gh` is already authenticated, read PR metadata/head SHA with read-only `gh pr view`/Git commands. Do not mutate the developer's primary checkout.

## 2. Create the review worktree

Create a detached worktree at the exact PR HEAD under `.agent-worktrees/` as specified by `pr-review`. Record its absolute path.

All reviewers must read the worktree path, not the primary checkout. All Bash test/static commands must use `cd <review-worktree> && ...` or equivalent because subagent shell cwd does not persist.

## 3. Parallel default lanes

Launch together:

- `smart-deep-worker` in PR_CORE mode, explicitly giving the review-worktree path and base/head refs;
- `smart-fast-executor` in PR_EXEC mode, explicitly giving the review-worktree path.

The execution lane must discover repository/CI commands and run the **complete feasible configured unit-test suite and complete feasible configured integration-test suite**, not merely targeted changed tests. Also run configured e2e/runtime tests when feasible and build/type/lint/static-analysis checks.

Independent test/static suites may run concurrently when they do not compete for the same database, ports, fixtures, or mutable external state.

## 4. High-risk lanes

For auth/permissions/tenant/security boundaries, persistence/schema migration, distributed state/concurrency, retries/idempotency/transactions, external contracts, deployment/rollback, or critical business/financial logic, launch in parallel:

- a fresh `smart-deep-worker` in PR_ADVERSARIAL mode;
- `smart-top-reviewer` in SECURITY_RESILIENCE mode.

Wait for every required parallel lane before synthesis.

## 5. Baseline failures

If PR-head tests fail and it is unclear whether the PR caused them, create a temporary base worktree and run the failing subset against the base commit when practical. Mark NEW / PRE-EXISTING / INCONCLUSIVE.

## 6. Verify BLOCKER/MAJOR findings

Attempt to falsify serious findings with a fresh independent context before publishing them. Prefer the other reasoning tier when practical: top reviewer verifies deep-worker findings; deep-worker verifies top-reviewer findings. Independent findings may be verified in parallel.

## 7. Report

Return:

- risk and recommendation APPROVE / COMMENT / REQUEST CHANGES / BLOCK;
- architecture/design/correctness/wiring findings;
- exact full unit/integration/e2e test commands and results;
- build/type/lint/static-analysis results;
- security/resilience findings when relevant;
- missing behavior tests required before merge;
- NOT EXECUTED checks and the exact blocker;
- concise GitHub-ready comments for verified BLOCKER/MAJOR findings.

Do not equate line coverage with behavioral correctness.

## 8. Cleanup

Remove/prune the review worktree after capturing the report unless preserving it is explicitly useful for ongoing investigation. Never edit/commit/push/rebase/merge the source checkout during review.
