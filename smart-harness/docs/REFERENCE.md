# Generated Smart Harness Reference

> Generated from repository-local files for version `0.7.0`. Do not edit by hand.

## Simplicity budget

- Shared discoverable skills: **5** (budget: 5)
- Copilot agent definitions: **7** (2 visible + 5 hidden)
- Claude Code hidden agents: **5** (budget: 5)
- Claude Code visible commands: **2** (budget: 2)

## Work-unit lifecycle

Every implementation unit is coherent and independently committable, with explicit dependencies and ownership:

```text
plan -> implement -> document -> simplify -> verify
```

Live authoritative documentation travels in the same logical commit as code. Changed Python functions can be scored with `.smart-harness/tools/complexity.py`; other languages use repository-native analyzers.

## Model routing

Active profile: **`balanced`**. Available profiles: `balanced`, `economy`, `quality`.

### Copilot

| Target | Model | Reasoning |
|---|---|---|
| `dev.coordinator` | `Claude Opus 5` | `high` |
| `review_pr.coordinator` | `Claude Opus 5` | `high` |
| `normal` | `Claude Sonnet 5` | `medium` |
| `deep` | `GPT-5.6 Sol` | `high` |
| `fast` | `GPT-5.6 Terra` | `low` |
| `top` | `Claude Opus 5` | `high` |

### Claude Code

| Target | Model | Reasoning |
|---|---|---|
| `dev.coordinator` | `sonnet[1m]` | `high` |
| `review_pr.coordinator` | `sonnet[1m]` | `high` |
| `normal` | `sonnet[1m]` | `high` |
| `deep` | `claude-opus-4-7` | `xhigh` |
| `fast` | `haiku` | `medium` |
| `top` | `claude-opus-4-8` | `high` |

### Pi

| Target | Model | Reasoning |
|---|---|---|
| `dev.coordinator` | `inherit` | `high` |
| `review_pr.coordinator` | `inherit` | `high` |
| `normal` | `inherit` | `high` |
| `deep` | `inherit` | `xhigh` |
| `fast` | `inherit` | `low` |
| `top` | `inherit` | `xhigh` |

## Shared skills

| Skill | Description | Local path |
|---|---|---|
| `engineering-workflow` | Default end-to-end engineering policy for coding tasks. Use for implementation, debugging, refactoring, architecture work, and maintenance: decompose work into coherent commit-sized units, run plan → implement → document → simplify → verify for every unit, keep authoritative documentation live with code, measure changed-code complexity, and verify with executable evidence. | `shared/skills/engineering-workflow` |
| `pr-review` | Default deep pull-request review policy. Review exact PR HEAD and each logical commit in an isolated worktree, verify plan → implement → document → simplify → verify coherence, measure changed-code complexity and deltas, run semantic and executable lanes, escalate only for high-risk changes, and independently challenge serious findings. | `shared/skills/pr-review` |
| `product-behavior-spec` | Build and maintain an outside-in product behavior specification from code, tests, and the running product. Use when asked for a product description, user-experience behavior spec, feature-by-feature behavior documentation, executable verification catalog, or when extending an existing behavior-spec directory. | `shared/skills/product-behavior-spec` |
| `skill-authoring` | Maintenance-only workflow for creating or changing Smart Harness skills, commands, prompts, or agent policies. Use when editing the harness itself; define precise triggers and observable behavior, keep instructions minimal, pressure-test conflicts and failure cases, update documentation/provenance, and run regression validation. | `shared/skills/skill-authoring` |
| `vscode` | Vendored Pi-compatible VS Code CLI skill for showing file and Git differences to the user. Use when a visual side-by-side comparison is helpful and the existing `code` CLI is available. | `shared/skills/vscode` |

## Adapter files

### Copilot

- `deep-reasoner.agent.md`
- `dev.agent.md`
- `fast-lane.agent.md`
- `review-pr.agent.md`
- `top-reviewer.agent.md`
- `worker-deep.agent.md`
- `worker-normal.agent.md`

### Claude Code hidden agents

- `deep-implementer.md`
- `deep-reasoner.md`
- `fast.md`
- `top-reviewer.md`
- `worker.md`

### Claude Code commands

- `dev.md`
- `review-pr.md`

## Vendored sources

| Component | Pinned commit | License | Local integration |
|---|---|---|---|
| Superpowers methodology adaptation | `b36e0829c6d0140e93cfef2ca599b1b07d4a7797` | MIT | `shared/skills/engineering-workflow`, `shared/skills/skill-authoring` |
| Ponytail adaptation | `2ed6c52c9d7e5e56942508591085fd45dea277d3` | MIT | `shared/skills/engineering-workflow`, `shared/skills/pr-review` |
| Pi VS Code skill adaptation | `90bb51cae36515a648515b633a81c0c6efc8c74d` | MIT | `shared/skills/vscode` |

## Installed support tools

- `.smart-harness/tools/complexity.py` — dependency-free Python function cyclomatic complexity and baseline deltas.
- `.smart-harness/tools/commit_docs.py` — commit-range documentation synchronization checks.
- `.smart-harness/config/models.json` — installed active profile and model/reasoning defaults for Pi children.
- `.smart-harness/install-manifest.json` — installed paths, checksums, platforms, version, and backup history.
- `.smart-harness/vendor/` — pinned provenance and license notices carried with installed artifacts.

Installation is preflighted and transactional, uses atomic settings/manifest writes, rolls back touched paths on failure, and supports `--dry-run` and `--status`.

## Runtime network dependency

None. Installers copy repository-local files only. Host applications and target-project dependencies are prerequisites, not downloaded by this harness.
