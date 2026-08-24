# Vendored Components

The Smart Harness contains a small reviewed subset of external methodologies as local Agent Skills.

## Selection principles

A component is copied/adapted only when it materially improves the two normal workflows and can run without another installation.

Included:

- Superpowers methodology and skill-authoring discipline;
- Ponytail minimal-correct-solution and complexity review;
- Pi Skills' VS Code diff workflow;
- a local context-snapshot skill and bundled Pi parallel runner.

Not included:

- upstream plugin hooks or marketplaces;
- telemetry/branding assets;
- MCP servers;
- browser/search/transcription/Google skills requiring APIs, Chrome, npm packages, or separate CLIs;
- Pi extension packages and their dependency graphs;
- redundant upstream skills already covered by stronger shared Smart Harness contracts.

## Maintenance

`vendor/SOURCES.json` records exact source commits and local paths. Full license notices are checked in. There is no scheduled external synchronization: updates arrive only through reviewed repository commits so behavior cannot change behind the user's back.
