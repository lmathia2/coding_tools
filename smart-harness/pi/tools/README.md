# Bundled Pi Tools

`parallel-pi.py` provides dependency-free parallel child-agent execution using Pi's own print-mode CLI.

Example:

```bash
cat > /tmp/tasks.json <<'JSON'
[
  {"name":"architecture","role":"deep","prompt":"Inspect the repository and propose the smallest safe design."},
  {"name":"tests","role":"fast","prompt":"Map existing tests and identify missing behavioral coverage."}
]
JSON

python3 .pi/tools/parallel-pi.py --tasks /tmp/tasks.json --cwd . --workflow dev
```

It installs no Pi package and uses only Python's standard library plus the already-installed `pi` host executable. By default it reads the project `.smart-harness/config/models.json`, falling back to the global `~/.smart-harness/config/models.json`, selects `active_profile`, and maps each task's semantic `role` to Pi `--model` and `--thinking` arguments. Use `--profile NAME` for a non-default experiment or explicit task-level `model`/`thinking` fields for one-off overrides. Child tasks receive read-only tools, a root-confined working directory, a sanitized environment, and interactive approval by default.

An execution lane in an isolated worktree can opt in explicitly:

```bash
python3 .pi/tools/parallel-pi.py --tasks /tmp/verify.json --cwd .agent-worktrees/review \
  --workflow review_pr --capability execute --auto-approve
```

Use `--capability write` only for disjoint work-unit worktrees. Use `--inherit-env` only when the child genuinely requires parent-process secrets. Requested tools are rejected when they exceed the selected capability.

Each result includes measured `duration_seconds`. To retain comparable per-child model evidence, save the JSON output and import it with the installed experiment tool:

```bash
python3 .pi/tools/parallel-pi.py --tasks /tmp/tasks.json --cwd . --workflow dev > /tmp/pi-results.json
python3 .smart-harness/tools/experiments.py import-pi /tmp/pi-results.json --workflow dev --profile quality
python3 .smart-harness/tools/experiments.py compare --group-by profile
```
