# WYSIWYShip

*What you spec is what you ship.*

**Plan it. Prove it. Just ship.**

[`wysiwyship/`](wysiwyship/README.md) is a self-contained engineering workflow for Codex, VS Code/GitHub Copilot, Claude Code, and Pi.

The daily interface is deliberately small:

- `Dev` / `/dev` — grill and lock the plan, then implement, document, simplify, and verify with minimal interruption;
- `ReviewPR` / `/review-pr` — isolated execution-based PR review.

The current harness starts every development request with an evidence-first planning grill. Interactive mode may ask several focused questions before one explicit plan lock; prefixing the task with `auto` makes the coordinator ask and answer the same questions itself. Once locked, it executes rapidly with almost no human input unless evidence invalidates a key decision or new authority is required.

The locked plan is decomposed into coherent commit-sized units. Every unit runs `plan -> implement -> document -> simplify -> verify`, keeps live documentation with the code commit, measures changed-code complexity, and uses additional models only when independence, uncertainty, or risk makes them valuable.

No external skill pack, plugin, MCP server, package, or repository is installed by the harness.
