---
name: skill-authoring
description: Maintenance-only workflow for creating or changing WYSIWYShip skills, commands, prompts, or agent policies. Use when editing the harness itself; define precise triggers and observable behavior, keep instructions minimal, pressure-test conflicts and failure cases, update documentation/provenance, and run regression validation.
license: Adapted from MIT-licensed obra/superpowers skill-writing concepts; see ${PLUGIN_ROOT}/vendor/THIRD_PARTY_NOTICES.md in an installed project.
---

# Skill Authoring

Treat skills as executable policy.

1. Define trigger, desired observable behavior, non-goals, tool/runtime assumptions, precedence, and failure/escalation behavior.
2. Put activation criteria in the description; keep mandatory steps explicit and short. Prefer references for detail that should load only on demand.
3. Do not duplicate rules already owned by `engineering-workflow` or `pr-review`.
4. Pressure-test normal, ambiguous, conflict, skip-the-process, long-context, and tool/environment-failure cases.
5. Update function/intent/goals, examples, provenance/licenses, generated reference, and changelog in the same change.
6. Run model/config drift checks, generated-reference checks, harness validation, syntax checks, and installation smoke tests.

A new skill must provide a capability that cannot be expressed cleanly as a conditional branch in an existing core skill. Keep the discoverable skill surface small.
