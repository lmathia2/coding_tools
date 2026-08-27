---
name: eli5
description: "Explain a completed coding project or technical change to a curious developer through its what, how, and why, and produce a polished, dependency-free visual HTML walkthrough. Use when the user invokes /eli5, asks to understand a project's purpose and implementation, or when a WYSIWYShip development workflow has completed successfully and needs its mandatory post-completion explanation."
---

# Project ELI5

Turn verified code into an accurate, approachable story and a self-contained visual explainer. Always teach a curious developer what changed, how the system works, and why the implementation and design choices exist.

## 1. Establish the completion boundary

For an automatic post-development run, start only after all required work units are integrated and verification has passed. Do not disguise blocked or unverified work as complete. For an explicit `/eli5` request, explain the requested repository state and label any uncertainty.

Use a curious developer who wants to learn the what, how, and why as the baseline audience for every run. Assume general programming literacy without assuming familiarity with the repository, architecture, or domain. Define project-specific terms on first use and include concrete source paths, contracts, flows, and tradeoffs when they aid understanding. If the user names a role or experience level, adapt emphasis and vocabulary on top of this baseline; never omit the what, how, or why. Do not interrupt a completed development workflow to ask about audience unless the choice materially changes a required deliverable.

## 2. Read evidence before explaining

Inspect the authoritative implementation, tests, live documentation, public contracts, configuration, verification results, and relevant commit/work-unit history. Build the explanation from evidence, not the plan or commit title alone.

Capture three explicit layers:

- **What** — the problem, changed behavior, affected surfaces, and what a user or operator can do now;
- **How** — the smallest useful system map, one representative end-to-end flow, and the key implementation or API contracts;
- **Why** — the intent, important design decisions, constraints, rejected or avoided alternatives when evidenced, and tradeoffs;
- **Proof** — tests, verification, complexity or other quality evidence, limitations, and sensible next steps.

Never expose secrets, credentials, private customer data, or irrelevant internal details.

## 3. Calibrate the story

Start with purpose and observable behavior, then move through architecture into a representative implementation flow. Retain proper names, source paths, architecture boundaries, contracts, tradeoffs, and failure behavior. Explain code selectively rather than dumping it. Use one coherent analogy only when it clarifies the mechanism, and state where it stops matching reality. Never reduce the explainer to a release summary or talk down to the reader.

Create a short story of 5–9 slides:

1. what was built and what changed;
2. why the old problem mattered and the intent behind the change;
3. the system map and ownership boundaries;
4. how one representative flow moves through the implementation;
5. one or two important design decisions and why they were chosen;
6. contracts, failure behavior, or an analogy where useful;
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
- the deck explicitly answers what changed, how it works, and why it was designed that way;
- the final slide distinguishes completed evidence from future ideas.

Visually inspect the rendered deck when browser or screenshot tooling is available. Otherwise report visual inspection as `NOT EXECUTED`, while still running the deterministic renderer and static tests.

Return a concise plain-language summary plus the absolute HTML path, audience, slide count, verification evidence, and any uncertainty. A successful WYSIWYShip development run is not ready for final handoff until this ELI5 artifact has been generated and checked.
