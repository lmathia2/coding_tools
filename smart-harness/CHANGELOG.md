# Changelog

## 0.5.0 — 2026-08-24

### Added

- Pi adapter with `/dev` and `/review-pr` prompt templates.
- Mandatory `documentation-sync` shared skill.
- Documentation impact planning, same-change docs updates, and documentation verification across every execution workflow.
- Architecture, workflow-contract, documentation-policy, integration, and generated-reference documentation.
- ADR and module README templates.
- Curated Pi extension profiles and Pi skills installer.
- Optional pinned Superpowers and Ponytail integrations.
- Upstream lock checking and scheduled update PR workflow.
- CI validation for workflow invariants, model/config drift, docs links, scripts, and generated reference.

### Changed

- Unified Copilot, Claude Code, and Pi around one shared skill library.
- PR review now explicitly validates docs in the isolated PR-head worktree alongside full feasible unit/integration/static checks.
- Model configuration and generated documentation are centralized.

### Removed

- Superseded standalone Copilot and Claude harness snapshots from the canonical repository layout.
