---
name: pragmatic-tdd
description: Use for behavior-changing code where an executable test can cheaply define the requirement. Applies test-first discipline without forcing it onto mechanical changes.
---
# Pragmatic TDD
For behavior-changing code, establish an executable failure condition first whenever practical.

## RED
Write or identify the smallest test expressing the requirement. Run it and confirm it fails for the intended behavioral reason.

## GREEN
Implement the smallest coherent change that satisfies the behavior. Run the targeted test.

## REFACTOR
Improve structure only after GREEN and rerun relevant tests.

Strong candidates: bugs, business logic, validation/APIs, parsers/transforms, permissions/security, state machines, concurrency, compatibility behavior.

Usually unnecessary: docs, formatting, generated artifacts, mechanical renames protected by compiler/typechecker, trivial metadata.

For risky refactors, create characterization tests first. Verification-before-completion always applies.
