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

It installs no Pi package and uses only Python's standard library plus the already-installed `pi` host executable. By default it reads the project `.wysiwyship/config/models.json`, falling back to the global `~/.wysiwyship/config/models.json`, selects `active_profile`, and maps each task's semantic `role` to Pi `--model` and `--thinking` arguments. Use `--profile NAME` for a non-default experiment or explicit task-level `model`/`thinking` fields for one-off overrides. Child tasks receive read-only tools, a root-confined working directory, a sanitized environment, and interactive approval by default.

An execution lane in an isolated worktree can opt in explicitly:

```bash
python3 .pi/tools/parallel-pi.py --tasks /tmp/verify.json --cwd .agent-worktrees/review \
  --workflow review_pr --capability execute --auto-approve
```

Use `--capability write` only for disjoint work-unit worktrees. Use `--inherit-env` only when the child genuinely requires parent-process secrets. Requested tools are rejected when they exceed the selected capability.

Each result includes measured `duration_seconds`. To retain comparable per-child model evidence, save the JSON output and import it with the installed experiment tool:

```bash
python3 .pi/tools/parallel-pi.py --tasks /tmp/tasks.json --cwd . --workflow dev > /tmp/pi-results.json
python3 .wysiwyship/tools/experiments.py import-pi /tmp/pi-results.json --workflow dev --profile quality
python3 .wysiwyship/tools/experiments.py compare --group-by profile
```

For workflow-managed dispatch, first resolve `routing.py plan --host pi --role normal --task <name>` and include its entire output as the task's `routing` object. Task name, role, and resolved runtime settings must match it; the whole batch is validated before launch. A task override that conflicts with the plan is rejected, not silently applied.

Each child result now contains `routing_receipt`: route ID, unique launcher invocation ID, requested settings, completion/failure, and a launcher evidence reference. Save the result and pass that receipt to `routing.py check` or `work_units.py advance --routing-receipt`. Effective settings remain `UNVERIFIED`: the print-mode launch arguments are not provider telemetry. With no explicit model, a fresh child uses its own host default; it does not inherit an interactive parent's selection. Model-based experiment grouping describes requested settings, not proven answering models.
