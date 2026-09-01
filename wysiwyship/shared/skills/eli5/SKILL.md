---
name: eli5
description: "Create a source-grounded visual onboarding guide for an entire software package: the problem it solves, installation, first run and expected behavior, core concepts, architecture, an under-the-hood flow, and where developers should learn more. Use for /eli5, package onboarding, architecture walkthroughs, and the mandatory handoff after a successful WYSIWYShip development workflow."
---

# Developer ELI5

Produce the simplest accurate visual guide a developer can use to install, run,
navigate, and extend the entire package. Do not produce a product pitch,
release-summary deck, diff walkthrough, or childish analogy.

## 1. Establish the boundary and audience

For an automatic post-development run, begin only after all required work units
are integrated and verification passes. For an explicit `/eli5`, explain the
requested repository state and label unverified or incomplete areas.

Default to a curious developer with general programming literacy but no
repository context. A requested role or experience level may change emphasis
and vocabulary, but never remove the package problem, installation, first run,
expected behavior, core concepts, architecture, under-the-hood flow, or pointers
to deeper documentation.

Every run is package onboarding, including the automatic handoff after a change.
Inspect the completed diff only after understanding the package. Use it to update
the affected package explanation and call out a change only when it materially
alters installation, use, architecture, a public contract, or an important
limitation. Never organize the deck around the diff.

## 2. Build an evidence map

Inspect authoritative implementation, tests, live documentation, public
contracts, configuration, verification results, and relevant commit/work-unit
history. Establish the whole-package model before reviewing the latest diff. Do
not build the story from a plan, README, commit title, or marketing language
alone.

Use `docs/wiki/` as a navigation map when present, never as final proof. Inspect
authoritative code, tests, contracts, and configuration before repeating its
technical statements.

Record enough evidence to answer:

- **Purpose:** what the package is, the concrete problem, and who experiences it;
- **Install:** prerequisites, exact installation command, created files/state, and the first likely failure;
- **Run:** exact first invocation, expected output/state, and the primary developer workflow;
- **Concepts:** the smallest vocabulary needed to understand the design;
- **Architecture:** named modules and their responsibilities, boundaries, dependencies, persistent state, and generated versus canonical files;
- **Flow:** one representative request from entry point through named files, symbols, data/contracts, side effects, and result;
- **More detail:** authoritative docs, key entry points, extension points, and troubleshooting paths;
- **Proof:** tests and verification actually executed, meaningful quality evidence, limitations, uncertainty, and any materially significant recent change.

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

Read [references/story-format.md](references/story-format.md). Create 6–8 focused
content slides for a normal package. The renderer adds title and closing slides,
so the complete deck contains at most 10 slides. Use fewer only when the package
is genuinely smaller.

Normally cover this sequence:

1. **Package and problem:** what it provides, who needs it, and the problem it solves;
2. **Install:** prerequisites, exact command, created state, and common setup failure;
3. **Run:** exact first invocation, expected behavior, and the primary workflow;
4. **Core concepts:** three to five terms that unlock the rest of the code;
5. **Architecture:** connected components with responsibilities and real source paths;
6. **Under the hood:** one end-to-end flow through named entry points, symbols, contracts, and outputs;
7. **Go deeper:** authoritative docs, important source entry points, extension points, and troubleshooting;
8. **Proof and limits:** executed checks, honest gaps, and only significant recent updates.

Fold a significant diff into the relevant package slide or one compact update
callout. Omit routine implementation details that do not change how a developer
understands, installs, runs, navigates, or extends the package.

Use `flow` for architecture and execution sequences, `code` for an exact command or compact contract, and `evidence` for source anchors. Every story must include:

- at least one exact installation command and one exact first-run invocation;
- at least one connected architecture or execution `flow`;
- at least three evidence anchors across the deck;
- at least one named source path and one named symbol or contract when code is available;
- at least one pointer to authoritative documentation or a source entry point for deeper study;
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
- the deck answers package purpose, installation, first run and expected behavior, core concepts, architecture, under-the-hood flow, where to learn more, proof, and limits;
- the complete rendered deck contains no more than 10 slides;
- recent changes appear only when they materially affect the package mental model;
- architecture edges describe real calls, copies, reads, writes, or ownership—not merely visual adjacency;
- the artifact contains no remote resource marker or runtime dependency;
- slides fit without overflow and keyboard, touch, print, and reduced-motion behavior remain present;
- completed evidence and future ideas are visibly distinct.

Visually inspect the rendered deck when permitted browser or screenshot tooling is available. Otherwise report visual inspection as `NOT EXECUTED` while still running deterministic rendering and static checks.

Return a concise summary plus the absolute HTML path, audience, slide count, verification evidence, and uncertainty. A successful WYSIWYShip development run is not ready for final handoff until this artifact has been generated and checked.
