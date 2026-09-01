# Workflow Contracts

## Product objective

WYSIWYShip provides one clear, low-interruption workflow that makes coding
quality enforceable across supported harnesses while minimizing model spend.

> **Quality is the constraint; efficiency is the optimization.**

The optimization order is normative: (1) satisfy the locked acceptance criteria,
safety boundaries, and repository contracts; (2) complete the required
`plan -> implement -> document -> simplify -> verify` evidence; (3) leave a
clear developer handoff; then (4) minimize code, files, process, loaded context,
model/reasoning spend, and output tokens. A lower token count never justifies an
ambiguous decision, weaker implementation, missing documentation, skipped gate,
or compressed safety/authorization message.

The quality guarantee is procedural and evidence-based, not a claim that defects
are impossible: a workflow run cannot report success until its locked criteria
and required gates pass. Missing or unobservable evidence stays explicit.

## Dev / `/dev`

### Function

Complete a coding task from plan through implementation, affected documentation, and executable verification.

### Intent

One dependable entry point with model and workflow selection hidden from the user.

### Contract

1. Before decomposition or source edits, run an evidence-first planning grill that resolves Goals, Acceptance, Boundaries, Alternatives, Assumptions, and relevant constraints/failure behavior.
2. In default interactive mode, ask high-value questions with recommendations and tradeoffs until the user locks the plan. When the first task argument is exactly `auto` or `--auto`, pose and answer the same questions internally, record the evidence/assumptions, and lock without routine user input.
3. Record planning mode, iterations, gate, key decisions, in/out scope, assumptions, open questions, ambiguity assessment, and plan lock. Accepted upstream specifications use `imported` mode.
4. Decompose the locked plan into coherent, independently committable units with dependencies, ownership, acceptance criteria, documentation impact, complexity scope, and verification.
5. Run `plan -> implement -> document -> simplify -> verify` for every implementation unit.
6. After lock, execute rapidly and autonomously. Reopen only the invalidated decision if evidence breaks a material assumption/criterion, scope or contracts must expand, consequences materially change, or new authority is required; append the decision, increment iterations, relock, and resume.
7. Use repository evidence to resolve ownership, callers/contracts, tests, and documentation impact.
8. Resolve and lock the cheapest capable route, actually invoke its named agent, and check its receipt; justify inline exceptions and disclose unverified effective settings.
9. Parallelize independent units only when it improves latency or reduces anchoring/uncertainty; parallel writers use isolated worktrees and disjoint ownership.
10. Update live authoritative documentation in the same logical commit, including implementation, APIs/contracts, purpose, intent, and invariants; otherwise record `Docs-Impact: none — <reason>`.
11. Measure changed-function cyclomatic complexity against the unit start ref when feasible, simplify coherently, and explain scores above 10 or material increases.
12. Execute proportional behavior/unit/integration/runtime/static/docs checks.
13. Escalate to another premium perspective only for material uncertainty or high risk.
14. After the committed-range gate passes, invoke `eli5`, render and check the visual explainer, and report its audience and path.
15. Report exact evidence and residual risk.

### Portable policy and native executor contract

This separation is a normative design constraint for every adapter and future
implementation:

> **WYSIWYShip policy is portable; execution is native to the host.**

The portable layer owns the planning grill/lock, work-unit and dependency
semantics, lifecycle order, documentation contract, simplicity evidence,
verification gate, routing meaning, receipts, and ELI5 handoff. It must not grow
a second-rate generic implementation of a host's agent loop, planning sandbox,
parallel scheduler, permission system, model router, or telemetry service.

The adapter/executor layer owns the concrete invocation of native capabilities:

```text
plan | run-to-completion | dispatch | parallelize | isolate/sandbox
permissions | bounds/cancel | observe
```

For each required capability, an implementation MUST:

1. invoke the strongest safe native mechanism supported by the active host;
2. keep policy, planning-answer mode, execution mode, permissions, and model
   selection as separate decisions;
3. preserve the locked work-unit contracts and lifecycle across native agents;
4. record the mechanism requested and host evidence actually observed;
5. label unavailable, partial, fallback, and unobservable behavior explicitly;
6. never infer execution, isolation, continuation, parallelism, model identity,
   or usage from an instruction/configuration alone; and
7. block the affected lane when no safe accepted fallback satisfies the contract.

`interactive | auto | imported` describes how planning answers are resolved.
`interactive | native-autonomous | bounded-fallback` describes execution. These
axes are not aliases: auto planning cannot silently approve an implementation
plan, enable an Autopilot mode, grant tools, bypass a sandbox, or broaden scope.
Similarly, native autonomous execution does not waive the planning record,
documentation, simplification, verification, or completion evidence.

Parallel host features may execute only work units already proven independent,
with explicit dependencies, exclusive ownership and suitable workspace isolation.
A host-selected generic fleet is not allowed to silently redefine the locked
decomposition. Outer-session and custom-agent model precedence must be accounted
for; host fallback keeps effective settings `UNVERIFIED` until reliable runtime
metadata confirms them.

The required fallback order is: native capability; explicitly accepted bounded
adapter fallback with its limitation recorded; otherwise blocked. A future host
joins by implementing this capability mapping, not by changing the portable SDLC
policy. See the canonical
[`routing.md`](../shared/skills/engineering-workflow/references/routing.md).

### Minimum sufficient change

After tracing the affected flow and callers, implementation MUST stop at the
first sufficient rung: **no code -> repository reuse -> standard library -> native platform -> installed dependency -> direct expression -> minimum new code**.
“Sufficient” means the complete locked acceptance, edge-case, safety,
compatibility, and operational contract—not the fewest lines in isolation.

Bug fixes prefer the shared causal point over repeated symptom patches. New
abstractions, dependencies, configuration, fallbacks, compatibility layers, and
boilerplate require an accepted requirement or evidenced risk. Known design
ceilings record the current limit, why it is acceptable, and the measurable
upgrade trigger rather than adding speculative extension points. Scope growth
triggers a smaller design or planning re-entry, not further scaffolding.

The simplification phase and PR semantic lane apply the same ladder backward to
the diff, looking for deletion, reuse, standard-library/native replacement, and
unjustified layers. They must not game line count, fragment cohesive code, or
remove trust-boundary validation, data-loss handling, security/privacy/
authorization, accessibility, compatibility/migration/recovery, necessary
hardware calibration, live documentation, or risk-proportional verification.
Existing tests come first; additions close specific acceptance, regression, or
risk gaps without arbitrary count or size limits.

This is a curated adaptation, not an embedded Ponytail runtime. WYSIWYShip does
not adopt the persona, intensity/session modes, lifecycle hooks, branded source
comments, fixed one-check ceiling, or code-first output restriction. The locked
plan controls scope, risk controls verification depth, and the documentation and
ELI5 contracts control explanation. Those higher-priority guarantees cannot be
disabled by a minimality setting.

### Planning grill, lock, and re-entry

The grill belongs inside the `plan` stage rather than becoming another required top-level workflow. This keeps `Dev` / `/dev` as the single implementation entry point while making requirements discovery unavoidable.

Interactive planning may use several rounds. Questions are ordered by their ability to prevent rework, asked only after repository facts have been inspected, and include a recommended answer plus downstream tradeoff. The user gets one final plan-lock checkpoint. `enough` or `good enough` may end the interview, but the resulting gate is recorded as `user-override` with remaining ambiguity visible.

`auto` is an answer mode, not a shortcut. The coordinator writes down each material question and its self-selected answer, preferring repository evidence, accepted project conventions, and the smallest reversible interpretation. It labels assumptions and cannot grant itself new authority for destructive/external actions or material scope expansion.

Once locked, ordinary implementation decisions, test failures, refactors, model routing, and local integration are handled without further questions. A genuine plan-breaking event reopens only the affected decision; the coordinator does not restart the entire interview.

### Deterministic lifecycle gate

The installed gate evaluates the committed range as one machine-readable contract:

```text
python3 .wysiwyship/tools/check.py <unit-start-ref> --head HEAD
```

It checks documentation evidence in every code commit, scores only Python functions intersecting changed lines, and runs the explicit argument-array commands in `.wysiwyship/config/checks.json`. A project can add unit, integration, build, type, lint, generated-artifact, or documentation commands without embedding shell evaluation in the harness. `--format json` provides CI/host automation output; `--require-clean` adds a repository-cleanliness assertion when appropriate.

Exit status `0` means all checks passed, `1` means a check failed, and `2` means configuration or gate execution was invalid. The default installed configuration has documentation and complexity checks enabled and leaves project-specific commands empty.

### Resumable work-unit state and hooks

The optional ledger is for complex, long, parallel, or handoff-prone tasks; routine fixes need no ledger. `work_units.py init` resolves the unit's base ref to an immutable commit and stores the locked planning mode/gate/iterations/decisions/scope/assumptions, acceptance criteria, dependencies, owners/owned paths, documentation impact, source artifact, and lifecycle evidence under ignored `.agent-state/work-units/`. Schema-v2 records require at least one key decision; existing schema-v1 state remains readable. `advance` accepts evidence only in `plan -> implement -> document -> simplify -> verify` order. Dependencies must complete and active ownership cannot overlap before implementation starts.

```text
work_units.py init ID --title TITLE --goal GOAL --acceptance CRITERION --owns PATH --base-ref REF --planning-mode interactive --planning-gate pass --decision "D1: resolution" --in-scope SCOPE --out-of-scope BOUNDARY --docs-impact required --doc-path PATH --activate
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
collaborative planning grill + plan lock + autonomous coordinator/implementation + deterministic verification
```

Fast models perform read-only exploration, measurement, and verification. Implementation stays in the normal or deep writing context. Deep/top models are exceptional paths.

### Product behavior specification

The full `product-behavior-spec` workflow runs only when explicitly requested. Existing behavior specs are maintained like other authoritative docs when a code change affects them.

### Project ELI5 completion handoff

Every successful `Dev` / `/dev` run invokes the shared `eli5` skill after all code units are integrated and the committed range passes. ELI5 means the simplest accurate developer mental model, not a product pitch or release-summary deck. Every explanation covers purpose, exact first use and expected behavior, core concepts, connected source architecture, one representative flow through named files/symbols/contracts, design rationale, proof, and limitations. A more specific audience changes emphasis without removing those layers.

The skill derives claims from implementation, tests, live documentation, contracts, configuration, and verification evidence. Its story schema requires a connected architecture or execution flow plus at least three visible evidence anchors such as source paths, symbols, commands, configuration keys, schemas, and tests. It writes story JSON under `.agent-state/eli5/` and uses its bundled `render_explainer.py` plus local HTML template to emit a single dependency-free file.

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

Each review lane uses the dispatch/evidence API below, including independent challenges. A coordinator-only pass is not an independent specialist review. Keep route IDs and evidence distinct across lanes, and validate every completed receipt before publishing the recommendation.

## Dispatch and evidence API

The shared [dispatch reference](../shared/skills/engineering-workflow/references/routing.md) owns the host-specific invocation instructions. `tools/routing.py` provides the same schema and checks for Codex, Claude Code, Copilot, and Pi:

```text
routing.py plan --host {codex|claude|copilot|pi} --workflow {dev|review_pr} --role {normal|deep|fast|top} --task ID
                [--execution inline --reason TEXT] [--profile NAME] [--config PATH]
                [--agent NAME] [--namespace NAME] [--require-confirmed]
routing.py check --plan route.json --receipt receipt.json [--started]
work_units.py init ID ... --routing-plan route.json
work_units.py route ID --routing-plan route.json --reason "accepted routing decision"
work_units.py advance ID --evidence TEXT [--routing-receipt receipt.json]
check.py BASE --head HEAD --routing-plan route.json --routing-receipt receipt.json
```

`plan` emits schema-v1 JSON containing a unique `route_id`, task, host, workflow, role, execution mode, agent, profile, configured/requested settings, reason, and confirmation policy. It does not call a model. Model IDs come from the active profile; an inline route explicitly requests no switch and requires a reason. Native-plugin Claude helpers add their agent namespace automatically. The host-loaded adapter must agree with the resolved profile; config edits alone do not reload a running host.

Receipts bind to that route ID, agent, and requested settings, and require an invocation ID, evidence reference, source (`report`, `launcher`, `host`), and status (`started`, `completed`, `failed`). Optional `observed` settings must come from host metadata, not a prompt, argv, or worker self-report. Each retry/fallback route has a new ID and must be accepted before use; the original failed attempt remains evidence. Routing changes never grant new permissions.

`check` exits 1 for mismatches/missing/failed invocations, 2 for malformed input/files, and 0 for consistent receipts. Its `status: PASS` is receipt consistency, not model confirmation: `model_status` separately reports `UNVERIFIED`, `CONFIRMED`, or `MISMATCH`. Missing metadata is allowed but visible by default; `--require-confirmed` makes it fail completion. Use exact model IDs for this policy; the checker does not guess alias resolution. Host-labelled JSON is still editable evidence, not an authenticated attestation.

For ledger units with `routing`, leaving plan requires a started or completed invocation; leaving verify requires completed evidence. The composed gate and active-unit hooks also validate stored receipts. Legacy units without routing remain readable; new dispatched workflows attach a route or, for small units/imported plans/PR lanes without routing-enabled ledgers, explicitly run the standalone check. This is not a global source-write interceptor, and no-commit work must still report the committed-range gate as `NOT EXECUTED`.

`work_units.py route` attaches routing to imported units or records an accepted routing-only change without discarding lifecycle work. Replacements require a new route ID; `routing_history` retains the previous plan/receipt and reason. The new route has no invocation receipt until dispatched. Completed units cannot be rerouted, and recording a reason does not grant permission for a fallback.

Pi tasks can include the full plan in `routing`. A mismatched task name/role/model/thinking/agent rejects the batch before any child launches. Each result includes a `routing_receipt` generated from the subprocess outcome; it proves which arguments were requested, not which model answered. Failed/timed-out calls cannot pass completion. Explicit task overrides must agree with the locked route; otherwise create and accept a new route before launching.

The Pi CLI also rejects a mismatched workflow and confirmation-required routes before launch: print mode does not expose effective model/effort metadata to this helper. Other hosts must check metadata availability before accepting that stricter policy.

## Model configuration API

`config/models.json` schema version 2 provides named profiles. Each profile defines platform-specific `{model, reasoning}` specifications for:

- workflow coordinators: `dev`, `review_pr`;
- reusable specialist roles: `normal`, `deep`, `fast`, `top`.

`model` may be `null` for any platform and means inherit the current session/default model. `reasoning` is translated to Codex `model_reasoning_effort`, Copilot CLI `reasoningEffort`, Claude Code `effort`, or Pi `thinking`.

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

Each JSON task accepts `role`, `model`, `thinking`, and optional `routing`. `role` defaults to `fast`; profile values supply missing runtime fields, and explicit task fields win only when they agree with an attached locked route. Pi's main coordinator remains controlled by the active Pi session because prompt files cannot switch the running session model. A child with `model: null` uses its own host default, not the parent's interactive selection.

The Pi helper resolves project `.wysiwyship/config/models.json` first and global `~/.wysiwyship/config/models.json` second. `--model-config` overrides both locations.

### Model experiment evidence

`.wysiwyship/tools/experiments.py` stores append-only JSONL records under `.agent-state/model-experiments.jsonl` by default. A record identifies workflow, semantic role, platform, profile, resolved model, and reasoning strength. It can also carry duration, reported tokens/cost, verification outcome, complexity before/after, review defects, and rework. Unreported provider telemetry stays `null`, and comparison output includes the observed sample count for every metric.

Model/reasoning labels and grouping are requested/configured settings, not confirmed answering-model identity. New records and comparisons explicitly label that attribution. Pi imports retain the launcher receipt for inspection without promoting argv to host-observed telemetry.

```text
experiments.py record --workflow dev --role normal --platform claude_code --profile quality --status pass --verification pass
experiments.py record --workflow dev --role deep --platform codex --profile detected --status pass --verification pass
experiments.py run --workflow dev --role fast --platform pi --profile economy -- <command>
experiments.py import-pi <parallel-pi-results.json> --workflow dev --profile economy
experiments.py compare --group-by profile [--format json]
```

`run` measures an external command without a shell and propagates its exit status. A zero exit records successful execution, but verification remains `unknown` unless explicitly supplied because command success alone does not prove the implementation contract.

## Installer API

```text
install.sh {codex|copilot|claude|pi|both|all} <project> [--dry-run|--status|--no-model-discovery]
install-global.sh {codex|copilot|claude|pi|both|all} [--dry-run|--status|--no-model-discovery]
```

The thin shell entry points share one Python implementation. It preflights before mutation, atomically writes settings, rolls back touched paths on failure, preserves unrelated customizations, records checksums in an install manifest, and supports dry-run/status inspection.

Unless disabled, preflight also scans local host capabilities and creates an installed `detected` model profile. Codex `model/list` is authoritative for the signed-in Codex catalog and supported reasoning levels; installed custom specialists use those routes while the workflow coordinator inherits the active Codex session because a skill cannot replace its parent model. Claude Code `availableModels` settings are treated as explicit restrictions. Copilot/VS Code presence can be detected, but its effective signed-in model picker is not exposed through a supported non-interactive API, so those routes inherit the active session. No paid inference probe is run. The human-readable report and `.wysiwyship/model-discovery.json` identify host/version, evidence class, models, selected routes, fallbacks, and limitations.

## Native package build API

```text
build_packages.py
build_packages.py --check
```

The builder regenerates `packages/copilot` and `packages/claude` only from canonical sources and the active model profile. Copilot uses a root `plugin.json`; Claude uses `.claude-plugin/plugin.json` plus the repository marketplace catalog. `--check` builds into a temporary directory and fails on missing, unexpected, or changed generated files.
