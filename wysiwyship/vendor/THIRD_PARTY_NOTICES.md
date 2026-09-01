# Third-Party Notices

WYSIWYShip is self-contained but includes curated/adapted concepts from MIT-licensed projects.

## Superpowers

- Source: `obra/superpowers`
- Pinned commit: `b36e0829c6d0140e93cfef2ca599b1b07d4a7797`
- v0.7 local integration: `shared/skills/engineering-workflow/`, `shared/skills/skill-authoring/`
- License: [`licenses/SUPERPOWERS-MIT.txt`](licenses/SUPERPOWERS-MIT.txt)

Design clarification, proportional planning, isolation, TDD/debugging, bounded delegation, review, and evidence-based completion concepts are integrated into the core workflow rather than exposed as a second process stack.

## Ponytail

- Source: `DietrichGebert/ponytail`
- Pinned commit: `2ed6c52c9d7e5e56942508591085fd45dea277d3`
- v0.7 local integration: `shared/skills/engineering-workflow/`, `shared/skills/pr-review/`
- License: [`licenses/PONYTAIL-MIT.txt`](licenses/PONYTAIL-MIT.txt)

Four rules are adapted into implementation and PR semantic review: source
priority, dependency discipline, protected safety/data-loss guardrails, and debt
annotations with current ceilings and measurable upgrade triggers. Deletion-first
behavior is excluded. There is no separate Ponytail skill, mode, hook, command,
or runtime.

## OpenWiki

- Source: `langchain-ai/openwiki`
- Pinned commit: `6be1e0148fa900cd5fae455d6f759380109a37e1`
- Local adaptation: `tools/wiki.py`,
  `shared/skills/engineering-workflow/references/grounded-wiki.md`, and
  `docs/DOCUMENTATION_POLICY.md`
- License: [`licenses/OPENWIKI-MIT.txt`](licenses/OPENWIKI-MIT.txt)

Grounded developer pages and durable updates informed a Python-standard-library
implementation. WYSIWYShip uses a configurable full-refresh commit
cadence and the active coding host; it does not bundle OpenWiki's runtime, Node
dependencies, provider clients, connectors, telemetry, CI bot, OKF output, CDN,
or visualizer.

## Pi Skills

- Source: `badlogic/pi-skills`
- Pinned commit: `90bb51cae36515a648515b633a81c0c6efc8c74d`
- Local adaptation: `shared/skills/vscode/`
- License: [`licenses/PI-SKILLS-MIT.txt`](licenses/PI-SKILLS-MIT.txt)

## ELI5

- Source: `dreambigou/eli5`
- Pinned commit: `a766623b062331fdde53467001379b4ddf3acc2f`
- Local adaptation: `shared/skills/eli5/SKILL.md`, `shared/skills/eli5/references/story-format.md`
- License: [`licenses/ELI5-MIT.txt`](licenses/ELI5-MIT.txt)

Audience calibration and purpose-first explanation structure are adapted into the mandatory post-development project explainer.

## Frontend Slides

- Source: `zarazhangrui/frontend-slides`
- Pinned commit: `9906a34d640d2111f724544cbc50f7f130569ae1`
- Local adaptation: `shared/skills/eli5/assets/project-eli5-template.html`, `shared/skills/eli5/scripts/render_explainer.py`
- License: [`licenses/FRONTEND-SLIDES-MIT.txt`](licenses/FRONTEND-SLIDES-MIT.txt)

Fixed 16:9 stage scaling, visual hierarchy, restrained reveal, keyboard/touch navigation, print layout, and reduced-motion patterns are adapted into an offline single-file renderer. No upstream templates, scripts, fonts, package managers, or network resources are required at runtime.

Machine-readable provenance is in [`SOURCES.json`](SOURCES.json). Non-code conceptual inspirations are recorded separately in [`INSPIRATIONS.md`](INSPIRATIONS.md).
