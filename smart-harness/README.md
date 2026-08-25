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
  -> proportional plan
  -> one implementation context
  -> deterministic verification
  -> done
```

Only add another agent/model when an independent answer can materially change quality: ambiguous root cause, architecture choice, high-risk boundary, or PR semantic review.

## Complexity budget

The harness intentionally caps its core discoverable surface:

- **5 shared skills**: `engineering-workflow`, `pr-review`, `product-behavior-spec`, `skill-authoring`, `vscode`;
- **Copilot**: 2 visible coordinators + 5 hidden specialists;
- **Claude Code**: 2 visible commands + 4 hidden specialists;
- **Pi**: 2 prompts + one local parallel-child helper.

CI rejects accidental re-expansion of these core budgets unless the validator is deliberately changed in the same review.

## Smart development routing

- fast/tool-heavy/mechanical → Terra (Copilot) or Haiku (Claude);
- normal implementation → Sonnet;
- complex implementation/debugging → Sol or Opus 4.7;
- architecture/security/adjudication → Opus only when warranted.

Routine work does not automatically receive a second premium LLM review when tests/compiler/static evidence are strong.

## Engineering workflow

`engineering-workflow` owns the default process in one place:

1. understand repository facts and plan before edits;
2. parallelize only meaningful independent work;
3. choose the smallest correct design;
4. debug from evidence and use pragmatic TDD where useful;
5. update affected authoritative documentation with code;
6. run executable verification before completion.

Documentation impact is always assessed, but `NOT AFFECTED` is valid with a concrete reason. The harness does not create documentation merely to satisfy a ritual.

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

## Models

Edit only:

```text
smart-harness/config/models.json
```

Then:

```bash
python3 smart-harness/config/configure-models.py
python3 smart-harness/config/configure-models.py --check
```

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/WORKFLOW_CONTRACTS.md`](docs/WORKFLOW_CONTRACTS.md)
- [`docs/DOCUMENTATION_POLICY.md`](docs/DOCUMENTATION_POLICY.md)
- [`docs/PRODUCT_BEHAVIOR_SPEC.md`](docs/PRODUCT_BEHAVIOR_SPEC.md)
- [`docs/SELF_CONTAINED.md`](docs/SELF_CONTAINED.md)
- [`docs/VENDORED_COMPONENTS.md`](docs/VENDORED_COMPONENTS.md)
- [`docs/REFERENCE.md`](docs/REFERENCE.md) — generated
