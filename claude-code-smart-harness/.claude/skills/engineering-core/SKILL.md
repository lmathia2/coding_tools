---
name: engineering-core
description: Core implementation discipline for harness workers: evidence-first debugging, pragmatic test-first development, and executable verification before completion.
user-invocable: false
---

# Engineering Core

## Verification before completion

Do not claim code is done, fixed, or passing without fresh executable evidence appropriate to the change.

Use the smallest useful ladder first:

1. targeted regression/behavior test;
2. owning module/package tests;
3. build/typecheck/lint/static analysis;
4. integration/e2e/runtime verification when the blast radius warrants it.

Never report an unexecuted check as PASS. Distinguish change-caused, pre-existing, and environment failures.

## Systematic debugging

For unclear bugs, do not begin with speculative production edits.

1. establish expected vs observed behavior;
2. obtain the smallest useful reproduction;
3. trace the relevant call/state path;
4. form 2-4 plausible hypotheses;
5. define an observation that would support/falsify each;
6. run discriminating checks;
7. state the causal mechanism supported by evidence;
8. fix minimally;
9. add/regress the failure with an executable test when practical.

For flaky/concurrent failures, one successful run is not proof of a fix.

## Pragmatic TDD

For behavior-changing work, establish a failing executable condition first when practical.

Strong candidates: bugs, business logic, validation/APIs, parsers, permissions, state machines, concurrency, compatibility behavior.

Do not force test-first ceremony onto docs, generated files, formatting, or mechanical edits already strongly protected by compiler/typechecker.

## Scope

Prefer existing repository abstractions. Avoid unrelated cleanup and speculative generalization.
