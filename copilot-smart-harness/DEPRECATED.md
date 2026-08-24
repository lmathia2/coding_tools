# Compatibility snapshot

This folder is retained as the Copilot v0.4.0 snapshot.

The canonical, shared implementation is now [`../smart-harness/`](../smart-harness/README.md), which shares skills with Claude Code and adds mandatory plan-first behavior, parallel independent work, and execution-based PR review in isolated worktrees.

Use:

```bash
bash smart-harness/install.sh copilot /path/to/project
# or
bash smart-harness/install.sh both /path/to/project
```
