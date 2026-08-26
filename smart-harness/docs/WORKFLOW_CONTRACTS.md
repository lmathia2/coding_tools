# Workflow Contracts

## Dev / `/dev`

### Function

Complete a coding task from plan through implementation, affected documentation, and executable verification.

### Intent

One dependable entry point with model and workflow selection hidden from the user.

### Contract

1. Decompose non-trivial work into coherent, independently committable units with dependencies, ownership, acceptance criteria, documentation impact, complexity scope, and verification.
2. Run `plan -> implement -> document -> simplify -> verify` for every implementation unit.
3. Use repository evidence to resolve ownership, callers/contracts, tests, and documentation impact.
4. Route to the cheapest capable implementation path.
5. Parallelize independent units only when it improves latency or reduces anchoring/uncertainty; parallel writers use isolated worktrees and disjoint ownership.
6. Update live authoritative documentation in the same logical commit, including implementation, APIs/contracts, purpose, intent, and invariants; otherwise record `Docs-Impact: none — <reason>`.
7. Measure changed-function cyclomatic complexity against the unit start ref when feasible, simplify coherently, and explain scores above 10 or material increases.
8. Execute proportional behavior/unit/integration/runtime/static/docs checks.
9. Escalate to another premium perspective only for material uncertainty or high risk.
10. Report exact evidence and residual risk.

### Normal-case cost shape

```text
coordinator + one implementation context + deterministic verification
```

Fast models perform read-only exploration, measurement, and verification. Implementation stays in the normal or deep writing context. Deep/top models are exceptional paths.

### Product behavior specification

The full `product-behavior-spec` workflow runs only when explicitly requested. Existing behavior specs are maintained like other authoritative docs when a code change affects them.

## ReviewPR / `/review-pr`

### Function

Review another developer's PR through semantic reasoning plus actual execution.

### Contract

1. Resolve exact base and committed PR HEAD.
2. Create a detached PR-head worktree.
3. Inspect logical commits for coherent work units and the `plan -> implement -> document -> simplify -> verify` lifecycle.
4. Run one deep semantic lane and one deterministic execution lane in parallel.
5. Execute complete feasible suites plus relevant e2e/runtime/build/type/lint/static/docs and changed-code complexity checks.
6. Verify live documentation in each code commit or a concrete `Docs-Impact: none` declaration.
7. Add adversarial and security/resilience review only for HIGH_RISK changes.
8. Compare failing subsets against base when regression causality is unclear.
9. Independently attempt to falsify every proposed BLOCKER/MAJOR.
10. Report recommendation, findings, exact commands/results, complexity deltas, missing tests/docs, and blocked checks.
11. Remove/prune the worktree unless intentionally preserved.

Minimality is part of semantic review; it is not a separate review lane.

## Model configuration API

`config/models.json` maps semantic roles (`coordinator`, `normal`, `deep`, `fast`, `top`) to provider-specific model identifiers. `config/configure-models.py` applies/checks adapter frontmatter.

## Installer API

```text
install.sh {copilot|claude|pi|both|all} <project> [--dry-run|--status]
install-global.sh {copilot|claude|pi|both|all} [--dry-run|--status]
```

The thin shell entry points share one Python implementation. It preflights before mutation, atomically writes settings, rolls back touched paths on failure, preserves unrelated customizations, records checksums in an install manifest, and supports dry-run/status inspection.
