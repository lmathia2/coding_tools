---
name: task-ledger
description: Use for long multi-step implementations to persist concise task state outside conversational memory and survive context compaction.
---
# Task Ledger
Use only when losing state would be costly. Recommended path: `.agent-state/<task-slug>/progress.md` (normally gitignored).

Keep:
- task and acceptance criteria;
- approved decisions;
- completed work;
- current step;
- verification evidence;
- open blockers;
- next action.

Update at phase boundaries, not every tool call. After compaction/handoff, trust repository state, git diff/history, executable verification, then the task ledger before conversational recollection.

The ledger is not architectural truth; stable decisions belong in durable repository documentation.
