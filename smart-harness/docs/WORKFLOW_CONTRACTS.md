# Workflow Contracts

This document describes the user-facing Smart Harness APIs: their function, intent, goals, inputs, outputs, and failure behavior.

## Dev / `/dev`

### Function

Plans and completes a coding task: implementation, tests, documentation, and verification.

### Intent

Give developers one dependable entry point instead of requiring them to select a model, planning depth, debugger, reviewer, or documentation workflow.

### Goals

- correct behavior with low human rework;
- proportional planning;
- independent work parallelized safely;
- appropriate model intelligence;
- minimal coherent implementation;
- synchronized code, tests, and documentation;
- executable evidence before completion.

### Input

A task description. Acceptance criteria and constraints are useful but not mandatory when repository evidence can resolve them.

### Contract

1. Produce and accept a plan before source edits.
2. Assess documentation impact.
3. Gather independent evidence in parallel where useful.
4. Route implementation according to uncertainty/risk.
5. Update code, tests, and required docs together.
6. Run proportional unit/integration/e2e/static/docs verification.
7. Report results, commands, docs impact, decisions, and residual risk.

### Failure behavior

The workflow stops or escalates when product intent is materially ambiguous, repository facts contradict the plan, required credentials/services are unavailable, or verification fails.

It never reports an unexecuted check as passing.

## ReviewPR / `/review-pr`

### Function

Reviews another developer's pull request through static reasoning and execution.

### Intent

Catch architecture, correctness, wiring, behavioral, security/resilience, documentation, and integration defects that a diff-only review can miss.

### Goals

- exact PR-head isolation;
- complete feasible unit/integration execution;
- deterministic static evidence;
- parallel independent review lanes;
- low false-positive high-severity findings;
- no mutation of the developer's primary checkout.

### Input

Base ref or PR number/URL plus optional intent and acceptance criteria.

### Contract

1. Resolve exact committed PR HEAD and base.
2. Plan the review.
3. Create a detached worktree at PR HEAD.
4. Run semantic and executable/documentation lanes in parallel.
5. Run full feasible configured unit/integration suites and relevant e2e/static/docs checks.
6. Compare failing subsets against base when causality is unclear.
7. Attempt to falsify BLOCKER/MAJOR findings independently.
8. Report recommendation, findings, exact commands/results, missing tests/docs, and blockers.
9. Remove/prune the worktree unless intentionally preserved.

### Output

One recommendation: APPROVE, COMMENT, REQUEST CHANGES, or BLOCK, plus evidence-backed findings.

## Model configuration API

`config/models.json` maps semantic roles to provider model identifiers.

- `coordinator` — routing, synthesis, ownership;
- `normal` — ordinary implementation;
- `deep` — complex implementation/reasoning;
- `fast` — exploration and deterministic execution;
- `top` — architecture/security/adjudication.

`config/configure-models.py` applies the mapping to provider adapters.

## Integration lock API

`integrations/upstreams.lock.json` records repository, branch/ref, exact commit, license, and integration mode.

`check-upstreams.py` checks or updates locks; generated reference and CI expose drift.

## Installer API

```text
install.sh {copilot|claude|pi|both|all} <project>
install-global.sh {copilot|claude|pi|both|all}
```

Installers synchronize canonical files, preserve unrelated customizations, and back up replaced paths.
