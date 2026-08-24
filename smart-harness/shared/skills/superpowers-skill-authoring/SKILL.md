---
name: superpowers-skill-authoring
description: Dependency-free skill-authoring and maintenance workflow adapted from Superpowers. Use when creating or modifying agent skills, commands, prompts, or orchestration rules; requires a clear trigger, minimal instructions, pressure tests, documentation, and regression validation.
license: MIT; adapted from obra/superpowers at b36e0829c6d0140e93cfef2ca599b1b07d4a7797
metadata:
  source: obra/superpowers
  source-commit: b36e0829c6d0140e93cfef2ca599b1b07d4a7797
---

# Skill Authoring

Treat a skill as executable policy, not inspirational prose.

## 1. Define the behavior

State:

- trigger conditions;
- desired observable behavior;
- non-goals;
- tools/runtime assumptions;
- precedence with other instructions;
- failure and escalation behavior.

## 2. Write the smallest effective skill

- Put activation criteria in the description.
- Keep mandatory steps explicit and ordered.
- Put detailed references/scripts beside the skill and load them only when needed.
- Avoid duplicated rules already enforced elsewhere.
- Avoid vague personas without concrete procedure or output contracts.

## 3. Pressure-test it

Create representative prompts including:

- normal success case;
- ambiguous input;
- pressure to skip planning/testing/docs;
- conflicting or overlapping skills;
- long-context/compaction scenario;
- tool/environment failure.

Verify the agent follows the intended behavior and does not over-trigger.

## 4. Maintain documentation and provenance

Document function, intent, goals, interfaces, examples, constraints, and source/license where derived. Update generated references and validation fixtures in the same change.

## 5. Regression gate

Run the harness validator, model/config drift check, generated-reference check, and installation smoke test. A skill change is incomplete if the documentation or validation contract is stale.
