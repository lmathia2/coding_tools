# Generated Smart Harness Reference

> Generated from repository-local files for version `0.6.0`. Do not edit by hand.

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
| `codebase-map` | Build a compact task-relevant map of ownership, callers, contracts, tests, and risk edges before complex changes. | `shared/skills/codebase-map` |
| `context-snapshot` | Create a compact immutable evidence bundle for a coding task or PR review using Git refs, diffs, file paths, line ranges, and command outputs. Use before parallel reviewers or long tasks so every lane works from the same repository facts without an external context extension. | `shared/skills/context-snapshot` |
| `documentation-sync` | Mandatory documentation-as-code protocol for implementation and PR review. Use whenever code, APIs, behavior, architecture, configuration, operations, or tests change; keeps function/API docs, intent, goals, examples, product behavior specs, ADRs, runbooks, and generated references synchronized with executable behavior. | `shared/skills/documentation-sync` |
| `engineering-core` | Core execution discipline shared by Copilot, Claude Code, and Pi: root-cause debugging, pragmatic TDD, scoped changes, documentation sync, and evidence-based completion. | `shared/skills/engineering-core` |
| `parallel-work` | Parallelization policy for agentic coding and review. Run independent analysis, documentation-impact discovery, and verification concurrently; parallelize writes only when isolated and dependency-safe. | `shared/skills/parallel-work` |
| `plan-first` | Mandatory planning protocol for every coding or review task. Plan depth scales with risk, but source editing never starts before an explicit plan and documentation impact assessment exist. | `shared/skills/plan-first` |
| `ponytail` | Vendored, dependency-free adaptation of Ponytail. Use on coding, design, refactoring, dependency selection, and bug fixes to choose the simplest correct solution after understanding the full flow. Enforces YAGNI, reuse, standard-library/native features, minimal coherent diffs, and deletion over speculative abstraction. | `shared/skills/ponytail` |
| `ponytail-review` | Vendored complexity-only review adapted from Ponytail. Use during implementation or PR review to identify code that can be deleted or replaced by existing repository code, standard-library/native features, or a smaller design. It complements and never replaces correctness, security, testing, or documentation review. | `shared/skills/ponytail-review` |
| `pr-review` | Portable deep PR-review protocol: isolated worktree at PR HEAD, parallel dynamic/static review, full feasible unit and integration execution, documentation validation, security/resilience analysis, and high-severity finding verification. | `shared/skills/pr-review` |
| `product-behavior-spec` | Build and maintain an outside-in product behavior specification from code, tests, and the running product. Use when asked for a product description, user-experience behavior spec, feature-by-feature behavior documentation, executable verification catalog, or when extending an existing behavior-spec directory. | `shared/skills/product-behavior-spec` |
| `superpowers-methodology` | Vendored, dependency-free adaptation of the Superpowers software-development methodology. Use for non-trivial feature work, refactors, and difficult fixes that benefit from design clarification, isolated work, an executable plan, TDD, subagent delegation, review, and evidence-based completion. | `shared/skills/superpowers-methodology` |
| `superpowers-skill-authoring` | Dependency-free skill-authoring and maintenance workflow adapted from Superpowers. Use when creating or modifying agent skills, commands, prompts, or orchestration rules; requires a clear trigger, minimal instructions, pressure tests, documentation, and regression validation. | `shared/skills/superpowers-skill-authoring` |
| `task-ledger` | Persistent concise state for long multi-stage agent tasks so compaction or handoff does not lose the accepted plan, progress, or verification evidence. | `shared/skills/task-ledger` |
| `vscode` | Vendored Pi-compatible VS Code CLI skill for showing file and Git differences to the user. Use when a visual side-by-side comparison is helpful and the existing `code` CLI is available. | `shared/skills/vscode` |

## Vendored sources

| Component | Pinned commit | License | Local paths |
|---|---|---|---|
| Superpowers methodology adaptation | `b36e0829c6d0140e93cfef2ca599b1b07d4a7797` | MIT | `shared/skills/superpowers-methodology`, `shared/skills/superpowers-skill-authoring` |
| Ponytail adaptation | `2ed6c52c9d7e5e56942508591085fd45dea277d3` | MIT | `shared/skills/ponytail`, `shared/skills/ponytail-review` |
| Pi VS Code skill adaptation | `90bb51cae36515a648515b633a81c0c6efc8c74d` | MIT | `shared/skills/vscode` |

## Runtime network dependency

None. Installers copy repository-local files only. Host applications and target-project dependencies are prerequisites, not downloaded by this harness.
