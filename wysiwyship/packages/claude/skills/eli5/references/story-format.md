# Developer ELI5 story format

Provide one JSON object to `render_explainer.py`.

```json
{
  "title": "How the release gate works",
  "subtitle": "Run it, trace it, and understand why it exists",
  "audience": "Curious developer",
  "summary": "One sentence describing the concrete capability and its value.",
  "slides": [
    {
      "eyebrow": "FIRST FIVE MINUTES",
      "title": "Run the gate against your current branch",
      "body": "The command compares the current commit range with the accepted base and executes the configured evidence checks.",
      "code": "python3 "${CLAUDE_PLUGIN_ROOT}/tools/check.py" <base-ref> --head HEAD",
      "evidence": ["tools/check.py:main", "config/checks.json"],
      "accent": "coral"
    },
    {
      "eyebrow": "UNDER THE HOOD",
      "title": "One command composes four independent checks",
      "flow": [
        {"title": "CLI", "body": "Parse the range and config", "path": "tools/check.py:main"},
        {"title": "Evidence", "body": "Run docs, complexity, project commands, and cleanliness", "path": "tools/check.py:run_checks"},
        {"title": "Result", "body": "Return text or structured JSON and a non-zero status on failure", "path": "tools/check.py:render_text"}
      ],
      "evidence": ["tests/test_harness.py:CheckGateTests"],
      "accent": "mint"
    },
    {
      "eyebrow": "PROOF",
      "title": "The contract is covered by executable tests",
      "metrics": [
        {"value": "4", "label": "check classes", "detail": "Docs, complexity, commands, cleanliness"}
      ],
      "evidence": ["tests/test_harness.py:test_gate_composes_docs_complexity_and_commands"],
      "accent": "gold"
    }
  ],
  "closing": {
    "title": "Trace one real change next",
    "body": "Start at the command, follow run_checks, then inspect the failing evidence object.",
    "next_steps": ["Run the gate on a small branch and open its JSON output"]
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

A normal project or non-trivial change should use 6–9 content slides. The renderer accepts 3–9 for genuinely small subjects and adds title and closing slides.

Every story must include:

- one exact installation, startup, invocation, or first-use command;
- one `flow` showing connected architecture or execution;
- at least three grounded evidence anchors;
- a representative source path and symbol or contract when code is available;
- proof and limitations that distinguish executed facts from inference;
- a closing action the developer can perform immediately.

Do not treat folders listed side by side as an architecture diagram. Each `flow` edge must have a real meaning stated by the ordered node bodies: calls, copies, reads, writes, transforms, delegates, owns, or emits.

## Density limits

- 3–9 content slides;
- up to five bullets, five flow nodes, four items, four metrics, and four evidence anchors per slide;
- titles under 90 characters, bullets under 180 characters, and body text under 700 characters;
- code excerpts under 1,200 characters and limited to a command, contract, or representative control path;
- no HTML markup in values; all values are rendered as escaped text.

Prefer multiple focused slides over dense combinations. Evidence anchors may accompany a body and one structured visual, but do not combine multiple structured visuals.
