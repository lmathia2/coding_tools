---
name: engineering-workflow
description: Default end-to-end engineering policy for coding tasks. Use for implementation, debugging, refactoring, architecture work, and maintenance: understand the repository, make a proportional plan before edits, parallelize only useful independent work, choose the smallest correct design, keep authoritative documentation synchronized, and verify with executable evidence.
license: Includes concepts adapted from MIT-licensed obra/superpowers and DietrichGebert/ponytail; see ../../vendor notices in the Smart Harness distribution.
---

# Engineering Workflow

One workflow replaces the former planning, engineering-core, parallelism, context, task-ledger, Superpowers, Ponytail, and documentation-sync policy stack.

## Goal

Finish the requested change correctly with the least process and model spend that preserves quality.

Default shape: **one coordinator + one implementation context + deterministic verification**. Add agents only when independent evidence or judgment can materially change the result.

## 1. Understand, then plan

No source edit before a plan. Scale the plan to risk:

- **Mechanical:** 1–3 steps.
- **Normal:** acceptance criteria, owning code/callers/contracts, implementation steps, tests, and documentation impact.
- **Complex/high-risk:** additionally capture invariants, alternatives, compatibility/migration/rollback, security/resilience, dependencies, and one independent challenge when useful.

Resolve repository facts by reading code/tests/configuration. Ask the user only when product intent remains materially ambiguous.

If execution disproves a plan assumption, revise the plan before continuing.

## 2. Spend tokens where they change the answer

Use the cheapest capable lane:

- fast/tool-heavy model for search, repository mapping, test discovery, builds, lint/static checks, and mechanical edits;
- normal coding model for ordinary implementation;
- deep model for subtle state/algorithm/integration work or ambiguous debugging;
- top model only for architecture adjudication, security/high-consequence review, or materially uncertain decisions.

Do not create a second premium review merely because one is available. Strong deterministic evidence is enough for low-risk work.

## 3. Parallelize meaningful independence

Run independent work concurrently when it reduces wall-clock time or anchoring, for example separate module/caller/test investigations, competing debugging hypotheses, or non-contending test/static/documentation checks.

Keep work sequential when it has unmet dependencies or shared mutable state.

Parallel writers require disjoint ownership, isolated branches/worktrees, and an explicit integration step. Otherwise use one writer.

For complex or long tasks, give parallel lanes the same compact evidence: goal, acceptance criteria, relevant refs/files/contracts, and known environment constraints. Persist a short `.agent-state/<task>/progress.md` only when compaction/handoff risk justifies it; do not create task ledgers for routine work.

## 4. Choose the smallest correct design

After tracing the real flow, stop at the first option that fully satisfies the accepted requirements:

1. do nothing if the requested behavior already exists or the need is speculative;
2. reuse an existing repository pattern/helper;
3. use the standard library or native platform/framework/database capability;
4. reuse an already-installed dependency;
5. write the minimum coherent new code.

Prefer deletion and boring code over speculative abstraction. Fix root causes at the shared causal boundary rather than patching symptoms.

Never simplify away validation, security/privacy, accessibility, compatibility, migration/rollback, data-loss protection, necessary error/retry/idempotency/concurrency/recovery behavior, tests, documentation, or explicit requirements.

## 5. Debug and change behavior with evidence

For ambiguous failures: reproduce → trace → form competing hypotheses → run discriminating checks → establish root cause → implement the smallest causal fix → add regression evidence.

For behavior changes, use RED → GREEN → REFACTOR when practical. Use characterization tests before risky refactors. Do not force ceremonial TDD for trivial deterministic edits.

## 6. Documentation is part of execution

Every plan contains **Documentation Impact**:

- `REQUIRED` — authoritative docs must change;
- `GENERATED` — regenerate/check generated references;
- `NOT AFFECTED` — state a concrete reason.

Update documentation in the same implementation pass when the change affects public/reusable APIs, non-obvious function/module intent, behavior/failure semantics, architecture/ADRs, configuration, schemas/data, migrations/compatibility, operations/recovery, examples/tutorials, or changelog/deprecation guidance.

Good documentation explains **function, intent, goal/invariant, contract, constraints, and relevant operational/failure behavior**. Do not comment obvious syntax.

If the repository already contains an outside-in product behavior specification and this change alters documented user-visible behavior, update only the affected feature/foundation/checklist/triage artifacts. **Do not create a product behavior specification unless the user asks for one.**

Run repository-native docs builds, doctests, examples, link checks, schema/reference generation, or clean-diff checks when applicable. Never report an unexecuted docs check as passing.

## 7. Verify before completion

Start with the smallest direct behavior check, then expand according to blast radius:

1. targeted regression/behavior tests;
2. relevant module/package tests;
3. build/compile/typecheck;
4. lint/static analysis;
5. integration/e2e/runtime checks when affected;
6. documentation checks when affected.

For high-risk work, add one focused independent semantic review of the risk dimension that caused escalation. Re-run affected verification after fixes.

Never turn `NOT EXECUTED` into `PASS`.

## Completion

Return concise:

- Result
- Verification (exact commands/results)
- Documentation impact and changed paths
- Important decisions only when non-obvious
- Residual risk / blocked checks
