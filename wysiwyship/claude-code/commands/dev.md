---
description: Default development command. Plans before editing, uses the cheapest capable model, parallelizes only useful independent work, keeps authoritative docs synchronized, and verifies before completion.
argument-hint: <coding task>
model: sonnet[1m]
effort: high
---
<!-- harness-role: coordinator -->
<!-- harness-workflow: dev -->

# /dev

Task: $ARGUMENTS

Use `engineering-workflow` as the complete development policy.

Resolve routes with `routing.py plan --host claude --workflow dev`. Invoke the
named subagent through Claude's Agent tool, including its plugin namespace when
present. Retain and validate the receipt; report unavailable effective settings
as `UNVERIFIED`. Do not replace a missing specialist with an unreported generic
agent.
