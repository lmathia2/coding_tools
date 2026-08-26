# Smart Harness Architecture

## Purpose

Provide one high-quality coding interface across Copilot, Claude Code, and Pi without requiring the developer to remember model or workflow commands.

## Goals

- two user-facing workflows: development and PR review;
- quality-first model routing with token/latency discipline;
- planning before source edits;
- coherent commit-sized work units and useful parallelism without agent fan-out for its own sake;
- smallest correct implementation;
- live authoritative documentation synchronized in every logical code commit;
- measured changed-code complexity and an explicit simplification stage;
- executable verification;
- exact-HEAD isolated PR review;
- self-contained installation.

## Default execution shape

```text
request
  -> coordinator defines work-unit dependency graph
  -> each unit: plan -> implement -> document -> simplify -> verify
  -> integrate independently completed units in dependency order
  -> completion
```

Independent agents are conditional, not ceremonial. Add them when they provide material independent evidence or judgment: ambiguous debugging, architecture alternatives, high-risk boundaries, or PR semantic review.

## Shared policy

Only five discoverable shared skills are intentional:

1. `engineering-workflow` — all ordinary coding process: plan, routing principles, parallelism, minimal design, debugging/TDD, documentation, verification;
2. `pr-review` — worktree-based semantic + executable review and high-risk escalation;
3. `product-behavior-spec` — explicit specialist outside-in product documentation;
4. `skill-authoring` — maintenance-only harness policy;
5. `vscode` — optional local visual diff utility.

Repository mapping, context snapshots, task ledgers, Superpowers process, Ponytail minimality, and documentation synchronization are techniques inside the core workflows rather than separately discoverable skills.

## Model profiles

`config/models.json` is the single source of truth for model and reasoning-strength experiments. A named active profile contains platform-specific settings for each workflow coordinator (`dev`, `review_pr`) and shared specialist lane (`normal`, `deep`, `fast`, `top`). `config/configure-models.py --profile <name>` persists the selection and regenerates static Copilot/Claude adapter frontmatter; validation rejects configuration or generated-file drift.

The config uses one provider-neutral `reasoning` property. Adapter translation is deliberately narrow:

| Adapter | Model setting | Reasoning setting | Enforcement boundary |
|---|---|---|---|
| Copilot CLI | `model` | `reasoningEffort` | Per custom agent; an unavailable override falls back to the session |
| VS Code Copilot | `model` | Session model picker | Current VS Code custom-agent frontmatter does not document per-agent effort |
| Claude Code | `model` | `effort` | Per command/agent frontmatter |
| Pi | `--model` | `--thinking` | Per parallel child; the coordinator inherits its active session |

Pi receives the selected config at `.smart-harness/config/models.json`. Its helper resolves defaults from `--workflow` plus each task's semantic `role`; explicit per-task values take precedence for controlled experiments.

## Platform adapters

### Copilot

Visible: `Dev`, `ReviewPR`.

Hidden specialists:

- `FastLane` — read-only exploration, deterministic execution, and complexity measurement;
- `WorkerNormal` — normal implementation;
- `WorkerDeep` — complex implementation;
- `DeepReasoner` — read-only debugging/challenge/PR reasoning;
- `TopReviewer` — focused high-risk security/resilience.

Agent identities are semantic rather than model-branded, so profile changes do not make delegation names or descriptions stale.

### Claude Code

Visible: `/dev`, `/review-pr`.

Hidden specialists:

- `smart-fast` — read-only exploration, deterministic execution, and complexity measurement;
- `smart-worker` — normal/mechanical implementation of one commit-sized unit;
- `smart-deep-reasoner` — read-only deep reasoning;
- `smart-deep-implementer` — complex implementation;
- `smart-top-reviewer` — architecture/security/adjudication.

Normal implementation uses one configured normal worker per independent commit-sized unit. This creates a real writer boundary while keeping the coordinator focused on dependency planning and integration.

### Capability boundary

Fast exploration agents have no structured edit/write tools, and exploration mode does not invoke shell execution. Verification necessarily executes repository commands, which may create caches or build outputs even when no source edit is intended; execution lanes therefore capture Git status before/after and use the delegated worktree. Pi additionally enforces capability allowlists, root-confined working directories, sanitized environments, and opt-in auto-approval. Prompt-level “read-only” wording is not treated as an operating-system sandbox.

### Pi

Visible: `/dev`, `/review-pr`. A bundled standard-library helper can run independent Pi print-mode children concurrently; no external extension is required.

## Development routing

```text
exploration/measurement/verification -> fast read-only
mechanical/normal implementation     -> normal
complex/debugging                    -> deep
architecture/security               -> top only when warranted
```

For normal low-risk work, passing behavior tests plus compiler/type/static evidence can complete the task without another premium semantic review.

## PR review flow

```text
resolve exact base + PR HEAD
  -> detached worktree
  -> inspect commit/work-unit coherence and live documentation
  -> parallel:
       semantic deep review
       full deterministic execution
  -> if HIGH_RISK:
       adversarial scenarios
       focused security/resilience
  -> falsify candidate BLOCKER/MAJOR
  -> recommendation + evidence
  -> cleanup
```

## Invariants

1. Every implementation unit runs `plan -> implement -> document -> simplify -> verify`.
2. Non-trivial work is decomposed into coherent, independently committable units.
3. Parallelism requires real independence; writers require isolated ownership/worktrees.
4. Live authoritative documentation changes in the same logical commit as code, or the commit records a concrete no-impact reason.
5. Changed-function complexity is measured and increases are explained; scores are not gamed at the expense of cohesion.
6. Unexecuted checks are never PASS.
7. PR review executes complete feasible configured unit and integration suites at exact PR HEAD.
8. Premium-model fan-out is conditional on uncertainty/risk.
9. Product behavior specification generation is explicit, never automatic.
10. Runtime setup performs no external dependency installation.
