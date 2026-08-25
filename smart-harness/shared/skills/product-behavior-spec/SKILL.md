---
name: product-behavior-spec
description: Build and maintain an outside-in product behavior specification from code, tests, and the running product. Use when asked for a product description, user-experience behavior spec, feature-by-feature behavior documentation, executable verification catalog, or when extending an existing behavior-spec directory.
license: Original Smart Harness implementation
metadata:
  inspiration: https://gist.github.com/steveruizok/83ae5c53f2784ebf8f5fe0a3fb94480f
  inspiration-note: Conceptual inspiration only; the public gist did not state a license when reviewed, so this implementation and its templates were written independently rather than copied.
---

# Product Behavior Specification

## Purpose

Create durable, outside-in documentation of what a product does from the user's point of view: how a feature begins, evolves, completes, fails, is interrupted, and interacts with the rest of the product.

This complements API, architecture, and implementation documentation. It does not replace them.

## Default output

Unless the user specifies another destination, use:

```text
docs/product-behavior/
  README.md
  goal.md
  glossary.md
  features/
  foundations/
  cross-cutting/
  verification/
    README.md
  bug-triage.md
```

Do not create a separate Git repository or commit automatically unless the user or existing repository workflow explicitly asks for it.

## Core principles

1. Describe observable experience, not internal implementation.
2. Ground every claim in code, tests, executable behavior, or an explicitly marked open question.
3. Use one stable feature-document structure so omissions become visible by comparison.
4. Track the exact source commit or build each document was checked against.
5. Treat cancellation, interruption, partial failure, and recovery as first-class behavior.
6. Separate drafted-from-code from verified-in-product status.
7. Consolidate suspected defects by root cause rather than repeating symptoms.
8. Keep the structure, glossary, coverage table, checklists, and triage in sync.

## Phase 0 — Scope and product shape

Before writing feature documents, establish:

- product and exact surface: route, command, role, mode, configuration, or device;
- source repository/path and source commit;
- how the product is run or exercised;
- what is intentionally out of scope;
- output location;
- interaction unit and lifecycle phases;
- variant axis: role, mode, flag, configuration, modifier, or current state;
- interrupt/failure families;
- cross-cutting concerns and their fixed order.

Use [`references/product-shapes.md`](references/product-shapes.md) to map these decisions for web apps, editors/mobile apps, CLIs, chat/agent products, and background workflows.

## Phase 1 — Reconnaissance and structure

Read only enough implementation and tests to build a reliable map:

- entry points and user-visible surfaces;
- state machines, reducers, controllers, handlers, or command definitions;
- domain objects and persistent state;
- behavioral/integration/e2e tests;
- defaults, limits, validation, timeouts, and feature flags;
- permissions and trust boundaries;
- existing user documentation and vocabulary.

Create a `context-snapshot` with the source commit and evidence paths.

Design the document tree by how the user encounters behavior, not by source package. Put every planned document in the README structure and coverage table before drafting it.

## Phase 2 — Scaffold

Create, in order:

1. `README.md` from [`references/README-template.md`](references/README-template.md).
2. `glossary.md` from [`references/glossary-template.md`](references/glossary-template.md).
3. `goal.md` from [`references/goal-template.md`](references/goal-template.md).
4. `verification/README.md` and initial checklist files from [`references/verification-template.md`](references/verification-template.md).
5. `bug-triage.md` from [`references/triage-template.md`](references/triage-template.md).

The README structure and coverage table must remain exact mirrors of files on disk.

## Phase 3 — Pilot and foundations

Write one small but representative feature first using [`references/feature-template.md`](references/feature-template.md). Use it to establish depth, tone, state names, interrupt families, variant tables, and evidence conventions.

Then write the foundation documents that own shared definitions, limits, lifecycle semantics, persistence rules, and cross-feature vocabulary.

Do not parallelize the pilot or first foundation set. They define the contract that later documents reuse.

## Phase 4 — Parallel feature drafting

After the pilot and foundations stabilize, independent feature documents may be drafted in parallel.

Each lane receives the same context snapshot, glossary, goal, feature template, source commit, and ownership boundary. Parallel lanes must not edit the same feature document, glossary section, coverage row, checklist table, or triage identifier range.

The coordinator integrates:

- glossary additions;
- cross-references;
- coverage status;
- verification items;
- suspected-defect triage;
- conflicting descriptions of shared behavior.

## Feature document contract

Each feature document covers the relevant portions of:

1. Summary and user-visible entry points.
2. Normal flow.
3. Lifecycle and state transitions.
4. Variants, permissions, modes, configuration, and state-dependent behavior.
5. Cancellation, interruption, failure, timeout, and recovery.
6. Interactions with cross-cutting systems.
7. Limits and edge cases.
8. Evidence, verification status, and unresolved questions.

Use a compact Mermaid state diagram when it materially clarifies user-visible transitions. Do not expose internal bookkeeping states that have no observable consequence.

## Phase 5 — Verification

For every material claim, choose the strongest feasible evidence:

- existing unit/integration/e2e test;
- targeted executable probe;
- running-product observation;
- code-level evidence when runtime verification is unavailable.

Verification items use stable IDs and record setup, steps, expected result, actual result, evidence, environment, and status: `PASS`, `FAIL`, `BLOCKED`, or `NOT RUN`.

Automated execution can verify state, output, persistence, and error behavior. It must not claim to verify visual feel, timing perception, accessibility with assistive technology, or device-specific interaction unless those were actually exercised.

A document becomes `verified` only when its required claims have passed or every unresolved failure is linked to triage.

## Phase 6 — Triage and consistency

Aggregate suspected defects from feature documents and failed verification items. Deduplicate by causal mechanism when evidence supports it.

Each triage entry records:

- observable impact;
- actual and expected behavior;
- reproduction;
- source/test evidence;
- severity and confidence;
- whether the next action is a fix, documentation correction, product decision, or further investigation;
- linked feature documents and verification IDs.

Then run the consistency pass:

- structure equals files on disk;
- coverage table equals structure;
- terminology matches the glossary;
- relative links and anchors resolve;
- shared behavior is described consistently;
- each document records source commit and evidence status;
- verification and triage links are reciprocal.

Run:

```bash
python3 references/check-links.py <behavior-spec-root>
```

## Maintaining an existing specification

When behavior changes:

1. locate affected feature, foundation, cross-cutting, verification, and triage documents;
2. update the source commit/build reference;
3. revise observable behavior and examples;
4. update or add executable verification items;
5. rerun affected checks;
6. update coverage and triage status;
7. report any behavior that could not be reverified.

`documentation-sync` treats an existing product behavior specification as authoritative documentation that must change with the code.

## Completion report

Return:

- scope and source commit;
- documents drafted or revised;
- coverage status;
- verification commands/items and results;
- suspected defects or documentation mismatches;
- blocked verification and required environment;
- remaining open questions.
