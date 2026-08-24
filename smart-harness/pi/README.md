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

Independent Pi reasoning lanes can use `.pi/tools/parallel-pi.py`, which spawns bounded Pi print-mode children concurrently. It requires only the already-installed Pi executable and Python standard library.

The shared skills include the dependency-free methodology/minimality/context skills selected from Superpowers, Ponytail, and Pi Skills. No external Pi package-manager command, npm dependency, API key, browser package, or external checkout is part of the harness setup.
