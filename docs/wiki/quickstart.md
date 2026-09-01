# Quickstart

WYSIWYShip is a host-portable SDLC policy for developers who want a coding agent
to resolve the important decisions up front, then implement, document, simplify,
verify, and explain the result with executable evidence.

## Install in five minutes

You need Bash, Python 3, a project directory, and at least one supported coding
host. The harness itself adds no Python, npm, MCP, or external-skill dependency.

```bash
git clone https://github.com/lmathia2/coding_tools.git ~/src/coding_tools
cd ~/src/coding_tools
bash wysiwyship/install.sh all /absolute/path/to/project
```

Use `codex`, `copilot`, `claude`, or `pi` instead of `all` to install one adapter.
The project installer copies the portable policy and tools, detects supported
model routes, writes an install manifest, and initializes `docs/wiki/` without
overwriting an existing wiki.

## Start a feature

Reload the host at the installed project root. In Codex, make a normal coding
request or invoke `$engineering-workflow`; in Copilot select `Dev`; in Claude or
Pi use `/dev <task>`. The first interaction is a planning grill. After you approve
the decision record, routine implementation proceeds with minimal interruption.

Use `auto` only when you want the workflow to ask and answer the planning
questions itself. It does not broaden permissions or scope.

## What appears in the project

- host-native skills, commands, or agents in the host's own directories;
- `.wysiwyship/` with portable tools, configuration, provenance, and manifest;
- `docs/wiki/` with versioned developer pages and a refresh marker;
- ignored `.agent-state/` for work ledgers, temporary drafts, and ELI5.

## Verify or upgrade

```bash
bash wysiwyship/install.sh all /absolute/path/to/project --status
python3 /absolute/path/to/project/.wysiwyship/tools/check.py <base-ref> --head HEAD
```

The composed check evaluates per-commit authoritative documentation, changed
Python complexity, wiki structure and refresh cadence, configured
project commands, and optional work-unit state. The wiki is rebuilt every five
commits by default; set `wiki.refresh_every_commits` to `1` for every commit.
