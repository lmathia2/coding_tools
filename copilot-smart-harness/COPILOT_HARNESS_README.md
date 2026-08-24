# Copilot Smart Harness v0.4.0

## The whole interface

You only need to remember two custom agents:

- **Dev** — coding, planning, refactoring, debugging
- **ReviewPR** — reviewing somebody else's pull request

Everything else is hidden and routed automatically.

The design goal is: **correct and fast with high quality first; save tokens where doing so does not materially reduce quality.**

## Install

From the repository root:

```bash
unzip /path/to/copilot-smart-harness-v0.4.0.zip
```

No Git pulls, skill installs, plugins, MCP servers, npm/pip installs, or external runtime dependencies are required.

Open VS Code and run **Chat: Open Customizations**. You should see only `Dev` and `ReviewPR` as user-facing agents.

## One-time model setting

Leave thinking effort at **VS Code's Adaptive/default** for Opus 5 and GPT-5.6 Sol. VS Code recommends adaptive reasoning for most tasks and increasing effort manually only for genuinely difficult architecture/debugging.

The two coordinators are deliberately pinned to **Claude Opus 5**, not Auto. VS Code currently will not let a subagent use a model in a higher cost tier than its parent. An Auto parent could be routed to Terra/Sonnet and then be unable to invoke Sol/Opus. The Opus coordinator stays context-light and delegates before broad exploration.

## Dev routing

```text
                  Dev — Opus coordinator
                           |
        +------------------+------------------+
        |                  |                  |
   mechanical            normal            complex
     Terra             Sonnet 5              Sol
                                               |
                                  architecture/high risk?
                                      /             \
                                    no              yes
                                    |         Opus + one Sol
                                  done          challenge
```

- **Terra**: deterministic/local work.
- **Sonnet 5**: default ordinary engineering.
- **Sol**: complex implementation and hard debugging.
- **Opus + Sol**: architecture/high-consequence decisions only.

No automatic multi-round debate.

## ReviewPR routing

Every non-trivial PR gets:

```text
               Opus lead
                 /    \
        Sol core       Terra execution
     design+correctness tests+static checks
                 \    /
                synthesis
```

Only high-risk PRs add:
- Sol adversarial behavior/test design
- Opus security/resilience

Only BLOCKER/MAJOR findings get a fresh Sol verification pass to reduce false positives.

## Auto

Auto is still excellent for ordinary standalone Copilot chat. The harness does not use Auto for its coordinator because of the parent/subagent cost-tier rule above.

## Skills

The ZIP includes a small automatic skill set: verification-before-completion, systematic-debugging, pragmatic-tdd, codebase-map, task-ledger, pr-behavioral-review, and security-resilience-review.

You do not invoke skills manually.

## Normal usage

For coding: select **Dev**, describe the task, and let it work.

For PR review: check out the PR, select **ReviewPR**, and say e.g. `Review this against origin/main and run relevant integration/static checks.`

That's it.

## References
- https://code.visualstudio.com/docs/agents/run/subagents
- https://code.visualstudio.com/docs/agent-customization/language-models
- https://code.visualstudio.com/docs/agents/guides/optimize-usage
- https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing
