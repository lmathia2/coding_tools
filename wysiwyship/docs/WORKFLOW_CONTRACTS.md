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
10. After the committed-range gate passes, invoke `eli5`, render and check the visual explainer, and report its audience and path.
11. Report exact evidence and residual risk.

### Deterministic lifecycle gate

The installed gate evaluates the committed range as one machine-readable contract:

```text
python3 .wysiwyship/tools/check.py <unit-start-ref> --head HEAD
```

It checks documentation evidence in every code commit, scores only Python functions intersecting changed lines, and runs the explicit argument-array commands in `.wysiwyship/config/checks.json`. A project can add unit, integration, build, type, lint, generated-artifact, or documentation commands without embedding shell evaluation in the harness. `--format json` provides CI/host automation output; `--require-clean` adds a repository-cleanliness assertion when appropriate.

Exit status `0` means all checks passed, `1` means a check failed, and `2` means configuration or gate execution was invalid. The default installed configuration has documentation and complexity checks enabled and leaves project-specific commands empty.

### Resumable work-unit state and hooks

The optional ledger is for complex, long, parallel, or handoff-prone tasks; routine fixes need no ledger. `work_units.py init` resolves the unit's base ref to an immutable commit and stores acceptance criteria, dependencies, owners/owned paths, documentation impact, source artifact, and lifecycle evidence under ignored `.agent-state/work-units/`. `advance` accepts evidence only in `plan -> implement -> document -> simplify -> verify` order. Dependencies must complete and active ownership cannot overlap before implementation starts.

```text
work_units.py init ID --title TITLE --goal GOAL --acceptance CRITERION --owns PATH --base-ref REF --docs-impact required --doc-path PATH --activate
work_units.py ready | list | show [ID] | validate
work_units.py advance ID --evidence EVIDENCE [--commit SHA]
check.py --active
work_units.py close [ID]
```

Project installation adds a Copilot `agentStop` hook and merges an idempotent Claude Code `Stop` hook. Both are no-ops without an active unit, self-limit when already continuing from a stop hook, block an incomplete active lifecycle, and run the deterministic gate after the unit reaches `complete`. A successful hook removes only the active pointer; unit history remains available. Manual/non-hook hosts run `check.py --active` followed by `work_units.py close`.

### Accepted-spec intake bridge

`spec_bridge.py` detects current repository artifacts at `specs/*/tasks.md` (Spec Kit), `openspec/changes/*/tasks.md` (OpenSpec), and BMAD implementation story/spec locations under `_bmad-output/implementation-artifacts/`. It parses Markdown checklist IDs, completion, `[P]` hints, explicit `depends:` IDs, section context, and referenced paths.

```text
spec_bridge.py detect
spec_bridge.py preview PATH [--framework spec-kit|openspec|bmad]
spec_bridge.py import PATH --accepted [--owner NAME] [--activate-first]
```

`preview` is read-only. `import` requires `--accepted`, preflights all IDs/conflicts before writing, resolves explicit task dependencies to generated unit IDs, and retains the source framework/path as authoritative provenance. It does not infer unstated dependencies or run any upstream generator, validator, apply, or archive command. Update/check off the upstream task artifact during the unit's documentation stage.

### Normal-case cost shape

```text
coordinator + one implementation context + deterministic verification
```

Fast models perform read-only exploration, measurement, and verification. Implementation stays in the normal or deep writing context. Deep/top models are exceptional paths.

### Product behavior specification

The full `product-behavior-spec` workflow runs only when explicitly requested. Existing behavior specs are maintained like other authoritative docs when a code change affects them.

### Project ELI5 completion handoff

Every successful `Dev` / `/dev` run invokes the shared `eli5` skill after all code units are integrated and the committed range passes. Every explanation targets a curious developer and explicitly teaches what changed, how it works, and why the implementation and design choices exist. A more specific requested audience changes emphasis, not those three required layers. The skill derives claims from implementation, tests, live documentation, contracts, and verification evidence; writes story JSON under `.agent-state/eli5/`; and uses its bundled `render_explainer.py` plus local HTML template to emit a single dependency-free file.

The default ignored output avoids making the repository dirty after the final gate. A user-requested versioned output belongs in the affected documentation commit and must pass the normal documentation and range gates. Blocked or incomplete development does not produce a misleading completion deck. A renderer or validation failure means the successful development handoff is not complete.

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

`config/models.json` schema version 2 provides named profiles. Each profile defines platform-specific `{model, reasoning}` specifications for:

- workflow coordinators: `dev`, `review_pr`;
- reusable specialist roles: `normal`, `deep`, `fast`, `top`.

`model` may be `null` only for Pi, where it means inherit the current session/default model. `reasoning` is translated to Copilot CLI `reasoningEffort`, Claude Code `effort`, or Pi `thinking`.

```text
configure-models.py --list-profiles
configure-models.py --show [--profile NAME]
configure-models.py --profile NAME
configure-models.py --check [--profile NAME]
```

Without `--profile`, commands resolve `active_profile`. Applying `--profile NAME` synchronizes adapter frontmatter, persists the selection, and regenerates `docs/REFERENCE.md`. With `--check`, selection is non-mutating and exits nonzero when adapter files do not match that profile.

Installed Pi child API:

```text
parallel-pi.py --workflow {dev|review_pr} [--profile NAME] [--model-config PATH]
```

Each JSON task accepts `role`, `model`, and `thinking`. `role` defaults to `fast`; profile values supply missing runtime fields, and explicit task fields win. Pi's main coordinator remains controlled by the active Pi session because prompt files cannot switch the running session model.

The Pi helper resolves project `.wysiwyship/config/models.json` first and global `~/.wysiwyship/config/models.json` second. `--model-config` overrides both locations.

### Model experiment evidence

`.wysiwyship/tools/experiments.py` stores append-only JSONL records under `.agent-state/model-experiments.jsonl` by default. A record identifies workflow, semantic role, platform, profile, resolved model, and reasoning strength. It can also carry duration, reported tokens/cost, verification outcome, complexity before/after, review defects, and rework. Unreported provider telemetry stays `null`, and comparison output includes the observed sample count for every metric.

```text
experiments.py record --workflow dev --role normal --platform claude_code --profile quality --status pass --verification pass
experiments.py run --workflow dev --role fast --platform pi --profile economy -- <command>
experiments.py import-pi <parallel-pi-results.json> --workflow dev --profile economy
experiments.py compare --group-by profile [--format json]
```

`run` measures an external command without a shell and propagates its exit status. A zero exit records successful execution, but verification remains `unknown` unless explicitly supplied because command success alone does not prove the implementation contract.

## Installer API

```text
install.sh {copilot|claude|pi|both|all} <project> [--dry-run|--status]
install-global.sh {copilot|claude|pi|both|all} [--dry-run|--status]
```

The thin shell entry points share one Python implementation. It preflights before mutation, atomically writes settings, rolls back touched paths on failure, preserves unrelated customizations, records checksums in an install manifest, and supports dry-run/status inspection.

## Native package build API

```text
build_packages.py
build_packages.py --check
```

The builder regenerates `packages/copilot` and `packages/claude` only from canonical sources and the active model profile. Copilot uses a root `plugin.json`; Claude uses `.claude-plugin/plugin.json` plus the repository marketplace catalog. `--check` builds into a temporary directory and fails on missing, unexpected, or changed generated files.
