---
name: plan-first
description: Mandatory planning protocol for every coding or review task. Plan depth scales with risk, but editing never starts before a plan exists.
---

# Plan First

Before any source edit, produce an explicit plan.

## Micro-plan

For mechanical/local work, 1–3 steps are enough:

1. files/behavior to change;
2. edit strategy;
3. verification command(s).

## Normal plan

For ordinary engineering work include:

- acceptance criteria;
- owning code/callers;
- implementation steps;
- tests and verification;
- compatibility/edge cases that matter.

## Deep plan

Use when architecture, migration, security, concurrency, distributed state, public contracts, or broad refactoring are involved:

- gather repository evidence;
- identify alternatives;
- state key invariants;
- include migration/rollback;
- get an independent challenge before implementation.

Do not keep planning merely to create consensus. Once material uncertainty is resolved, execute.
