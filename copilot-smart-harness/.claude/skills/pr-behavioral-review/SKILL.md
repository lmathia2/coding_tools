---
name: pr-behavioral-review
description: Use when reviewing a PR to judge tests by observable behavior and execute targeted integration/e2e checks instead of relying on line coverage or unit tests alone.
---

# PR Behavioral Review

A PR is not adequately tested merely because new lines have unit coverage.

Map each material behavior change to executable evidence.

Check:

- happy path;
- invalid/error path;
- boundary values;
- integration wiring;
- state transitions;
- compatibility with old callers/data;
- retries/idempotency where relevant;
- migration/rollback behavior;
- externally visible effects.

Prefer the lowest-level test that proves the behavior without mocking away the changed boundary.

When the PR changes interaction between components, require at least one test that crosses that integration boundary when practical.

Report separately:

- tests observed in the PR;
- tests actually executed during review;
- missing behavioral tests;
- coverage metrics, if available.

Do not equate raw line coverage with behavioral correctness.
