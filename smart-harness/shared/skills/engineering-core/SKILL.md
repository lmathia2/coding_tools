---
name: engineering-core
description: Core execution discipline shared by Copilot, Claude Code, and Pi: root-cause debugging, pragmatic TDD, scoped changes, documentation sync, and evidence-based completion.
---

# Engineering Core

## Understand before editing

Read the owning code, callers/contracts, tests, and relevant documentation.

Use the accepted plan. If facts contradict it, stop and revise rather than silently redesigning.

## Debug systematically

For unclear failures:

1. reproduce;
2. gather evidence;
3. form competing hypotheses;
4. run discriminating checks;
5. state the causal mechanism;
6. implement the minimal root-cause fix;
7. add regression evidence.

## Use pragmatic TDD

For behavior-changing work, establish a failing executable condition first when practical.

Use characterization tests before risky refactors.

## Keep scope coherent

Prefer existing abstractions, standard-library/native features, and the smallest design that fully satisfies the requirement.

Do not simplify away validation, security, failure handling, accessibility, compatibility, documentation, or explicitly requested behavior.

## Keep documentation synchronized

Apply `documentation-sync` during execution, not after completion.

Update function/API docs, intent/goals, architecture/ADRs, examples, configuration, migrations, and runbooks when affected.

## Verify before completion

Run focused tests first, then broader unit/integration/e2e/build/type/lint/static and documentation checks according to blast radius.

Report exact commands and results.

Never claim an unexecuted check passed.
