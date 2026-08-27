---
name: engineering-workflow
description: "Default end-to-end engineering policy for coding tasks. Use for implementation, debugging, refactoring, architecture work, and maintenance: decompose work into coherent commit-sized units, run plan → implement → document → simplify → verify for every unit, keep authoritative documentation live with code, measure changed-code complexity, and verify with executable evidence."
license: Includes concepts adapted from MIT-licensed obra/superpowers and DietrichGebert/ponytail; see .wysiwyship/vendor/THIRD_PARTY_NOTICES.md in an installed project.
---

# Engineering Workflow

One workflow replaces the former planning, engineering-core, parallelism, context, task-ledger, Superpowers, Ponytail, and documentation-sync policy stack.

## Goal

Finish the requested change correctly with the least process and model spend that preserves quality.

Default shape: **one coordinator + one implementation context per coherent work unit + deterministic verification**. Add agents only when independent evidence or judgment can materially change the result.

Every implementation unit follows this invariant, without skipping or reordering stages:

```text
plan -> implement -> document -> simplify -> verify
```

## 1. Understand, then plan

No source edit before a plan. Scale the plan to risk:

- **Mechanical:** 1–3 steps.
- **Normal:** acceptance criteria, owning code/callers/contracts, implementation steps, tests, and documentation impact.
- **Complex/high-risk:** additionally capture invariants, alternatives, compatibility/migration/rollback, security/resilience, dependencies, and one independent challenge when useful.

Resolve repository facts by reading code/tests/configuration. Ask the user only when product intent remains materially ambiguous.

Decompose non-trivial work into the smallest coherent, independently committable units. Each unit records:

- goal and observable acceptance criteria;
- dependencies and integration order;
- exclusive file/module ownership;
- contracts and invariants it may change;
- authoritative documentation it must update, or a concrete `Docs-Impact: none — <reason>`;
- functions or modules whose complexity should be compared;
- exact verification commands.

One unit should produce one reviewable commit or commit-ready change. Do not split code from its tests or documentation merely to create more parallelism. Commit only when the user or repository workflow authorizes it.

If the repository already contains an accepted Spec Kit `tasks.md`, OpenSpec change `tasks.md`, or BMAD implementation story/spec, treat that artifact as authoritative planning input. Preview its translation with `.wysiwyship/tools/spec_bridge.py`; import ledger units only with explicit acceptance. Do not regenerate, reinterpret, or replace the upstream specification workflow.

If execution disproves a plan assumption, revise the plan before continuing.

## 2. Spend tokens where they change the answer

Use the cheapest capable lane:

- fast/tool-heavy read-only model for search, repository mapping, test discovery, builds, lint/static checks, and complexity measurement;
- normal coding model for ordinary implementation;
- deep model for subtle state/algorithm/integration work or ambiguous debugging;
- top model only for architecture adjudication, security/high-consequence review, or materially uncertain decisions.

Do not create a second premium review merely because one is available. Strong deterministic evidence is enough for low-risk work.

## 3. Parallelize meaningful independence

Run independent work units concurrently when it reduces wall-clock time or anchoring, for example disjoint modules, separate caller/test investigations, competing debugging hypotheses, or non-contending test/static/documentation checks.

Keep work sequential when it has unmet dependencies or shared mutable state.

Parallel writers require disjoint ownership, isolated branches/worktrees, one accountable agent per unit, and an explicit integration step. Each agent receives the same unit contract and runs the complete `plan -> implement -> document -> simplify -> verify` cycle. Otherwise use one writer.

For complex, long, parallel, or resumable tasks, give every lane the same compact evidence and use `.wysiwyship/tools/work_units.py` to persist dependencies, ownership, lifecycle evidence, documentation impact, verification, and commit SHA under ignored `.agent-state/work-units/`. Activate one unit so installed stop hooks can enforce its lifecycle gate. Do not create ledger state for routine fixes where it adds no handoff value.

```bash
python3 .wysiwyship/tools/work_units.py init <id> --title <title> --goal <goal> \
  --acceptance <criterion> --owns <path> --base-ref HEAD --docs-impact required --doc-path <path> --activate
python3 .wysiwyship/tools/work_units.py advance <id> --evidence <stage-evidence>
python3 .wysiwyship/tools/check.py --active
python3 .wysiwyship/tools/work_units.py close
```

## 4. Implement the smallest correct design

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

## 6. Document in the same unit and commit

Documentation is a live specification of the system, not a release-end summary. Every plan and work unit contains **Documentation Impact**:

- `REQUIRED` — authoritative docs must change;
- `GENERATED` — regenerate/check generated references;
- `NOT AFFECTED` — state a concrete reason.

Update documentation after implementation and before simplification. The authoritative documentation must travel in the same logical commit as the code it explains. It captures what changed and, where relevant, the API methods and contracts, purpose, intent, protected goal/invariant, constraints, compatibility, and operational/failure behavior.

A code commit without documentation changes must carry a concrete `Docs-Impact: none — <reason>` in its commit message or unit evidence. A later documentation-only commit does not repair a code commit that was knowingly incomplete; amend or squash the logical unit so the specification and code agree at every reviewable commit.

When commits are produced, verify the range before handoff:

```bash
python3 .wysiwyship/tools/commit_docs.py <base-ref>
```

Good documentation explains **function, intent, goal/invariant, contract, constraints, and relevant operational/failure behavior**. Do not comment obvious syntax.

If the repository already contains an outside-in product behavior specification and this change alters documented user-visible behavior, update only the affected feature/foundation/checklist/triage artifacts. **Do not create a product behavior specification unless the user asks for one.**

Run repository-native docs builds, doctests, examples, link checks, schema/reference generation, or clean-diff checks when applicable. Never report an unexecuted docs check as passing.

## 7. Simplify with measured complexity

After documentation is current, simplify the implementation without changing accepted behavior:

1. remove duplication, dead paths, speculative abstraction, and unnecessary dependencies;
2. prefer guard clauses, cohesive helpers, data-driven dispatch, and existing native patterns when they improve clarity;
3. score changed Python functions with `.wysiwyship/tools/complexity.py` (or the repository-native equivalent for another language);
4. compare against the unit's starting ref when possible and report current score plus delta;
5. treat `1–5` as Excellent, `6–10` as Good, `11–20` as Moderate Risk, and `>20` as High Risk / Refactor Required.

Complexity is evidence, not a gameable gate. Do not extract meaningless one-line helpers or obscure control flow merely to lower a number. Any score above 10 or material increase requires a concrete simplification recommendation or an explicit justification tied to cohesion, correctness, or performance. If simplification changes a documented contract, return to the documentation stage before verification.

Example:

```bash
python3 .wysiwyship/tools/complexity.py changed_file.py --compare-ref <unit-start-ref>
```

## 8. Verify before completion

Start with the smallest direct behavior check, then expand according to blast radius:

1. targeted regression/behavior tests;
2. relevant module/package tests;
3. build/compile/typecheck;
4. lint/static analysis;
5. integration/e2e/runtime checks when affected;
6. documentation checks when affected.

For high-risk work, add one focused independent semantic review of the risk dimension that caused escalation. Re-run affected verification after fixes.

Never turn `NOT EXECUTED` into `PASS`.

For a committed work unit, finish verification with the composed deterministic range gate so documentation sync, changed-function complexity, configured checks, and optional ledger evidence are evaluated under one contract:

```bash
python3 .wysiwyship/tools/check.py <unit-start-ref> --head HEAD
```

Use `--active` when an active work-unit ledger supplies the immutable base ref. Before a commit exists, run the applicable component checks and report the commit-range gate as `NOT EXECUTED`; do not point the gate at a range that omits the working-tree change.

## 9. Explain every completed project

After all work units are integrated and the committed-range gate passes, invoke the `eli5` skill before final handoff. This is mandatory for every successful development workflow. Generate and check the dependency-free visual explainer under `.agent-state/eli5/` unless the user requests a versioned documentation path, then include its path and audience in the completion report.

Do not run the completion explainer for blocked or incomplete work. The project is not complete if the explainer fails to render or validate. The ELI5 artifact is a post-verification handoff, not a substitute for live authoritative documentation or executable evidence.

## Completion

Return concise:

- Result
- Work units / commits and dependency order
- Verification (exact commands/results)
- Documentation impact and changed paths
- Complexity scores/deltas and simplification decisions
- ELI5 audience, slide count, verification, and artifact path
- Important decisions only when non-obvious
- Residual risk / blocked checks
