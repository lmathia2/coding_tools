# Documentation Policy

## Definition of done

Documentation is part of done when a change affects:

- public or reusable APIs;
- user-visible behavior or failure semantics;
- module/service purpose;
- architecture or durable decisions;
- configuration;
- schemas or persisted data;
- migrations and compatibility;
- operations, rollout, recovery, or troubleshooting;
- examples or tutorials;
- an existing product behavior specification, verification checklist, glossary, coverage table, or behavior-triage item.

## Quality bar

Documentation should communicate:

- **function** — what the code or system does;
- **intent** — why it exists;
- **goals** — the outcome or invariant it protects;
- **contract** — inputs, outputs, errors, side effects, and compatibility;
- **observable behavior** — lifecycle, cancellation, interruption, failure, and recovery from the user/operator point of view;
- **constraints** — boundaries, trade-offs, and non-goals;
- **operation** — how it behaves under failure and how to verify/recover it.

Do not document obvious syntax. Document the reasoning, contract, and behavior that cannot be safely inferred.

## Documentation layers

Use the right durable artifact:

- API/reference docs for callable interfaces;
- module/package docs for code ownership and internal contracts;
- ADRs/design docs for durable decisions and trade-offs;
- runbooks for operation and recovery;
- `product-behavior-spec` for outside-in, feature-by-feature user behavior and verification;
- executable tests and generated specifications whenever they are the stronger source of truth.

## Sync mechanism

The `documentation-sync` skill is explicitly invoked by all execution and PR-review workflows.

If an outside-in behavior specification exists, changed behavior updates its feature/foundation/cross-cutting docs, glossary, coverage status, verification items, source commit, and triage in the same change.

CI validates:

- workflow files mention documentation;
- generated reference content is current;
- core skills and model config are structurally valid;
- the self-contained product behavior skill and references exist.

Repositories using the harness should add their native docs build, doctest, behavior-checklist/probe, link, and generated-spec checks to CI.
