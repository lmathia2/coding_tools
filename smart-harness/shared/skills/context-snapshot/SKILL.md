---
name: context-snapshot
description: Create a compact immutable evidence bundle for a coding task or PR review using Git refs, diffs, file paths, line ranges, and command outputs. Use before parallel reviewers or long tasks so every lane works from the same repository facts without an external context extension.
---

# Context Snapshot

Create a bounded evidence package, not a copy of the whole repository.

Record:

- repository root;
- base/head commits or current HEAD;
- changed files and diff stat;
- task intent and acceptance criteria;
- relevant file paths, symbols, and line ranges;
- public/data/config contracts;
- test and documentation commands;
- known environment limitations.

For a PR, prefer `git diff <base>...<head>` and exact committed refs. For long tasks, store the snapshot under `.agent-state/<task>/context.md` and refresh it when the accepted plan or HEAD changes.

Parallel lanes must cite evidence from the same snapshot or explicitly report new evidence. Do not pass the coordinator's private narrative as fact.
