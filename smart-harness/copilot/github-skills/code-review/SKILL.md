---
name: focused-deep-code-review
description: Review PRs for substantive architecture, correctness/wiring, behavioral testing, security/resilience, and deterministic-analysis risk without flooding the PR with style comments.
---

# Focused Deep Code Review

Prioritize merge risk over style.

Review design/contracts, runtime wiring, callers, state/error/concurrency behavior, API/data/schema compatibility, migration/rollback, and behavioral test adequacy.

For changed trust/failure boundaries, review authz, validation, secrets, unsafe sinks, retries, idempotency, partial failure, recovery, and rollback.

Respect compiler/type/lint/static-analysis/CodeQL/coverage expectations in the repository.

Focus comments on BLOCKER, MAJOR, and meaningful MINOR issues. For high severity include location, concrete execution/failure scenario, impact, evidence, and smallest remediation or missing test. State uncertainty rather than presenting speculation as fact.
