---
name: security-resilience-review
description: Use for PRs that cross trust boundaries, alter external I/O, state, retries, concurrency, permissions, persistence, or operational failure behavior.
---

# Security and Resilience Review

Review concrete changed paths rather than reciting a generic checklist.

## Security

Ask:

- who controls this input?
- what trust boundary does it cross?
- what identity/authorization is assumed?
- can input reach command/query/path/URL/parser sinks unsafely?
- can secrets or sensitive data be exposed?
- did privilege or default access expand?

## Resilience

Construct failure scenarios:

- downstream timeout;
- partial success;
- duplicate request/event;
- retry after side effect;
- concurrent update;
- restart between steps;
- exhausted resource;
- stale config/state;
- rollback after schema/data change.

For each material issue state:

- precondition;
- execution sequence;
- impact;
- evidence;
- mitigation;
- test that would prove the fix.
