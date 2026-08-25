# Product Behavior Specification

`product-behavior-spec` is an optional specialist skill for explicitly requested outside-in product documentation. It is not part of every coding or PR task.

## Function

Create durable feature-by-feature documentation of user-visible behavior from code, tests, and feasible running-product verification, including lifecycle, variants, interruption/failure/recovery, evidence, and unresolved discrepancies.

## When to use

Use when the user explicitly asks for a product description, outside-in behavior specification, feature behavior catalog, or executable verification catalog.

Do not invoke the full workflow merely because a normal feature changes behavior. If a repository already has a behavior specification, `engineering-workflow` and `pr-review` maintain only the affected existing artifacts.

## Default output

```text
docs/product-behavior/
  README.md
  goal.md
  glossary.md
  foundations/
  features/
  cross-cutting/
  verification/
  bug-triage.md
```

The specialist skill and its references own the detailed authoring/verification structure.

## Verification principle

Keep code/test-derived claims distinct from behavior actually exercised in the running product. Never claim visual feel, device interaction, accessibility behavior, or timing perception was verified unless that environment was actually exercised.
