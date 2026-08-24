# Documentation Policy

## Definition of done

Documentation is part of done when a change affects:

- public or reusable APIs;
- behavior or failure semantics;
- module/service purpose;
- architecture or durable decisions;
- configuration;
- schemas or persisted data;
- migrations and compatibility;
- operations, rollout, recovery, or troubleshooting;
- examples or tutorials.

## Quality bar

Documentation should communicate:

- **function** — what the code or system does;
- **intent** — why it exists;
- **goals** — the outcome or invariant it protects;
- **contract** — inputs, outputs, errors, side effects, and compatibility;
- **constraints** — boundaries, trade-offs, and non-goals;
- **operation** — how it behaves under failure and how to verify/recover it.

Do not document obvious syntax. Document the reasoning and contract that cannot be safely inferred.

## Sync mechanism

The `documentation-sync` skill is explicitly invoked by all execution and PR-review workflows.

CI validates:

- workflow files mention documentation;
- generated reference content is current;
- local Markdown links resolve;
- core skills and model config are structurally valid.

Repositories using the harness should add their native docs build, doctest, link, and generated-spec checks to CI.
