# Host Adapters

WYSIWYShip provides one portable policy and maps it onto Codex, GitHub Copilot,
Claude Code, and Pi using each host's real execution mechanisms. Installing an
agent definition or naming a model is configuration, not proof that a specialist
was invoked.

## Entry points

| Host | Development | PR review | Explanation |
|---|---|---|---|
| Codex | coding request or `$engineering-workflow` | `$pr-review` | `$eli5` |
| Copilot | `Dev` | `ReviewPR` | `eli5` |
| Claude Code | `/dev` | `/review-pr` | `/eli5` |
| Pi | `/dev` | `/review-pr` | `/eli5` |

## Routing flow

1. The coordinator resolves a semantic role (`fast`, `normal`, `deep`, or `top`)
   through the active model profile.
2. It records host, named agent, requested model/reasoning, task, and route ID.
3. It invokes the host's native agent/subagent mechanism—or Pi's bundled launcher.
4. A receipt binds the route to an invocation and completion result.
5. Effective model settings remain `UNVERIFIED` unless host-produced metadata
   confirms them.

Codex and Pi coordinators inherit their active session model by default; their
specialist roles may request configured models. The balanced Codex profile, for
example, requests Terra for normal work, Sol for deep/top work, and Luna for fast
work. Other hosts translate the same semantic roles into their supported model
and effort controls.

## Capability boundary

Planning mode, execution continuation, model selection, and permission are
separate. If native continuation, isolation, dispatch, bounds, or observation is
missing, the adapter must disclose an accepted bounded fallback or block the
lane. It never implements a generic fake scheduler to make all hosts look alike.

The developer wiki follows the same rule: the currently active host writes pages
only on the configured full-refresh cadence. `wiki.py` tracks that cadence
without launching another provider or requiring OpenWiki.
