---
name: eli5
description: "Teach a curious developer what a completed coding project or change is for, how to use it, its core concepts, how the code is organized and executes under the hood, why key design choices exist, and what evidence proves it works. Produce a precise, source-grounded, dependency-free visual HTML walkthrough. Use for /eli5, project or codebase explanations, architecture walkthroughs, onboarding guides, and the mandatory handoff after a successful WYSIWYShip development workflow."
---

# Developer ELI5

Produce the simplest accurate mental model a developer can use to navigate and extend the code. Do not produce a product pitch, release-summary deck, or childish analogy.

## 1. Establish the boundary and audience

For an automatic post-development run, begin only after all required work units are integrated and verification passes. For an explicit `/eli5`, explain the requested repository state and label unverified or incomplete areas.

Default to a curious developer with general programming literacy but no repository context. A requested role or experience level may change emphasis and vocabulary, but never remove purpose, first use, core concepts, code architecture, execution flow, design rationale, or proof.

Classify the request before reading:

- **Project onboarding:** explain the repository's current purpose, installation or startup path, primary user workflow, source architecture, and extension points.
- **Completed change:** explain the observable delta, how a developer uses it, where it fits in the existing architecture, the changed execution path, and why the implementation was chosen.

## 2. Build an evidence map

Inspect authoritative implementation, tests, live documentation, public contracts, configuration, verification results, and relevant commit/work-unit history. Do not build the story from a plan, README, commit title, or marketing language alone.

Record enough evidence to answer:

- **Purpose:** the concrete problem and who experiences it;
- **Use:** exact install/start/invoke commands, prerequisites, expected output or state, and the first likely failure;
- **Concepts:** the smallest vocabulary needed to understand the design;
- **Architecture:** named modules and their responsibilities, boundaries, dependencies, persistent state, and generated versus canonical files;
- **Flow:** one representative request from entry point through named files, symbols, data/contracts, side effects, and result;
- **Rationale:** evidenced decisions, constraints, alternatives, and tradeoffs;
- **Proof:** tests and verification actually executed, meaningful quality evidence, limitations, and uncertainty.

Use source paths, symbols, commands, configuration keys, schemas, tests, or captured output as evidence anchors. Every technical claim must be traceable to inspected evidence. Never invent an API, runtime path, metric, capability, or design rationale.

## 3. Simplify without becoming vague

Prefer a concrete noun over a slogan and a representative path over a generic lifecycle. Define a project term on first use. Show only code that reveals a contract or decision boundary. Use one analogy only when it shortens the explanation, and state where it stops matching the implementation.

Keep these distinctions explicit:

- canonical source versus generated or installed copies;
- build-time or install-time behavior versus runtime behavior;
- required behavior versus optional tooling;
- verified facts versus inference or future work;
- user-facing entry points versus internal helpers.

Do not use vanity metrics, generic benefits, or labels such as “smart,” “safe,” or “powerful” without showing the mechanism and evidence.

## 4. Design the walkthrough

Read [references/story-format.md](references/story-format.md). Create 6–9 focused content slides for a normal repository or non-trivial change; use fewer only when the evidence is genuinely smaller.

For project onboarding, normally cover this sequence:

1. **Purpose:** the problem, intended developer, and concrete capability;
2. **First five minutes:** prerequisites, exact command or invocation, created state, and what to expect;
3. **Core concepts:** three to five terms that unlock the rest of the code;
4. **Architecture:** connected components with responsibilities and real source paths;
5. **Under the hood:** one end-to-end flow through named entry points, symbols, contracts, and outputs;
6. **Key boundary:** canonical/generated state, data ownership, API contract, or failure behavior;
7. **Why this design:** important choices and tradeoffs grounded in code or live docs;
8. **Proof and limits:** executed tests/checks plus honest gaps and next steps.

For a completed change, keep the same learning path but lead with the behavioral delta and show the impacted slice of architecture. Do not omit first use or under-the-hood flow merely because the change is small.

Use `flow` for architecture and execution sequences, `code` for an exact command or compact contract, and `evidence` for source anchors. Every story must include:

- at least one exact first-use command or invocation;
- at least one connected architecture or execution `flow`;
- at least three evidence anchors across the deck;
- at least one named source path and one named symbol or contract when code is available;
- a final action the developer can take immediately.

## 5. Render the offline explainer

Write the story JSON under `.agent-state/eli5/<project-slug>.json`, then use the bundled standard-library renderer:

```bash
python3 <skill-directory>/scripts/render_explainer.py \
  --input .agent-state/eli5/<project-slug>.json \
  --output .agent-state/eli5/<project-slug>.html
```

Keep the output as one offline file with no CDN, external font, package manager, analytics, or network request. Use short labels and readable diagrams. Split overloaded slides instead of shrinking text.

## 6. Verify and deliver

Run the renderer with `--check` before writing. Verify that:

- commands, paths, symbols, contracts, and claims match the inspected repository state;
- the deck answers purpose, first use, core concepts, architecture, under-the-hood flow, rationale, proof, and limits;
- architecture edges describe real calls, copies, reads, writes, or ownership—not merely visual adjacency;
- the artifact contains no remote resource marker or runtime dependency;
- slides fit without overflow and keyboard, touch, print, and reduced-motion behavior remain present;
- completed evidence and future ideas are visibly distinct.

Visually inspect the rendered deck when permitted browser or screenshot tooling is available. Otherwise report visual inspection as `NOT EXECUTED` while still running deterministic rendering and static checks.

Return a concise summary plus the absolute HTML path, audience, slide count, verification evidence, and uncertainty. A successful WYSIWYShip development run is not ready for final handoff until this artifact has been generated and checked.
