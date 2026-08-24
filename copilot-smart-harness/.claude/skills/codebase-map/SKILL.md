---
name: codebase-map
description: Use before risky work in an unfamiliar code area to build a compact evidence map of ownership, callers, tests, contracts, and change boundaries.
---
# Codebase Map
Do not read the entire repository. Map only the slice relevant to the task.

Return:
- Owning implementation: paths and important symbols.
- Entry points/callers: direct callers and public surface.
- Data/contracts: schemas, interfaces, config, serialization, persistent state.
- Tests: owning tests, integration tests, analogous tests.
- Similar patterns: one or two implementations worth copying.
- Change boundary: likely-to-change files and files that should probably not change.
- Risk edges: compatibility, state/concurrency, migration, security, generated code.
- Unknowns: facts not established.

Keep the map compact enough that another agent can consume it without repeating exploration.
