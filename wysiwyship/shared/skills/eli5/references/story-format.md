# Package ELI5 story format

Provide one JSON object to `render_explainer.py`.

```json
{
  "title": "Understand and run the package",
  "subtitle": "The problem, first five minutes, architecture, and deeper paths",
  "audience": "Curious developer",
  "summary": "One sentence describing the package, its user, and the problem it solves.",
  "slides": [
    {
      "eyebrow": "INSTALL",
      "title": "Install the package, then run one request",
      "body": "The installer copies package-local tools and host adapters, then the native host accepts the first developer request.",
      "code": "bash install.sh all /absolute/path/to/project\n\n/dev add one bounded feature",
      "evidence": ["README.md:Getting started", "scripts/install_harness.py:Installer.run"],
      "accent": "coral"
    },
    {
      "eyebrow": "UNDER THE HOOD",
      "title": "A request moves through the package's main components",
      "flow": [
        {"title": "Host entry", "body": "Accept the developer request", "path": "host adapter"},
        {"title": "Shared policy", "body": "Plan and execute the package workflow", "path": "shared/skills/"},
        {"title": "Evidence tools", "body": "Verify the result and report failures", "path": "tools/"}
      ],
      "evidence": ["docs/ARCHITECTURE.md", "tests/test_harness.py"],
      "accent": "mint"
    },
    {
      "eyebrow": "PROOF",
      "title": "Follow the authoritative paths when you need more detail",
      "metrics": [
        {"value": "3", "label": "starting points", "detail": "Architecture, contracts, and source entry points"}
      ],
      "evidence": ["docs/ARCHITECTURE.md", "docs/WORKFLOW_CONTRACTS.md", "README.md"],
      "accent": "gold"
    }
  ],
  "closing": {
    "title": "Install it, run one request, then trace the flow",
    "body": "Use the package once, then follow the named architecture path into the source.",
    "next_steps": ["Open the architecture guide and trace the first-run command"]
  }
}
```

## Fields

- Required top level: `title`, `summary`, `slides`.
- Optional top level: `subtitle`, `audience`, `closing`.
- Use `Curious developer` unless the user supplies a more specific developer profile.
- Each slide requires `title` and may use `eyebrow`, `body`, one structured visual, `evidence`, and `accent`.
- The structured visual is exactly one of `flow`, `code`, `items`, `metrics`, `bullets`, or `analogy`.
- `flow` contains two to five ordered nodes with `title`, `body`, and optional `path`. Use it for real calls, copies, reads, writes, transformations, or ownership boundaries.
- `evidence` contains up to four inspected source paths, symbols, commands, configuration keys, schemas, tests, or result identifiers. The renderer requires at least three evidence anchors across the story.
- `analogy` is an object with `title`, `body`, and optional `boundary`.
- `items` contains up to four peer concepts with `title`, `body`, and optional `tag`. Do not use it when order or connections matter.
- `metrics` contains up to four objects with `value`, `label`, and optional `detail`. Use only measured, relevant values.
- `accent` is `coral`, `mint`, `gold`, `sky`, or `violet`.
- `closing` accepts `title`, `body`, and up to four immediate actions or honest next steps.

## Content contract

A normal package should use 6–8 content slides. The renderer accepts 3–8 for
genuinely small packages and adds title and closing slides, keeping the complete
deck at 10 slides or fewer. A recent diff updates the package story only when it
materially changes installation, use, architecture, a public contract, or an
important limitation.

Every story must include:

- one exact installation command and one exact first-run invocation;
- one `flow` showing connected architecture or execution;
- at least three grounded evidence anchors;
- a representative source path and symbol or contract when code is available;
- a pointer to authoritative documentation or source entry point for more detail;
- proof and limitations that distinguish executed facts from inference;
- a closing action the developer can perform immediately.

Do not treat folders listed side by side as an architecture diagram. Each `flow` edge must have a real meaning stated by the ordered node bodies: calls, copies, reads, writes, transforms, delegates, owns, or emits.

## Density limits

- 3–8 content slides, producing at most 10 rendered slides including title and closing;
- up to five bullets, five flow nodes, four items, four metrics, and four evidence anchors per slide;
- titles under 90 characters, bullets under 180 characters, and body text under 700 characters;
- code excerpts under 1,200 characters and limited to a command, contract, or representative control path;
- no HTML markup in values; all values are rendered as escaped text.

Prefer multiple focused slides over dense combinations. Evidence anchors may accompany a body and one structured visual, but do not combine multiple structured visuals.
