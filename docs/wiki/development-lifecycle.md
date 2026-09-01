# Development Lifecycle

The workflow concentrates human judgment before code changes, then makes
execution fast and evidence-driven.

## 1. Grill and lock

The coordinator inspects the repository, resolves goals, acceptance, scope,
alternatives, assumptions, constraints, and failure behavior, and records the
decision lock. `auto` answers the same material questions from evidence and the
smallest reversible assumptions. A non-trivial plan is decomposed into coherent,
independently committable units with ownership and exact verification commands.

## 2. Execute each unit in one order

```text
plan → implement → document → simplify → verify
```

Implementation follows source priority and dependency discipline without using
deletion or line count as a goal. Safety guardrails remain protected, and known
design ceilings carry an upgrade trigger. Documentation then updates the
authoritative purpose, intent, contracts, invariants, and operational behavior
in the same logical commit.

During documentation, `wiki.py due --every N` checks the full-refresh cadence.
If it passes, no model work is spent on the wiki. If due, the active host rebuilds
every manifest page from current repository evidence, then `mark-refreshed`
advances the generation.

## 3. Simplify and verify

The simplification phase removes duplication and speculation, then measures
changed-function cyclomatic complexity. Verification expands from focused tests
to package/build/static/integration/documentation checks according to blast
radius. The final composed range gate must pass; an unexecuted check is never
reported as success.

## 4. Explain the finished result

After integrated committed-range verification, the required ELI5 handoff creates
an offline visual guide to the entire package for a curious developer: problem,
installation, first run, architecture, under-the-hood flow, and deeper paths.
The completed diff contributes only significant package-level updates. The deck
is capped at 10 slides and remains a learning artifact, not a substitute for
source, authoritative documentation, or tests.
