---
name: superpowers-methodology
description: Vendored, dependency-free adaptation of the Superpowers software-development methodology. Use for non-trivial feature work, refactors, and difficult fixes that benefit from design clarification, isolated work, an executable plan, TDD, subagent delegation, review, and evidence-based completion.
license: MIT; adapted from obra/superpowers at b36e0829c6d0140e93cfef2ca599b1b07d4a7797
metadata:
  source: obra/superpowers
  source-commit: b36e0829c6d0140e93cfef2ca599b1b07d4a7797
---

# Superpowers Methodology — Smart Harness Edition

This is the self-contained methodology layer. It does not require the upstream plugin, hooks, marketplace, or runtime scripts.

## Use the lightest complete workflow

For a trivial task, a micro-plan plus verification is enough. For non-trivial work, follow the full sequence.

## 1. Clarify the design

Before coding, establish:

- user/system outcome;
- acceptance criteria;
- constraints and non-goals;
- relevant existing architecture;
- realistic alternatives;
- failure, compatibility, migration, and operational implications;
- documentation impact.

Ask product questions only when repository evidence cannot resolve intent. Avoid speculative features and design only what the accepted requirement needs.

## 2. Isolate risky work

For feature work, competing implementations, or long autonomous execution, use an isolated branch/worktree. Detect an existing worktree before creating another. Run a clean baseline check when practical.

## 3. Write an executable plan

The plan must be dependency-aware and specific enough to execute without rediscovering the design. Each task should name:

- goal and acceptance criteria;
- exact files/components;
- implementation action;
- tests and expected observations;
- documentation changes;
- verification command;
- dependencies and parallel-safe ownership.

## 4. Execute with fresh bounded contexts

Delegate independent tasks or investigations when context isolation improves quality. The coordinator retains the accepted plan, integrates results, and owns final verification.

A writing task may run in parallel only with disjoint ownership and isolated worktrees/branches. Review the task for:

1. specification/acceptance-criteria compliance;
2. code quality, simplicity, safety, tests, and documentation.

## 5. Develop behavior with executable evidence

For behavioral changes and bugs, use RED → GREEN → REFACTOR when practical:

- make the expected behavior fail for the right reason;
- implement the smallest coherent fix;
- observe the test pass;
- refactor under passing tests.

For unclear failures, diagnose root cause before editing. Do not substitute guess-and-patch loops for evidence.

## 6. Review and finish

Before completion:

- run targeted and broader relevant tests;
- run build/type/lint/static/documentation checks;
- request independent review when risk warrants it;
- resolve serious findings and re-verify;
- update code, tests, docs, examples, ADRs/runbooks, and changelog together;
- present branch/PR/merge options without deleting work unless explicitly requested.

## Smart Harness precedence

`documentation-sync`, security, compatibility, accessibility, validation, data-safety, and explicit user requirements are mandatory. Ponytail can reduce unnecessary implementation but cannot weaken these contracts.
