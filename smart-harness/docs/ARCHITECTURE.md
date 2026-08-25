# Smart Harness Architecture

## Purpose

Provide one high-quality coding interface across Copilot, Claude Code, and Pi without requiring the developer to remember model or workflow commands.

## Goals

- two user-facing workflows: development and PR review;
- quality-first model routing with token/latency discipline;
- planning before source edits;
- useful parallelism without agent fan-out for its own sake;
- smallest correct implementation;
- authoritative documentation synchronized with behavior;
- executable verification;
- exact-HEAD isolated PR review;
- self-contained installation.

## Default execution shape

```text
request
  -> coordinator makes proportional plan
  -> one implementation context
  -> deterministic verification
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

## Platform adapters

### Copilot

Visible: `Dev`, `ReviewPR`.

Hidden specialists:

- `FastTerra` — exploration, deterministic execution, mechanical edits;
- `WorkerSonnet` — normal implementation;
- `WorkerSol` — complex implementation;
- `DeepSol` — read-only debugging/challenge/PR reasoning;
- `SecurityOpus` — focused high-risk security/resilience.

The Opus coordinator remains pinned so Copilot can legally dispatch all configured specialist tiers.

### Claude Code

Visible: `/dev`, `/review-pr`.

Hidden specialists:

- `smart-fast` — Haiku exploration, deterministic execution, mechanical edits;
- `smart-deep-reasoner` — Opus 4.7 read-only deep reasoning;
- `smart-deep-implementer` — Opus 4.7 complex implementation;
- `smart-top-reviewer` — Opus 4.8 architecture/security/adjudication.

Normal implementation stays in the Sonnet coordinator conversation to avoid unnecessary context duplication.

### Pi

Visible: `/dev`, `/review-pr`. A bundled standard-library helper can run independent Pi print-mode children concurrently; no external extension is required.

## Development routing

```text
mechanical/tool-heavy -> fast
normal                 -> Sonnet
complex/debugging      -> Sol / Opus 4.7
architecture/security  -> Opus only when warranted
```

For normal low-risk work, passing behavior tests plus compiler/type/static evidence can complete the task without another premium semantic review.

## PR review flow

```text
resolve exact base + PR HEAD
  -> detached worktree
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

1. No source edit before a proportional plan.
2. Parallelism requires real independence; writers require isolated ownership/worktrees.
3. Affected authoritative documentation changes with code.
4. Unexecuted checks are never PASS.
5. PR review executes complete feasible configured unit and integration suites at exact PR HEAD.
6. Premium-model fan-out is conditional on uncertainty/risk.
7. Product behavior specification generation is explicit, never automatic.
8. Runtime setup performs no external dependency installation.
