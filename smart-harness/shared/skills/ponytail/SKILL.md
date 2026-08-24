---
name: ponytail
description: Vendored, dependency-free adaptation of Ponytail. Use on coding, design, refactoring, dependency selection, and bug fixes to choose the simplest correct solution after understanding the full flow. Enforces YAGNI, reuse, standard-library/native features, minimal coherent diffs, and deletion over speculative abstraction.
license: MIT; adapted from DietrichGebert/ponytail at 2ed6c52c9d7e5e56942508591085fd45dea277d3
metadata:
  source: DietrichGebert/ponytail
  source-commit: 2ed6c52c9d7e5e56942508591085fd45dea277d3
---

# Ponytail — Smart Harness Edition

Lazy means efficient, never careless. Understand the task and trace the real code path before minimizing the solution.

## The ladder

Stop at the first rung that fully satisfies the accepted requirements:

1. Does this need to exist at all? Skip speculative work.
2. Does the repository already contain the needed helper, type, pattern, or abstraction? Reuse it.
3. Does the standard library solve it correctly? Use it.
4. Does the language, browser, database, framework, or platform provide it natively? Use that.
5. Does an already-installed dependency solve it cleanly? Reuse it; do not add a package for a few reliable lines.
6. Can the same correct behavior be expressed with a smaller coherent change? Prefer it.
7. Only then write the minimum new code that works.

## Rules

- Fix root causes at the shared boundary rather than patching every symptom/caller.
- Avoid one-implementation interfaces, one-product factories, unused configuration, and scaffolding “for later.”
- Prefer deletion and boring code over clever abstractions.
- Minimize files and moving parts only after understanding callers, contracts, state, and failure paths.
- Mark deliberate simplifications with a concrete ceiling and upgrade trigger when the trade-off is non-obvious.
- Non-trivial behavior still needs the smallest meaningful executable check.

## Non-negotiable boundaries

Never simplify away:

- accepted requirements;
- documentation required by `documentation-sync`;
- behavior/integration tests and verification evidence;
- input validation at trust boundaries;
- security, privacy, accessibility, compatibility, migration, rollback, and data-loss protections;
- necessary error handling, observability, retries/idempotency, concurrency controls, or recovery behavior.

When Ponytail conflicts with an explicit repository/user/harness requirement, the requirement wins.
