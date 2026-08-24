---
name: documentation-sync
description: Mandatory documentation-as-code protocol for implementation and PR review. Use whenever code, APIs, behavior, architecture, configuration, operations, or tests change; keeps function/API docs, intent, goals, examples, ADRs, runbooks, and generated references synchronized with executable behavior.
---

# Documentation Sync

Documentation is part of the implementation, not a cleanup task after coding.

A change is not complete when the code works but the durable explanation of its contract, intent, or operation is stale.

## 1. Assess documentation impact during planning

Every implementation plan must include a **Documentation Impact** section.

Inspect the repository's documentation surfaces:

- public API/reference documentation;
- docstrings, JSDoc, language-native API comments;
- module/package README files;
- architecture and design documents;
- ADRs and decision logs;
- configuration/environment references;
- schemas and generated API specifications;
- migration and compatibility guides;
- operational runbooks and troubleshooting;
- examples, tutorials, and sample code;
- changelog/deprecation notes;
- diagrams whose behavior or boundaries changed.

Classify the task:

- `DOCS_REQUIRED`
- `DOCS_GENERATED`
- `DOCS_NOT_AFFECTED`

`DOCS_NOT_AFFECTED` requires a concrete reason; it is not the default shortcut.

## 2. Document function, intent, and goals

For every public or non-obvious function, class, module, endpoint, job, schema, or configuration surface affected by the change, documentation should answer the relevant questions:

1. **Function:** What does it do?
2. **Intent:** Why does this abstraction or behavior exist?
3. **Goal:** What user/system outcome or invariant is it responsible for?
4. **Contract:** Inputs, outputs, errors, side effects, state changes, and compatibility.
5. **Boundaries:** What is intentionally out of scope?
6. **Operational behavior:** Timeouts, retries, idempotency, concurrency, transactions, resource use, or failure recovery when relevant.
7. **Example:** The smallest realistic example when the API is not self-evident.

Document **why, contract, and non-obvious constraints**. Do not add comments that merely translate obvious syntax into English.

## 3. Update docs in the same change

When behavior changes, update the authoritative documentation in the same implementation pass.

Prefer one source of truth:

- generate reference docs from schemas or code when practical;
- link to the authoritative contract instead of copying it;
- update examples so they execute against the current API;
- add an ADR when the change introduces a durable architectural decision or trade-off;
- document migration and rollback when callers, persisted data, or operations must change.

Do not leave "update docs later" unless the user explicitly accepts that debt and it is tracked.

## 4. Validate documentation

Discover repository-native documentation checks from CI and build configuration.

Run applicable checks:

- documentation build;
- link/reference validation;
- doctests;
- example compilation/execution;
- schema/OpenAPI generation and clean-diff check;
- API reference generation;
- spelling/style checks when configured;
- diagram generation when configured.

Never report an unexecuted documentation check as passing.

## 5. Completion gate

Before reporting completion, include:

```text
Documentation impact: REQUIRED | GENERATED | NOT AFFECTED
Documentation changed: <paths or none>
Documentation checks: <commands and PASS/FAIL/NOT EXECUTED>
```

A behavior, API, architecture, configuration, migration, or operational change with stale or missing required documentation is incomplete.

## 6. PR review gate

During PR review, verify that:

- changed public behavior and APIs are documented;
- docs explain intent/goals, not only signatures;
- examples and generated references match the code;
- architecture/ADR/runbook changes are present when warranted;
- documentation checks were executed;
- missing documentation is severity-calibrated by user and operational impact.

See the references in this skill for detailed checklists.
