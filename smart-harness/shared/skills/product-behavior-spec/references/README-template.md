# {Product} behavior specification

An outside-in description of what users can observe and do in {surface}, verified against {source repository/build}.

## Purpose

Explain why this specification exists, who uses it, and which decisions it should support.

## Scope

- **Included surface:** {route, command, role, mode, device, or configuration}
- **Source of truth:** {repository/path and commit}
- **Runtime used for verification:** {command, URL, binary, account, environment}
- **Excluded:** {explicit non-goals and reason}

## Documentation stance

- Describe observable product behavior before implementation details.
- Mark technical details as implementation notes only when they explain a user-visible result.
- Use glossary terms consistently.
- Distinguish drafted-from-source from verified-in-product.
- State surprising behavior and unresolved uncertainty plainly.

## Interaction model

### Unit and lifecycle

{Define the unit of interaction and its named phases.}

### Variants

{List the stable variant axis used by feature documents.}

### Interrupt and failure families

{List the stable ordered interrupt/failure rows.}

### Cross-cutting concerns

{List the stable ordered cross-cutting concerns.}

## Document contract

Every feature document uses the project’s feature template and covers normal flow, lifecycle, variants, interruptions/failures, cross-cutting systems, edge cases, evidence, and open questions.

## Method

1. Read source and behavioral tests.
2. Draft observable behavior.
3. Create stable verification items.
4. Run feasible tests/probes and observe the product.
5. Triage mismatches.
6. Reconcile vocabulary, links, coverage, and source commits.

## Structure

```text
README.md
 goal.md
 glossary.md
 bug-triage.md
 foundations/
 features/
 cross-cutting/
 verification/
```

Replace this block with the exact planned tree and one-line purpose for every document. Keep it synchronized with disk.

## Coverage

| Document | Owner/scope | Status | Source commit | Verification |
|---|---|---|---|---|
| `glossary.md` | shared vocabulary | not started | — | — |
| `foundations/{name}.md` | {purpose} | not started | — | — |
| `features/{feature}.md` | {purpose} | not started | — | — |

Allowed status values: `not started`, `drafted`, `verified`, `needs revision`.

## Reference map

| Area | Authoritative paths/tests/docs |
|---|---|
| User-visible entry points | {paths} |
| State/lifecycle | {paths} |
| Domain and persistence | {paths} |
| Behavioral tests | {paths} |
| Existing user docs | {paths} |

## Verification summary

Link to `verification/README.md` and summarize the latest pass, environment, blockers, and source commit.
