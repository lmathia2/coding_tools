---
description: Self-contained execution-based PR review: plan, create an isolated PR-head worktree, run semantic and executable lanes in parallel, review complexity/documentation/security, execute full feasible unit/integration/static checks, and verify serious findings.
argument-hint: [base-ref] [PR intent/details]
---

Review request: $ARGUMENTS

Use `plan-first`, `parallel-work`, `context-snapshot`, `pr-review`, `documentation-sync`, and `ponytail-review`.

1. Resolve exact base/committed PR HEAD, changed contracts/runtime/docs, expected test/static/docs commands, and risk.
2. If a product behavior specification exists, map changed behavior to affected feature/foundation/cross-cutting docs, glossary, coverage, verification items, source commit, and triage.
3. Create a detached PR-head worktree under `.agent-worktrees/`; every read and command targets it.
4. Use `.pi/tools/parallel-pi.py` for independent read-only architecture/correctness/wiring, adversarial, documentation/behavior-spec, security/resilience, and complexity lanes. Do not require external Pi extensions.
5. In parallel where resources permit, execute the complete feasible configured unit suite, complete feasible integration suite, relevant e2e/runtime tests, build/type/lint/static analysis, documentation checks, and applicable product-behavior checklist/probes.
6. If PR-head tests fail and causality is unclear, run the failing subset against a temporary base worktree.
7. Attempt to falsify every BLOCKER/MAJOR in a fresh independent child context.
8. Report recommendation, verified findings, exact commands/results, stale/missing behavior-spec artifacts, documentation gaps/checks, NOT EXECUTED blockers, and GitHub-ready serious comments.
9. Remove/prune review worktrees after capturing evidence unless intentionally preserved.

Ponytail review is complexity-only and never replaces correctness, security, tests, accessibility, compatibility, or documentation review.
