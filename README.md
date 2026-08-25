# Coding Tools

Reusable coding-agent tools and orchestration configurations.

## Smart Harness

[`smart-harness/`](smart-harness/README.md) is the single self-contained harness for VS Code/GitHub Copilot, Claude Code, and Pi.

The daily interface is deliberately small:

- `Dev` / `/dev` — plan, implement, document, and verify;
- `ReviewPR` / `/review-pr` — isolated execution-based PR review.

v0.7 consolidates overlapping policies and agents around a simple default: one coordinator, one implementation context, deterministic verification; additional models run only when uncertainty or risk makes an independent perspective valuable.

No external skill pack, plugin, MCP server, package, or repository is installed by the harness.
