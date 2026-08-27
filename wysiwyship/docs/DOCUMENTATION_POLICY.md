# Documentation Policy

Documentation is a live specification and a commit-level gate inside `engineering-workflow` and `pr-review`, not a release-end phase or separate default workflow.

## Commit-level synchronization

Every logical code commit contains the authoritative documentation needed to understand that version of the system. Documentation records not only what was implemented but why it exists: purpose, intent, protected goals/invariants, API methods and contracts, constraints, and relevant failure or operational behavior.

When a code commit genuinely has no documentation impact, record `Docs-Impact: none — <concrete reason>` in the commit message or work-unit evidence. Do not defer known documentation changes to a later commit; amend or squash so every reviewable commit is internally coherent.

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

`NOT AFFECTED` is valid only with a concrete reason. Do not create low-value prose merely to satisfy the gate; improve the nearest authoritative specification, API reference, module README, ADR, runbook, or example.

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

PR review checks documentation synchronization both per logical commit and across the final aggregate diff.

The installed check is:

```bash
python3 .wysiwyship/tools/commit_docs.py <base-ref>
```

It treats Markdown/reStructuredText/AsciiDoc and conventional documentation directories/files as documentation. Repositories with generated or unusual documentation formats may supplement it with a native check; the semantic PR lane still verifies content quality, purpose, intent, and contract accuracy.

## Product behavior specifications

Do not generate `docs/product-behavior/` automatically. Run the specialist workflow only when explicitly requested. If the repository already has such a specification and a code change affects documented user-visible behavior, update and reverify only the affected artifacts.
