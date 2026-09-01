---
description: Default self-contained development workflow: plan before editing, use the cheapest capable path, parallelize only useful independent work, keep authoritative docs synchronized, and verify before completion.
argument-hint: <coding task>
---

<!-- harness-role: coordinator -->
<!-- harness-workflow: dev -->

Task: $ARGUMENTS

Use `engineering-workflow` as the complete development policy.

Resolve routes with `routing.py plan --host pi --workflow dev`. Dispatch every
delegated unit through `.pi/tools/parallel-pi.py --workflow dev` with the locked
route as its `routing` object, then validate `routing_receipt`. A missing model
means the child host default; launcher arguments never prove the effective model.
Grant write capability or auto-approval only when the accepted plan and isolated
worktree authorize it.
