# Workflow Contracts

## Dev / `/dev`

### Function

Complete a coding task from plan through implementation, affected documentation, and executable verification.

### Intent

One dependable entry point with model and workflow selection hidden from the user.

### Contract

1. Make a proportional plan before edits.
2. Use repository evidence to resolve ownership, callers/contracts, tests, and documentation impact.
3. Route to the cheapest capable implementation path.
4. Parallelize independent work only when it improves latency or reduces anchoring/uncertainty.
5. Choose the smallest correct design; no speculative abstractions or dependencies.
6. Update affected authoritative documentation in the same pass.
7. Execute proportional behavior/unit/integration/runtime/static/docs checks.
8. Escalate to another premium perspective only for material uncertainty or high risk.
9. Report exact evidence and residual risk.

### Normal-case cost shape

```text
coordinator + one implementation context + deterministic verification
```

Mechanical tasks use the fast model. Normal tasks use Sonnet. Deep/top models are exceptional paths.

### Product behavior specification

The full `product-behavior-spec` workflow runs only when explicitly requested. Existing behavior specs are maintained like other authoritative docs when a code change affects them.

## ReviewPR / `/review-pr`

### Function

Review another developer's PR through semantic reasoning plus actual execution.

### Contract

1. Resolve exact base and committed PR HEAD.
2. Create a detached PR-head worktree.
3. Run one deep semantic lane and one deterministic execution lane in parallel.
4. Execute the complete feasible configured unit and integration suites, plus relevant e2e/runtime/build/type/lint/static/docs checks.
5. Add adversarial and security/resilience review only for HIGH_RISK changes.
6. Compare failing subsets against base when regression causality is unclear.
7. Independently attempt to falsify every proposed BLOCKER/MAJOR.
8. Report recommendation, findings, exact commands/results, missing tests/docs, and blocked checks.
9. Remove/prune the worktree unless intentionally preserved.

Minimality is part of semantic review; it is not a separate review lane.

## Model configuration API

`config/models.json` maps semantic roles (`coordinator`, `normal`, `deep`, `fast`, `top`) to provider-specific model identifiers. `config/configure-models.py` applies/checks adapter frontmatter.

## Installer API

```text
install.sh {copilot|claude|pi|both|all} <project>
install-global.sh {copilot|claude|pi|both|all}
```

Installers copy only repository-local content, remove known legacy harness-managed skill/agent paths, preserve unrelated customizations, and back up replaced files.
