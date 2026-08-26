# Coding Tools

Reusable coding-agent tools and orchestration configurations.

## Smart Harness

[`smart-harness/`](smart-harness/README.md) is the single self-contained harness for VS Code/GitHub Copilot, Claude Code, and Pi.

The daily interface is deliberately small:

- `Dev` / `/dev` — plan, implement, document, and verify;
- `ReviewPR` / `/review-pr` — isolated execution-based PR review.

The current harness decomposes non-trivial work into coherent commit-sized units. Every implementation unit runs `plan -> implement -> document -> simplify -> verify`, keeps live documentation with the code commit, measures changed-code complexity, and uses additional models only when independence, uncertainty, or risk makes them valuable.

No external skill pack, plugin, MCP server, package, or repository is installed by the harness.
