---
name: systematic-debugging
description: Use for bugs, regressions, flaky tests, unclear failures, or repeated failed fixes. Requires reproduction, evidence, competing hypotheses, root cause, and regression verification.
---
# Systematic Debugging
## 1. Reproduce
Establish expected behavior, observed behavior, smallest useful reproduction, environment/state, and whether the failure is deterministic. Prefer a failing automated test when practical.

## 2. Gather evidence
Inspect only what bears on the failure: errors/stacks, call and state path, configuration/data assumptions, analogous working paths, relevant changes, and tests.

## 3. Competing hypotheses
For a non-obvious failure, form 2-4 plausible causes. For each ask: if true, what should we observe, and what would disprove it? Run cheap discriminating checks before editing production code.

## 4. Root-cause gate
Before the fix, be able to state: `The failure occurs because <mechanism>, supported by <evidence>.` If not, investigate further.

## 5. Minimal repair
Fix the causal mechanism rather than masking the symptom.

## 6. Regression verification
When practical, add a test that fails before the fix and passes after it. Verify nearby behavior according to blast radius. One successful run is not proof for flaky/concurrent failures.
