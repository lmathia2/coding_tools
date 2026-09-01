---
description: Default self-contained PR review: exact PR-head worktree, one semantic lane plus one executable lane in parallel, full feasible unit/integration execution, and specialist escalation only for high-risk changes.
argument-hint: [base-ref] [PR intent/details]
---

<!-- harness-role: coordinator -->
<!-- harness-workflow: review-pr -->

Review request: $ARGUMENTS

Use `pr-review` as the complete review policy.

Resolve routes with `routing.py plan --host pi --workflow review_pr`. Dispatch
delegated lanes through `.pi/tools/parallel-pi.py --workflow review_pr` with the
locked route as `routing`, then validate each `routing_receipt`. Record inline
lanes explicitly; never claim they ran on a specialist model.
