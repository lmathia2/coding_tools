# Changelog

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
