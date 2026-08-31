# Blind review rubric — durable jobs

Review candidate artifacts with arm, route, model, timings, author and reference
implementation hidden. Use the same rubric and task contract for both arms.
Do not award points for resembling the reference, using its helper names, number
of files, SQL layout, prose style, workflow ritual or commit history.

Automated acceptance is reported separately by requirement family, alongside
legacy regressions. A syntax/import failure is not evidence that all families
were exercised. Report test discovery, failures/errors, and any harness problem.
Do not infer effective model from route names or artifacts.

## Human scores (0–4 each; 20 total)

### 1. Purpose and safety boundaries

- 0: Queue purpose or delivery guarantee is materially wrong.
- 1: Feature names are present but crash/cancellation consequences are unclear.
- 2: Main lease/retry behavior is explained; important edge intent is missing.
- 3: Fencing, expiry equality, cooperative cancellation and crash recovery are
  explained correctly with the at-least-once external-effect boundary.
- 4: The above is grounded in actual code and concrete operational examples,
  including why submission deduplication does not deduplicate handler effects.

### 2. Engineering coherence and intent

- 0: Nonfunctional replacement, stubs, or safety claims unsupported by code.
- 1: Several independent state decisions disagree or are unsafe to maintain.
- 2: Core design works but transaction ownership or failure propagation is murky.
- 3: State decisions, token validation, recovery and event commits have clear
  ownership; worker and persistence boundaries are understandable.
- 4: Cross-cutting decisions stay consistent under migration, storage faults,
  stale results and cancellation; intent explains non-obvious tradeoffs.

Judge semantics, not whether one helper, several methods or a different
transaction organization was chosen. Do not demand a particular schema beyond
preserving the existing database's data and required API behavior.

### 3. Documentation and developer explainer

- 0: Required docs absent or materially misleading.
- 1: README changes only, or a decorative explainer with no implementation trace.
- 2: Most APIs documented, but examples/limits or migration behavior are incomplete.
- 3: README, architecture, contracts and offline HTML explain what/how/why/use,
  accurate commands, compatibility changes and operational limits.
- 4: A new maintainer can follow source links from claims, understand failure
  boundaries, run examples, and identify what is deliberately not guaranteed.

No graphic polish premium; a readable semantic HTML document is sufficient.
Check code/docs agreement instead of matching reference wording.

### 4. Simplicity, complexity and maintainability

- 0: Large unrelated rewrite, obscured control flow, or needless dependencies.
- 1: Tangled policy duplication or abstractions make key invariants hard to see.
- 2: Reasonable overall design with some avoidable branch/exception complexity.
- 3: Cohesive modules, readable transactions, focused validation and no padding.
- 4: Smallest credible design for the full contract, with deliberate reuse where
  it keeps retry/cancellation/fencing behavior consistent and tests understandable.

Function complexity is supporting evidence, not an exact implementation grade.
A cohesive command dispatcher may score above ten without warranting a framework.
Do not reward splitting a readable transaction solely to lower a metric.

### 5. Scope, compatibility and verification honesty

- 0: Destructive migration, removed regressions, out-of-scope service/dependency,
  or fabricated test/difficulty claims.
- 1: Major compatibility or verification gaps are unreported.
- 2: Most intended scope preserved but evidence or limitations are imprecise.
- 3: Legacy functionality preserved, focused local tests added, exact verification
  commands/outcomes given, and known limits acknowledged.
- 4: Tests cover distinct risks with deterministic synchronization; handoff
  distinguishes measured facts from assumptions and documents any uncovered gap.

## Critical findings (report separately)

Flag any stale worker overwriting durable state, double current claim, terminal
resurrection, lost migrated data, event/state divergence, silent storage failure,
claim of exactly-once external effects, dependency/network violation, evaluator
test tampering or undisclosed inability to run tests. A numeric score must not
hide these findings. Record file/function evidence and user-visible consequence.

## Difficulty calibration, not a grade

The proposed 45–120 minute difficulty band is UNMEASURED. This pilot bundles
roughly four coherent engineering units: leased persistence and migration;
retry/cancel/worker integration; atomic observability/idempotency and CLI;
regression verification and maintainable documentation. Only timed actual Codex
runs can establish whether the workload lands in the intended band. Human or
authoring elapsed time and raw line count are not substitutes.
