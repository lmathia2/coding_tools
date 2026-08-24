# Smart Harness — Copilot + Claude Code

One canonical harness for both **VS Code / GitHub Copilot** and **Claude Code**.

## The interface

You only need two workflows on either platform:

- **Dev** / `/dev` — build, fix, refactor, debug
- **ReviewPR** / `/review-pr` — deep, execution-based review of somebody else's PR

Everything else is hidden orchestration.

## One shared skill library

The two harnesses use the **same canonical engineering skills** from:

```text
smart-harness/shared/skills/
```

When installed, those skills are copied once to `.claude/skills/` for a project or `~/.claude/skills/` globally. Claude Code uses that location natively, and current VS Code Copilot also discovers Agent Skills there.

So there is no separate Copilot-vs-Claude copy to maintain.

## Repository layout

```text
smart-harness/
  shared/skills/              # canonical skills used by BOTH harnesses
    plan-first/
    parallel-work/
    engineering-core/
    codebase-map/
    task-ledger/
    pr-review/

  copilot/
    agents/                   # VS Code Copilot Dev/ReviewPR + hidden workers
    github-skills/            # GitHub.com native Copilot code-review guidance

  claude-code/
    agents/                   # Claude Code hidden subagents
    commands/                 # Claude-only /dev and /review-pr entry points

  config/
    models.json               # all model choices in ONE place
    configure-models.py       # applies model config to both harnesses

  templates/
    CLAUDE.md.example

  install.sh                  # install into one project
  install-global.sh           # install once for this machine
```

Claude's entry points live under `.claude/commands`, rather than the shared skill directory, so installing both products does not create duplicate `/dev` or `/review-pr` skill definitions.

## Install both into a project

```bash
bash smart-harness/install.sh both /path/to/project
```

Or one platform only:

```bash
bash smart-harness/install.sh copilot /path/to/project
bash smart-harness/install.sh claude /path/to/project
```

Installed layout:

```text
project/
  .claude/
    skills/       # ONE shared skill library used by both products
    agents/       # Claude-only subagents
    commands/     # Claude-only /dev and /review-pr
  .github/
    agents/       # Copilot-only Dev/ReviewPR + hidden workers
    skills/       # GitHub.com native Copilot code-review guidance
```

Re-running the installer syncs updates. Replaced files are backed up under `.smart-harness-backups/` rather than inside a discoverable skills directory.

## Install once for the whole machine

If these are personal defaults across repositories:

```bash
bash smart-harness/install-global.sh both
```

That installs:

```text
~/.claude/skills/     # shared by Claude Code + VS Code Copilot
~/.claude/agents/     # Claude-only
~/.claude/commands/   # Claude-only /dev and /review-pr
~/.copilot/agents/    # Copilot-only
```

Project-local rules and customizations can still override/augment the global setup.

## Models: edit one file

Edit:

```text
smart-harness/config/models.json
```

Then run:

```bash
python3 smart-harness/config/configure-models.py
```

The model identifiers are deliberately opaque strings. When model generations change, update that file instead of redesigning the harness.

Current defaults:

### Copilot

- coordinator/top: Claude Opus 5
- normal implementation: Claude Sonnet 5
- deep reasoning/implementation: GPT-5.6 Sol
- fast exploration/execution: GPT-5.6 Terra

### Claude Code

- coordinator/normal: Sonnet 4.6 1M (`sonnet[1m]`)
- fast: Haiku 4.5 200K (`haiku`)
- deep: Opus 4.7 1M
- top: Opus 4.8 1M

Change the IDs/effort values as your available models evolve.

# Non-negotiable workflow rules

## 1. Always plan before editing

Every coding task starts with a plan. Plan depth is proportional to risk:

- trivial change: 1–3 step micro-plan;
- ordinary feature: explicit implementation + verification plan;
- complex/high-risk change: codebase evidence + architecture plan + independent challenge.

No worker should begin source edits before the coordinator has an accepted plan.

## 2. Parallelize independent work

The harness parallelizes genuinely independent work:

- repository exploration of separate modules;
- competing debugging hypotheses;
- architecture/correctness/security review perspectives;
- static analysis and test execution;
- independent unit/integration suites when they do not contend for shared resources.

Writing is parallelized only when components are cleanly separable **and** isolated worktrees/branches prevent collisions. Sequential dependencies remain sequential.

Claude Code uses subagents for normal parallelism. Agent Teams are reserved for rare large tasks where independent peers need sustained direct collaboration.

## 3. PR review is execution-based, not diff-only

`ReviewPR` / `/review-pr` must create an isolated Git worktree at the committed PR HEAD and review **that checkout**.

It must:

1. plan the review before executing it;
2. inspect design, architecture, correctness, and runtime wiring;
3. run the complete feasible configured **unit-test suite**;
4. run the complete feasible configured **integration-test suite**;
5. run relevant e2e/runtime tests when configured and feasible;
6. run compiler/build/type/lint/static-analysis checks;
7. perform adversarial behavioral review;
8. perform security/resilience review when risk warrants it;
9. clearly mark unavailable checks **NOT EXECUTED**, never PASS;
10. independently verify/falsify BLOCKER/MAJOR findings.

Static reasoning and dynamic test/static execution run in parallel where safe.

If PR-head tests fail and regression status is unclear, the harness should run the failing subset against the base commit in a temporary base worktree when practical.

## PR worktree protocol

The shared `pr-review` skill defines the portable flow:

```bash
git worktree add --detach <review-dir> <PR_HEAD_SHA>
```

All review reads, tests, analyzers, and probes target that worktree. The developer's main checkout is not edited.

After the report:

```bash
git worktree remove --force <review-dir>
git worktree prune
```

A worktree is a code-isolation boundary, not a security sandbox.

# Managing both on the same machine

The simplest approach is:

1. clone `coding_tools` once;
2. treat `smart-harness/` as the source of truth;
3. edit shared skills only under `smart-harness/shared/skills/`;
4. edit models only in `smart-harness/config/models.json`;
5. rerun the installer to sync one or more projects.

Example:

```bash
cd coding_tools
python3 smart-harness/config/configure-models.py
bash smart-harness/install.sh both ~/src/project-a
bash smart-harness/install.sh both ~/src/project-b
```

Or use the global installer if the harness should be your default everywhere:

```bash
bash smart-harness/install-global.sh both
```

Repository-specific facts belong in each project's `CLAUDE.md`, `.claude/rules/`, ADRs, schemas, and tests. Do not fork shared skills just to store project facts.

# Old folders

`copilot-smart-harness/` and `claude-code-smart-harness/` are retained temporarily as compatibility snapshots. **`smart-harness/` is the canonical source going forward.**

# References

- VS Code subagents / parallel orchestration: https://code.visualstudio.com/docs/agents/run/subagents
- VS Code worktree isolation: https://code.visualstudio.com/docs/agents/concepts/agent-harnesses
- VS Code Agent Skills: https://code.visualstudio.com/docs/agent-customization/agent-skills
- Claude Code subagents: https://code.claude.com/docs/en/sub-agents
- Claude Code worktrees: https://code.claude.com/docs/en/worktrees
- Claude Code skills: https://code.claude.com/docs/en/skills
- Claude Code agent teams: https://code.claude.com/docs/en/agent-teams
