---
name: engineering-core
description: Core implementation discipline shared by Copilot and Claude Code: root-cause debugging, pragmatic TDD, scoped changes, and evidence-based completion.
---

# Engineering Core

## Bugs

Do not guess-and-patch unclear failures.

1. reproduce expected vs observed behavior;
2. gather evidence along the relevant call/state path;
3. for non-obvious failures, form competing hypotheses and discriminating checks;
4. state the causal mechanism before fixing;
5. make the smallest causal repair;
6. add a regression test when practical.

For flaky/concurrent failures, one successful run is not proof.

## Behavior changes

Prefer a failing executable condition before implementation when practical:

- RED: test expresses the desired behavior and fails for the right reason;
- GREEN: smallest coherent implementation;
- REFACTOR: clean up only after behavior passes.

Strict test-first is optional for docs, generated artifacts, formatting, and mechanical changes already protected by deterministic checks.

## Scope

Prefer existing repository abstractions. Avoid unrelated cleanup and speculative generalization.

## Verification before completion

Never claim done/fixed/passing without fresh evidence.

Verification ladder:

1. targeted behavior/regression test;
2. relevant module/package suite;
3. build/typecheck/lint/static analysis;
4. integration/e2e/runtime checks according to blast radius.

List commands actually executed and PASS / FAIL. Never report an unexecuted check as PASS.
