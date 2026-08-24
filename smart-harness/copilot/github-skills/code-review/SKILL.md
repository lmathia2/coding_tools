---
name: focused-deep-code-review
description: Review pull requests for substantive architecture, correctness/wiring, behavioral testing, documentation synchronization, security/resilience, and deterministic-analysis risk without flooding the PR with style comments.
---

# Focused Deep Code Review

Prioritize merge risk over style.

Review:

- design, ownership, coupling, contracts, migration, and rollback;
- runtime wiring through routes/handlers/DI/config/flags/callers/state/error paths;
- happy, error, boundary, integration, state-transition, compatibility, retry/idempotency tests;
- documentation of function, intent, goals, API contracts, architecture, configuration, migration, and operations;
- relevant security/resilience boundaries;
- compiler/type/lint/static-analysis/CodeQL/coverage/docs-build expectations.

A correct-looking implementation that is not wired into runtime behavior is a correctness defect. A behavior/API/architecture change with stale required documentation is incomplete.

Focus comments on BLOCKER, MAJOR, and meaningful MINOR issues. For high-severity comments include location, execution/failure scenario, impact, evidence, and smallest remediation/test. State uncertainty rather than presenting speculation as fact.
