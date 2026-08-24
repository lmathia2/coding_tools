---
name: codebase-map
description: Build a compact task-relevant map of ownership, callers, contracts, tests, and risk edges before complex changes.
---

# Codebase Map

Map only the slice relevant to the task.

Return:

- owning implementation paths/symbols;
- entry points and callers;
- interfaces, schemas, config, persistent state;
- relevant unit/integration/e2e tests;
- one or two analogous repository patterns;
- likely change boundary;
- compatibility/security/state/migration risk edges;
- unresolved facts.

Use independent exploration subagents in parallel when separate modules can be investigated without dependency.

Keep the result concise enough that another worker can act on it without repeating discovery.
