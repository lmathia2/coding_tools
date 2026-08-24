---
name: pr-review
description: Portable deep PR-review protocol: isolated worktree at PR HEAD, parallel dynamic/static review, full unit and integration execution, security/resilience analysis, and high-severity finding verification.
user-invocable: false
---

# PR Review

A PR review is not complete if it only reads the diff.

## 1. Plan first

Before review execution, define:

- base ref and PR HEAD;
- PR intent/acceptance criteria;
- changed runtime/contracts;
- test/static commands to discover;
- review perspectives to run in parallel;
- risk classification: NORMAL or HIGH_RISK.

## 2. Create an isolated review worktree

Use the committed PR HEAD, not the developer's mutable checkout:

```bash
ROOT=$(git rev-parse --show-toplevel)
HEAD_SHA=$(git rev-parse HEAD)
REVIEW_DIR="$ROOT/.agent-worktrees/pr-review-${HEAD_SHA:0:10}-$(date +%s)"
git worktree add --detach "$REVIEW_DIR" "$HEAD_SHA"
```

All file reads, tests, analyzers, and probes for the review must target `REVIEW_DIR`.

Do not edit the source checkout. Do not commit, push, rebase, or merge during review.

A worktree is code isolation, not a security sandbox.

## 3. Parallel review lanes

Run independent lanes concurrently when safe.

### Reasoning lane

Review architecture/design fit, correctness and runtime wiring, callers/DI/routes/config, state/error/concurrency/transaction/retry/idempotency behavior, public/API/data/schema compatibility, migration/rollback, and behavioral test adequacy.

### Execution lane

Inside the worktree, discover authoritative commands from CI/build configuration and run **all feasible configured suites**, including:

1. full unit-test suite;
2. full integration-test suite;
3. e2e/runtime suites when configured and feasible;
4. build/compiler/typecheck;
5. lint/static analysis;
6. repository-native security/code scanning when already available.

Targeted tests may run first for fast feedback, but they do not replace the full unit + integration suites.

Unit/integration/static lanes may run concurrently only when they do not contend for the same database, port, fixtures, or mutable external state.

Anything blocked by missing credentials/services is `NOT EXECUTED`, never PASS.

### High-risk lanes

For auth/permissions/tenant boundaries, secrets/crypto, persistent migrations, distributed state/concurrency, retries/idempotency/transactions, external contracts, deployment/rollback, or critical financial/business logic, add in parallel adversarial behavioral analysis plus security/resilience failure modeling.

## 4. Adversarial behavior

Derive concrete scenarios such as malformed/boundary input, duplicate events, partial failure, timeout/cancellation, retry after side effect, stale/reordered state, concurrent updates, restart/recovery, old callers/data, and rollback. Turn important scenarios into executable probes/tests when repository tooling supports them.

## 5. Distinguish PR regressions from baseline failures

If PR-head tests fail and the cause is unclear, create a temporary base worktree or otherwise execute the failing subset against the base commit when practical. Report whether the failure is new, pre-existing, or inconclusive.

## 6. Findings

Use BLOCKER / MAJOR / MINOR / SUGGESTION. For BLOCKER/MAJOR require concrete evidence, impact, reproduction/verification, and smallest remediation. Independently verify/falsify high-severity findings before finalizing them.

## 7. Report

Include risk and merge recommendation, architecture/correctness findings, exact test commands/results, static-analysis results, security/resilience findings when relevant, missing tests required before merge, and clearly separated NOT EXECUTED checks.

## 8. Cleanup

After capturing the report:

```bash
git worktree remove --force "$REVIEW_DIR"
git worktree prune
```

Preserve the worktree only when ongoing investigation requires it, and say so explicitly.
