# Optional Methodology Integrations

Smart Harness keeps its default interface small. Superpowers and Ponytail are included as **tracked, optional integrations**, not silently activated defaults.

## Why optional

Superpowers is a complete development methodology with its own planning, TDD, worktree, subagent, and review lifecycle. Ponytail is an always-on minimality/YAGNI discipline. Both are useful, but automatic activation can duplicate or override Smart Harness orchestration.

Smart Harness invariants always win:

- plan before source edits;
- documentation is part of execution;
- do not simplify away tests, validation, security, accessibility, compatibility, failure handling, migration/rollback, or explicit requirements;
- PR review runs executable unit/integration/static/documentation checks in an isolated worktree.

## Curated skill-only installation

Install a reviewed subset of upstream skills into the same shared skill directory used by Copilot, Claude Code, and Pi:

```bash
bash smart-harness/integrations/install-methodologies.sh project /path/to/project
```

Or globally:

```bash
bash smart-harness/integrations/install-methodologies.sh global
```

The curated install includes:

### Superpowers

- brainstorming
- writing-plans
- executing-plans
- dispatching-parallel-agents
- systematic-debugging
- test-driven-development
- verification-before-completion
- using-git-worktrees
- requesting-code-review
- receiving-code-review
- finishing-a-development-branch
- subagent-driven-development

It intentionally omits the `using-superpowers` bootstrap because that bootstrap mandates a Superpowers skill check before every response and would replace the simple Dev/ReviewPR interface.

### Ponytail

- ponytail
- ponytail-review
- ponytail-audit

Ponytail remains opt-in. Its minimality policy cannot weaken `documentation-sync` or other safety/quality gates.

## Full native plugins

Use the full upstream packages when you deliberately want their entire lifecycle, hooks, commands, and update behavior.

### Claude Code

```text
/plugin install superpowers@claude-plugins-official
/plugin marketplace add DietrichGebert/ponytail
/plugin install ponytail@ponytail
```

### Pi

```bash
bash smart-harness/pi/install-extensions.sh methodology
```

### GitHub Copilot CLI

```bash
copilot plugin marketplace add obra/superpowers-marketplace
copilot plugin install superpowers@superpowers-marketplace
copilot plugin marketplace add DietrichGebert/ponytail
copilot plugin install ponytail@ponytail
```

For VS Code Copilot, use **Chat: Install Plugin From Source** if enterprise policy allows Agent Plugins, or use the curated shared-skill installation above.

## Updates

Pinned upstream commits live in `upstreams.lock.json`.

A scheduled workflow checks for upstream changes and opens a reviewable PR updating the lock and generated reference. Re-run the methodology installer after accepting an upstream update.

Third-party skills/extensions execute instructions or code with developer permissions. Review upstream changes before updating.
