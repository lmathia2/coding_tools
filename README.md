# coding_tools

Various coding tools, skills, and agent configurations.

## Smart Harness

The canonical multi-harness setup is now:

**[`smart-harness/`](./smart-harness/README.md)**

It provides one shared engineering policy/skill layer with platform-specific orchestration for:

- VS Code + GitHub Copilot
- Claude Code

Install both into a project with:

```bash
bash smart-harness/install.sh both /path/to/project
```

Daily interface:

- Copilot: `Dev` / `ReviewPR`
- Claude Code: `/dev` / `/review-pr`

The older `copilot-smart-harness/` and `claude-code-smart-harness/` folders are retained as compatibility snapshots; new work should use `smart-harness/`.
