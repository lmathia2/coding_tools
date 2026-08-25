# Product Behavior Specification

## Function

`product-behavior-spec` creates or maintains an outside-in account of a software product's observable behavior. It organizes documentation by user-facing feature rather than source package and links every important claim to code, tests, executable verification, or an explicit open question.

## Intent

API and architecture documentation explain interfaces and implementation decisions, but they often do not answer questions such as:

- What exactly happens when a user starts and then abandons an interaction?
- Which state becomes durable, and when?
- How do role, configuration, offline state, retry, or concurrent edits change the outcome?
- What does the user see during partial failure?
- Is surprising behavior intentional, a documentation error, or a product defect?

The behavior specification provides one stable place to answer those questions.

## Goals

- document user-visible behavior feature by feature;
- make lifecycle, interruption, failure, and recovery explicit;
- keep a canonical glossary and cross-feature foundations;
- distinguish source-derived drafts from runtime-verified claims;
- generate stable executable/manual verification items;
- consolidate suspected defects into evidence-backed triage;
- stay synchronized with code through `documentation-sync` and PR review.

## Default structure

```text
docs/product-behavior/
  README.md              scope, interaction model, structure, coverage
  goal.md                standing drafting/maintenance instructions
  glossary.md            canonical vocabulary
  foundations/           shared lifecycle, state, limits, and definitions
  features/              user-facing feature documents
  cross-cutting/         identity, persistence, offline, accessibility, etc.
  verification/          protocol and stable claim checklists
  bug-triage.md          consolidated behavior mismatches
```

## Workflow

```text
scope and product shape
  -> repository/runtime reconnaissance
  -> scaffold and coverage plan
  -> pilot feature
  -> foundations
  -> parallel independent feature drafting
  -> executable/runtime verification
  -> triage and consistency pass
  -> ongoing sync with code changes
```

## Relationship to normal documentation

This is complementary to:

- API/reference docs — callable interfaces and types;
- architecture/ADRs — implementation boundaries and decisions;
- runbooks — operational procedures;
- module docs — code ownership and internal contracts.

A product behavior document states what the user or operator can observe. Technical detail appears only when it explains that outcome.

## Triggering the workflow

The normal `Dev` or `/dev` entry point should load the skill when asked to:

- write a product description;
- document how an application behaves;
- create a user-experience behavior spec;
- catalog feature behavior and edge cases;
- build verification checklists from code/tests;
- extend or refresh an existing behavior-spec directory.

No additional user-facing command is required.

## PR review integration

When a repository already has a behavior specification, `ReviewPR`/`/review-pr` checks whether changed user-visible behavior also updates relevant feature/foundation documents, verification items, coverage status, and triage.

## Provenance

The design was conceptually inspired by Steve Ruiz's public `product-description` gist. Because no explicit license was visible when reviewed, this repository contains an independently written implementation rather than copied gist files. See [`../vendor/INSPIRATIONS.md`](../vendor/INSPIRATIONS.md).
