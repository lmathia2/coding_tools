# Changelog

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
