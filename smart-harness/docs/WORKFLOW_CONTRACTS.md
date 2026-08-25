# Workflow Contracts

This document describes the user-facing Smart Harness APIs: their function, intent, goals, inputs, outputs, and failure behavior.

## Dev / `/dev`

### Function

Plans and completes a coding or product-behavior-documentation task: implementation, tests, durable documentation, verification, and triage when applicable.

### Intent

Give developers one dependable entry point instead of requiring them to select a model, planning depth, debugger, reviewer, methodology plugin, behavior-spec command, or documentation workflow.

### Goals

- correct behavior with low human rework;
- proportional planning and safe parallelism;
- appropriate model intelligence;
- smallest coherent implementation;
- synchronized code, tests, and documentation;
- optional outside-in feature behavior specifications grounded in evidence;
- executable evidence before completion;
- no runtime external harness dependency.

### Contract

1. Produce and accept a plan before source edits.
2. Assess documentation impact and build a shared context snapshot.
3. Use the local Superpowers methodology for non-trivial work.
4. Gather independent evidence in parallel where useful.
5. Apply Ponytail after comprehension to minimize the design without weakening requirements.
6. Route implementation according to uncertainty/risk.
7. When the request is product-behavior documentation, apply `product-behavior-spec` through the same entry point.
8. Update code, tests, required docs, and any existing behavior specification together.
9. Run proportional unit/integration/e2e/static/docs/product-behavior verification.
10. Run a complexity-only review for non-trivial diffs and focused semantic review when risk warrants.
11. Report results, commands, docs/behavior-spec impact, decisions, triage, and residual risk.

### Failure behavior

The workflow stops or escalates when product intent is materially ambiguous, repository facts contradict the plan, required credentials/services/devices are unavailable, or verification fails. It never reports an unexecuted check as passing.

## Product behavior specification route

### Function

Builds or extends a structured, outside-in account of a product's observable behavior from source, tests, and runtime evidence.

### Trigger

Requests such as product description, user behavior spec, feature-by-feature behavior catalog, behavior verification checklist, or extension of an existing `docs/product-behavior/` directory.

### Contract

1. Define exact product surface, source commit/build, runtime, and exclusions.
2. Define interaction lifecycle, variants, interruption/failure families, and cross-cutting concerns.
3. Build the document/coverage structure and canonical glossary.
4. Write a pilot and foundations sequentially.
5. Draft independent feature documents/checklists in parallel with disjoint ownership.
6. Verify claims through existing tests, targeted probes, and actual product use where feasible.
7. Consolidate mismatches into behavior triage and run consistency/link checks.
8. Keep the specification synchronized through `documentation-sync` and PR review.

No extra user-facing command is added.

## ReviewPR / `/review-pr`

### Function

Reviews another developer's pull request through static reasoning and execution.

### Intent

Catch architecture, correctness, wiring, behavioral, security/resilience, documentation, product-behavior-spec, integration, and unnecessary-complexity defects that a diff-only review can miss.

### Contract

1. Resolve exact committed PR HEAD and base.
2. Plan the review and capture common evidence.
3. Create a detached worktree at PR HEAD.
4. Run semantic, executable, documentation, existing behavior-spec, and Ponytail complexity lanes in parallel.
5. Run full feasible configured unit/integration suites and relevant e2e/static/docs/behavior checks.
6. Add adversarial and security/resilience lanes for high-risk changes.
7. Compare failing subsets against base when causality is unclear.
8. Attempt to falsify BLOCKER/MAJOR findings independently.
9. Report recommendation, findings, exact commands/results, missing tests/docs/behavior artifacts, and blockers.
10. Remove/prune the worktree unless intentionally preserved.

### Output

One recommendation: APPROVE, COMMENT, REQUEST CHANGES, or BLOCK, plus evidence-backed findings.

## Model configuration API

`config/models.json` maps semantic roles to provider model identifiers. `config/configure-models.py` applies and checks the mapping locally.

## Vendored component and inspiration APIs

`vendor/SOURCES.json` records licensed source repository, pinned commit, license, local paths, and adaptation mode.

`vendor/INSPIRATIONS.md` records conceptual sources that were not copied because no explicit license was available.

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
