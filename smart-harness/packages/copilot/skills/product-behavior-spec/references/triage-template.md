# Product behavior triage

Consolidated mismatches, inconsistencies, and suspected defects found while drafting or verifying the behavior specification.

## Summary

| ID | Title | Severity | Confidence | Area | Decision/next action | Status |
|---|---|---|---|---|---|---|
| `B-001` | {Observable problem} | high | strong | {area} | fix / product decision / docs correction / investigate | open |

## Entry template

### B-001 — {Observable problem}

- **Where users encounter it:** {surface and precondition}
- **Actual behavior:** {what happens}
- **Expected/claimed behavior:** {what should happen or what the documentation claimed}
- **Impact:** {data loss, blocked workflow, inconsistency, confusion, cosmetic issue, etc.}
- **Reproduction:**
  1. {step}
  2. {step}
- **Source/test evidence:** {paths, symbols, test names, logs}
- **Root-cause confidence:** `confirmed` | `strong hypothesis` | `unknown`
- **Severity:** `high` | `medium` | `low`
- **Decision needed:** `fix` | `product decision` | `documentation correction` | `further investigation`
- **Raised by:** {feature document links and verification IDs}
- **Status:** `open` | `confirmed` | `not reproduced` | `resolved` | `accepted behavior`
- **Issue/PR:** {link when the user asks to file it}

## Rules

- Merge symptoms only when evidence supports a shared cause.
- Keep an unresolved observation in the feature's open questions when no actionable cause or reproducible mismatch exists.
- A failed checklist can mean the implementation is wrong, the document is wrong, or the environment differs; state which is supported.
- Filing external issues is a separate user-authorized action.
