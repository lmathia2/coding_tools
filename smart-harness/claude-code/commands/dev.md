---
description: Smart self-contained development workflow: always plans first, parallelizes independent work, chooses the simplest correct design, keeps documentation synchronized, and escalates model intelligence only as needed.
argument-hint: <coding task>
model: sonnet[1m]
effort: high
---
<!-- harness-role: coordinator -->

# /dev

Task: $ARGUMENTS

Apply `plan-first`, `parallel-work`, `context-snapshot`, `engineering-core`, `documentation-sync`, and `ponytail`. For non-trivial work, also apply `superpowers-methodology`.

## 1. Plan before edits

No source edit before an explicit accepted plan. Every plan includes acceptance criteria, implementation order, verification, Documentation Impact, and parallel work lanes.

- mechanical: 1–3 step micro-plan;
- normal: implementation, tests, and docs plan;
- complex/high risk: repository evidence, alternatives/invariants, migration/rollback, docs/ADR/runbook impact, and independent challenge.

Launch `smart-fast-executor` agents for independent code, caller, test, and documentation discovery in parallel.

## 2. Minimize after understanding

Use Ponytail only after tracing the complete flow. Reuse repository code, standard-library/native features, and the smallest coherent implementation. Never simplify away accepted behavior, docs, tests, validation, security, accessibility, compatibility, migration/rollback, data safety, or operational resilience.

## 3. Route intelligently

### Mechanical

Delegate to `smart-fast-worker` after the micro-plan.

### Normal

Implement in this main Sonnet conversation after the plan.

### Complex

Delegate implementation to `smart-deep-implementer` after the plan.

### Product behavior specification

When asked for a product description, outside-in user-behavior specification, feature behavior catalog, verification checklist set, or extension of an existing behavior-spec directory, load `product-behavior-spec`.

Scope the exact surface/source commit, build a common context snapshot, map lifecycle/variants/interruptions/cross-cutting concerns, write the pilot and foundations sequentially, then parallelize disjoint feature documents. Use `smart-deep-reasoner` for complex state/behavior and `smart-fast-executor` for source/test/runtime evidence and deterministic checks.

No extra slash command is required; this is part of `/dev`.

### Debug ambiguous

Before edits, launch `smart-deep-reasoner` in DEBUG mode. Launch independent hypothesis investigations in parallel when useful. Implement only after root cause or a discriminating experiment is established.

### Architecture or high risk

Launch in parallel:

- `smart-top-reviewer` in ARCHITECTURE mode;
- `smart-deep-reasoner` in INDEPENDENT_PLAN_CHALLENGE mode;
- `smart-fast-executor` repository/test/docs investigations as needed.

Synthesize once from evidence. Avoid repeated debate unless new evidence invalidates the plan.

## 4. Parallel implementation only when safely partitioned

Parallel writers require stable interfaces, disjoint ownership, isolated worktrees/branches, and an integration step. Behavior-spec lanes also require disjoint feature/checklist/triage ownership. Otherwise write sequentially.

## 5. Documentation executes with code

Apply `documentation-sync` during implementation. Update required API/function docs, intent/goals, examples, ADRs, configuration, migration, runbooks, and existing product behavior specifications before verification.

## 6. Verify and complexity-review

Run targeted tests and broader unit/integration/e2e/build/type/lint/static/docs/product-behavior checks. Use `smart-fast-executor` for verbose deterministic execution. For non-trivial diffs, run `ponytail-review` once as a complexity-only pass.

Return Result, Verification, Documentation Impact/paths/checks, Product behavior coverage/triage when applicable, Important Decisions, and Residual Risk.
