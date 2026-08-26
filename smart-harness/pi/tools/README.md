# Bundled Pi Tools

`parallel-pi.py` provides dependency-free parallel child-agent execution using Pi's own print-mode CLI.

Example:

```bash
cat > /tmp/tasks.json <<'JSON'
[
  {"name":"architecture","prompt":"Inspect the repository and propose the smallest safe design."},
  {"name":"tests","prompt":"Map existing tests and identify missing behavioral coverage."}
]
JSON

python3 .pi/tools/parallel-pi.py --tasks /tmp/tasks.json --cwd .
```

It installs no Pi package and uses only Python's standard library plus the already-installed `pi` host executable. Child tasks receive read-only tools, a root-confined working directory, a sanitized environment, and interactive approval by default.

An execution lane in an isolated worktree can opt in explicitly:

```bash
python3 .pi/tools/parallel-pi.py --tasks /tmp/verify.json --cwd .agent-worktrees/review \
  --capability execute --auto-approve
```

Use `--capability write` only for disjoint work-unit worktrees. Use `--inherit-env` only when the child genuinely requires parent-process secrets. Requested tools are rejected when they exceed the selected capability.
