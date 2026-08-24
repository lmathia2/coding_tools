# Compatibility snapshot

This folder is retained as the original Claude Code v0.1.0 snapshot.

The canonical, shared implementation is now [`../smart-harness/`](../smart-harness/README.md), which shares engineering skills with the Copilot harness and adds mandatory plan-first behavior, parallel independent work, and execution-based PR review in isolated worktrees.

Use:

```bash
bash smart-harness/install.sh claude /path/to/project
# or
bash smart-harness/install.sh both /path/to/project
```
