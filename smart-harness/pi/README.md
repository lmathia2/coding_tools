# Pi Adapter

Pi uses the same shared engineering skills as Copilot and Claude Code.

## Install the harness into a project

```bash
bash smart-harness/install.sh pi /path/to/project
```

This installs:

```text
.claude/skills/       shared skills
.pi/prompts/dev.md    /dev
.pi/prompts/review-pr.md
.pi/settings.json     references ../.claude/skills
```

## Recommended core extensions

```bash
bash smart-harness/pi/install-extensions.sh core
```

The core profile contains independently installable packages for subagents, worktrees, language-server diagnostics, GitHub PR status, and immutable file/diff context.

After installing `pi-subagents`, open `/subagents` and choose **Keep Pi available (async)** when you want the main agent to continue useful work while independent lanes run.

## Optional profiles

```bash
bash smart-harness/pi/install-extensions.sh testing
bash smart-harness/pi/install-extensions.sh observability
bash smart-harness/pi/install-extensions.sh productivity
bash smart-harness/pi/install-extensions.sh methodology
```

`methodology` installs full pinned Superpowers and Ponytail packages. It is not part of the core default because each adds its own always-on methodology.

## Curated Pi skills

Pi's official documentation points to `badlogic/pi-skills` for browser automation, web search, VS Code integration, Google APIs, and transcription.

Install the useful coding/research set globally:

```bash
bash smart-harness/pi/install-skills.sh useful
```

Or into one project:

```bash
bash smart-harness/pi/install-skills.sh useful --project /path/to/project
```

Some skills require Node.js, Chrome, API credentials, or their own setup. Add `--with-deps` to run `npm install --omit=dev` where a selected skill has a package manifest.

## Daily use

```text
/dev <task>
/review-pr <base ref and PR details>
```

Both workflows always plan first, parallelize independent lanes, update documentation during execution, and use PR-head worktrees for executable review.

Pi extensions run with full user permissions. Review extension source and pin/update deliberately.
