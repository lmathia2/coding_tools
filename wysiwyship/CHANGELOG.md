# Changelog

## Unreleased

- Added a self-contained, default-on developer wiki inspired by OpenWiki: four
  starter pages, safe local paths, structural validation, and a full refresh
  every five commits by default (`1` for every commit). Generated wiki pages
  remain derived and cannot satisfy authoritative per-commit documentation;
  no OpenWiki runtime, provider, Node dependency, connector, telemetry, CDN, or
  graph viewer is required.
- Applied a whole-repository minimum-sufficient audit: removed the claim/hash
  reconciliation protocol, experiment logger, accepted-spec bridge, duplicated
  adapter policy, and prose-substring validation. External planning artifacts
  are read directly, model comparisons use the existing evaluation runner, and
  only the four runtime skills are packaged; contributor helpers stay in source.

- Reduced the Ponytail adaptation to four lightweight rules: source priority,
  dependency discipline, protected safety/data-loss guardrails, and annotated
  design ceilings with upgrade triggers. Deletion-first review, line-count
  optimization, persona/intensity modes, hooks, and output restrictions remain
  excluded; no Ponytail runtime is required.
- Made the product objective normative: enforce quality through locked criteria
  and executable SDLC evidence, then minimize implementation surface, context,
  model/reasoning spend and output tokens without weakening clarity or safety.
- Kept Caveman native-policy integration as follow-up work, with no external
  runtime dependency and no Caveman BSL proxy/engine vendoring.

- Specified the normative portable-policy/native-executor boundary: WYSIWYShip
  owns lifecycle and evidence while each adapter invokes real host planning,
  continuation, dispatch, isolation, permission, cancellation and observation
  capabilities. Planning-answer and execution modes are explicitly independent;
  missing capabilities degrade visibly or block rather than being imitated.

- Added root `TODOS.md` tracking pilot calibration, the remaining evaluation
  tasks, real-host validation, and known maintenance gaps.

- Added an offline engineering-evaluation pilot suite: durable jobs and tenant
  isolation, with working starter projects, separate reference overlays and
  acceptance tests, and a standard-library runner. The ten-task catalog labels
  eight follow-on tasks as planned pending measured difficulty calibration.
- Added explicit baseline/workflow preparation, bounded opt-in Codex execution,
  authoritative regression/acceptance grading, and evidence-oriented comparisons;
  model runs and claimed workflow improvements remain unverified until calibration.

- Added a cross-host dispatch/evidence contract for development and PR lanes: resolved named agents, explicit inline/fallback decisions, invocation receipts, and separately reported effective settings. Codex, Claude, Copilot, and Pi adapters now require actual dispatch rather than treating configuration as a model switch.
- Added `routing.py`, optional ledger/range-gate receipt checks, and Pi batch route validation plus launcher-generated receipts. Host metadata gaps remain `UNVERIFIED`; confirmation-required routes fail without matching metadata. Local receipts are consistency evidence, not authenticated runtime enforcement.

- Consolidated a compact minimum-sufficient-change policy into the existing engineering workflow and PR review: evidence-backed structural additions, bounded scope, proportional regression tests, and configured lower-cost routine execution without weakening safety or required verification.

- Reworked the root and product READMEs around developer onboarding: problem, quick start, expected workflow, core concepts, source ownership, and architecture diagrams.
- Tightened the ELI5 skill from a high-level story into a grounded developer walkthrough that must cover purpose, first use, core concepts, connected source architecture, a named under-the-hood flow, rationale, proof, and limitations.
- Added renderer support for ordered architecture/execution flows and visible evidence anchors; validation now requires a flow and at least three inspected paths, symbols, commands, configuration keys, schemas, or tests.

## 0.11.0 — Planning grill and execution lock

- Added first-class Codex installation through `.agents/skills` and `.codex/agents`, with semantic fast/normal/deep/top specialists that use the existing Codex account.
- Added default installer-time model discovery and an explicit setup report: Codex uses account-visible `model/list` capabilities, Claude Code honors configured model restrictions, Copilot/VS Code safely inherits its session picker, and `--no-model-discovery` retains a static/offline path.
- Made every ELI5 explanation target a curious developer and explicitly teach what changed, how the implementation works, and why the design choices exist; requested audience variants now adjust emphasis without dropping those layers.
- Added an evidence-first planning grill inside every `Dev` / `/dev` plan stage, covering goals, acceptance, boundaries, alternatives, assumptions, and relevant constraints before work-unit decomposition.
- Added interactive multi-round planning with recommendations/tradeoffs and one explicit plan lock, plus `auto` / `--auto` mode that poses and answers the same questions from repository evidence and reversible assumptions.
- Made post-lock execution deliberately rapid and low-interruption; planning reopens only for an invalidated material decision, necessary scope/contract expansion, materially changed consequences, or new authority.
- Added schema-v2 work-unit planning records for mode, iterations, gate, key decisions, in/out scope, assumptions, open questions, ambiguity assessment, and lock timestamp while retaining schema-v1 compatibility.

## 0.10.0 — WYSIWYShip

- Renamed the product, source directory, native plugin ID, Claude namespace, installed support directory, hooks, and CI workflow to **WYSIWYShip**: *What you spec is what you ship.*
- Added transactional migration of project and global installations from the previous product paths, including removal of the obsolete Claude stop hook while preserving unrelated hooks.
- Kept the existing `lmathia2/coding_tools` repository URL and documented the upgrade path for installer and native-plugin users.

## 0.9.0 — Visual project explanations

- Added a self-contained `eli5` skill that reads verified code, tests, live documentation, contracts, and completion evidence; calibrates its explanation to the audience; and preserves honest limitations.
- Added a Python-standard-library renderer and bundled visual template that produce one offline 1920×1080 HTML explainer with editorial layouts, diagrams/cards/metrics, keyboard/touch navigation, print support, and reduced-motion behavior.
- Made the ELI5 visual handoff mandatory after the committed-range gate passes in every successful Copilot, Claude Code, and Pi development workflow, while keeping blocked/incomplete work from being presented as done.
- Vendored pinned MIT provenance and licenses for `dreambigou/eli5` and `zarazhangrui/frontend-slides`; no upstream repository, package manager, CDN, hosted font, or runtime network request is required.

## 0.8.0 — Evidence and interoperability release

- Added reproducible native Copilot and Claude Code plugin bundles plus a Claude marketplace catalog; retained the project/global installer as the cross-host and Pi baseline.
- Added a read-only-preview/explicit-import bridge from accepted Spec Kit, OpenSpec, and BMAD task artifacts into optional WYSIWYShip work units without replacing upstream spec workflows.
- Added an optional resumable work-unit ledger with immutable base refs, dependency/ownership validation, ordered lifecycle evidence, active-unit gates, and no-op-by-default Copilot/Claude stop hooks.
- Added append-only model experiment records and profile/model/role comparisons with honest per-metric sample counts, optional token/cost/quality evidence, command timing, and Pi child-result import.
- Added a deterministic committed-range lifecycle gate for per-commit documentation evidence, changed-function complexity, configured project checks, JSON automation output, and PR CI.
- Added a README getting-started guide covering prerequisites, project-local and global installation, host discovery paths, first use, verification, upgrades, and model-profile deployment.
- Added selectable `balanced`, `economy`, and `quality` model profiles with separately configurable development/review coordinators, specialist models, and canonical reasoning strength translated across Copilot CLI, Claude Code, and Pi.
- Renamed Copilot specialist identities around stable semantic roles so model-profile experiments cannot leave model-branded names or descriptions stale.
- Made `plan -> implement -> document -> simplify -> verify` mandatory for every coherent work unit and added isolated parallel work-unit guidance.
- Added a normal-cost Claude Sonnet work-unit agent so independent commit-sized units can run concurrently without granting write tools to the fast exploration agent.
- Made live authoritative documentation a commit-level contract covering implementation, APIs/contracts, purpose, intent, invariants, and relevant operational behavior.
- Added a dependency-free Python cyclomatic-complexity analyzer with per-function baseline deltas and integrated it into development and PR review.
- Made fast Copilot and Claude specialists read-only, and hardened Pi children with capability allowlists, root confinement, sanitized environments, opt-in auto-approval, and reliable timeout serialization.
- Replaced duplicated installers with one preflighted transactional implementation supporting rollback, atomic settings updates, manifests, dry runs, status checks, and installed provenance notices.
- Expanded CI and validation around adapter role contracts, failure paths, installation idempotency, and runtime helpers.

## 0.7.0 — Simplification release

- Collapsed eleven overlapping process skills into one `engineering-workflow` skill while preserving plan-first execution, evidence-based debugging/TDD, safe parallelism, minimal design, documentation synchronization, and verification.
- Folded Ponytail/minimality review into normal engineering and PR review instead of running a separate review lane.
- Kept `product-behavior-spec` as an explicit specialist capability; normal coding updates existing behavior docs only when affected and never creates a spec automatically.
- Reduced the shared discoverable skill surface from 13 to 5: `engineering-workflow`, `pr-review`, `product-behavior-spec`, `skill-authoring`, and `vscode`.
- Reduced Claude Code hidden agents from 7 to 4: `smart-fast`, `smart-deep-reasoner`, `smart-deep-implementer`, and `smart-top-reviewer`.
- Reduced Copilot hidden agents from 6 to 5 by merging Terra exploration, deterministic verification, and mechanical implementation into `FastTerra`.
- Established the default cost/quality shape as one coordinator + one implementation context + deterministic verification; extra premium agents are conditional on uncertainty or risk.
- Preserved execution-based PR review: exact PR-head worktree, semantic + execution lanes in parallel, complete feasible unit/integration suites, high-risk specialist escalation, and independent serious-finding verification.
- Installers now remove legacy harness-managed skills/agents so upgrading actually shrinks the discovered surface.
- CI now enforces a simplicity budget for core skills and hidden agents.

## 0.6.0 — Outside-in product behavior specifications

- Added the self-contained `product-behavior-spec` specialist skill and integrated maintenance of existing behavior documentation into coding and PR review.

## 0.5.0 — Self-contained distribution

- Vendored selected methodology/minimality capabilities, removed runtime external dependencies, and added self-contained Pi parallel tooling.

## 0.4.0 — Unified documentation-first harness

- Unified Copilot, Claude Code, and Pi around one shared skill library with plan-first execution, safe parallelism, worktree PR review, model routing, documentation synchronization, and validation.
