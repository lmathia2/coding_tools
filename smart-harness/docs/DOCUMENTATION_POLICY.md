# Documentation Policy

Documentation is a completion gate inside `engineering-workflow` and `pr-review`, not a separate default workflow.

## When documentation changes

Update authoritative documentation when code changes affect:

- public or reusable APIs;
- non-obvious function/module responsibility or intent;
- observable behavior or failure semantics;
- architecture or durable decisions;
- configuration;
- schemas or persisted data;
- migrations and compatibility;
- operations, rollout, recovery, or troubleshooting;
- examples/tutorials;
- deprecation/changelog guidance.

`NOT AFFECTED` is valid when the plan states a concrete reason. Do not create documentation just to satisfy a ritual.

## Quality bar

Useful documentation explains the relevant portions of:

- **function** — what it does;
- **intent** — why it exists;
- **goal/invariant** — what outcome it protects;
- **contract** — inputs, outputs, errors, side effects, compatibility;
- **constraints/non-goals**;
- **operational/failure behavior** — retries, timeouts, idempotency, recovery, rollback, observability when relevant;
- the smallest realistic example when the interface is not self-evident.

Do not translate obvious syntax into comments.

## Verification

Run repository-native docs builds, doctests, examples, link checks, schema/API-reference generation, or generated-file clean-diff checks when affected. Never report an unexecuted docs check as passing.

## Product behavior specifications

Do not generate `docs/product-behavior/` automatically. Run the specialist workflow only when explicitly requested. If the repository already has such a specification and a code change affects documented user-visible behavior, update and reverify only the affected artifacts.
