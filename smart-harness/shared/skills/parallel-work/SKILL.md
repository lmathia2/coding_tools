---
name: parallel-work
description: Parallelization policy for agentic coding and review. Run independent analysis and verification concurrently; parallelize writes only when isolated and dependency-safe.
---

# Parallel Work

After the plan, identify the dependency graph.

## Parallelize by default when independent

Good parallel work:

- repository exploration of separate modules;
- competing debugging hypotheses;
- architecture/correctness/security review perspectives;
- test execution and static analysis;
- independent unit/integration suites that do not contend for the same service/port/state;
- documentation or analysis that does not modify shared files.

Launch independent subagents together rather than serially.

## Keep sequential when dependent

Do not parallelize steps where one depends on another's output, or when agents would edit the same files/state.

## Parallel writes

Parallel code implementation is allowed only when:

1. the plan cleanly partitions work by component/file ownership;
2. each writer has an isolated branch/worktree;
3. interfaces between partitions are agreed before edits;
4. integration is explicit and followed by the full relevant verification suite.

Prefer parallel read-only analysis over parallel writers when boundaries are uncertain.

## Completion barrier

Do not synthesize or implement downstream work until all required parallel predecessors have returned or been explicitly cancelled.
