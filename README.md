# Coding Tools

Reusable coding-agent tools and orchestration configurations.

## Smart Harness

[`smart-harness/`](smart-harness/README.md) is the single canonical implementation for:

- VS Code / GitHub Copilot
- Claude Code
- Pi

It is self-contained: all required agents, prompts, shared skills, selected Superpowers/Ponytail/Pi-derived skills, scripts, templates, licenses, and documentation are stored in this repository. Runtime use does not clone another repository, install a plugin, install an MCP server, or download a skill pack.

The user-facing interface stays small:

- `Dev` / `/dev` — plan, implement, document, and verify
- `ReviewPR` / `/review-pr` — isolated, execution-based PR review

The host product itself and the target repository's normal build/test dependencies are still required.
