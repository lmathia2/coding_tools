# Goal: maintain the {Product} behavior specification

## Outcome

Produce a complete, internally consistent, outside-in specification for {surface} that is grounded in source and tests and checked against the running product where feasible.

## Authoritative inputs

- source repository/path: {path}
- source commit/build: {commit}
- runtime/verification surface: {how to run}
- specification root: {path}

## Reading order

1. `README.md` — scope, structure, interaction model, and coverage.
2. `glossary.md` — canonical vocabulary.
3. Pilot feature — depth and evidence example.
4. Relevant foundations and cross-cutting documents.
5. Current feature’s source, tests, and existing docs.

## Established facts

Record load-bearing definitions, limits, defaults, lifecycle rules, and cross-feature decisions here with links to the owning foundation document. Do not re-derive them independently in every lane.

## Working rules

- Treat source code as read-only unless the task explicitly includes product fixes.
- Do not guess when source/tests/runtime disagree; record the conflict.
- Keep README structure, coverage, glossary, verification, and triage synchronized.
- Use the same variant, interrupt, and cross-cutting order throughout.
- Parallel drafting requires disjoint document/checklist/triage ownership.
- Do not mark a document verified without recorded evidence.
- Follow repository commit and attribution policy; do not commit or push unless authorized.

## Current work

- document(s): {paths}
- ownership boundary: {scope}
- source/test evidence: {paths}
- verification items: {IDs or planned prefix}
- open dependencies: {items}

## Done definition

- every planned coverage row is resolved;
- required feature and foundation documents are complete;
- terminology and cross-references are consistent;
- relative links pass;
- required verification items pass or link to triage;
- unresolved questions and environment blockers are explicit;
- source commits/builds are recorded.
