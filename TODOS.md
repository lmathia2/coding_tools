# Remaining work

Current milestone: two runnable evaluation pilots and the local runner are
implemented and verified. Eight tasks remain planned. No live benchmark attempts
have run; difficulty and workflow benefit are still unmeasured.

## Next: calibrate before expanding

- [ ] Agree an exact available Codex model, reasoning effort and run budget;
  freeze revisions and host settings using the
  [calibration protocol](wysiwyship/evals/CALIBRATION.md).
- [ ] Explicitly authorize and run four attempts: durable jobs and tenant
  isolation, each with baseline and workflow conditions. Use fresh workspaces,
  identical settings and a two-hour maximum per attempt; alternate condition
  order. This is an eight-hour aggregate cap, not an expected duration or cost.
- [ ] Grade every attempt, retaining failures, timeouts and interventions. Audit
  traces for actual workflow/specialist invocation; distinguish requested models
  from runtime-confirmed identity and report missing token usage as unknown.
- [ ] Review code, tests, documentation and explainers with each task's blind
  rubric. Report correctness, execution status, elapsed time, usage, complexity,
  scope and reviewability separately.
- [ ] Check that tasks require substantial cross-module work. Revise ambiguous
  contracts or weak acceptance tests using near-solutions/mutations; never add
  delays or tune tasks solely to manufacture a workflow win. Freeze calibrated
  versions before further comparisons.

## Then: complete the ten-task suite

Each follow-on needs a working starter, explicit task contract, reference overlay,
canonical regressions and acceptance tests, review rubric, provenance and local
validation. Keep pilot data separate from follow-on evaluation data.

- [ ] Webhook delivery.
- [ ] Inventory reservations.
- [ ] Schema migration.
- [ ] Offline synchronization.
- [ ] Streaming ingestion.
- [ ] Artifact cache.
- [ ] Dependency workflows.
- [ ] Audit reporting.
- [ ] Run the frozen ten-task paired comparison and publish all task-level
  outcomes and limitations. Predefine repeats; ten tasks are directional
  evidence, not proof of universal workflow improvement.

## Validation and maintenance gaps

- [ ] Run real-host development and PR smoke tests for Codex, Claude Code,
  GitHub Copilot and Pi. Verify dispatch, fallbacks and receipt behavior;
  existing offline tests do not prove host execution.
- [ ] Visually inspect the developer ELI5 HTML for layout, navigation and mobile
  overflow. Static checks passed, but browser policy blocked automated local-file
  inspection; no visual pass is claimed.
- [ ] Correct `work_units.py` completion attribution: without an explicit commit,
  it currently records HEAD even when the unit's changes are uncommitted. Preserve
  an uncommitted state instead, with a focused regression test.
- [ ] Decide a repository license before presenting these original fixtures as a
  redistributable dataset; retain upstream inspiration/provenance distinctions.

## Later experiments—not prerequisites

- [ ] Compare configured multi-model routing separately from the fixed-model
  workflow experiment, so model quality does not confound the first comparison.
- [ ] Evaluate interactive planning separately from auto mode, recording human
  effort and interventions consistently across conditions.

See the [evaluation guide](wysiwyship/evals/README.md),
[catalog](wysiwyship/evals/catalog.json) and
[verification record](wysiwyship/evals/VERIFICATION.md) for current evidence.
