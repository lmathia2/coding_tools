# Planning grill and execution lock

Use this reference during the planning stage of every `Dev` / `/dev` implementation request. The grill is a planning subroutine, not another implementation workflow.

## Outcome

Produce a plan that an implementation context can execute without asking the user ordinary design or scope questions. Planning may take several human iterations; execution after plan lock should be rapid and autonomous.

The planning record must explicitly resolve:

- **Goals** — the observable outcome and who benefits;
- **Acceptance** — verifiable behaviors that distinguish done from almost done;
- **Boundaries** — in scope, out of scope, and surfaces that must not change;
- **Alternatives** — material options considered and why one was selected;
- **Assumptions** — inferred repository or product facts, their evidence, and confidence;
- **Constraints and failure behavior** — only those relevant to the change.

Inspect code, tests, configuration, history, and live documentation before asking. Resolve repository facts yourself. Ask the user only for intent, preference, priority, or authorization that evidence cannot determine.

## Select the mode

The default is `interactive`. A task whose first argument is exactly `auto` or `--auto` uses `auto`; remove that mode token before interpreting the task. The user may switch to auto during an interview.

### Interactive mode

1. Map the material decision tree from the request and repository evidence.
2. Ask the highest-value unresolved question first. Ask one focused question at a time unless two or three tightly coupled choices are more efficient in the host's structured question UI.
3. Include a recommended answer and the downstream tradeoff. Do not make the user invent options the repository already narrows.
4. Use each answer to close a branch or identify the next material branch. Do not march through a generic checklist or ask low-impact questions to appear thorough.
5. Iterate until the ambiguity assessment is acceptable or the user explicitly overrides it.
6. Present the decision record and ask once whether to lock the plan and execute. A clear instruction such as `proceed`, `ship it`, or `auto` is approval to lock.

The user can say `enough`, `good enough`, or equivalent at any point. Record this as `user-override`, preserve remaining ambiguity in the decision record, and ask for the final lock rather than hiding unresolved risk.

### Auto mode

Run the same decision tree, but pose each material question to yourself and record the selected answer. Resolve it in this order:

1. direct repository evidence or an accepted upstream specification;
2. an existing project convention or public contract;
3. the smallest reversible interpretation that satisfies the stated outcome;
4. an explicit assumption with rationale and confidence.

Auto mode does not broaden authority. It cannot self-authorize destructive operations, external publication, credential use, spending, access changes, or a material scope expansion. Within the authorized coding task, it should make ordinary implementation choices itself.

If product intent is unknowable, choose the smallest reversible behavior, record the assumption and alternative, and continue. Pause only when every reasonable assumption would materially change the requested outcome or require new authority.

## Ambiguity assessment

Assess the plan qualitatively across Goals, Acceptance, Boundaries, Alternatives, and Assumptions:

- `clear` — specific and executable without another decision;
- `mostly-clear` — a minor detail can safely follow evidence or convention;
- `mixed` — a reasonable implementer could choose materially different behavior;
- `vague` — the implementation would substantially guess at intent.

Lock normally when no dimension is `mixed` or `vague`. A user may lock with an explicit override; auto mode must turn remaining uncertainty into recorded, reversible assumptions before locking.

## Decision record

Include this block in the plan before work-unit decomposition:

```text
Planning grill
  Mode: interactive | auto | imported
  Iterations: <count>
  Gate: pass | user-override

Key decisions
  D1 [dimension] Question → resolution
     Why: evidence, recommendation, or tradeoff

In scope
  - ...

Out of scope
  - ...

Assumptions
  - assumption — evidence — confidence — consequence if false

Open questions
  - non-blocking unknown and how execution will handle it

Ambiguity
  - Goals: clear — reason
  - Acceptance: clear — reason
  - Boundaries: mostly-clear — reason
  - Alternatives: clear — reason
  - Assumptions: mostly-clear — reason

Plan lock
  Locked at: <timestamp or conversational checkpoint>
  Re-entry triggers: <material events that would reopen planning>
```

Copy the relevant decisions, scopes, assumptions, open questions, ambiguity notes, mode, gate, and iteration count into schema-v2 work-unit ledger records when the ledger is used. An imported accepted specification uses `imported` mode and records the source artifact as the controlling decision.

## Rapid execution after lock

Once locked, treat the plan as the execution contract and proceed through `implement -> document -> simplify -> verify` with almost no human input. Do not ask the user to choose routine code structure, naming, test placement, refactoring, model routing, retry strategy, or other decisions already bounded by the plan and repository conventions.

Solve ordinary implementation surprises, test failures, and local integration issues autonomously. Reopen planning only when evidence shows that:

- a key assumption or acceptance criterion is materially false or impossible;
- the requested outcome requires a scope or public-contract change outside the lock;
- alternatives now have materially different user-visible, compatibility, security, data-loss, or operational consequences;
- progress requires new authority or a destructive/external action not already authorized.

When re-entry is necessary, stop implementation, state the invalidated decision and evidence, ask only the smallest blocking question (or self-resolve in auto mode), append the new decision, increment the iteration count, and lock the revised plan before resuming. Do not restart the whole interview.
