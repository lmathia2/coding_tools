# Pi Adapter

The Pi adapter is fully contained in this repository. It does not install packages or extensions from npm/GitHub.

Installed project layout:

```text
.pi/
  prompts/dev.md
  prompts/review-pr.md
  tools/parallel-pi.py
  settings.json          # references ../.claude/skills
```

Use:

```text
/dev <task>
/review-pr <base ref and PR details>
```

Independent Pi reasoning lanes can use `.pi/tools/parallel-pi.py`, which spawns bounded Pi print-mode children concurrently. It requires only the already-installed Pi executable and Python standard library. Children are confined to the configured root, receive read-only tools and a sanitized environment by default, and do not auto-approve tool use unless explicitly requested.

The installation also provides `.wysiwyship/tools/complexity.py` for dependency-free Python function complexity scoring and baseline comparison.

The five shared skills fold selected dependency-free planning, minimality, and context concepts from the pinned sources documented under `.wysiwyship/vendor/`. No external Pi package-manager command, npm dependency, API key, browser package, or external checkout is installed by the harness.
