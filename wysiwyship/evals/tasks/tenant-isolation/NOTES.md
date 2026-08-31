# Maintainer verification and limits

## Contents and ownership

This directory is one bounded pilot authoring unit, not a calibrated benchmark
result. Requested route: `137ee98c-f0cf-4388-b926-008427f27d61`
(`wysiwyship_deep`). The route identifier records the requested route; it does
not establish an effective model, provider, or hidden execution configuration.

- `task.md`: condition-neutral public requirements and identical deliverables.
- `starter/`: 12-module runnable app (621 Python source lines), original README
  and architecture/contracts docs, and 17 passing legacy regression tests.
- `reference/`: overlay only: six changed application modules, updated README
  and architecture/contracts, new offline HTML explainer, eight solution-owned
  regression tests. It is not a standalone import root; overlay it on starter.
- `acceptance/`: evaluator-owned unittest modules, common synthetic fixture, and
  an independent v1 SQL fixture. Keep these outside the candidate root.
- `rubric.md`: condition-blind human review of purpose/intent/scope/complexity,
  regression reasoning, and source-grounded developer explanation.

Do not expose `reference/`, `acceptance/`, this file, or the rubric to a candidate
when asking it to implement the public task. The runner owns separation. A local
`.verification/golden/` may exist as disposable verification output; exclude it
from catalog transfer/distribution. It is not part of the artifact layout.

The authoring work stayed in this pilot's temporary directory, used stdlib only,
and did not invoke model providers, network services, commits, pushes, or recursive
delegation. Those authoring restrictions are not benchmark treatment rules:
the shared public task permits host tools, delegation, and local disposable
commits equally; workflow-specific instructions belong to the runner.

## Exact verification commands

Commands below reproduce the authoring checks from this task directory. They
use a fresh temporary output directory so stale files cannot be mistaken for
delivered files. The authoring run used equivalent absolute paths.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/starter" python3 -m issuehub
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/starter" python3 -m unittest discover -s starter/tests -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/starter" python3 -m unittest discover -s acceptance -p 'test_*.py' -v

EVAL_GOLDEN="$(mktemp -d)"
cp -R starter/. "$EVAL_GOLDEN/"
cp -R reference/. "$EVAL_GOLDEN/"
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$EVAL_GOLDEN" python3 -m unittest discover -s "$EVAL_GOLDEN/tests" -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$EVAL_GOLDEN" python3 -m unittest discover -s acceptance -p 'test_*.py' -v

python3 ../../../tools/complexity.py starter reference acceptance --min-score 10 --fail-above 20
```

Observed on 2026-08-31:

| Candidate | Discovery root | Result |
| --- | --- | --- |
| starter | starter/tests | 17/17 pass |
| starter | acceptance | 61 discovered; 10 methods pass, 51 methods fail; 81 failure assertions including subtests; 0 errors |
| starter + reference overlay | candidate/tests | 25/25 pass (17 original + 8 new) |
| starter + reference overlay | acceptance | 61/61 pass |

The starter fails assertions in every acceptance family: boundary/roles, scoped
reads/cache, write integrity/bulk, exports, audit, and migration/storage. It does
not fail from missing imports or reference-only symbols. Discovery is separate;
solution-owned tests do not import evaluator modules. The final complexity check
exited 0 at threshold 20, with highest score 13 in App._dispatch. Source was
simplified into cohesive route handlers rather than disabling the checker.

The demo runs deterministically. Acceptance tests use no sleeps, clocks, random
race timing, or external services. Persistence tests create local temporary
SQLite files and reopen Apps. A trigger-injected audit failure checks transactional
rollback without relying on a particular private helper implementation.

## Behavioral coverage and explicit contracts

The 61 evaluator tests cover fresh actor/tenant/role boundaries including direct
service calls; SQL-scoped projects/issues/search; warmed detail/list cache
partitioning and tenant-only eviction; relation validation; atomic batches and
cache/audit consequences; job ownership, FIFO progression, execution-time rows,
revoked/deleted membership, ready-byte access, and viewer compatibility; sanitized
tenant audit events; v1 preservation/idempotence/rollback, legacy artifact
requeue, durable tenant constraints, and tenant-leading indexed paths.

Tests inspect documented payloads and maintenance ports, not private helper
names. The task explicitly publishes durable table/column/version and index-path
requirements where SQL inspection is used. Index names, class decomposition,
specific query text, timing, and line counts are not graded. Low-level repository
and cache interfaces are declared public maintenance contracts, not accidental
structural assumptions. API-level tests predominate.

The solution's own tests use tenant IDs 17/29 and actors 101/202, while evaluator
fixtures use a different synthetic layout. This is useful generality evidence,
not exhaustive arbitrary-ID testing. The public task requires arbitrary valid
IDs; it does not claim hidden randomization that the current verifier lacks.

## Known limits and calibration status

One App/connection/cache is used serially. Membership edits take effect on the
next call; concurrent in-flight revocation linearizability is not promised.
Independent App restart is tested, but simultaneous multi-App resource-cache
coherence and concurrent workers are excluded. Trusted maintenance SQL is not an
untrusted route. Synthetic actor IDs are not production authentication.

No side-channel timing, full security audit, load/scalability testing, distributed
queue behavior, full-text search, attachment storage, or CSV formula sanitization
is claimed. Acceptance breadth is finite and can be supplemented by blind human
probes. The HTML is a source-grounded offline explainer, not an elaborate UI.

No real candidate-model execution or 45–120 minute difficulty measurement was
performed in this authoring unit. Code size, 61 acceptance methods, and low local
cyclomatic complexity do not prove substantial human/model effort. Run both
substantial pilots under the actual Codex conditions, record timings and outcomes,
and calibrate task difficulty before authoring the remaining eight tasks.
