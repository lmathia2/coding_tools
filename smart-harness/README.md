# Smart Harness

One self-contained engineering harness for VS Code/GitHub Copilot, Claude Code, and Pi.

## Daily interface

| Product | Development | PR review |
|---|---|---|
| Copilot | `Dev` | `ReviewPR` |
| Claude Code | `/dev` | `/review-pr` |
| Pi | `/dev` | `/review-pr` |

Everything else is hidden orchestration.

## Self-contained guarantee

All required agents, commands, prompts, skills, selected third-party-derived methodology text, Pi helper scripts, templates, licenses, validation, and documentation are checked into this repository.

Runtime setup performs **no**:

- Git clone/pull of another repository;
- skill/plugin/marketplace installation;
- Pi/npm/pip package installation;
- MCP server setup;
- curl/wget download;
- scheduled upstream replacement.

You still need the host you intend to use—VS Code/GitHub Copilot, Claude Code, or Pi—and the target project's normal build/test dependencies.

## Install from this checkout

```bash
# All three adapters into a project
bash smart-harness/install.sh all /path/to/project

# Or one/two adapters
bash smart-harness/install.sh copilot /path/to/project
bash smart-harness/install.sh claude /path/to/project
bash smart-harness/install.sh pi /path/to/project
bash smart-harness/install.sh both /path/to/project   # Copilot + Claude
```

Global personal defaults:

```bash
bash smart-harness/install-global.sh all
```

Re-running an installer synchronizes local files and backs up replaced harness paths.

## Shared skills

One canonical library under `shared/skills/` is installed to `.claude/skills/` (or `~/.claude/skills/`). Current Copilot and Claude Code discover it directly; Pi settings reference the same location.

Core policies include plan-first, parallel-work, engineering-core, documentation-sync, codebase-map/context-snapshot, task-ledger, and worktree-based PR review.

Vendored/adapted dependency-free skills include:

- `superpowers-methodology`
- `superpowers-skill-authoring`
- `ponytail`
- `ponytail-review`
- `vscode`

Provenance and MIT licenses are under [`vendor/`](vendor/THIRD_PARTY_NOTICES.md).

## Development defaults

Every task:

1. plans before editing;
2. assesses documentation impact;
3. parallelizes independent evidence/hypotheses;
4. uses the smallest correct implementation;
5. updates code, tests, and required documentation together;
6. runs executable verification before completion.

Non-trivial tasks use the vendored Superpowers methodology. Ponytail minimizes implementation only after the full flow is understood and cannot override documentation, tests, security, accessibility, compatibility, migration, data safety, or explicit requirements.

## PR review defaults

Review runs at the exact committed PR HEAD in an isolated worktree. Static reasoning, full feasible unit/integration suites, e2e/runtime checks, build/type/lint/static analysis, documentation checks, complexity review, adversarial behavior, and security/resilience lanes run in parallel where safe. Serious findings are independently challenged before publication.

## Pi parallelism without extensions

The bundled `.pi/tools/parallel-pi.py` uses Pi print-mode children to run independent bounded tasks concurrently. It requires no third-party Pi extension or npm dependency.

## Models

Edit one file:

```text
smart-harness/config/models.json
```

Then apply/check:

```bash
python3 smart-harness/config/configure-models.py
python3 smart-harness/config/configure-models.py --check
```

## Documentation and validation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/WORKFLOW_CONTRACTS.md`](docs/WORKFLOW_CONTRACTS.md)
- [`docs/DOCUMENTATION_POLICY.md`](docs/DOCUMENTATION_POLICY.md)
- [`docs/SELF_CONTAINED.md`](docs/SELF_CONTAINED.md)
- [`docs/VENDORED_COMPONENTS.md`](docs/VENDORED_COMPONENTS.md)
- [`docs/REFERENCE.md`](docs/REFERENCE.md) — generated

CI verifies model/config drift, generated docs, skill frontmatter, provenance/licenses, local links, workflow invariants, forbidden runtime external-install patterns, shell/Python syntax, and an all-platform local installation smoke test.
