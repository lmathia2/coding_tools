---
name: engineering-workflow
description: "Default end-to-end engineering policy for coding tasks. Use for implementation, debugging, refactoring, architecture work, and maintenance: grill and lock the plan, decompose work into coherent commit-sized units, run plan → implement → document → simplify → verify for every unit, keep authoritative documentation live with code, measure changed-code complexity, and verify with executable evidence."
license: Includes concepts adapted from MIT-licensed obra/superpowers and DietrichGebert/ponytail; see ${CLAUDE_PLUGIN_ROOT}/vendor/THIRD_PARTY_NOTICES.md in an installed project.
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

## 1. Grill, lock, then plan execution

No source edit before a locked plan. Read [references/planning-grill.md](references/planning-grill.md) and run its planning interview before work-unit decomposition.

- **Interactive by default:** inspect repository evidence, then ask high-value questions that resolve goals, acceptance, in/out scope, alternatives, assumptions, relevant constraints, and failure behavior. Provide a recommendation and tradeoff with each question. Several iterations are expected when they prevent downstream rework.
- **Auto when explicitly requested:** if the first task argument is exactly `auto` or `--auto`, pose the same material questions to yourself, answer from repository evidence and the smallest reversible assumptions, and record the results. Auto mode changes who answers; it does not skip the grill or broaden authority.
- **Decision record:** before decomposition, explicitly record mode, iteration count, gate, key question/resolution decisions, in scope, out of scope, assumptions, open questions, a Goals/Acceptance/Boundaries/Alternatives/Assumptions ambiguity assessment, and the plan lock.

Scale the resulting execution plan to risk:

- **Mechanical:** 1–3 steps.
- **Normal:** acceptance criteria, owning code/callers/contracts, implementation steps, tests, and documentation impact.
- **Complex/high-risk:** additionally capture invariants, alternatives, compatibility/migration/rollback, security/resilience, dependencies, and one independent challenge when useful.

Resolve repository facts by reading code/tests/configuration. In interactive mode, ask the user only when product intent remains materially ambiguous. In auto mode, make and record the smallest reversible assumption unless doing so would change the requested outcome or require new authority.

Decompose non-trivial work into the smallest coherent, independently committable units. Each unit records:

- goal and observable acceptance criteria;
- dependencies and integration order;
- exclusive file/module ownership;
- contracts and invariants it may change;
- authoritative documentation it must update, or a concrete `Docs-Impact: none — <reason>`;
- functions or modules whose complexity should be compared;
- exact verification commands.

One unit should produce one reviewable commit or commit-ready change. Do not split code from its tests or documentation merely to create more parallelism. Commit only when the user or repository workflow authorizes it.

Once the user approves the decision record, or auto mode locks it, execution should be rapid and autonomous. Do not ask for routine implementation decisions already bounded by the plan. Reopen only the invalidated decision when evidence disproves a material assumption or acceptance criterion, scope/public contracts must expand, consequences materially change, or new authority is required; then append the decision, increment the iteration count, relock, and resume.

If the repository already contains an accepted Spec Kit `tasks.md`, OpenSpec change `tasks.md`, or BMAD implementation story/spec, treat that artifact as authoritative planning input. Preview its translation with `${CLAUDE_PLUGIN_ROOT}/tools/spec_bridge.py`; import ledger units only with explicit acceptance. Do not regenerate, reinterpret, or replace the upstream specification workflow.

If execution disproves a plan assumption, use the focused planning re-entry rule above before continuing.

## 2. Spend tokens where they change the answer

Use the cheapest capable lane:

- fast/tool-heavy read-only model for search, repository mapping, test discovery, builds, lint/static checks, and complexity measurement;
- normal coding model for ordinary implementation;
- deep model for subtle state/algorithm/integration work or ambiguous debugging;
- top model only for architecture adjudication, security/high-consequence review, or materially uncertain decisions.

Use stronger reasoning for unresolved planning; return routine execution to configured normal/fast lanes after lock. Maximum reasoning, extra agents, and skills require task-relevant value, not availability. Use supported host controls and report unapplied model switches honestly. Strong deterministic evidence is enough for low-risk work.

**Dispatch is an action, not a preference.** Before execution, read [references/routing.md](references/routing.md), resolve and lock each unit's host, role, named agent, requested model/effort, and delegated or justified inline mode. For delegated units, invoke that agent through the host before any source edits; do not silently implement in the coordinator. Pass the complete unit contract and wait for its result. Record invocation evidence separately from effective-model evidence; missing host metadata stays `UNVERIFIED`. Report blocked routing or an explicitly accepted fallback. Workers execute their assigned unit without recursively redispatching themselves.

## 3. Parallelize meaningful independence

Run independent work units concurrently when it reduces wall-clock time or anchoring, for example disjoint modules, separate caller/test investigations, competing debugging hypotheses, or non-contending test/static/documentation checks.

Keep work sequential when it has unmet dependencies or shared mutable state.

Parallel writers require disjoint ownership, isolated branches/worktrees, one accountable agent per unit, and an explicit integration step. Each agent receives the same unit contract and runs the complete `plan -> implement -> document -> simplify -> verify` cycle. Otherwise use one writer.

For complex, long, parallel, or resumable tasks, give every lane the same compact evidence and use `${CLAUDE_PLUGIN_ROOT}/tools/work_units.py` to persist the locked planning decisions, dependencies, ownership, lifecycle evidence, documentation impact, verification, and commit SHA under ignored `.agent-state/work-units/`. Activate one unit so installed stop hooks can enforce its lifecycle gate. Do not create ledger state for routine fixes where it adds no handoff value.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/tools/work_units.py" init <id> --title <title> --goal <goal> \
  --acceptance <criterion> --owns <path> --base-ref HEAD \
  --planning-mode interactive --planning-gate pass --decision "D1: accepted approach" \
  --in-scope <scope> --out-of-scope <boundary> --docs-impact required --doc-path <path> --activate
python3 "${CLAUDE_PLUGIN_ROOT}/tools/work_units.py" advance <id> --evidence <stage-evidence>
python3 "${CLAUDE_PLUGIN_ROOT}/tools/check.py" --active
python3 "${CLAUDE_PLUGIN_ROOT}/tools/work_units.py" close
```

## 4. Implement the smallest correct design

**Minimum sufficient change:**

- Read affected code/callers; preserve the locked goal, acceptance criteria, non-goals, and untouched surfaces.
- Prefer no change when behavior exists; otherwise delete, reuse, or use native capabilities before adding code. Fix root causes, not stacked symptoms.
- Justify new abstractions, dependencies, configuration, fallbacks, or duplicate implementations by accepted requirements or evidenced risks—not future possibilities.
- If unrelated scope or scaffolding grows, pause and choose a smaller coherent design; do not fragment code to game metrics.
- Stop after acceptance, affected documentation, and required verification pass. Preserve safety, compatibility, accessibility, recovery, and authorization boundaries.

## 5. Debug and change behavior with evidence

For ambiguous failures: reproduce → trace → form competing hypotheses → run discriminating checks → establish root cause → implement the smallest causal fix → add regression evidence.

For behavior changes, use RED → GREEN → REFACTOR when practical. Use characterization tests before risky refactors. Do not force ceremonial TDD for trivial deterministic edits.

Run relevant existing tests first. Add/change tests for uncovered acceptance, regressions, or credible affected risks; state what would otherwise go undetected. Reuse infrastructure; avoid redundant cases and unrelated coverage backfills. Size coverage to risk, not arbitrary test-count or test-to-code-size limits.

## 6. Document in the same unit and commit

Documentation is a live specification of the system, not a release-end summary. Every plan and work unit contains **Documentation Impact**:

- `REQUIRED` — authoritative docs must change;
- `GENERATED` — regenerate/check generated references;
- `NOT AFFECTED` — state a concrete reason.

Update documentation after implementation and before simplification. The authoritative documentation must travel in the same logical commit as the code it explains. It captures what changed and, where relevant, the API methods and contracts, purpose, intent, protected goal/invariant, constraints, compatibility, and operational/failure behavior.

A code commit without documentation changes must carry a concrete `Docs-Impact: none — <reason>` in its commit message or unit evidence. A later documentation-only commit does not repair a code commit that was knowingly incomplete; amend or squash the logical unit so the specification and code agree at every reviewable commit.

When commits are produced, verify the range before handoff:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/tools/commit_docs.py" <base-ref>
```

Good documentation explains **function, intent, goal/invariant, contract, constraints, and relevant operational/failure behavior**. Do not comment obvious syntax.

If the repository already contains an outside-in product behavior specification and this change alters documented user-visible behavior, update only the affected feature/foundation/checklist/triage artifacts. **Do not create a product behavior specification unless the user asks for one.**

Run repository-native docs builds, doctests, examples, link checks, schema/reference generation, or clean-diff checks when applicable. Never report an unexecuted docs check as passing.

## 7. Simplify with measured complexity

After documentation is current, simplify the implementation without changing accepted behavior:

1. remove duplication, dead paths, speculative abstraction, and unnecessary dependencies;
2. prefer guard clauses, cohesive helpers, data-driven dispatch, and existing native patterns when they improve clarity;
3. score changed Python functions with `${CLAUDE_PLUGIN_ROOT}/tools/complexity.py` (or the repository-native equivalent for another language);
4. compare against the unit's starting ref when possible and report current score plus delta;
5. treat `1–5` as Excellent, `6–10` as Good, `11–20` as Moderate Risk, and `>20` as High Risk / Refactor Required.

Complexity is evidence, not a gameable gate. Do not extract meaningless one-line helpers or obscure control flow merely to lower a number. Any score above 10 or material increase requires a concrete simplification recommendation or an explicit justification tied to cohesion, correctness, or performance. If simplification changes a documented contract, return to the documentation stage before verification.

Example:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/tools/complexity.py" changed_file.py --compare-ref <unit-start-ref>
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
python3 "${CLAUDE_PLUGIN_ROOT}/tools/check.py" <unit-start-ref> --head HEAD
```

Use `--active` when an active work-unit ledger supplies the immutable base ref. Before a commit exists, run the applicable component checks and report the commit-range gate as `NOT EXECUTED`; do not point the gate at a range that omits the working-tree change.

## 9. Explain every completed project

After all work units are integrated and the committed-range gate passes, invoke the `eli5` skill before final handoff. This is mandatory for every successful development workflow. Generate and check the dependency-free visual explainer under `.agent-state/eli5/` unless the user requests a versioned documentation path, then include its path and audience in the completion report.

Do not run the completion explainer for blocked or incomplete work. The project is not complete if the explainer fails to render or validate. The ELI5 artifact is a post-verification handoff, not a substitute for live authoritative documentation or executable evidence.

## Completion

Return concise:

- Result
- Work units / commits and dependency order
- Planning grill mode, iterations, key decisions, assumptions, boundaries, and lock/re-entry events
- Verification (exact commands/results)
- Routing: configured/requested settings, actual invocation reference, effective settings or `UNVERIFIED`, and any approved fallback
- Documentation impact and changed paths
- Complexity scores/deltas and simplification decisions
- ELI5 audience, slide count, verification, and artifact path
- Important decisions only when non-obvious
- Residual risk / blocked checks
