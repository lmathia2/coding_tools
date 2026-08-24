---
name: review-pr
description: Deep but risk-adaptive review of another developer's pull request: architecture, correctness/wiring, executed behavioral tests, static analysis, security/resilience, and high-severity false-positive verification.
disable-model-invocation: true
argument-hint: <base ref and/or PR intent>
model: sonnet[1m]
effort: high
---
<!-- harness-role: coordinator -->

# Smart Pull Request Review

Review: **$ARGUMENTS**

You are the read-only review coordinator. Do not modify source files, commit, merge, rebase, reset, push, or otherwise mutate the PR branch.

## 1. Establish the review range

Prefer a user-provided base ref. Determine the merge base, changed files/stat, PR intent/acceptance criteria, relevant runtime paths/contracts, tests changed, and repository-native CI/static checks.

If the user supplied a PR number and `gh` is already installed/authenticated, read-only `gh pr view` / `gh pr checks` may be useful. The workflow must not depend on GitHub CLI.

## 2. Classify risk

### NORMAL

Localized feature/refactor/bug fix with bounded blast radius and no important trust, persistence, or distributed-state boundary.

### HIGH_RISK

Any meaningful change involving authentication/authorization/tenant isolation, secrets/crypto/trust boundaries, persistent data/schema migration, distributed state/concurrency, retry/idempotency/transactions, externally consumed contracts, deployment/rollback, critical financial/business logic, or broad architecture.

## 3. Default review for every non-trivial PR

Run these in parallel when practical:

### `deep-reasoner` — PR_CORE mode

Ask for one integrated reasoning pass over:

- architecture/design fit;
- semantic correctness;
- runtime wiring, routes, registrations, DI, config, feature flags and callers;
- API/data/schema compatibility;
- error/state/concurrency/retry/idempotency behavior where relevant;
- test adequacy and missing behavioral coverage.

### `fast-verifier` — PR_EXECUTION mode

Ask it to discover and actually run relevant repository-native:

- targeted tests;
- integration/e2e tests crossing changed boundaries;
- build/compile/type checks;
- lint/static analysis;
- other CI-equivalent checks already available locally.

Never treat an unexecuted check as PASS.

## 4. Conditional high-risk review

Only for HIGH_RISK PRs, or when the default passes expose a concrete risk signal:

- invoke `top-reviewer` in **SECURITY_RESILIENCE** mode for the specific changed trust/failure boundaries;
- invoke a fresh `deep-reasoner` in **PR_ADVERSARIAL** mode to derive concrete failure scenarios and tests/probes that could falsify the implementation;
- ask `fast-verifier` to execute those deterministic probes when feasible rather than spending premium reasoning tokens on terminal I/O.

## 5. Synthesize and control false positives

De-duplicate findings. Severity:

- BLOCKER — unsafe/unshippable or core behavior broken;
- MAJOR — likely correctness/security/resilience/architecture defect that should be fixed before merge;
- MINOR — real issue worth addressing but not a merge blocker;
- SUGGESTION — optional preference/improvement.

A style preference is not a defect.

For each finding require a concrete location/path, execution or failure scenario, impact, evidence, smallest remediation/missing test, and confidence.

If any BLOCKER or MAJOR is proposed, invoke a **fresh `top-reviewer` in FINDING_VERIFY mode** with only the candidate high-severity findings and relevant evidence. Its job is to attempt to falsify them. Publish high severity only when it survives verification; otherwise downgrade/reject or state uncertainty.

## 6. Final output

## Executive Summary
- PR intent
- risk: NORMAL / HIGH_RISK
- recommendation

Use exactly one:

`RECOMMENDATION: APPROVE`
`RECOMMENDATION: COMMENT`
`RECOMMENDATION: REQUEST CHANGES`
`RECOMMENDATION: BLOCK`

## Findings
Sorted by severity.

## Architecture / Compatibility

## Correctness & Wiring

## Executed Behavioral Tests

| Test/check | Result | What it proves |

## Static Analysis / CI

| Check | Result | Notes |

## Security / Resilience
Only when relevant.

## Missing Tests Required Before Merge
Only material gaps.

## GitHub-Ready Comments
Concise comments for verified BLOCKER/MAJOR findings with file/line references when available.

## Merge Gate
- [ ] required behavior verified
- [ ] integration wiring verified
- [ ] relevant deterministic checks pass or exceptions are understood
- [ ] security/resilience reviewed when relevant
- [ ] no verified BLOCKER/MAJOR remains

Do not automatically submit a GitHub review or alter the branch.
