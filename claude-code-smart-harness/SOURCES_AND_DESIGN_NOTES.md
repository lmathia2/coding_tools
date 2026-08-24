# Design Notes and Sources

This harness uses Claude Code-native primitives rather than mechanically translating the VS Code/Copilot files.

## Key design choices

### Main Sonnet context for ordinary work

Anthropic recommends the main conversation when a task needs frequent back-and-forth, shares substantial context across planning/implementation/testing, or latency matters. Subagents are used when isolation or specialization is worth the fresh context cost.

Source: https://code.claude.com/docs/en/sub-agents

### Built-in Explore instead of a custom search agent

Claude Code's built-in Explore subagent is read-only and Haiku-based, specifically for codebase discovery/search. The `/dev` workflow can use it naturally rather than carrying another custom explorer.

Source: https://code.claude.com/docs/en/sub-agents

### Subagents, not Agent Teams, by default

Anthropic documents subagents as lower-overhead workers that return summaries to the parent. Agent Teams add separate full sessions, shared task coordination and peer messaging, and use substantially more tokens. Teams are valuable when workers must communicate independently; that is not required for the two default workflows here.

Source: https://code.claude.com/docs/en/agent-teams

### Skills as the user interface

Skills are the recommended successor to custom commands and can be directly invoked as `/dev` and `/review-pr`. `disable-model-invocation: true` makes these user-triggered workflows cost zero context until invoked.

Source: https://code.claude.com/docs/en/slash-commands

### Model and effort per role

Claude Code supports model and effort fields on skills and custom subagents. Full model IDs and aliases are accepted. Effort can be low/medium/high/xhigh/max where supported; Anthropic warns that max can show diminishing returns/overthinking.

Source: https://code.claude.com/docs/en/model-config

### Central model configuration

Claude Code does not natively interpolate variables into Markdown frontmatter. This harness therefore keeps an explicit `.claude/harness/model-config.json` plus a small standard-library Python updater. Daily use never depends on that script; it is only for changing role mappings when the available models change.

### No persistent subagent memory by default

Claude Code supports `memory: user|project|local` for subagents. The harness leaves it off by default to reduce stale-review risk and startup context. Repository truth should live in `CLAUDE.md`, rules, tests and ADRs; task state can use a temporary ledger when necessary.

Source: https://code.claude.com/docs/en/sub-agents
