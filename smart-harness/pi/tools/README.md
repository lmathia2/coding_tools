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

It installs no Pi package and uses only Python's standard library plus the already-installed `pi` host executable. Child tasks are read-only by default. Writing tools must be explicitly supplied and should target isolated worktrees with disjoint ownership.
