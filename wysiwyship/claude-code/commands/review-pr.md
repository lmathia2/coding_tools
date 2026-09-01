---
description: Default PR review command. Reviews exact PR HEAD in an isolated worktree using one semantic lane plus one executable lane, escalating to adversarial/security specialists only for high-risk changes.
argument-hint: "[base-ref] [PR intent/details]"
model: sonnet[1m]
effort: high
---
<!-- harness-role: coordinator -->
<!-- harness-workflow: review-pr -->

# /review-pr

Review request: $ARGUMENTS

Use `pr-review` as the complete review policy.

Resolve routes with `routing.py plan --host claude --workflow review_pr`.
Invoke the named subagent through Claude's Agent tool, including its plugin
namespace when present, then validate its receipt. Never silently substitute a
generic agent.
