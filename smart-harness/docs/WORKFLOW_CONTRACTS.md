# Workflow Contracts

This document describes the user-facing Smart Harness APIs: their function, intent, goals, inputs, outputs, and failure behavior.

## Dev / `/dev`

### Function

Plans and completes a coding task: implementation, tests, documentation, and verification.

### Intent

Give developers one dependable entry point instead of requiring them to select a model, planning depth, debugger, reviewer, methodology plugin, or documentation workflow.

### Goals

- correct behavior with low human rework;
- proportional planning and safe parallelism;
- appropriate model intelligence;
- smallest coherent implementation;
- synchronized code, tests, and documentation;
- executable evidence before completion;
- no runtime external harness dependency.

### Contract

1. Produce and accept a plan before source edits.
2. Assess documentation impact and build a shared context snapshot.
3. Use the local Superpowers methodology for non-trivial work.
4. Gather independent evidence in parallel where useful.
5. Apply Ponytail after comprehension to minimize the design without weakening requirements.
6. Route implementation according to uncertainty/risk.
7. Update code, tests, and required docs together.
8. Run proportional unit/integration/e2e/static/docs verification.
9. Run a complexity-only review for non-trivial diffs and focused semantic review when risk warrants.
10. Report results, commands, docs impact, decisions, and residual risk.

### Failure behavior

The workflow stops or escalates when product intent is materially ambiguous, repository facts contradict the plan, required credentials/services are unavailable, or verification fails. It never reports an unexecuted check as passing.

## ReviewPR / `/review-pr`

### Function

Reviews another developer's pull request through static reasoning and execution.

### Intent

Catch architecture, correctness, wiring, behavioral, security/resilience, documentation, integration, and unnecessary-complexity defects that a diff-only review can miss.

### Contract

1. Resolve exact committed PR HEAD and base.
2. Plan the review and capture common evidence.
3. Create a detached worktree at PR HEAD.
4. Run semantic, executable, documentation, and Ponytail complexity lanes in parallel.
5. Run full feasible configured unit/integration suites and relevant e2e/static/docs checks.
6. Add adversarial and security/resilience lanes for high-risk changes.
7. Compare failing subsets against base when causality is unclear.
8. Attempt to falsify BLOCKER/MAJOR findings independently.
9. Report recommendation, findings, exact commands/results, missing tests/docs, and blockers.
10. Remove/prune the worktree unless intentionally preserved.

### Output

One recommendation: APPROVE, COMMENT, REQUEST CHANGES, or BLOCK, plus evidence-backed findings.

## Model configuration API

`config/models.json` maps semantic roles to provider model identifiers. `config/configure-models.py` applies and checks the mapping locally.

## Vendored component API

`vendor/SOURCES.json` records source repository, pinned commit, license, local paths, and adaptation mode. It is provenance, not a runtime updater.

## Pi parallel runner API

```text
.pi/tools/parallel-pi.py --tasks <json> [--cwd <dir>] [--max-workers N]
```

The task JSON is an array containing `name`, `prompt`, and optional `cwd`, `model`, `thinking`, `tools`, and `timeout_seconds`. Output is one JSON array of child results. It invokes only the installed Pi host in print mode and uses Python standard library.

## Installer API

```text
install.sh {copilot|claude|pi|both|all} <project>
install-global.sh {copilot|claude|pi|both|all}
```

Installers copy repository-local files, preserve unrelated customization, back up replaced paths, and perform no network/package/plugin installation.
