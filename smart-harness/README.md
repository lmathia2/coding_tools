# Smart Harness v0.7

A self-contained, low-friction engineering harness for VS Code/GitHub Copilot, Claude Code, and Pi.

## Two things to remember

| Product | Development | PR review |
|---|---|---|
| Copilot | `Dev` | `ReviewPR` |
| Claude Code | `/dev` | `/review-pr` |
| Pi | `/dev` | `/review-pr` |

Everything else is routing and evidence gathering.

## Getting started

### Prerequisites

- Python 3 and Bash;
- at least one supported host installed: GitHub Copilot, Claude Code, or Pi;
- an existing project directory where the host will run.

The harness itself installs no packages and downloads nothing at runtime.

### 1. Get the harness

```bash
git clone https://github.com/lmathia2/coding_tools.git ~/src/coding_tools
cd ~/src/coding_tools
```

If the repository is already cloned, update it normally and run the commands from its root.

### 2. Install into a project (recommended)

Install all three adapters into the project where you want to use them:

```bash
bash smart-harness/install.sh all /absolute/path/to/project
```

The project-local install creates or updates:

| Host | Discovery files | What becomes available |
|---|---|---|
| GitHub Copilot | `.github/agents/`, `.github/skills/`, shared `.claude/skills/` | `Dev` and `ReviewPR` custom agents |
| Claude Code | `.claude/commands/`, `.claude/agents/`, `.claude/skills/` | `/dev`, `/review-pr`, and their specialists |
| Pi | `.pi/prompts/`, `.pi/tools/`, `.pi/settings.json` | `/dev`, `/review-pr`, shared skills, and parallel children |
| All hosts | `.smart-harness/` | Model profile, complexity/documentation tools, templates, provenance, and install manifest |

Project-local installation is recommended because the workflow definitions travel with the codebase and can be reviewed with other project changes.

### 3. Reload the host and use it

Open the project root in a new host session, or reload the current session so customization discovery runs again. Then use:

- GitHub Copilot: select the `Dev` agent for implementation or `ReviewPR` for pull-request review.
- Claude Code: run `/dev <task>` or `/review-pr <base-ref and intent>`.
- Pi: run `/dev <task>` or `/review-pr <base-ref and intent>`.

If a command or agent does not appear, confirm the host was opened at the installed project root and check the paths in the table above.

### 4. Verify or upgrade

Inspect the installed checksums and platform set:

```bash
bash smart-harness/install.sh all /absolute/path/to/project --status
```

To upgrade, pull the harness repository and rerun the same install command. Installation is preflighted, transactional, and preserves unrelated host customizations.

### Global alternative

To make the workflows available by default across projects for the current user:

```bash
cd ~/src/coding_tools
bash smart-harness/install-global.sh all
bash smart-harness/install-global.sh all --status
```

Global installation uses `~/.copilot/agents`, `~/.claude/{commands,agents,skills}`, and `~/.pi/agent`. Host precedence rules differ when the same customization exists in both scopes, so avoid conflicting global and project definitions unless that override is intentional.

Discovery behavior is documented upstream for [Copilot custom agents and skills](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference), [Claude Code skills and commands](https://code.claude.com/docs/en/slash-commands), and [Pi settings](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/settings.md).

## Design target

The default is intentionally small:

```text
request
  -> coherent commit-sized work units
  -> plan -> implement -> document -> simplify -> verify per unit
  -> integrate independent units in dependency order
  -> done
```

Only add another agent/model when an independent answer can materially change quality: ambiguous root cause, architecture choice, high-risk boundary, or PR semantic review.

## Complexity budget

The harness intentionally caps its core discoverable surface:

- **5 shared skills**: `engineering-workflow`, `pr-review`, `product-behavior-spec`, `skill-authoring`, `vscode`;
- **Copilot**: 2 visible coordinators + 5 hidden specialists;
- **Claude Code**: 2 visible commands + 5 hidden specialists;
- **Pi**: 2 prompts + one local parallel-child helper.

CI rejects accidental re-expansion of these core budgets unless the validator is deliberately changed in the same review.

## Smart development routing

- fast/tool-heavy read-only exploration, measurement, and verification → configured `fast` lane;
- mechanical and normal implementation → configured `normal` lane;
- complex implementation/debugging → configured `deep` lane;
- architecture/security/adjudication → configured `top` lane only when warranted.

Routine work does not automatically receive a second premium LLM review when tests/compiler/static evidence are strong.

## Engineering workflow

`engineering-workflow` owns the default process in one place:

1. decompose non-trivial work into coherent, independently committable units;
2. run `plan -> implement -> document -> simplify -> verify` for every unit;
3. parallelize only independent units with disjoint ownership and isolated worktrees;
4. keep implementation, API/contracts, purpose, intent, and invariants live in the same commit as code;
5. score changed-function cyclomatic complexity and simplify without gaming the number;
6. run executable verification before completion.

Documentation impact is always assessed. A code commit with no documentation changes records `Docs-Impact: none — <reason>`. The harness does not create low-value documentation merely to satisfy a ritual.

For Python, the installed dependency-free analyzer reports function scores and optional baseline deltas:

```bash
python3 .smart-harness/tools/complexity.py path/to/code.py --compare-ref <unit-start-ref>
```

## PR review

`ReviewPR` / `/review-pr` preserves the stronger review path:

```text
exact PR HEAD worktree
      ├── semantic review
      └── executable verification
             ├── full feasible unit suite
             ├── full feasible integration suite
             ├── relevant e2e/runtime
             ├── build/type/lint/static
             └── affected docs checks
```

High-risk PRs add adversarial and security/resilience review. Candidate BLOCKER/MAJOR findings get one fresh falsification attempt before publication.

Minimality is part of semantic review; there is no separate Ponytail lane.

## Product behavior specifications

`product-behavior-spec` remains available for explicit outside-in product documentation requests. It is **not** part of every coding task. If a repository already has such documentation and a change affects it, the normal documentation gate updates only the impacted artifacts.

## Installation reference

All runtime harness content is in this repository. No plugin, skill pack, MCP server, npm/pip package, or external repository is installed by the harness.

Install only the adapters you use:

```bash
bash smart-harness/install.sh copilot /path/to/project
bash smart-harness/install.sh claude /path/to/project
bash smart-harness/install.sh pi /path/to/project
bash smart-harness/install.sh both /path/to/project  # Copilot + Claude Code
```

Preview or inspect installation state:

```bash
bash smart-harness/install.sh all /path/to/project --dry-run
bash smart-harness/install.sh all /path/to/project --status
```

## Models

Model and reasoning choices live in one versioned file:

```text
smart-harness/config/models.json
```

It contains selectable `balanced`, `economy`, and `quality` profiles. List, inspect, activate, or verify them with:

```bash
python3 smart-harness/config/configure-models.py --list-profiles
python3 smart-harness/config/configure-models.py --show --profile quality
python3 smart-harness/config/configure-models.py --profile economy
python3 smart-harness/config/configure-models.py --check
```

Activating a profile updates `active_profile`, regenerates Copilot and Claude Code frontmatter, and refreshes the generated reference. Each profile configures the `dev` and `review_pr` coordinators separately plus the reusable `normal`, `deep`, `fast`, and `top` specialist lanes. Copy a profile under a new name to run a custom model experiment.

After changing the active profile, rerun the relevant project or global installer so already-installed adapters receive the new settings.

The canonical `reasoning` field maps to Copilot CLI `reasoningEffort`, Claude Code `effort`, and Pi `thinking`. VS Code currently applies configured agent models but manages thinking effort at the chat-session model picker, so it may ignore the Copilot CLI effort field. Pi installs the config at `.smart-harness/config/models.json`; parallel tasks select a semantic `role`, while explicit task-level `model` and `thinking` values override the profile.

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/WORKFLOW_CONTRACTS.md`](docs/WORKFLOW_CONTRACTS.md)
- [`docs/DOCUMENTATION_POLICY.md`](docs/DOCUMENTATION_POLICY.md)
- [`docs/PRODUCT_BEHAVIOR_SPEC.md`](docs/PRODUCT_BEHAVIOR_SPEC.md)
- [`docs/SELF_CONTAINED.md`](docs/SELF_CONTAINED.md)
- [`docs/VENDORED_COMPONENTS.md`](docs/VENDORED_COMPONENTS.md)
- [`docs/REFERENCE.md`](docs/REFERENCE.md) — generated
