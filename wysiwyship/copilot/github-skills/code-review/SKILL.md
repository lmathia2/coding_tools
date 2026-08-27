---
name: focused-deep-code-review
description: GitHub-native review guidance focused on substantive merge risk: architecture, correctness/wiring, behavioral tests, documentation accuracy, security/resilience, and unnecessary complexity without style noise.
---

# Focused Deep Code Review

Prioritize defects that can change runtime behavior, compatibility, operations, or maintainability.

Review architecture/design fit, actual runtime wiring, contracts/state/error paths, relevant concurrency/retry/idempotency, behavioral test adequacy, authoritative documentation, changed security/resilience boundaries, and avoidable complexity.

Minimality is one dimension of the same review: recommend deletion/reuse/native/stdlib simplification only when it preserves requirements, tests, security, accessibility, compatibility, documentation, and operations.

Focus comments on BLOCKER, MAJOR, and meaningful MINOR issues. For serious findings provide location, concrete execution/failure scenario, impact, evidence, and the smallest remediation/test. State uncertainty instead of presenting speculation as fact.
