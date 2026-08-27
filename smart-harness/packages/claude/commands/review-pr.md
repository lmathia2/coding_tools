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

Use `smart-harness:pr-review`.

1. Resolve exact base/HEAD, intent, logical commit/work-unit order, changed boundaries, authoritative commands, and risk.
2. Create the detached PR-head worktree required by `smart-harness:pr-review`.
3. Launch together:
   - `smart-harness:smart-deep-reasoner` in PR_CORE mode;
   - `smart-harness:smart-fast` in PR_EXEC mode for full feasible unit/integration execution plus relevant runtime/static/docs checks.
4. Check each implementation commit for coherent `plan -> implement -> document -> simplify -> verify` evidence, live documentation in the same commit (or `Docs-Impact: none — <reason>`), and changed-function complexity score/delta.
5. For HIGH_RISK changes, add only the relevant specialist lanes:
   - `smart-harness:smart-deep-reasoner` PR_ADVERSARIAL;
   - `smart-harness:smart-top-reviewer` SECURITY_RESILIENCE.
6. If a BLOCKER/MAJOR is proposed, launch a fresh `smart-harness:smart-deep-reasoner` VERIFY_FINDING for that finding before publishing high severity.
7. Synthesize the recommendation and exact execution evidence, then clean up worktrees.

Product-behavior documentation is checked only when it already exists and the PR changes behavior it covers. There is no separate minimality/Ponytail lane; simplicity is part of PR_CORE.
