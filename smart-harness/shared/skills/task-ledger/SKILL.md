---
name: task-ledger
description: Persistent concise state for long multi-stage agent tasks so compaction or handoff does not lose the accepted plan, progress, or verification evidence.
user-invocable: false
---

# Task Ledger

Use only when the task is long enough that losing state would be costly.

Recommended path:

```text
.agent-state/<task-slug>/progress.md
```

Keep:

- acceptance criteria;
- accepted plan/key decisions;
- completed steps;
- current step;
- verification evidence;
- blockers;
- next action.

Update at meaningful phase boundaries, not after every tool call.

After compaction/handoff, trust repository state, Git diff/history, executable evidence, and the ledger before conversational recollection.

Stable architecture belongs in ADRs/rules, not the task ledger.
