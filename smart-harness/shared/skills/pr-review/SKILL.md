---
name: pr-review
description: Default deep pull-request review policy. Use for reviewing another developer's PR: plan briefly, check out the exact committed PR HEAD in an isolated worktree, run one semantic review and one executable verification lane in parallel, execute complete feasible unit/integration suites plus relevant static/runtime/docs checks, add specialist security/adversarial review only for high-risk changes, and independently challenge serious findings.
---

# PR Review

The objective is merge confidence, not maximum reviewer count.

Default shape: **one semantic reviewer + one deterministic execution lane in parallel**, coordinated from an isolated PR worktree.

## 1. Establish the review target

Resolve base ref, exact committed PR HEAD, intent/acceptance criteria, changed runtime/contracts/data/docs, expected test/static/docs commands, and risk (`NORMAL` or `HIGH_RISK`).

Create a compact common evidence snapshot from refs/diff and relevant contracts. Do not make every lane rediscover the whole repository.

## 2. Isolate execution

Create a detached worktree under `.agent-worktrees/` at exact PR HEAD. Every reviewer, test, analyzer, docs build, and probe uses that path. Never mutate the developer's primary checkout; never commit, push, rebase, or merge during review.

## 3. Run the two default lanes in parallel

### Semantic lane

Review architecture/design fit, ownership/coupling, semantic correctness, runtime wiring (routes/handlers/DI/registrations/config/flags/callers), input/output/data contracts, error/cancellation/state paths, concurrency/retry/idempotency/transactions when relevant, compatibility/migration, behavioral test adequacy, documentation accuracy, and unnecessary complexity.

Minimality is a review dimension, not a separate reviewer. Recommend deletion/reuse/native/stdlib simplification only when it preserves requirements, tests, security, accessibility, compatibility, documentation, and operations.

### Execution lane

Discover authoritative commands from repository/CI configuration. Run:

- complete feasible configured unit-test suite;
- complete feasible configured integration-test suite;
- relevant e2e/runtime tests;
- build/compile/typecheck;
- lint/static analysis;
- applicable docs build/doctest/example/link/generated-reference checks.

Parallelize independent checks only when they do not contend for databases, ports, fixtures, accounts, devices, or mutable external state.

If a repository already has a product behavior specification, check it **only when the PR changes behavior covered by that specification**. Do not create one during review.

## 4. Escalate only on risk

`HIGH_RISK` includes auth/authorization/tenant/trust boundaries, secrets/crypto, schema/persistent-data migrations, distributed/concurrent state, retries/idempotency/transactions, public/external contracts, deployment/rollback, or critical financial/business logic.

For high-risk changes add, in parallel where useful:

- one adversarial scenario/test-design pass;
- one focused security/resilience pass.

Do not run premium multi-round debate by default.

## 5. Classify failures against base

If PR-head tests fail and causality is unclear, run the failing subset against the base commit in a temporary base worktree when practical. Report `NEW`, `PRE-EXISTING`, or `INCONCLUSIVE`.

## 6. Challenge high severity

Every candidate `BLOCKER` or `MAJOR` gets one fresh independent attempt to falsify it using cited code/contracts and a focused safe diagnostic when useful. Publish high severity only if it survives attempted disproof; otherwise downgrade/reject/inconclusive.

## 7. Report

Return:

- risk and recommendation: `APPROVE`, `COMMENT`, `REQUEST CHANGES`, or `BLOCK`;
- evidence-backed findings, severity, confidence, and smallest remediation/test;
- exact unit/integration/e2e/static/docs commands and results;
- missing behavior tests or stale authoritative docs;
- `NOT EXECUTED` checks with blockers;
- concise GitHub-ready comments for verified serious findings.

Coverage percentage alone is not behavioral correctness.

## 8. Cleanup

Remove/prune review worktrees after capturing evidence unless preserving one is explicitly useful for continuing investigation.
