# Project ELI5 story format

Provide one JSON object to `render_explainer.py`.

```json
{
  "title": "What we built",
  "subtitle": "A plain-language walkthrough",
  "audience": "Curious non-technical teammate",
  "summary": "One sentence describing the result and its value.",
  "slides": [
    {
      "eyebrow": "THE PROBLEM",
      "title": "Why this work mattered",
      "body": "Two or three short sentences.",
      "bullets": ["Concrete pain", "Concrete outcome"],
      "accent": "coral"
    },
    {
      "eyebrow": "THE MAP",
      "title": "The pieces that work together",
      "items": [
        {"title": "Input", "body": "What enters the system", "tag": "1"},
        {"title": "Decision", "body": "What the project decides", "tag": "2"},
        {"title": "Result", "body": "What comes out", "tag": "3"}
      ],
      "accent": "mint"
    },
    {
      "eyebrow": "PROOF",
      "title": "How we know it works",
      "metrics": [
        {"value": "41", "label": "tests passed", "detail": "Full local suite"}
      ],
      "accent": "gold"
    }
  ],
  "closing": {
    "title": "The simple takeaway",
    "body": "Restate the value without jargon.",
    "next_steps": ["One honest limitation or next step"]
  }
}
```

## Fields

- Required top level: `title`, `summary`, `slides`.
- Optional top level: `subtitle`, `audience`, `closing`.
- Each slide requires `title` and may use `eyebrow`, `body`, `analogy`, `bullets`, `items`, `metrics`, `code`, and `accent`.
- `analogy` is an object with `title`, `body`, and optional `boundary`.
- `items` contains up to four objects with `title`, `body`, and optional `tag`.
- `metrics` contains up to four objects with `value`, `label`, and optional `detail`.
- `accent` is `coral`, `mint`, `gold`, `sky`, or `violet`.
- `closing` accepts `title`, `body`, and up to four `next_steps`.

## Density limits

- 3–9 content slides; the renderer adds title and closing slides.
- Up to five bullets, four items, and four metrics per slide.
- Keep titles under 90 characters, bullets under 180 characters, and body text under 700 characters.
- Keep code excerpts under 1,200 characters and use them only for audiences that benefit.
- Use no HTML markup in values. The renderer treats every value as text and escapes embedded JSON safely.

Prefer multiple focused slides over dense combinations. A slide may use body plus one structured element; avoid combining bullets, cards, metrics, analogy, and code unless the content remains sparse.
