# WYSIWYShip v0.10

*What you spec is what you ship.*

**Plan it. Prove it. Just ship.**

A self-contained, low-friction engineering workflow for VS Code/GitHub Copilot, Claude Code, and Pi.

## Two things to remember

| Product | Development | PR review | Explain a project |
|---|---|---|---|
| Copilot | `Dev` | `ReviewPR` | `eli5` skill |
| Claude Code | `/dev` | `/review-pr` | `/eli5` |
| Pi | `/dev` | `/review-pr` | `/eli5` |

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

### Upgrading from Smart Harness

The repository URL remains `lmathia2/coding_tools`, but the product directory, plugin ID, command namespace, installed support directory, and hooks are now `wysiwyship`.

Rerun the project or global installer from `wysiwyship/`. It transactionally backs up and removes the previous `.smart-harness/` support directory and obsolete hook/helper paths before installing `.wysiwyship/`. Native-plugin users should remove the old `smart-harness` plugin through their host's plugin manager and install `wysiwyship` using the commands below.

### 2. Install into a project (recommended)

Install all three adapters into the project where you want to use them:

```bash
bash wysiwyship/install.sh all /absolute/path/to/project
```

The project-local install creates or updates:

| Host | Discovery files | What becomes available |
|---|---|---|
| GitHub Copilot | `.github/agents/`, `.github/skills/`, shared `.claude/skills/` | `Dev`, `ReviewPR`, and the `eli5` skill |
| Claude Code | `.claude/commands/`, `.claude/agents/`, `.claude/skills/` | `/dev`, `/review-pr`, `/eli5`, and their specialists |
| Pi | `.pi/prompts/`, `.pi/tools/`, `.pi/settings.json` | `/dev`, `/review-pr`, `/eli5`, shared skills, and parallel children |
| All hosts | `.wysiwyship/` | Model profile, complexity/documentation tools, templates, provenance, and install manifest |

Project-local installation is recommended because the workflow definitions travel with the codebase and can be reviewed with other project changes.

### 3. Reload the host and use it

Open the project root in a new host session, or reload the current session so customization discovery runs again. Then use:

- GitHub Copilot: select the `Dev` agent for implementation or `ReviewPR` for pull-request review; invoke `eli5` explicitly for an explanation-only run.
- Claude Code: run `/dev <task>`, `/review-pr <base-ref and intent>`, or `/eli5 <project and audience>`.
- Pi: run `/dev <task>`, `/review-pr <base-ref and intent>`, or `/eli5 <project and audience>`.

If a command or agent does not appear, confirm the host was opened at the installed project root and check the paths in the table above.

### 4. Verify or upgrade

Inspect the installed checksums and platform set:

```bash
bash wysiwyship/install.sh all /absolute/path/to/project --status
```

To upgrade, pull the harness repository and rerun the same install command. Installation is preflighted, transactional, and preserves unrelated host customizations.

### Global alternative

To make the workflows available by default across projects for the current user:

```bash
cd ~/src/coding_tools
bash wysiwyship/install-global.sh all
bash wysiwyship/install-global.sh all --status
```

Global installation uses `~/.copilot/agents`, `~/.claude/{commands,agents,skills}`, and `~/.pi/agent`. Host precedence rules differ when the same customization exists in both scopes, so avoid conflicting global and project definitions unless that override is intentional.

### Native plugin alternative

For personal reuse where repository-local configuration is unnecessary, install the generated native bundle:

```bash
copilot plugin install lmathia2/coding_tools:wysiwyship/packages/copilot

claude plugin marketplace add lmathia2/coding_tools
claude plugin install wysiwyship@coding-tools
```

The plugin bundles are generated from the same canonical agents, skills, tools, model profile, and checks as the installer. Claude commands are namespaced (for example `/wysiwyship:dev`). Copilot keeps the `Dev` and `ReviewPR` agent names. The selected model profile is fixed at package build time; edit `config/models.json`, apply the profile, and rebuild to publish a different routing experiment.

Use the project installer when policies/configuration should travel with the target repository, when Pi is required, or when project-local discovery names (`/dev`) are preferred. Do not install both forms for the same host unless you intentionally want project files to take precedence over plugin components.

Discovery behavior is documented upstream for [Copilot custom agents and skills](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference), [Claude Code skills and commands](https://code.claude.com/docs/en/slash-commands), and [Pi settings](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/settings.md).

## Design target

The default is intentionally small:

```text
request
  -> coherent commit-sized work units
  -> plan -> implement -> document -> simplify -> verify per unit
  -> integrate independent units in dependency order
  -> deterministic range gate
  -> ELI5 visual handoff
  -> done
```

Only add another agent/model when an independent answer can materially change quality: ambiguous root cause, architecture choice, high-risk boundary, or PR semantic review.

## Complexity budget

The harness intentionally caps its core discoverable surface:

- **6 shared skills**: `engineering-workflow`, `eli5`, `pr-review`, `product-behavior-spec`, `skill-authoring`, `vscode`;
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
6. run executable verification before completion;
7. after the committed-range gate passes, run `eli5` and produce a checked visual project handoff.

Documentation impact is always assessed. A code commit with no documentation changes records `Docs-Impact: none — <reason>`. The harness does not create low-value documentation merely to satisfy a ritual.

For Python, the installed dependency-free analyzer reports function scores and optional baseline deltas:

```bash
python3 .wysiwyship/tools/complexity.py path/to/code.py --compare-ref <unit-start-ref>
```

The deterministic lifecycle gate composes that metric with per-commit documentation evidence and the repository's configured verification commands:

```bash
python3 .wysiwyship/tools/check.py <unit-start-ref> --head HEAD
python3 .wysiwyship/tools/check.py <unit-start-ref> --head HEAD --format json
```

Edit `.wysiwyship/config/checks.json` to add project checks as argument arrays. For example, `{"name": "tests", "argv": ["python3", "-m", "pytest", "-q"]}`. Commands execute directly without a shell, from the repository root unless a safe repository-relative `cwd` is supplied.

For a long, parallel, or resumable change, persist the execution contract and activate it for the installed Copilot/Claude stop hook:

```bash
python3 .wysiwyship/tools/work_units.py init api-contract \
  --title "API contract" --goal "Add the accepted contract" \
  --acceptance "contract tests pass" --owns src/api.py --base-ref HEAD \
  --docs-impact required --doc-path docs/api.md --activate
python3 .wysiwyship/tools/work_units.py advance api-contract --evidence "plan: callers and contract mapped"
# Repeat advance after implement, document, simplify, and verify.
python3 .wysiwyship/tools/check.py --active
python3 .wysiwyship/tools/work_units.py close
```

The ledger is deliberately optional and ignored by Git. Installed stop hooks do nothing when no unit is active. With an active unit, they prevent premature completion, run the committed-range gate after verification, and retain the completed unit history for handoff/audit.

If the project already uses Spec Kit, OpenSpec, or BMAD, preview accepted implementation tasks instead of maintaining a second plan:

```bash
python3 .wysiwyship/tools/spec_bridge.py detect
python3 .wysiwyship/tools/spec_bridge.py preview specs/001-auth/tasks.md
python3 .wysiwyship/tools/spec_bridge.py import specs/001-auth/tasks.md --accepted --activate-first
```

Import is explicit and one-way. The upstream artifact remains authoritative; the bridge preserves its task IDs/path, imports only checklist execution state, and never invokes or replaces the framework's specification, validation, apply, or archive workflow.

## Project ELI5 handoff

Every successful development workflow finishes by invoking the bundled `eli5` skill. Its baseline audience is always a curious developer who wants to learn what changed, how the implementation works, and why the design choices exist. It reads the verified implementation, tests, live documentation, public contracts, and completion evidence, then produces a 5–9 slide visual walkthrough under ignored `.agent-state/eli5/` by default. A requested role or experience level changes the emphasis without removing the what, how, or why.

The renderer is Python-standard-library only and emits one offline HTML file with all CSS, JavaScript, content, and fonts resolved locally. It uses a fixed 1920×1080 stage, strong editorial hierarchy, diagrams/cards/metrics, keyboard and touch navigation, print layout, and reduced-motion support. It makes no CDN, package-manager, analytics, or runtime network request.

Run it explicitly at any time with `/eli5 <project or change and audience>`. To preserve an explainer as authoritative project documentation, request a versioned output path such as `docs/project-eli5.html`; otherwise the automatic post-development artifact stays outside the commit under `.agent-state/eli5/`.

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
bash wysiwyship/install.sh copilot /path/to/project
bash wysiwyship/install.sh claude /path/to/project
bash wysiwyship/install.sh pi /path/to/project
bash wysiwyship/install.sh both /path/to/project  # Copilot + Claude Code
```

Preview or inspect installation state:

```bash
bash wysiwyship/install.sh all /path/to/project --dry-run
bash wysiwyship/install.sh all /path/to/project --status
```

## Models

Model and reasoning choices live in one versioned file:

```text
wysiwyship/config/models.json
```

It contains selectable `balanced`, `economy`, and `quality` profiles. List, inspect, activate, or verify them with:

```bash
python3 wysiwyship/config/configure-models.py --list-profiles
python3 wysiwyship/config/configure-models.py --show --profile quality
python3 wysiwyship/config/configure-models.py --profile economy
python3 wysiwyship/config/configure-models.py --check
```

Activating a profile updates `active_profile`, regenerates Copilot and Claude Code frontmatter, and refreshes the generated reference. Each profile configures the `dev` and `review_pr` coordinators separately plus the reusable `normal`, `deep`, `fast`, and `top` specialist lanes. Copy a profile under a new name to run a custom model experiment.

After changing the active profile, rerun the relevant project or global installer so already-installed adapters receive the new settings.

Record evidence when comparing profiles instead of choosing from impressions alone:

```bash
python3 .wysiwyship/tools/experiments.py record \
  --workflow dev --role normal --platform claude_code --profile quality \
  --status pass --verification pass --duration-seconds 84 --complexity-before 12 --complexity-after 8
python3 .wysiwyship/tools/experiments.py compare --group-by profile
```

The append-only log lives under ignored `.agent-state/` by default. Tokens, cost, defects, and rework are optional; missing host telemetry remains visibly unreported rather than being estimated. The `run` subcommand times a command, and `import-pi` converts measured `parallel-pi.py` child results into the same schema.

The canonical `reasoning` field maps to Copilot CLI `reasoningEffort`, Claude Code `effort`, and Pi `thinking`. VS Code currently applies configured agent models but manages thinking effort at the chat-session model picker, so it may ignore the Copilot CLI effort field. Pi installs the config at `.wysiwyship/config/models.json`; parallel tasks select a semantic `role`, while explicit task-level `model` and `thinking` values override the profile.

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/WORKFLOW_CONTRACTS.md`](docs/WORKFLOW_CONTRACTS.md)
- [`docs/DOCUMENTATION_POLICY.md`](docs/DOCUMENTATION_POLICY.md)
- [`docs/PRODUCT_BEHAVIOR_SPEC.md`](docs/PRODUCT_BEHAVIOR_SPEC.md)
- [`docs/SELF_CONTAINED.md`](docs/SELF_CONTAINED.md)
- [`docs/VENDORED_COMPONENTS.md`](docs/VENDORED_COMPONENTS.md)
- [`docs/REFERENCE.md`](docs/REFERENCE.md) — generated
