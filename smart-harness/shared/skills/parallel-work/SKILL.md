---
name: parallel-work
description: Parallelization policy for agentic coding and review. Run independent analysis, documentation-impact discovery, and verification concurrently; parallelize writes only when isolated and dependency-safe.
---

# Parallel Work

Parallelize work when tasks are independent and results can be synthesized without shared mutable state.

Good parallel lanes:

- separate module/caller/test/documentation discovery;
- competing debugging hypotheses;
- independent architecture/correctness/security/minimality reviews;
- tests, static analysis, and documentation validation that do not contend;
- separate implementation components with stable interfaces and disjoint ownership.

Keep sequential:

- work with unmet dependencies;
- migrations before code that requires them;
- multiple writers touching the same files/contracts;
- tests sharing mutable databases, ports, accounts, or fixtures;
- review before implementation is complete.

Parallel writers require isolated worktrees or branches, explicit ownership, an integration step, and full verification of the combined result.

Wait for every required lane before synthesis. Do not start duplicate agents just to appear parallel.
