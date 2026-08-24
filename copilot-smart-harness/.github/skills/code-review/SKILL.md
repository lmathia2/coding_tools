---
name: deep-pr-code-review
description: Deep pull-request review guidance for architecture, correctness/wiring, security/resilience, behavioral tests, integration testing, and static-analysis expectations.
---

# Deep PR Code Review

When reviewing a pull request, prioritize substantive merge risk over style.

Review the PR in these dimensions.

## Architecture and design

- requirement-to-design fit;
- ownership/component boundaries;
- coupling and duplicated abstractions;
- public/API/data/schema contracts;
- migration and rollback;
- consistency with intentional repository patterns.

## Correctness and wiring

Trace changed behavior end-to-end:

- routes/handlers/registrations/DI;
- config and feature flags;
- callers and downstream consumers;
- data/type/schema compatibility;
- error paths;
- state transitions;
- concurrency;
- retries/idempotency;
- transaction boundaries.

A new implementation that is not actually wired into runtime behavior is a correctness defect.

## Security and resilience

Review changed trust/failure boundaries:

- authentication/authorization;
- input validation/injection;
- secrets/sensitive logging;
- SSRF/path/file access;
- partial failure;
- timeouts/retries;
- idempotency;
- saturation/resource cleanup;
- restart/recovery;
- observability;
- rollback.

Report concrete scenarios, not generic checklist advice.

## Behavioral test adequacy

Judge whether tests prove externally meaningful behavior:

- happy path;
- error path;
- boundary conditions;
- integration wiring;
- state transitions;
- compatibility;
- retry/idempotency;
- migration/rollback where relevant.

Prefer behavioral/integration evidence over raw line coverage.

## Static analysis / deterministic checks

Pay attention to repository compiler/type/lint/static-analysis/CodeQL/coverage expectations and CI configuration.

If deterministic analysis should catch a class of issue, prefer that enforcement over a recurring prose comment.

## Severity

Focus comments on:

- BLOCKER
- MAJOR
- meaningful MINOR issues

Avoid flooding the PR with style preferences.

For a high-severity comment include:

- specific location;
- execution/failure scenario;
- impact;
- evidence;
- smallest remediation or missing test.

If the evidence is uncertain, say so rather than presenting speculation as fact.
