# Inspirations without copied source

## Product behavior specification

- Public gist: `steveruizok/83ae5c53f2784ebf8f5fe0a3fb94480f`
- URL: https://gist.github.com/steveruizok/83ae5c53f2784ebf8f5fe0a3fb94480f
- Reviewed: 2026-08-24
- Local implementation: `shared/skills/product-behavior-spec/`

The gist presents a useful methodology for building an outside-in, feature-by-feature description of a product from code/tests and validating it against the running product.

No explicit license was visible in the gist when reviewed. For that reason, the WYSIWYShip does not vendor the gist files or copy its templates/code. The local `product-behavior-spec` skill, templates, and link checker are independently written and use only the general ideas of outside-in feature documentation, stable lifecycle/interrupt questions, verification checklists, and behavior triage.

This file is attribution and design provenance, not a license grant.

## Planning grill

- Public repositories reviewed: `mattpocock/skills` (`skills/productivity/grill-me` and `grilling`) and `max4c/skills` (`skills/grill-me`)
- URLs: https://github.com/mattpocock/skills and https://github.com/max4c/skills
- Reviewed: 2026-08-27
- Local implementation: `shared/skills/engineering-workflow/references/planning-grill.md`

These projects demonstrate the value of an evidence-first, one-decision-at-a-time interview before implementation and of explicitly assessing goals, acceptance, boundaries, alternatives, and assumptions.

WYSIWYShip does not install or invoke either skill and does not copy their skill text. Its independently written planning subroutine adds WYSIWYShip-specific interactive/auto modes, a durable schema-v2 decision record, an explicit plan lock, and a narrow re-entry contract so execution after planning remains rapid and low-interruption.
