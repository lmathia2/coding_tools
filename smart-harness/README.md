# Smart Harness — Copilot, Claude Code, and Pi

One high-quality development harness with **two workflows** and **one shared skill library**.

## The interface

| Work | VS Code Copilot | Claude Code | Pi |
|---|---|---|---|
| Build, fix, refactor, debug | `Dev` | `/dev` | `/dev` |
| Review another developer's PR | `ReviewPR` | `/review-pr` | `/review-pr` |

Everything else is hidden orchestration.

The goal is simple: **finish correctly and quickly with high quality; save tokens where doing so does not reduce quality.**

## Non-negotiable behavior

### Plan before execution

Every source change starts with a plan. A tiny edit gets a micro-plan; complex work gets repository evidence, alternatives, risk analysis, and an independent challenge.

### Parallelize independent work

Independent code/test/documentation discovery, debugging hypotheses, review perspectives, and non-conflicting verification run concurrently. Parallel writers require disjoint ownership and isolated worktrees.

### Documentation executes with code

Every plan contains `Documentation Impact`.

When code changes function, behavior, APIs, architecture, configuration, schemas, migrations, or operations, the same execution pass updates the authoritative documentation. Documentation explains:

- function — what it does;
- intent — why it exists;
- goals — the outcome/invariant it owns;
- contract — inputs, outputs, errors, side effects, and compatibility;
- constraints and non-goals;
- operational/failure behavior;
- a realistic example when useful.

Documentation builds, doctests, examples, links, and generated-reference drift are verification gates when the repository provides them.

### PR review runs the code

PR review creates a detached worktree at the exact committed PR HEAD. Semantic review and executable lanes run in parallel against that worktree.

The review runs the complete feasible configured unit and integration suites, relevant e2e/runtime tests, build/type/lint/static analysis, and documentation checks. Anything blocked is `NOT EXECUTED`, never silently treated as passing.

## Repository structure

```text
smart-harness/
  shared/skills/              provider-neutral workflow and quality policy
  copilot/                    VS Code Copilot agents and GitHub review guidance
  claude-code/                Claude subagents and /dev /review-pr commands
  pi/                         Pi prompts and curated extension/skill profiles
  config/                     centralized model configuration
  integrations/               Superpowers, Ponytail, Pi upstream locks/installers
  scripts/                    generation, validation, and upstream checks
  docs/                       architecture, workflow contracts, docs policy, reference
  templates/                  CLAUDE.md, ADR, and module documentation templates
  install.sh                  project install
  install-global.sh           machine-wide install
```

## Install into a project

All three adapters:

```bash
bash smart-harness/install.sh all /path/to/project
```

Or select one/two:

```bash
bash smart-harness/install.sh copilot /path/to/project
bash smart-harness/install.sh claude /path/to/project
bash smart-harness/install.sh pi /path/to/project
bash smart-harness/install.sh both /path/to/project   # Copilot + Claude
```

Shared skills are installed once into `.claude/skills/`. Current VS Code Copilot and Claude Code discover that location; Pi's project settings reference it.

Re-running the installer synchronizes updates and backs up replaced files under `.smart-harness-backups/`.

## Install globally on one machine

```bash
bash smart-harness/install-global.sh all
```

This installs shared skills to `~/.claude/skills`, Copilot agents to `~/.copilot/agents`, Claude agents/commands to `~/.claude`, and Pi prompts/settings to `~/.pi/agent`.

## Models: one configuration file

Edit:

```text
config/models.json
```

Then run:

```bash
python3 config/configure-models.py
```

Model identifiers are intentionally opaque so generations can change without redesigning the harness.

## Optional Superpowers and Ponytail

Smart Harness tracks pinned upstream revisions for both projects.

Install the curated skill-only subset globally or into a project:

```bash
bash smart-harness/integrations/install-methodologies.sh global
bash smart-harness/integrations/install-methodologies.sh project /path/to/project
```

The forceful Superpowers bootstrap is intentionally excluded from the curated profile so the two-command Smart Harness interface stays intact. Full native plugin instructions are in [integrations/README.md](integrations/README.md).

Ponytail is optional and cannot simplify away documentation, tests, validation, security, accessibility, compatibility, failure handling, or explicit requirements.

## Pi extensions and skills

Install the recommended Pi core:

```bash
bash smart-harness/pi/install-extensions.sh core
```

Optional profiles cover browser testing, observability, productivity, and full Superpowers/Ponytail methodology.

Curated Pi skills from the tracked `badlogic/pi-skills` source:

```bash
bash smart-harness/pi/install-skills.sh useful
```

See [pi/README.md](pi/README.md).

## Keeping code and documentation synchronized

- `documentation-sync` is explicitly invoked by every development and PR-review entry point.
- `docs/REFERENCE.md` is generated from model/integration/profile configuration.
- CI validates workflow invariants, generated docs, local links, model routing, and installer syntax.
- A scheduled workflow checks tracked upstreams and opens a reviewable update PR.

Run locally:

```bash
python3 smart-harness/config/configure-models.py --check
python3 smart-harness/scripts/generate-reference.py --check
python3 smart-harness/scripts/validate-harness.py
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Workflow contracts](docs/WORKFLOW_CONTRACTS.md)
- [Documentation policy](docs/DOCUMENTATION_POLICY.md)
- [Integrations](docs/INTEGRATIONS.md)
- [Generated reference](docs/REFERENCE.md)
- [Changelog](CHANGELOG.md)

## Updating

```bash
cd coding_tools
python3 smart-harness/scripts/check-upstreams.py
python3 smart-harness/config/configure-models.py
python3 smart-harness/scripts/generate-reference.py
python3 smart-harness/scripts/validate-harness.py
bash smart-harness/install.sh all /path/to/project
```

Review upstream methodology/extension changes before accepting updated locks: skills can instruct agents to act, and extensions execute with developer permissions.
