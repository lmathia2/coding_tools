# Claude Code Smart Harness

A Claude Code-native version of the smart coding harness, designed around the same principle as the Copilot version:

> **Get the work correct and fast at high quality. Save tokens where doing so does not materially reduce quality.**

## The whole interface

You only need to remember two skills:

```text
/dev <task>          build, fix, refactor, debug, plan
/review-pr <details> review somebody else's pull request
```

Everything else is hidden subagent routing.

## Why this is different from the Copilot harness

Claude Code has a better native primitive for this design: the **main conversation + isolated subagents**. Subagents cannot spawn other subagents, so the main `/dev` or `/review-pr` turn coordinates them. This keeps the interface simple while preserving isolated contexts for expensive reasoning and noisy test/search work.

Claude Code also already has a built-in **Explore** subagent that uses Haiku for codebase search. The harness uses that instead of inventing another explorer.

Agent Teams are deliberately **not** used by default. Anthropic documents them as higher-overhead and higher-token than subagents; they are useful when workers need sustained peer-to-peer coordination, not for the normal coding/review workflows here.

## Default model mapping

The shipped configuration reflects the models currently available to this setup:

| Role | Default model | Context | Effort | Purpose |
|---|---|---:|---|---|
| Coordinator / normal coding | `sonnet[1m]` | 1M | high | Most day-to-day engineering and orchestration |
| Fast execution/search | `haiku` | 200K | model default | Deterministic test/static execution; built-in Explore |
| Deep reasoning | `claude-opus-4-7` | 1M available | xhigh | Difficult implementation, debugging, architecture challenge, deep PR reasoning |
| Top reasoning | `claude-opus-4-8` | 1M available | high | Architecture lead/adjudication, security/resilience, high-severity verification |

The exact model strings are configurable in one file:

```text
.claude/harness/model-config.json
```

When your model inventory changes, edit that file and run once:

```bash
python3 .claude/harness/configure-models.py
```

That rewrites only the `model:` and `effort:` frontmatter for the harness skills/agents. You do **not** need to edit every agent definition.

Use any model value Claude Code accepts via `/model` or `--model`: aliases such as `sonnet[1m]` / `opus[1m]`, full Anthropic model IDs, or provider-specific deployment names. If your provider exposes a specific 1M-qualified model string, put that exact string in the config.

## Install into a repository

Clone/download `coding_tools`, then:

```bash
bash claude-code-smart-harness/install-workspace.sh /path/to/target-repo
```

The installer copies:

```text
.claude/agents/
.claude/skills/
.claude/harness/
```

It backs up same-name harness files before replacing them and does not overwrite an existing `CLAUDE.md`.

If the target repo has no `CLAUDE.md`, it copies `CLAUDE.md.example` for you to customize.

Restart the Claude Code session after installing/editing agent files; Claude Code loads project subagents at session startup.

## `/dev`

For ordinary work, **Sonnet 4.6 does the task directly in the main context**. This is intentional: Anthropic recommends the main conversation when planning, implementation, and testing share significant context and latency matters.

The harness escalates only when the problem changes:

```text
                         /dev
                  Sonnet coordinator
                          |
          +---------------+----------------+
          |               |                |
       normal          complex        architecture/
       work            reasoning        high risk
          |               |                |
      Sonnet       Opus 4.7 worker   Opus 4.8 architect
      directly            |           + Opus 4.7 challenge
          |               |                |
          +---------------+----------------+
                          |
                     verification
                          |
            high-risk implementation?
                     /          \
                   no            yes
                   |         Opus 4.8 review
                 done
```

For ambiguous bugs, Opus 4.7 diagnoses root cause in an isolated read-only context before implementation begins.

For architecture/high-consequence changes, the default is one independent Opus 4.8 design plus one independent Opus 4.7 challenge. A fresh Opus 4.8 adjudication pass is used only when there is material disagreement. There is no automatic endless debate.

## `/review-pr`

Normal PR review:

```text
                  Sonnet coordinator
                    /            \
          Opus 4.7 core       Haiku verifier
          design/correctness  tests/static checks
                    \            /
                       synthesis
```

High-risk PRs conditionally add:

- Opus 4.8 security/resilience review
- Opus 4.7 adversarial behavior/test design
- fresh Opus 4.8 verification of proposed BLOCKER/MAJOR findings

The review is explicitly behavior-oriented: architecture, runtime wiring, error/state/concurrency behavior, integration tests, static analysis, security and resiliency where relevant.

## Why the main coordinator is Sonnet rather than Opus

Unlike the current VS Code/Copilot subagent tier restriction, Claude Code lets the main conversation delegate to explicitly configured subagent models. That means the coordinator does not need to consume Opus tokens on every turn.

Sonnet is therefore the smart default for orchestration and normal implementation; Opus contexts are created only for tasks that benefit from them.

## Model effort

Claude Code supports per-skill and per-subagent effort. The defaults here are conservative about quality:

- Sonnet coordinator: `high`
- Opus 4.7 deep worker: `xhigh`
- Opus 4.8 top worker: `high` by default; change to `xhigh` in the model config if supported in your environment and desired
- Haiku verifier: no explicit effort override

`max` is intentionally not a workflow default. Anthropic notes it can show diminishing returns and overthinking. Use it as a deliberate one-off when needed.

## Memory

The harness does **not** enable persistent subagent memory by default. That avoids stale architectural beliefs entering reviews and avoids always loading another memory index.

Use:

```text
CLAUDE.md / .claude/rules/  stable repository truth
skills                      repeatable procedures
ADRs/design docs            architecture decisions
.agent-state/               long-running task state only
executable tests/checks     behavioral invariants whenever possible
```

Claude Code's normal auto-memory remains available if you use it.

## No extra infrastructure

The harness requires no MCP servers, hooks, plugins, Agent Teams, npm packages, or Python packages. Python is used only by the optional model-config updater and only from the standard library.

## Official references

- Subagents: https://code.claude.com/docs/en/sub-agents
- Skills: https://code.claude.com/docs/en/slash-commands
- Model configuration and effort: https://code.claude.com/docs/en/model-config
- Extension/context guidance: https://code.claude.com/docs/en/features-overview
- Agent teams comparison: https://code.claude.com/docs/en/agent-teams
