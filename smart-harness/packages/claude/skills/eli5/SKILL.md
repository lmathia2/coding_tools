---
name: eli5
description: "Explain a completed coding project or technical change for a chosen audience and produce a polished, dependency-free visual HTML walkthrough. Use when the user invokes /eli5, asks to explain a project simply or to a particular role/age, or when a Smart Harness development workflow has completed successfully and needs its mandatory post-completion explanation."
---

# Project ELI5

Turn verified code into an accurate, approachable story and a self-contained visual explainer. Preserve the project's real purpose and constraints while changing vocabulary, depth, and analogies for the audience.

## 1. Establish the completion boundary

For an automatic post-development run, start only after all required work units are integrated and verification has passed. Do not disguise blocked or unverified work as complete. For an explicit `/eli5` request, explain the requested repository state and label any uncertainty.

Infer the audience from the request and conversation. If none is stated, use a curious non-technical teammate: plain language, respectful tone, concrete examples, and essential technical terms defined on first use. Do not interrupt a completed development workflow to ask about audience unless the choice materially changes a required deliverable.

## 2. Read evidence before explaining

Inspect the authoritative implementation, tests, live documentation, public contracts, configuration, verification results, and relevant commit/work-unit history. Build the explanation from evidence, not the plan or commit title alone.

Capture:

- the problem and why it mattered;
- what a user or operator can do now;
- the smallest useful system map;
- one representative end-to-end flow;
- important contracts, constraints, and tradeoffs;
- proof that the result works;
- limitations or sensible next steps.

Never expose secrets, credentials, private customer data, or irrelevant internal details.

## 3. Calibrate the story

Start with the purpose, then explain the mechanism. Use one coherent analogy and state where it stops matching reality. Prefer one idea per sentence for beginners. For technical audiences, retain proper names, architecture boundaries, tradeoffs, and failure behavior without re-teaching basics. For managers, lead with outcome, risk, cost, and decisions. Never talk down to the audience.

Create a short story of 5–9 slides:

1. what was built and for whom;
2. the old problem or friction;
3. the analogy and its boundary;
4. the system map;
5. the main flow;
6. one or two important design decisions;
7. evidence and verification;
8. limitations or next steps.

Combine or omit slides when the project is small. Do not pad the deck.

## 4. Render the visual explainer

Read [references/story-format.md](references/story-format.md), then create the story JSON under `.agent-state/eli5/<project-slug>.json`. Render it with the bundled standard-library tool:

```bash
python3 <skill-directory>/scripts/render_explainer.py \
  --input .agent-state/eli5/<project-slug>.json \
  --output .agent-state/eli5/<project-slug>.html
```

The generated HTML must remain a single offline file: no CDN, external font, package manager, build tool, tracking, or network request. It uses a fixed 1920×1080 stage, uniform viewport scaling, strong editorial hierarchy, accessible semantic structure, keyboard/buttons/swipe navigation, progress, restrained reveals, print styles, and reduced-motion support.

Use short labels, visual grouping, flow arrows, metrics, and code only when they clarify the explanation. Do not turn every concept into a card or fill slides with prose. Split overloaded slides rather than shrinking text.

## 5. Verify and deliver

Run the renderer once with `--check` before writing. Then verify:

- the source paths and claims still match the completed code;
- the artifact contains no `http://`, `https://`, remote script, remote stylesheet, or runtime dependency;
- every slide is readable at the fixed stage without overflow or overlap;
- keyboard navigation and reduced-motion behavior are present;
- the analogy is helpful but not misleading;
- the final slide distinguishes completed evidence from future ideas.

Visually inspect the rendered deck when browser or screenshot tooling is available. Otherwise report visual inspection as `NOT EXECUTED`, while still running the deterministic renderer and static tests.

Return a concise plain-language summary plus the absolute HTML path, audience, slide count, verification evidence, and any uncertainty. A successful Smart Harness development run is not ready for final handoff until this ELI5 artifact has been generated and checked.
