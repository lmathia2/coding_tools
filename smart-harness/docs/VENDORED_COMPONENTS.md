# Vendored and Inspired Components

The Smart Harness contains a small reviewed subset of external methodologies as local Agent Skills and one independently written skill derived from an unlicensed public methodology description.

## Selection principles

A component is included only when it materially improves the two normal workflows, can run without another installation, and has an acceptable provenance/licensing path.

### Vendored/adapted under MIT

- Superpowers methodology and skill-authoring discipline;
- Ponytail minimal-correct-solution and complexity review;
- Pi Skills' VS Code diff workflow.

Exact commits and full notices are in `vendor/SOURCES.json` and `vendor/licenses/`.

### Independently implemented from conceptual inspiration

- `product-behavior-spec`, inspired by Steve Ruiz's public product-description gist.

The gist did not display an explicit license when reviewed, so its files/templates/code were not copied. The local skill and references were written independently. See `vendor/INSPIRATIONS.md`.

### Local Smart Harness components

- context-snapshot;
- documentation-sync;
- plan-first/parallel-work/engineering-core;
- worktree-based PR-review protocol;
- bundled Pi parallel runner.

## Not included

- upstream plugin hooks or marketplaces;
- telemetry/branding assets;
- MCP servers;
- browser/search/transcription/Google skills requiring APIs, Chrome, npm packages, or separate CLIs;
- Pi extension packages and their dependency graphs;
- redundant upstream skills already covered by stronger shared Smart Harness contracts.

## Maintenance

There is no scheduled external synchronization. Updates arrive only through reviewed repository commits. Changes to vendored/adapted material update source commits/licenses; changes inspired by unlicensed sources remain independently written and are recorded in `vendor/INSPIRATIONS.md`.
