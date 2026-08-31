# Pilot milestone verification

Local verification on 2026-08-31, macOS, Python 3.9.6 and 3.12. This records the
pre-commit pilot verification, not an executed coding-model experiment.

## Executed checks

From the repository root:

```bash
python3 -m unittest discover -s wysiwyship/evals/tests -v
python3 wysiwyship/evals/runner.py validate
python3 -m unittest discover -s wysiwyship/tests -b -q
python3 wysiwyship/tools/complexity.py wysiwyship/evals --min-score 11 --fail-above 20
python3 wysiwyship/scripts/build_packages.py --check
python3 wysiwyship/scripts/generate-reference.py --check
python3 wysiwyship/scripts/validate-harness.py
python3 wysiwyship/config/configure-models.py --check
git diff --check
```

- Runner: **22 tests pass on each of Python 3.9 and 3.12**. Includes actual
  workflow installation/native model pinning, fake Codex processes, authoritative
  grading, stale/mismatched comparisons, timeout/interruption and child cleanup.
- Existing harness: **66 tests pass on Python 3.12**.
- Native packages, generated reference, harness structure and balanced model
  profile: current/pass. No evaluation fixtures enter installed native packages.
- Complexity: no new evaluation function exceeds 20. See the bounded hotspots
  and simplification rationale in [RUNNER_NOTES.md](RUNNER_NOTES.md).
- Whitespace/diff check: pass. During this pre-commit verification, a
  committed-range release gate was **not run** and no push was performed.

## Canonical fixture validation

| Pilot | Starter original regressions | Reference original regressions | Reference acceptance |
|---|---:|---:|---:|
| Durable jobs | 13/13 pass | 13/13 pass | 47/47 pass |
| Tenant isolation | 17/17 pass | 17/17 pass | 61/61 pass |

Both incomplete starters correctly fail the new acceptance suite without a
test-discovery collapse. Durable jobs discovers 47 tests with 8 assertion-failure
and 40 runtime-error records; tenant isolation discovers 61 with 81
assertion-failure records and no errors. Subtests can produce multiple records
per test method, so these are **not pass-rate denominators**. Eight catalog
entries are explicitly planned/skipped, not validated tasks.

The task authors also verified the reference's own additional regressions:
durable jobs 19/19 and tenant isolation 25/25. These are separate from the
evaluator-owned original suites above. A durable-jobs near-solution mutant
without expiry fencing was rejected. Reproduction commands and limitations live
in each task's `NOTES.md`.

## End-to-end command smoke check

Fresh durable-jobs baseline and workflow trials were prepared outside the source
repository with requested model `gpt-5.6-sol`, effort `high`, and a 7,200-second
cap. This setting was used for **preview only**, not a model-availability claim.

- Preparation completed, including the real installer for the workflow arm.
- `run` without `--execute` returned `execute: false` for both. Neither created
  `STARTED.json` or launched Codex.
- `grade` returned the expected unsuccessful starter result for both, while
  all 13 original regressions passed and 47 acceptance tests were discovered.
- `compare` rejected the pair as `UNEXECUTED` with exit status 2, instead of
  inventing a measured workflow result.

## What this does not establish

No live Codex benchmark attempts, quota consumption measurement, effective-model
attestation, task runtime calibration or workflow improvement measurement has
been performed. Development subagents helped build these fixtures; they are not
evaluation attempts. Requested routes and invocation receipts are local build
evidence, not host-confirmed model identity.

Reference success proves fixture solvability under the written checks, not full
test coverage or production readiness. Separate local directories are not an
adversarial security boundary. Human documentation/design review remains
unassessed for any future agent submission. The next experiment is four attempts
requiring explicit approval, described in [CALIBRATION.md](CALIBRATION.md),
before constructing the other eight tasks.

## Developer walkthrough

The mandatory local ELI5 artifact is
`.agent-state/eli5/local-engineering-evals-pilots.html` (ignored, generated from
the adjacent JSON story). Audience: curious developer; nine content slides plus
title and closing. It includes exact first-use commands, preparation/grading
flows, lease-fencing and export-reauthorization code paths, and measured limits.

The bundled renderer's `--check` passes for all 11 rendered slides. Static
inspection found no remote resource markers; keyboard, touch, print and
reduced-motion code remain present. Visual/interactive inspection is **NOT
EXECUTED**: Browser Use URL policy rejected the local `file:` URL. No alternate
server or browser workaround was used. Open the HTML link manually to inspect
layout; static validation does not prove absence of visual overflow.
