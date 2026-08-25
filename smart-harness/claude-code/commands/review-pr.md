---
description: Default PR review command. Reviews exact PR HEAD in an isolated worktree using one semantic lane plus one executable lane, escalating to adversarial/security specialists only for high-risk changes.
argument-hint: [base-ref] [PR intent/details]
model: sonnet[1m]
effort: high
---
<!-- harness-role: coordinator -->

# /review-pr

Review request: $ARGUMENTS

Use `pr-review`.

1. Resolve exact base/HEAD, intent, changed boundaries, authoritative commands, and risk.
2. Create the detached PR-head worktree required by `pr-review`.
3. Launch together:
   - `smart-deep-reasoner` in PR_CORE mode;
   - `smart-fast` in PR_EXEC mode.
4. For HIGH_RISK changes, add only the relevant specialist lanes:
   - `smart-deep-reasoner` PR_ADVERSARIAL;
   - `smart-top-reviewer` SECURITY_RESILIENCE.
5. If a BLOCKER/MAJOR is proposed, launch a fresh `smart-deep-reasoner` VERIFY_FINDING for that finding before publishing high severity.
6. Synthesize the recommendation and clean up worktrees.

Product-behavior documentation is checked only when it already exists and the PR changes behavior it covers. There is no separate minimality/Ponytail lane; simplicity is part of PR_CORE.
