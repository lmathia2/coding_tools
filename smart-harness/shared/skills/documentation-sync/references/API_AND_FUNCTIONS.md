# API and Function Documentation

Use this reference when a change affects a public API, reusable module, important internal abstraction, schema, command, endpoint, background job, or configuration surface.

## Minimum contract

Document the applicable parts:

- purpose and user/system outcome;
- why the abstraction exists;
- parameters and accepted forms;
- return/result semantics;
- errors and failure behavior;
- side effects and state mutations;
- authorization/trust assumptions;
- thread/async/concurrency safety;
- idempotency and retry behavior;
- performance or scale limits;
- lifecycle and ownership;
- compatibility and deprecation;
- smallest realistic example.

## Comments versus durable docs

Use code comments/docstrings for facts that must stay next to the symbol.

Use README/reference docs for workflows and cross-symbol concepts.

Use schemas/generated docs for machine-readable contracts.

Use tests for executable examples and invariants.

Avoid:

- restating names or syntax;
- documenting speculative future features;
- copying the same contract into multiple places;
- examples that are not compiled or tested when the repository can test them.
