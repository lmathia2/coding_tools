# Smart Harness Architecture

## Purpose

Provide one high-quality, low-friction development interface across VS Code Copilot, Claude Code, and Pi while sharing engineering policy and routing specialized work to the right model/tool context.

## Goals

- two everyday workflows: development and PR review;
- plan before editing;
- safe parallelism;
- execution-based verification;
- documentation synchronized with behavior;
- isolated PR review worktrees;
- centralized model and integration configuration;
- optional methodologies without polluting the default workflow.

## Non-goals

- replace repository-specific architecture or build tooling;
- make every task multi-agent;
- treat a worktree as a security sandbox;
- auto-enable every third-party skill or Pi extension;
- use documentation as a substitute for executable tests.

## Layers

### Shared policy

`shared/skills/` contains provider-neutral process and quality contracts.

### Platform adapters

- `copilot/agents/`
- `claude-code/agents/` and `claude-code/commands/`
- `pi/prompts/`

Adapters translate shared policy into native orchestration primitives.

### Configuration

`config/models.json` is the model source of truth.

`integrations/upstreams.lock.json` tracks optional external projects.

`pi/extensions.json` defines curated Pi extension profiles.

### Documentation

Human-authored architecture and policy live in `docs/`.

`docs/REFERENCE.md` is generated from canonical configuration.

## Execution flow

```text
request
  -> proportional plan
  -> documentation impact
  -> parallel evidence gathering
  -> accepted dependency-aware plan
  -> scoped implementation
  -> code + tests + docs
  -> unit/integration/static/docs verification
  -> focused independent review where risk warrants
```

## PR review flow

```text
PR metadata + exact HEAD
  -> review plan
  -> detached worktree
  -> parallel semantic review and full executable checks
  -> documentation + security/resilience lanes
  -> falsify high-severity findings
  -> report
  -> remove worktree
```

## Invariants

1. No source edit before a plan.
2. Documentation impact is assessed in every plan.
3. Behavior/API/architecture changes update required docs in the same change.
4. Required checks are never reported as passing unless executed.
5. Parallel writers require isolated ownership/worktrees.
6. PR review runs against exact committed PR HEAD.
7. Optional methodologies cannot weaken safety or documentation invariants.
