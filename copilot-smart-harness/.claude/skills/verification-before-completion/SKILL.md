---
name: verification-before-completion
description: Use before claiming code/config/schema/test work is complete. Requires current executable evidence proportional to the change.
---
# Verification Before Completion
A plausible change is not a verified change.

Before saying done/fixed/passes:
1. Identify the observable behavior that must be true.
2. Run the smallest check that directly proves it.
3. Inspect the actual result.
4. Expand verification according to blast radius: targeted test -> module/package suite -> build/typecheck/lint -> integration/runtime checks when needed.
5. If a check fails, report and classify it rather than hiding it.
6. List only commands actually executed, with PASS/FAIL.

Do not run huge suites reflexively for tiny changes; match verification breadth to risk.
