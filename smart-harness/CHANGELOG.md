# Changelog

## 0.6.0 — Outside-in product behavior specifications

- Added the self-contained `product-behavior-spec` skill for feature-by-feature, user-visible behavior documentation grounded in code, tests, and running-product verification.
- Added original local templates for scope/coverage, goal state, glossary, feature lifecycle, verification checklists, defect triage, product-shape mapping, and Markdown link validation.
- Integrated behavior-spec creation and maintenance into the existing `Dev`/`/dev` workflow without adding another command.
- Integrated stale behavior-spec detection and checklist execution into Copilot, Claude Code, Pi, and GitHub-native PR review.
- Extended `documentation-sync` so existing behavior documents, source commits, glossary, coverage, verification, and triage remain synchronized with code changes.
- Recorded conceptual inspiration from Steve Ruiz's public product-description gist. Because no explicit license was visible, the local implementation was written independently instead of copying gist files.

## 0.5.0 — Self-contained distribution

- Removed runtime installers and scheduled synchronization for external skill/plugin repositories.
- Vendored the selected Superpowers methodology, Ponytail, Ponytail review, and Pi VS Code skill directly under `shared/skills/`.
- Added source provenance and full MIT license notices under `vendor/`.
- Replaced Pi extension dependencies with a bundled standard-library parallel Pi runner.
- Updated Copilot, Claude Code, and Pi workflows to use the vendored methodology/minimality skills while preserving documentation, testing, security, and compatibility requirements.
- Added CI gates that reject external clone/install commands in the runtime harness and validate vendored notices, generated reference docs, model routing, shell syntax, and installation smoke tests.

## 0.4.0 — Unified documentation-first harness

- Unified Copilot, Claude Code, and Pi around one shared skill library.
- Added mandatory plan-first, documentation-sync, safe parallelism, execution-based PR review, model routing, worktree isolation, generated reference documentation, and validation workflows.
