---
name: vscode
description: Vendored Pi-compatible VS Code CLI skill for showing file and Git differences to the user. Use when a visual side-by-side comparison is helpful and the existing `code` CLI is available.
license: MIT; adapted from badlogic/pi-skills at 90bb51cae36515a648515b633a81c0c6efc8c74d
metadata:
  source: badlogic/pi-skills
  source-commit: 90bb51cae36515a648515b633a81c0c6efc8c74d
---

# VS Code Diff Tools

This skill uses the VS Code host already present on machines running the VS Code harness. It installs nothing.

Compare files:

```bash
code -d <file1> <file2>
```

Compare the working file with a revision:

```bash
tmp="$(mktemp)"
git show <revision>:path/to/file > "$tmp"
code -d "$tmp" path/to/file
```

Compare staged and working versions:

```bash
tmp="$(mktemp)"
git show :path/to/file > "$tmp"
code -d "$tmp" path/to/file
```

Use only when `code` is already available. Otherwise report the ordinary textual diff; do not install VS Code or modify shell configuration.
