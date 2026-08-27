# Changelog

## Unreleased

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
