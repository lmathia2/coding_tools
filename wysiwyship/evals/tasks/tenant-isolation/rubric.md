# Blind human review — tenant isolation

Review the candidate artifact without condition labels, model/provider metadata,
task timing, or access to the reference overlay. Passing automated tests is
necessary evidence, not proof of a complete security boundary. Do not reward
code volume, extra abstractions, delegation count, commit count, or resemblance
to reference helper names.

## Scoring

Score each category 0–4: 0 absent/incorrect, 1 superficial or materially unsafe,
2 partially sound with substantive gaps, 3 complete and clear with minor issues,
4 exceptionally coherent and well verified without unnecessary complexity.
Record concrete source/doc evidence and a short rationale for each score.

| Category | Review questions |
| --- | --- |
| Purpose and user outcome | Does README explain the tracker and how tenant isolation changes actual use? Does the offline HTML explain what/how/why with a runnable example and source-grounded flow? Are readers told this is synthetic identity rather than production authentication? |
| Intent and architecture | Do docs explain why authorization, query scoping, durable relations, cache partitions, and delayed export access are separate boundaries? Do code ownership and transaction boundaries match that explanation? |
| Contract and scope fidelity | Are exact role, error precedence, same-tenant compatibility, ownership, denial audit, and migration rules preserved? Are serial App behavior, revocation freshness, unsupported concurrency, and cache limitations stated accurately? |
| Engineering coherence and complexity | Is there a single understandable authorization policy applied to API and direct callers? Are bulk rollback, post-commit invalidation, and execution/download checks easy to trace? Are helpers cohesive rather than metric-driven fragmentation? Are shortcuts, special fixtures, catch-all success, and duplicated policy avoided? |
| Regression reasoning | Do candidate tests cover positive same-tenant behavior as well as adversarial scope, stale membership, atomicity, relation integrity, and export lifecycle? Are reported commands/results reproducible? Do migration tests and documentation discuss safe old artifact treatment and rollback? |

Maximum human score: 20. Report automated results separately by contract family;
do not convert an unmeasured target duration into a score. A concrete tenant
data leak, cross-tenant mutation, authorization bypass, or partial batch commit
is a critical correctness finding regardless of documentation quality.

## Review procedure

Read the task contract, candidate README, architecture/contracts docs, and HTML.
Trace one issue read, a failed mixed-tenant batch, and a revoked export through
source. Check explanations against symbols and behavior; a file list or generic
security prose is not sufficient. Review new candidate tests rather than only
the evaluator suite. Make one small additional boundary probe if useful without
modifying the candidate's deliverables.

For the HTML, confirm it loads offline, source links resolve locally, and the
usage/flow/why/limits narrative is legible. Visual polish is secondary; accurate
explanation is the deliverable. Do not penalize a different valid design or a
different visual treatment merely because it differs from the reference.

## Difficulty calibration

This pilot deliberately combines a working 600+ source-line application and
several interacting contract families. That is an authoring property, not a
measurement of effort or difficulty. The 45–120 minute target remains unmeasured
until real Codex trials record elapsed time, independent work-unit quality,
interventions, acceptance results, and reviewer findings. Use the two pilot
trials to calibrate before constructing the remaining eight tasks. Static
complexity scores describe local decision points, not overall task difficulty.
