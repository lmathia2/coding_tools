# Smart Harness Architecture

## Purpose

Provide one self-contained, high-quality, low-friction development interface across VS Code Copilot, Claude Code, and Pi while sharing engineering policy and routing specialized work to the appropriate model/tool context.

## Goals

- two everyday workflows: development and PR review;
- plan before editing;
- safe parallelism;
- execution-based verification;
- documentation synchronized with behavior;
- outside-in product behavior specifications when requested or already present;
- isolated PR review worktrees;
- centralized model configuration;
- selected methodology/context capabilities stored locally with no runtime network dependency.

## Non-goals

- replace repository-specific architecture or build tooling;
- make every task multi-agent;
- treat a worktree as a security sandbox;
- auto-enable every upstream skill or extension;
- use documentation as a substitute for executable tests;
- force every repository to maintain a product behavior specification;
- silently track upstream plugin behavior.

## Layers

### Shared policy and local skills

`shared/skills/` contains provider-neutral process, quality, methodology, minimality, context, documentation, product-behavior, and review contracts.

Third-party-derived skills are curated and adapted locally; provenance and licenses live under `vendor/`. Conceptual inspirations without a usable license are recorded separately and implemented independently.

### Platform adapters

- `copilot/agents/`
- `claude-code/agents/` and `claude-code/commands/`
- `pi/prompts/` and bundled `pi/tools/`

Adapters translate shared policy into native orchestration primitives. Pi uses a standard-library helper to run independent print-mode children concurrently without an extension package.

### Configuration

`config/models.json` is the model source of truth. `config/configure-models.py` applies it using only local files.

### Documentation

Human-authored architecture and policy live in `docs/`. `docs/REFERENCE.md` is generated from local model and skill/provenance configuration.

An optional repository-level outside-in specification normally lives under `docs/product-behavior/` and is governed by `product-behavior-spec` plus `documentation-sync`.

## Development flow

```text
request
  -> proportional plan
  -> documentation impact
  -> context snapshot + parallel evidence
  -> accepted dependency-aware plan
  -> Ponytail minimum-correct-design gate
  -> scoped implementation or product-behavior drafting
  -> code + tests + docs
  -> unit/integration/static/docs/behavior verification
  -> complexity review + focused semantic review where risk warrants
```

For non-trivial work, `superpowers-methodology` supplies design, isolation, executable-plan, TDD, delegated execution, review, and completion discipline without the upstream plugin runtime.

For outside-in behavior documentation, `product-behavior-spec` adds scope/product-shape mapping, a pilot and foundations, parallel feature drafting, stable verification items, and consolidated behavior triage.

## PR review flow

```text
PR metadata + exact HEAD
  -> review plan/context snapshot
  -> detached worktree
  -> parallel semantic, execution, documentation, behavior-spec, and complexity lanes
  -> high-risk adversarial/security lanes
  -> falsify high-severity findings
  -> evidence report
  -> remove worktree
```

## Invariants

1. No source edit before a plan.
2. Documentation impact is assessed in every plan.
3. Behavior/API/architecture changes update required docs in the same change.
4. Existing product behavior specifications stay synchronized with user-visible changes.
5. Required checks are never reported as passing unless executed.
6. Parallel writers require isolated ownership/worktrees.
7. PR review runs against exact committed PR HEAD.
8. Minimality cannot weaken safety, documentation, tests, compatibility, or accepted requirements.
9. Runtime setup never downloads another skill, plugin, package, or repository.
