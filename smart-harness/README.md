# Smart Harness — Copilot + Claude Code

One canonical harness for both **VS Code / GitHub Copilot** and **Claude Code**.

## The interface

You only need two workflows on either platform:

- **Dev** / `/dev` — build, fix, refactor, debug
- **ReviewPR** / `/review-pr` — deep review of somebody else's PR

Both harnesses share the same engineering skills. Platform-specific agents live separately.

## Repository layout

```text
smart-harness/
  shared/skills/              # canonical skills used by BOTH harnesses
  copilot/agents/             # VS Code Copilot agents
  copilot/github-skills/      # GitHub.com native Copilot review skill
  claude-code/agents/         # Claude Code subagents
  claude-code/skills/         # /dev and /review-pr entry points
  config/models.json          # all model choices in ONE place
  config/configure-models.py  # applies model config to both harnesses
  install.sh                  # install copilot | claude | both
```

## Install both into the same project

```bash
bash smart-harness/install.sh both /path/to/project
```

Or one platform only:

```bash
bash smart-harness/install.sh copilot /path/to/project
bash smart-harness/install.sh claude /path/to/project
```

When `both` is installed, shared skills are copied **once** to `.claude/skills/`. Current VS Code Copilot discovers Agent Skills from `.claude/skills`, and Claude Code uses that location natively.

Installed layout:

```text
project/
  .claude/
    skills/       # shared skills + Claude /dev and /review-pr
    agents/       # Claude-only subagents
  .github/
    agents/       # Copilot-only agents
    skills/       # GitHub.com Copilot code-review guidance
```

This means there is no duplicate copy of shared skills inside one working project.

## Models: edit one file

Edit:

```text
smart-harness/config/models.json
```

Then run:

```bash
python3 smart-harness/config/configure-models.py
```

The script accepts arbitrary model identifiers, so model generations can change without redesigning the harness.

Defaults currently reflect the available model sets discussed when this harness was built.

## Non-negotiable workflow rules

### 1. Always plan before editing

Every coding task starts with a plan. Plan depth is proportional to risk:

- trivial change: 1–3 step micro-plan
- ordinary feature: explicit implementation + verification plan
- complex/high-risk change: codebase evidence + architecture plan + independent challenge

No worker should begin edits before the coordinator has an accepted plan.

### 2. Parallelize independent work

The harness should parallelize when work is genuinely independent:

- repository exploration
- competing hypotheses
- architecture / correctness / security review perspectives
- static analysis and test execution
- independent test suites when they do not contend for shared resources

Writing is parallelized only when components are cleanly separable and isolated worktrees/branches prevent collisions. Sequential dependencies stay sequential.

### 3. PR review is execution-based, not diff-only

`ReviewPR` / `/review-pr` must create an isolated Git worktree at the PR HEAD and review **that checkout**.

It must:

1. inspect design, architecture, correctness, and wiring;
2. run the complete discoverable unit-test suite;
3. run the complete discoverable integration-test suite;
4. run relevant e2e/runtime tests when configured and feasible;
5. run compiler/type/lint/static-analysis checks;
6. perform adversarial behavioral review;
7. perform security/resilience review when risk warrants it;
8. clearly mark anything blocked by unavailable credentials/services as **NOT EXECUTED**, never PASS.

Static review and test/static execution should run in parallel where safe.

If the PR fails a test, run the failing subset against the base commit when practical to distinguish a PR regression from a pre-existing failure.

## Worktree behavior for PR review

The shared `pr-review` skill defines the portable protocol:

```bash
git worktree add --detach <review-dir> <PR_HEAD_SHA>
```

All reads and execution happen inside that worktree. The source checkout is not edited.

The worktree is removed after the report unless it is useful to preserve it for investigation.

A worktree is a code-isolation boundary, not a security sandbox.

## Parallelism by platform

### Copilot

The `Dev` and `ReviewPR` coordinators explicitly ask VS Code to launch independent custom subagents in parallel. VS Code supports parallel subagent execution and isolated contexts.

### Claude Code

Claude Code uses parallel subagents for independent work. The harness does **not** require Agent Teams for normal work: Anthropic recommends teams only where independent peers need sustained collaboration, because they add coordination/token overhead. Teams remain an optional escalation for a clearly partitioned large feature.

## Managing both on one machine

Recommended: clone `coding_tools` once and treat `smart-harness/` as the source of truth.

When you change a model or skill:

```bash
cd coding_tools
python3 smart-harness/config/configure-models.py
bash smart-harness/install.sh both /path/to/project
```

Repeat the installer for other projects that should receive the update.

For project-specific rules, edit the target project's `CLAUDE.md` / `.claude/rules/`; do not fork shared skills unless the workflow genuinely differs.

## Old folders

`copilot-smart-harness/` and `claude-code-smart-harness/` are retained temporarily as v0.x compatibility snapshots. **`smart-harness/` is the canonical source going forward.**

## References

- VS Code subagents / parallel orchestration: https://code.visualstudio.com/docs/agents/run/subagents
- VS Code worktree isolation: https://code.visualstudio.com/docs/agents/concepts/agent-harnesses
- Claude Code subagents: https://code.claude.com/docs/en/sub-agents
- Claude Code worktrees: https://code.claude.com/docs/en/worktrees
- Claude Code skills: https://code.claude.com/docs/en/skills
- Claude Code agent teams: https://code.claude.com/docs/en/agent-teams
