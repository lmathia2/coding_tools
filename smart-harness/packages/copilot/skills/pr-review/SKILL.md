---
name: pr-review
description: Default deep pull-request review policy. Review exact PR HEAD and each logical commit in an isolated worktree, verify plan → implement → document → simplify → verify coherence, measure changed-code complexity and deltas, run semantic and executable lanes, escalate only for high-risk changes, and independently challenge serious findings.
license: Includes concepts adapted from MIT-licensed DietrichGebert/ponytail; see ${PLUGIN_ROOT}/vendor/THIRD_PARTY_NOTICES.md in an installed project.
---

# PR Review

The objective is merge confidence, not maximum reviewer count.

Default shape: **one semantic reviewer + one deterministic execution lane in parallel**, coordinated from an isolated PR worktree.

## 1. Establish the review target

Resolve base ref, exact committed PR HEAD, intent/acceptance criteria, commit/work-unit dependency order, changed runtime/contracts/data/docs, expected test/static/docs commands, and risk (`NORMAL` or `HIGH_RISK`).

Create a compact common evidence snapshot from refs/diff and relevant contracts. Do not make every lane rediscover the whole repository.

## 2. Isolate execution

Create a detached worktree under `.agent-worktrees/` at exact PR HEAD. Every reviewer, test, analyzer, docs build, and probe uses that path. Never mutate the developer's primary checkout; never commit, push, rebase, or merge during review.

## 3. Run the two default lanes in parallel

### Semantic lane

Review architecture/design fit, ownership/coupling, semantic correctness, runtime wiring (routes/handlers/DI/registrations/config/flags/callers), input/output/data contracts, error/cancellation/state paths, concurrency/retry/idempotency/transactions when relevant, compatibility/migration, behavioral test adequacy, documentation accuracy, and unnecessary complexity.

Inspect logical commits as well as the aggregate diff. Each implementation commit should be coherent, independently reviewable, and follow `plan -> implement -> document -> simplify -> verify`. Code, tests, and its live authoritative documentation belong in the same commit. A code-only commit requires `Docs-Impact: none — <concrete reason>`; otherwise request an amend/squash even when the final PR aggregate contains later documentation. Run `${PLUGIN_ROOT}/tools/commit_docs.py <base-ref>` when installed.

Minimality is a review dimension, not a separate reviewer. Recommend deletion/reuse/native/stdlib simplification only when it preserves requirements, tests, security, accessibility, compatibility, documentation, and operations.

### Execution lane

Discover authoritative commands from repository/CI configuration. Run:

- complete feasible configured unit-test suite;
- complete feasible configured integration-test suite;
- relevant e2e/runtime tests;
- build/compile/typecheck;
- lint/static analysis;
- applicable docs build/doctest/example/link/generated-reference checks.
- changed-function cyclomatic complexity using `${PLUGIN_ROOT}/tools/complexity.py --compare-ref <base>` for Python, or the repository-native equivalent for other languages.

When Smart Harness is installed, run `${PLUGIN_ROOT}/tools/check.py <base> --head <exact-pr-head>` as the composed deterministic range gate. Treat its documentation-sync, complexity, configured-check, and optional ledger results as the shared execution contract; retain additional repository-native checks required by the PR's blast radius.

Parallelize independent checks only when they do not contend for databases, ports, fixtures, accounts, devices, or mutable external state.

If a repository already has a product behavior specification, check it **only when the PR changes behavior covered by that specification**. Do not create one during review.

Report score and delta for materially changed functions. Scores above 10, material increases, or newly complicated branching require a specific simplification proposal or an evidence-backed justification. Complexity alone is not a defect: do not recommend fragmentation that reduces cohesion or obscures behavior.

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
- commit/work-unit coherence and documentation-sync results;
- changed-function complexity scores/deltas and actionable simplifications;
- missing behavior tests or stale authoritative docs;
- `NOT EXECUTED` checks with blockers;
- concise GitHub-ready comments for verified serious findings.

Coverage percentage alone is not behavioral correctness.

## 8. Cleanup

Remove/prune review worktrees after capturing evidence unless preserving one is explicitly useful for continuing investigation.
