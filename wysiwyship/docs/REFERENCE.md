# Generated WYSIWYShip Reference

*What you spec is what you ship. Plan it. Prove it. Just ship.*

> Generated from repository-local files for version `0.11.0`. Do not edit by hand.

## Simplicity budget

- Shared discoverable skills: **6** (budget: 6)
- Codex specialist definitions: **4** (budget: 4)
- Copilot agent definitions: **7** (2 visible + 5 hidden)
- Claude Code hidden agents: **5** (budget: 5)
- Claude Code visible commands: **2** (budget: 2)

## Work-unit lifecycle

Every development request starts with an evidence-first planning grill and an explicit human or auto plan lock. After lock, execution is rapid and low-interruption unless a material decision is invalidated or new authority is required.

Every implementation unit is coherent and independently committable, with explicit planning decisions, dependencies, and ownership:

```text
plan -> implement -> document -> simplify -> verify
```

Live authoritative documentation travels in the same logical commit as code. Changed Python functions can be scored with `.wysiwyship/tools/complexity.py`; other languages use repository-native analyzers.

## Model routing

Profiles below describe intended settings, not proof of model execution. Workflows resolve a named route, invoke the host, and check a receipt; effective model/effort remains UNVERIFIED without host metadata. Pi children with no explicit model use their own host default.

Active profile: **`balanced`**. Available profiles: `balanced`, `economy`, `quality`.

### Codex

| Target | Model | Reasoning |
|---|---|---|
| `dev.coordinator` | `inherit` | `high` |
| `review_pr.coordinator` | `inherit` | `high` |
| `normal` | `gpt-5.6-terra` | `medium` |
| `deep` | `gpt-5.6-sol` | `high` |
| `fast` | `gpt-5.6-luna` | `low` |
| `top` | `gpt-5.6-sol` | `high` |

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
| `eli5` | Teach a curious developer what a completed coding project or change is for, how to use it, its core concepts, how the code is organized and executes under the hood, why key design choices exist, and what evidence proves it works. Produce a precise, source-grounded, dependency-free visual HTML walkthrough. Use for /eli5, project or codebase explanations, architecture walkthroughs, onboarding guides, and the mandatory handoff after a successful WYSIWYShip development workflow. | `shared/skills/eli5` |
| `engineering-workflow` | Default end-to-end engineering policy for coding tasks. Use for implementation, debugging, refactoring, architecture work, and maintenance: grill and lock the plan, decompose work into coherent commit-sized units, run plan → implement → document → simplify → verify for every unit, keep authoritative documentation live with code, measure changed-code complexity, and verify with executable evidence. | `shared/skills/engineering-workflow` |
| `pr-review` | Default deep pull-request review policy. Review exact PR HEAD and each logical commit in an isolated worktree, verify plan → implement → document → simplify → verify coherence, measure changed-code complexity and deltas, run semantic and executable lanes, escalate only for high-risk changes, and independently challenge serious findings. | `shared/skills/pr-review` |
| `product-behavior-spec` | Build and maintain an outside-in product behavior specification from code, tests, and the running product. Use when asked for a product description, user-experience behavior spec, feature-by-feature behavior documentation, executable verification catalog, or when extending an existing behavior-spec directory. | `shared/skills/product-behavior-spec` |
| `skill-authoring` | Maintenance-only workflow for creating or changing WYSIWYShip skills, commands, prompts, or agent policies. Use when editing the harness itself; define precise triggers and observable behavior, keep instructions minimal, pressure-test conflicts and failure cases, update documentation/provenance, and run regression validation. | `shared/skills/skill-authoring` |
| `vscode` | Vendored Pi-compatible VS Code CLI skill for showing file and Git differences to the user. Use when a visual side-by-side comparison is helpful and the existing `code` CLI is available. | `shared/skills/vscode` |

## Adapter files

### Codex specialists

- `wysiwyship-deep.toml`
- `wysiwyship-fast.toml`
- `wysiwyship-reviewer.toml`
- `wysiwyship-worker.toml`

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
| ELI5 adaptation | `a766623b062331fdde53467001379b4ddf3acc2f` | MIT | `shared/skills/eli5/SKILL.md`, `shared/skills/eli5/references/story-format.md` |
| Frontend Slides adaptation | `9906a34d640d2111f724544cbc50f7f130569ae1` | MIT | `shared/skills/eli5/assets/project-eli5-template.html`, `shared/skills/eli5/scripts/render_explainer.py`, `shared/skills/eli5/SKILL.md` |

## Installed support tools

- `.wysiwyship/tools/complexity.py` — dependency-free Python function cyclomatic complexity and baseline deltas.
- `.wysiwyship/tools/commit_docs.py` — commit-range documentation synchronization checks.
- `.wysiwyship/tools/routing.py` — cross-host route resolution and invocation-receipt consistency checks; not a model launcher or authenticated attestation.
- `.wysiwyship/config/models.json` — installed active profile and model/reasoning routes for every host.
- `.wysiwyship/model-discovery.json` — installer evidence, account-visible capabilities, fallbacks, and limitations when discovery is enabled.
- `.wysiwyship/install-manifest.json` — installed paths, checksums, platforms, version, and backup history.
- `.wysiwyship/vendor/` — pinned provenance and license notices carried with installed artifacts.

Installation is preflighted and transactional, uses atomic settings/manifest writes, rolls back touched paths on failure, and supports `--dry-run`, `--status`, and `--no-model-discovery`.

## Runtime network dependency

None. Installers copy repository-local files only. Host applications and target-project dependencies are prerequisites, not downloaded by this harness.
