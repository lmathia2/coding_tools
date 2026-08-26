# Smart Harness v0.7

A self-contained, low-friction engineering harness for VS Code/GitHub Copilot, Claude Code, and Pi.

## Two things to remember

| Product | Development | PR review |
|---|---|---|
| Copilot | `Dev` | `ReviewPR` |
| Claude Code | `/dev` | `/review-pr` |
| Pi | `/dev` | `/review-pr` |

Everything else is routing and evidence gathering.

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

## Self-contained installation

All runtime harness content is in this repository. No plugin, skill pack, MCP server, npm/pip package, or external repository is installed by the harness.

```bash
bash smart-harness/install.sh all /path/to/project
```

Or install only what you use:

```bash
bash smart-harness/install.sh copilot /path/to/project
bash smart-harness/install.sh claude /path/to/project
bash smart-harness/install.sh pi /path/to/project
bash smart-harness/install.sh both /path/to/project
```

Global defaults:

```bash
bash smart-harness/install-global.sh all
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

The canonical `reasoning` field maps to Copilot CLI `reasoningEffort`, Claude Code `effort`, and Pi `thinking`. VS Code currently applies configured agent models but manages thinking effort at the chat-session model picker, so it may ignore the Copilot CLI effort field. Pi installs the config at `.smart-harness/config/models.json`; parallel tasks select a semantic `role`, while explicit task-level `model` and `thinking` values override the profile.

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/WORKFLOW_CONTRACTS.md`](docs/WORKFLOW_CONTRACTS.md)
- [`docs/DOCUMENTATION_POLICY.md`](docs/DOCUMENTATION_POLICY.md)
- [`docs/PRODUCT_BEHAVIOR_SPEC.md`](docs/PRODUCT_BEHAVIOR_SPEC.md)
- [`docs/SELF_CONTAINED.md`](docs/SELF_CONTAINED.md)
- [`docs/VENDORED_COMPONENTS.md`](docs/VENDORED_COMPONENTS.md)
- [`docs/REFERENCE.md`](docs/REFERENCE.md) — generated
