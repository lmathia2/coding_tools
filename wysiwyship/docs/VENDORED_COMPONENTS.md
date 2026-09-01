# Vendored Components

WYSIWYShip is self-contained but incorporates selected concepts from MIT-licensed external projects.

## Integration style

External methodologies are no longer exposed as separate default skills when their behavior belongs in the core workflow.

- Superpowers design/planning/isolation/TDD/delegation/review concepts are folded into `engineering-workflow`; its skill-authoring concepts remain in a contributor-only source skill.
- Ponytail minimal-correct-solution concepts are folded into `engineering-workflow` and the simplicity dimension of `pr-review`; there is no separate Ponytail execution/review lane.
- The dependency-free VS Code diff utility remains an optional source helper and is not installed by default.
- The audience-calibration structure from `dreambigou/eli5` and fixed-stage visual presentation patterns from `zarazhangrui/frontend-slides` are combined in the local `eli5` skill and offline renderer.
- The evidence-first interview discipline associated with public `grill-me` / `grilling` skills is independently implemented as a planning subroutine inside `engineering-workflow`; no external skill or separate command is required. See `vendor/INSPIRATIONS.md`.
- `product-behavior-spec` is an original WYSIWYShip implementation conceptually inspired by Steve Ruiz's public gist; see `vendor/INSPIRATIONS.md`.

## Selection principles

A separate discoverable skill exists only when it provides a distinct specialist capability that cannot be expressed cleanly as a conditional branch in `engineering-workflow` or `pr-review`.

No upstream plugin hooks, marketplaces, telemetry, MCP servers, browser/search/Google dependencies, hosted fonts, or Pi extension dependency graphs are included.

## Maintenance

`vendor/SOURCES.json` records pinned source commits and local integration paths. Full license notices are checked in. Updates arrive only through reviewed commits; there is no runtime or scheduled upstream synchronization.
