# Generated Smart Harness Reference

> Generated from repository-local files for version `0.7.0`. Do not edit by hand.

## Simplicity budget

- Shared discoverable skills: **5** (budget: 5)
- Copilot agent definitions: **7** (2 visible + 5 hidden)
- Claude Code hidden agents: **4** (budget: 4)
- Claude Code visible commands: **2** (budget: 2)

## Model routing

### Copilot

| Role | Model | Effort |
|---|---|---|
| `coordinator` | `Claude Opus 5` | `` |
| `normal` | `Claude Sonnet 5` | `` |
| `deep` | `GPT-5.6 Sol` | `` |
| `fast` | `GPT-5.6 Terra` | `` |
| `top` | `Claude Opus 5` | `` |

### Claude Code

| Role | Model | Effort |
|---|---|---|
| `coordinator` | `sonnet[1m]` | `high` |
| `normal` | `sonnet[1m]` | `high` |
| `deep` | `claude-opus-4-7` | `xhigh` |
| `fast` | `haiku` | `medium` |
| `top` | `claude-opus-4-8` | `high` |

## Shared skills

| Skill | Description | Local path |
|---|---|---|
| `engineering-workflow` | Default end-to-end engineering policy for coding tasks. Use for implementation, debugging, refactoring, architecture work, and maintenance: understand the repository, make a proportional plan before edits, parallelize only useful independent work, choose the smallest correct design, keep authoritative documentation synchronized, and verify with executable evidence. | `shared/skills/engineering-workflow` |
| `pr-review` | Default deep pull-request review policy. Use for reviewing another developer's PR: plan briefly, check out the exact committed PR HEAD in an isolated worktree, run one semantic review and one executable verification lane in parallel, execute complete feasible unit/integration suites plus relevant static/runtime/docs checks, add specialist security/adversarial review only for high-risk changes, and independently challenge serious findings. | `shared/skills/pr-review` |
| `product-behavior-spec` | Build and maintain an outside-in product behavior specification from code, tests, and the running product. Use when asked for a product description, user-experience behavior spec, feature-by-feature behavior documentation, executable verification catalog, or when extending an existing behavior-spec directory. | `shared/skills/product-behavior-spec` |
| `skill-authoring` | Maintenance-only workflow for creating or changing Smart Harness skills, commands, prompts, or agent policies. Use when editing the harness itself; define precise triggers and observable behavior, keep instructions minimal, pressure-test conflicts and failure cases, update documentation/provenance, and run regression validation. | `shared/skills/skill-authoring` |
| `vscode` | Vendored Pi-compatible VS Code CLI skill for showing file and Git differences to the user. Use when a visual side-by-side comparison is helpful and the existing `code` CLI is available. | `shared/skills/vscode` |

## Adapter files

### Copilot

- `deep-sol.agent.md`
- `dev.agent.md`
- `fast-terra.agent.md`
- `review-pr.agent.md`
- `security-opus.agent.md`
- `worker-sol.agent.md`
- `worker-sonnet.agent.md`

### Claude Code hidden agents

- `deep-implementer.md`
- `deep-reasoner.md`
- `fast.md`
- `top-reviewer.md`

### Claude Code commands

- `dev.md`
- `review-pr.md`

## Vendored sources

| Component | Pinned commit | License | Local integration |
|---|---|---|---|
| Superpowers methodology adaptation | `b36e0829c6d0140e93cfef2ca599b1b07d4a7797` | MIT | `shared/skills/engineering-workflow`, `shared/skills/skill-authoring` |
| Ponytail adaptation | `2ed6c52c9d7e5e56942508591085fd45dea277d3` | MIT | `shared/skills/engineering-workflow`, `shared/skills/pr-review` |
| Pi VS Code skill adaptation | `90bb51cae36515a648515b633a81c0c6efc8c74d` | MIT | `shared/skills/vscode` |

## Runtime network dependency

None. Installers copy repository-local files only. Host applications and target-project dependencies are prerequisites, not downloaded by this harness.
