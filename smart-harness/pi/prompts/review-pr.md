---
description: Default self-contained PR review: exact PR-head worktree, one semantic lane plus one executable lane in parallel, full feasible unit/integration execution, and specialist escalation only for high-risk changes.
argument-hint: [base-ref] [PR intent/details]
---

Review request: $ARGUMENTS

Use `pr-review`.

1. Resolve exact base/HEAD, intent, changed boundaries, authoritative commands, and risk.
2. Create the detached PR-head worktree.
3. Run two default lanes in parallel using the main context plus `.pi/tools/parallel-pi.py` when useful:
   - semantic architecture/correctness/wiring/contracts/tests/docs/simplicity review;
   - execution lane with complete feasible unit and integration suites plus relevant runtime/static/docs checks.
4. Add adversarial and security/resilience reasoning only for HIGH_RISK changes.
5. Independently attempt to falsify candidate BLOCKER/MAJOR findings before publishing high severity.
6. Report recommendation and exact execution evidence, then clean up worktrees.

Check existing product-behavior documentation only when the PR changes behavior it covers. Do not create a product behavior specification during review.
