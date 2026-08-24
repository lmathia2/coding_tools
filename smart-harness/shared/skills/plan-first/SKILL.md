---
name: plan-first
description: Mandatory planning protocol for every coding or review task. Plan depth scales with risk, but source editing never starts before an explicit plan and documentation impact assessment exist.
---

# Plan First

Before any source edit, produce an explicit plan.

## Required plan fields

Every plan includes:

1. Goal and acceptance criteria.
2. Repository evidence and affected boundaries.
3. Implementation steps in dependency order.
4. Verification plan.
5. **Documentation Impact** using `documentation-sync`.
6. Parallel work map: what can run concurrently and what must remain sequential.

## Proportional depth

### Mechanical

Use a 1–3 step micro-plan.

### Normal

Identify owning code, callers/contracts, tests, documentation surfaces, and verification.

### Complex/high risk

Map architecture, invariants, alternatives, compatibility/migration/rollback, security/resilience, docs/ADR/runbook impact, and an independent challenge.

## Gate

Do not dispatch a writing worker until the plan is accepted by the coordinator.

If repository evidence invalidates the plan during execution, pause, revise the plan, and then continue.
