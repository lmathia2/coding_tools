---
name: pr-review
description: Portable deep PR-review protocol: isolated worktree at PR HEAD, parallel dynamic/static review, full feasible unit and integration execution, documentation validation, security/resilience analysis, and high-severity finding verification.
---

# PR Review

## 1. Plan

Establish:

- base ref and exact committed PR HEAD;
- PR intent and acceptance criteria;
- changed runtime, contracts, data, operations, and documentation;
- expected unit, integration, e2e, static, and documentation commands;
- NORMAL or HIGH_RISK classification;
- independent parallel review lanes.

## 2. Isolated worktree

Review the exact PR HEAD in a detached worktree:

```bash
git worktree add --detach <review-dir> <PR_HEAD_SHA>
```

All reads, tests, analyzers, examples, and probes run from that worktree.

The primary developer checkout remains untouched.

A worktree is isolation from the developer branch, not a security sandbox.

## 3. Parallel lanes

Run independent lanes concurrently where safe:

- architecture, correctness, runtime wiring, compatibility, and documentation semantics;
- complete feasible configured unit suite;
- complete feasible configured integration suite;
- relevant e2e/runtime tests;
- compiler/build/type/lint/static analysis;
- documentation build, doctests, example execution, link/schema drift checks;
- adversarial behavior;
- security/resilience for high-risk changes.

Do not parallelize suites that contend for the same database, ports, fixtures, accounts, or mutable external state.

## 4. Test completeness

Targeted tests are fast feedback, not the review gate.

Run the complete feasible configured unit and integration suites.

Mark blocked checks `NOT EXECUTED` with the exact missing credential, service, platform, or dependency.

## 5. Baseline comparison

If PR-head tests fail and causality is unclear, create a temporary base worktree and run the failing subset there when practical.

Classify the failure:

- NEW REGRESSION
- PRE-EXISTING
- INCONCLUSIVE

## 6. Documentation review

Apply `documentation-sync`.

Verify documentation describes:

- function and contract;
- intent and goals;
- architecture/decision rationale;
- configuration and operational behavior;
- migration/rollback;
- realistic examples.

Run repository-native documentation checks. Stale required docs are a merge issue.

## 7. Findings

Use:

- BLOCKER
- MAJOR
- MINOR
- SUGGESTION

For each finding include location, evidence, concrete failure/risk, remediation or missing test, and confidence.

Attempt to falsify every BLOCKER/MAJOR in a fresh independent context before publishing it.

## 8. Cleanup

After capturing the report:

```bash
git worktree remove --force <review-dir>
git worktree prune
```

Preserve the worktree only when explicitly useful for continuing investigation.
