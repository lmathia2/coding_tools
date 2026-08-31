# Provenance and limitations

These are original engineering exercises authored for this repository, not
copied dataset tasks, upstream patches, or official benchmark instances. No
third-party source code is incorporated into the exercises. This document does
not grant a new license; the repository currently has no top-level LICENSE file.
No external repository or skill is fetched to prepare, execute the application,
or grade a task.

Design inspiration, inspected 2026-08-30:

- [DeepSWE](https://github.com/datacurve-ai/deep-swe): long-horizon repository
  engineering, agent-visible task briefs, held-out behavioral verification, and
  separate reference implementations. This suite adopts the separation of those
  concerns, not its Harbor/Pier infrastructure or leaderboard methodology.
- [FrontierCode](https://cognition.com/frontiercode): assess whether a change is
  maintainable and reviewable, including correctness, tests, scope, and project
  conventions. Our blind human rubric is much smaller and is not its grader.

The durable job and tenant-isolation scenarios are original domain choices.
There is no one-to-one mapping to a published task, and no claim that these tasks
match the measured difficulty of either benchmark. Source links are attribution
and optional reading, not runtime dependencies.

## What results can establish

- Within a frozen local task revision and controlled setup, compare observed
  behavior, regression results, elapsed time, and recorded usage across conditions.
- Separate deterministic functional evidence from human judgments about design,
  documentation, and ease of maintenance.
- Diagnose whether the workflow was actually used and whether routing evidence
  exists; installed configuration alone does not prove either.

## What results cannot establish

- Official DeepSWE, FrontierCode, SWE-bench, or Terminal-Bench scores.
- A general model ranking, or performance on frontend/mobile/large upstream repos.
- Statistical proof of improvement from ten selected tasks or one attempt each.
- Guaranteed isolation: workspaces and evaluator files share a local user account.
  A model must not read the reference or evaluator source, but this runner cannot
  enforce that against an adversarial agent. Test execution is trusted local code,
  not a sandbox for unknown submissions.
- Absence of contamination from global host instructions, skills, plugins, or
  memories. Inspect the host environment before comparisons and record exceptions.
- Total model cost or complete child-agent token usage unless the host supplies
  the necessary evidence. Missing observations must remain unknown.

Reference solutions prove the supplied tests are satisfiable, not that the tests
are exhaustive or the reference is uniquely correct. Review the briefs, reference,
and tests together before running agents; intentionally incomplete solutions
should fail meaningful requirement groups. Do not grade by patch similarity.
