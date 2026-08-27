---
description: Default self-contained PR review: exact PR-head worktree, one semantic lane plus one executable lane in parallel, full feasible unit/integration execution, and specialist escalation only for high-risk changes.
argument-hint: [base-ref] [PR intent/details]
---

<!-- harness-role: coordinator -->
<!-- harness-workflow: review-pr -->

Review request: $ARGUMENTS

Use `pr-review`.

1. Resolve exact base/HEAD, intent, logical commit/work-unit order, changed boundaries, authoritative commands, and risk.
2. Create the detached PR-head worktree.
3. Run two default lanes in parallel using the main context plus `.pi/tools/parallel-pi.py --workflow review_pr` when useful. Give each child a semantic `role` so the active profile supplies its model and thinking strength; explicit task settings override the profile:
   - semantic architecture/correctness/wiring/contracts/tests/docs/simplicity review;
   - execution lane with complete feasible unit and integration suites plus relevant runtime/static/docs checks.
4. Check each implementation commit for coherent `plan -> implement -> document -> simplify -> verify` evidence, live documentation in the same commit (or `Docs-Impact: none — <reason>`), and changed-function complexity score/delta.
5. Run `.smart-harness/tools/check.py <base> --head <exact-pr-head>` as the composed deterministic range gate when installed, plus any additional repository-native checks required by the blast radius.
6. Add adversarial and security/resilience reasoning only for HIGH_RISK changes.
7. Independently attempt to falsify candidate BLOCKER/MAJOR findings before publishing high severity.
8. Report recommendation and exact execution evidence, then clean up worktrees.

Check existing product-behavior documentation only when the PR changes behavior it covers. Do not create a product behavior specification during review.
