---
name: focused-deep-code-review
description: Review pull requests for substantive architecture, correctness/wiring, behavioral testing, documentation and product-behavior-spec synchronization, security/resilience, and deterministic-analysis risk without flooding the PR with style comments.
---

# Focused Deep Code Review

Prioritize merge risk over style.

Review:

- design, ownership, coupling, contracts, migration, and rollback;
- runtime wiring through routes/handlers/DI/config/flags/callers/state/error paths;
- happy, error, boundary, integration, state-transition, compatibility, retry/idempotency tests;
- documentation of function, intent, goals, API contracts, architecture, configuration, migration, and operations;
- existing product behavior feature/foundation docs, glossary, coverage, verification items, source commit, and triage when user-visible behavior changes;
- relevant security/resilience boundaries;
- compiler/type/lint/static-analysis/CodeQL/coverage/docs-build expectations.

A correct-looking implementation that is not wired into runtime behavior is a correctness defect. A behavior/API/architecture change with stale required documentation or an outdated existing behavior specification is incomplete.

Focus comments on BLOCKER, MAJOR, and meaningful MINOR issues. For high-severity comments include location, execution/failure scenario, impact, evidence, and smallest remediation/test. State uncertainty rather than presenting speculation as fact.
