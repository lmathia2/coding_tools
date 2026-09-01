# WYSIWYShip Architecture

## Purpose

Provide one clear, low-interruption coding interface across Codex, Copilot,
Claude Code, and Pi that enforces an evidence-backed SDLC and minimizes total
model spend without weakening quality. Quality is the constraint; efficiency is the optimization.

## Goals

- two user-facing coordination workflows, development and PR review, plus an explicit/automatic project explanation skill;
- quality-first model routing with token/latency discipline;
- an evidence-first interactive or auto planning grill before source edits;
- an explicit plan lock followed by rapid, low-interruption execution;
- coherent commit-sized work units and useful parallelism without agent fan-out for its own sake;
- smallest correct implementation;
- live authoritative documentation synchronized in every logical code commit;
- measured changed-code complexity and an explicit simplification stage;
- executable verification;
- exact-HEAD isolated PR review;
- self-contained installation.

The architecture optimizes in a fixed order: locked acceptance and safety,
required SDLC evidence, developer clarity, then the smallest implementation,
context window, reasoning/model spend, and response. “Guaranteed quality” means
the workflow cannot claim completion while required evidence is missing; it does
not mean any agent or test suite can prove the absence of all defects.

## Default execution shape

```text
request
  -> planning grill resolves goals / acceptance / boundaries / alternatives / assumptions
  -> human or auto mode locks an explicit decision record
  -> coordinator defines work-unit dependency graph from the lock
  -> resolve each unit's route and invoke its named host agent (or explicit inline exception)
  -> each unit: plan -> implement -> document -> simplify -> verify
  -> integrate independently completed units in dependency order
  -> validate invocation receipts; report effective settings separately
  -> committed-range gate
  -> ELI5 visual handoff
  -> completion
```

## Portable policy over native executors

WYSIWYShip is the control policy, not another agent runtime. The same accepted
plan and evidence contract flows through a thin host adapter to the strongest
safe mechanism already supplied by that harness:

```text
portable policy
  planning decisions + work units + lifecycle + docs + simplicity + gates
        |
        v
host capability adapter
  plan | continue | dispatch | parallelize | isolate | observe | cancel
        |
        +--> Copilot native modes, custom agents and Fleet
        +--> Codex native task, subagent and sandbox controls
        +--> Claude Code native agent and permission controls
        +--> Pi native process/session controls plus parallel-pi
        `--> future harness: map supported capabilities; expose the gaps
```

The adapter does not reinterpret acceptance or implement its own SDLC. It maps
capabilities, invokes native execution, and reports evidence. Unsupported or
unobservable behavior is explicit; instructions and configuration never become
proof that a turn continued, an agent launched, a sandbox held, or a model
answered. Native capability first, accepted bounded fallback second, otherwise
blocked.

Planning-answer mode and execution mode are orthogonal. Interactive/auto/imported
controls who resolves the planning decisions. Interactive/native-autonomous/
bounded-fallback controls how the locked plan runs. Permissions, isolation and
model routing are additional independent axes. This prevents an `auto` request
from silently enabling broad permissions or mapping one host's Autopilot semantics
onto every harness.

Independent agents are conditional, not ceremonial. Add them when they provide material independent evidence or judgment: ambiguous debugging, architecture alternatives, high-risk boundaries, or PR semantic review.

`.agent-state/work-units/` is an optional operational checkpoint, not another planning system. It makes long or parallel work resumable and gives deterministic stop hooks an immutable base ref. The accepted plan and repository documentation remain authoritative; ignored ledger state records execution progress and evidence. Routine fixes omit it.

Planning is the deliberate human-collaboration boundary. Interactive mode may require several question/answer rounds and one final lock; `auto` runs the same decision tree internally and records its assumptions. Once locked, the execution coordinator handles routine design choices, implementation surprises, tests, refactoring, integration, and documentation without further user input. Planning re-entry is narrow: only an invalidated material decision, required scope/contract expansion, materially changed consequences, or new authority can reopen the lock.

Accepted Spec Kit, OpenSpec, or BMAD artifacts remain authoritative planning input.
The coordinator reads them directly rather than translating them into another
task schema.

## Shared policy

Four skills are distributed to projects and native packages:

1. `engineering-workflow` — all ordinary coding process: planning grill/lock, rapid autonomous execution, routing principles, parallelism, minimal design, debugging/TDD, documentation, verification, and successful-completion handoff;
2. `eli5` — evidence-based developer onboarding and change explanation covering purpose, first use, core concepts, connected source architecture, representative execution flow, rationale, proof, and limits in a dependency-free visual HTML artifact;
3. `pr-review` — worktree-based semantic + executable review and high-risk escalation;
4. `product-behavior-spec` — explicit specialist outside-in product documentation.

Contributor-only `skill-authoring` and optional `vscode` helpers remain in the
source repository but are not installed into user projects.

Repository mapping, context snapshots, task ledgers, Superpowers process, the four Ponytail-derived coding rules, and documentation synchronization are techniques inside the core workflows rather than separately discoverable skills.

## Model profiles

`config/models.json` is the single source of truth for model and reasoning-strength experiments. A named active profile contains platform-specific settings for each workflow coordinator (`dev`, `review_pr`) and shared specialist lane (`normal`, `deep`, `fast`, `top`). `config/configure-models.py --profile <name>` persists the selection and regenerates static Copilot/Claude frontmatter and Codex specialist TOML; validation rejects configuration or generated-file drift.

The installer normally derives a `detected` profile without mutating the canonical source. It asks each installed host only through documented or configuration-file surfaces, records the evidence class, and writes `.wysiwyship/model-discovery.json`. Account-visible or configured-restriction catalogs may select explicit models; an unprovable entitlement becomes `model: null` and inherits the active session. This prevents host detection from turning a supported model name into a false access claim.

The automatic ELI5 handoff runs in the configured `dev` coordinator after verification; an explicit `/eli5` invocation uses the host session model. Both retain the curious-developer baseline. The renderer validates that the story includes a connected architecture or execution flow and at least three inspected evidence anchors, then renders those paths and symbols beside the explanation. The renderer itself is deterministic and model-independent.

The config uses one provider-neutral `reasoning` property. Adapter translation is deliberately narrow:

| Adapter | Model setting | Reasoning setting | Enforcement boundary |
|---|---|---|---|
| Codex | `model` | `model_reasoning_effort` | Account-visible `model/list` catalog for custom specialists; coordinator inherits the active session |
| Copilot CLI | `model` | `reasoningEffort` | Per invoked custom agent; unavailable settings block or require an accepted fallback |
| VS Code Copilot | `model` | Session model picker | Current VS Code custom-agent frontmatter does not document per-agent effort |
| Claude Code | `model` | `effort` | Per command/agent frontmatter |
| Pi | `--model` | `--thinking` | Per parallel child; the coordinator inherits its active session |

Pi receives the selected config at `.wysiwyship/config/models.json`. Its helper resolves defaults from `--workflow` plus each task's semantic `role`; explicit per-task values take precedence for controlled experiments.

## Dispatch and evidence boundary

`tools/routing.py:resolve_route` reads that profile and maps a role to the host's named agent; it emits a unique locked route, not an invocation. The shared workflow requires the coordinator to invoke the native agent tool (Codex, Claude, Copilot) or `parallel-pi.py` (Pi), then retain a receipt. The same contract applies to development and each PR lane. One implementation worker owns the full lifecycle; it does not redispatch itself at each phase.

`routing.py:check_route` compares route ID, agent, requested settings, completion, and evidence references. `work_units.py` embeds the plan/receipt and blocks stage transitions on inconsistency; `check.py` composes that validation with functional checks. Pi additionally validates a batch's locked routes before launch and emits launcher receipts from actual subprocess results. A null Pi child model means host-default selection, not parent-session inheritance.

Requested settings and answering-model metadata are distinct. Launcher argv or coordinator reports stay `UNVERIFIED`; only attributed host metadata can yield `CONFIRMED`, and conflicting metadata fails. The optional `require_confirmed` policy blocks completion without matching effective settings. These are consistency checks on local evidence, not authenticated attestations, a universal scheduler, or interception of every source edit. Native clients still decide whether to follow the dispatch instruction; unsupported tools/permissions must be disclosed rather than silently substituted.

Controlled comparisons of profiles and workflows use the self-contained
`evals/runner.py` suite. Profile configuration still describes requested routing,
not confirmed answering-model identity.

## Platform adapters

### Copilot

Visible: `Dev`, `ReviewPR`.

Hidden specialists:

- `FastLane` — read-only exploration, deterministic execution, and complexity measurement;
- `WorkerNormal` — normal implementation;
- `WorkerDeep` — complex implementation;
- `DeepReasoner` — read-only debugging/challenge/PR reasoning;
- `TopReviewer` — focused high-risk security/resilience.

Agent identities are semantic rather than model-branded, so profile changes do not make delegation names or descriptions stale.

### Claude Code

Visible: `/dev`, `/review-pr`.

Hidden specialists:

- `smart-fast` — read-only exploration, deterministic execution, and complexity measurement;
- `smart-worker` — normal/mechanical implementation of one commit-sized unit;
- `smart-deep-reasoner` — read-only deep reasoning;
- `smart-deep-implementer` — complex implementation;
- `smart-top-reviewer` — architecture/security/adjudication.

Normal implementation uses one configured normal worker per independent commit-sized unit. This creates a real writer boundary while keeping the coordinator focused on dependency planning and integration.

### Capability boundary

Fast exploration agents have no structured edit/write tools, and exploration mode does not invoke shell execution. Verification necessarily executes repository commands, which may create caches or build outputs even when no source edit is intended; execution lanes therefore capture Git status before/after and use the delegated worktree. Pi additionally enforces capability allowlists, root-confined working directories, sanitized environments, and opt-in auto-approval. Prompt-level “read-only” wording is not treated as an operating-system sandbox.

### Pi

Visible: `/dev`, `/review-pr`. A bundled standard-library helper can run independent Pi print-mode children concurrently; no external extension is required.

## Distribution surfaces

The transactional installer remains the cross-host baseline and is the only Pi distribution. `scripts/build_packages.py` derives versioned Copilot and Claude Code plugin directories from the same canonical source tree. Generated package checks make drift a CI failure; package files are not edited directly. Plugin path placeholders point tools and hooks at their cached bundle, while operational state continues to live in the current repository's ignored `.agent-state/`.

## Development routing

```text
exploration/measurement/verification -> fast read-only
mechanical/normal implementation     -> normal
complex/debugging                    -> deep
architecture/security               -> top only when warranted
```

For normal low-risk work, passing behavior tests plus compiler/type/static evidence can complete the task without another premium semantic review.

## PR review flow

```text
resolve exact base + PR HEAD
  -> detached worktree
  -> inspect commit/work-unit coherence and live documentation
  -> parallel:
       semantic deep review
       full deterministic execution
  -> if HIGH_RISK:
       adversarial scenarios
       focused security/resilience
  -> falsify candidate BLOCKER/MAJOR
  -> recommendation + evidence
  -> cleanup
```

## Invariants

1. Every implementation unit runs `plan -> implement -> document -> simplify -> verify`.
2. Every implementation request runs a planning grill and records a lock before source edits; `auto` self-answers rather than skipping the decision work.
3. After lock, execution proceeds without routine human input and reopens only the invalidated material decision.
4. Non-trivial work is decomposed into coherent, independently committable units.
5. Parallelism requires real independence; writers require isolated ownership/worktrees.
6. Live authoritative documentation changes in the same logical commit as code, or the commit records a concrete no-impact reason.
7. Changed-function complexity is measured and increases are explained; scores are not gamed at the expense of cohesion.
8. Implementation applies the four lightweight coding rules without treating deletion or line count as a goal; quality boundaries outrank brevity.
9. Unexecuted checks are never PASS.
10. PR review executes complete feasible configured unit and integration suites at exact PR HEAD.
11. Premium-model fan-out is conditional on uncertainty/risk.
12. Product behavior specification generation is explicit, never automatic.
13. Runtime setup performs no external dependency installation.
14. Installed stop hooks are inert unless an active work-unit pointer exists.
15. Every successful development workflow produces and verifies a local ELI5 visual handoff after the committed-range gate passes.
16. The grounded repository wiki is initialized by default, remains derived rather than authoritative, and is fully rebuilt at its configured commit cadence using the active host rather than an external provider runtime.
