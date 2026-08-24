---
name: ponytail-review
description: Vendored complexity-only review adapted from Ponytail. Use during implementation or PR review to identify code that can be deleted or replaced by existing repository code, standard-library/native features, or a smaller design. It complements and never replaces correctness, security, testing, or documentation review.
license: MIT; adapted from DietrichGebert/ponytail at 2ed6c52c9d7e5e56942508591085fd45dea277d3
metadata:
  source: DietrichGebert/ponytail
  source-commit: 2ed6c52c9d7e5e56942508591085fd45dea277d3
---

# Ponytail Review

Review only for unnecessary complexity.

For each finding state:

`<file>:<line/range> — <tag>: <what to remove>. <smallest replacement>.`

Tags:

- `delete` — dead/speculative behavior or unused flexibility;
- `reuse` — repository code already solves it;
- `stdlib` — a standard-library feature replaces it;
- `native` — the platform/framework/database already provides it;
- `yagni` — abstraction/configuration has no current need;
- `shrink` — equivalent correct logic can be materially smaller.

Do not report correctness, security, performance, accessibility, test, or documentation defects in this lane; those belong to the normal reviewers. Never recommend deleting required safety checks, behavior tests, documentation, examples, migration guidance, or operational controls.

If there is nothing material to remove, return: `Lean already. Ship.`
