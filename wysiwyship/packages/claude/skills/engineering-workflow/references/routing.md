# Resolve, dispatch, record, check

Use for development units and PR review lanes on every host. A skill describes work; an agent definition configures a potential child. Neither invokes a model. Keep the parent session's model separate from the child's route.

## Lock the route

Run the installed helper before dispatch and retain its JSON output with the unit's plan:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/tools/routing.py" plan --host codex --workflow dev --role normal --task filter-tasks
```

Use the active host (`codex`, `claude`, `copilot`, `pi`), `dev` or `review_pr`, and the selected semantic role. The helper reads the project's installed models.json, otherwise the configuration beside its runtime (including native-plugin or global installations). Use `--config` for an explicit alternate configuration. Model profiles supply settings; instructions must not embed model IDs. `--profile` is an explicit experiment, not a silent fallback. Verify that the host-loaded agent configuration agrees with the resolved profile; changing JSON alone does not reload native agents.

Default non-trivial implementation to one delegated normal/deep worker. A mechanical change can use `--execution inline --reason "<why delegation adds no value>"` only in a context permitted to write; this explicitly inherits the current session, not the specialist's model. Normal helper commands, planning, integration, and ELI5 can stay in the coordinator. Do not create a new model call for each lifecycle phase.

Record exceptions/fallbacks in the plan before use. If an agent, model, reasoning control, or required permission is unavailable, stop that lane or use a previously accepted alternative with a new route ID and a reason; never silently substitute. Auto planning does not expand permissions. Scope and acceptance remain locked through a routing-only change.

## Invoke the host, not a role in prose

| Host | Actual dispatch action |
| --- | --- |
| Codex | Invoke the resolved custom agent through the available subagent tool. If the tool only exposes explicit model/effort overrides, pass those settings plus the installed agent instructions and record this mechanism; a role label alone is insufficient. Do not use full-history inheritance when the host disallows overrides in that mode. |
| Claude Code | Invoke the Agent tool with the resolved subagent type, not the built-in general-purpose fallback. Native-plugin agents use the `wysiwyship:` namespace, which the plugin helper resolves automatically. |
| Copilot | Invoke the available `agent`/`runSubagent` tool with the resolved custom-agent name. Confirm it is exposed in the coordinator's allowed agents. Do not substitute a generic subagent without recording a new route. |
| Pi | Launch `parallel-pi.py` even for a single delegated unit. Give the task `name`, `prompt`, `role`, and the complete plan object in `routing`. Use the same configuration/profile for both helpers. The launcher rejects settings inconsistent with that plan. |

Development workers receive scope, acceptance, owned paths, dependencies, documentation, verification, and the route ID. They run the complete lifecycle without asking again about locked choices or recursively dispatching another copy of themselves. Parallel writers still need disjoint ownership and isolated worktrees. Review workers receive the exact PR HEAD and worktree, lane scope, and route ID. Wait for results before integration or a review recommendation.

Permission is separate from model selection. Read-only agents cannot necessarily run builds/tests that write files; use a permitted execution context or record `NOT EXECUTED`. For Pi, `--capability execute`/`write` and any approval override require existing authorization. A fresh Pi process with no explicit model uses its own host default; it does not inherit the parent's interactive selection.

## Record evidence without inventing certainty

Normalize the actual tool result/session metadata into a receipt. Do not invent IDs, references, settings, or completion. Keep raw evidence local and omit secrets. Each receipt has:

```json
{
  "schema_version": 1,
  "route_id": "<from the locked plan>",
  "agent": "<from the locked plan>",
  "requested": {"model": "<requested ID or null>", "reasoning": "<requested effort or null>"},
  "invocation_id": "<host tool/session ID>",
  "source": "report",
  "evidence_ref": "<tool result or local transcript reference>",
  "status": "completed",
  "observed": null
}
```

`source: report` is coordinator transcription; `launcher` is runner-produced evidence (Pi emits `routing_receipt` automatically); `host` is host-produced metadata with a traceable reference. Use `started` while work runs and `failed` on failure. Only actual host metadata belongs in `observed: {model, reasoning}`. Model names in prompts, configuration, argv, or worker self-reports are not observations. Do not promote copied fields to host evidence.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/tools/routing.py" check --plan route.json --receipt receipt.json
```

`status: PASS` means the supplied receipt is consistent and completed; inspect `model_status` separately. It is `UNVERIFIED` without effective host metadata, `CONFIRMED` for matching host evidence, or `MISMATCH` (failure) for conflicting settings. `--require-confirmed` at plan creation makes missing effective settings fail completion; pin exact model IDs for that policy because aliases cannot be independently resolved here.

The checker validates consistency, not authenticity: user-editable JSON is not an attestation or proof that a model ran. Native dispatch remains a host/agent action; no generic scheduler, billing guarantee, or source-edit interception is implied.

Pi print mode supplies launcher evidence only, so it rejects confirmation-required routes before launching. On other hosts, check metadata availability before accepting that policy; do not promise unsupported confirmation.

## Gate and handoff

For ledger-managed units, pass `--routing-plan route.json` to `work_units.py init`. Pass `--routing-receipt receipt.json` to `advance`: invocation evidence is required before leaving plan, and completed evidence before leaving verify. Existing ledgers without a route remain readable. Newly dispatched workflows must attach their route; imported units can attach one at initialization or validate it separately before execution.

Use `work_units.py route ID --routing-plan route.json --reason "<accepted decision>"` to attach a route to an imported unit or change a blocked route. It preserves the prior route/receipt in `routing_history`, requires a new route ID for replacements, and clears current invocation evidence. Obtain a fresh receipt before advancing; completed units cannot be rerouted. This command records a decision, not user approval or new permissions.

For a PR lane or a small unit without a ledger, retain the plan/receipt together and run `routing.py check` before handoff. The range gate also accepts `--routing-plan` and `--routing-receipt`; call it per lane or check each lane separately. Missing/failed routing cannot be reported as successful independent review or model savings. Report requested settings, invocation, observed settings or `UNVERIFIED`, and fallback reasons alongside functional verification.
