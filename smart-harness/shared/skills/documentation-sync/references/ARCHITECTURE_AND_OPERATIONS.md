# Architecture, Decisions, and Operations

## Architecture documentation

Update architecture documentation when a change affects:

- component ownership or boundaries;
- data/control flow;
- trust boundaries;
- persistence or schemas;
- deployment topology;
- queues, jobs, retries, or transactions;
- external integrations;
- failure isolation or recovery;
- compatibility and migration strategy.

Document the **intent and goal** of the architecture, not only the boxes and arrows.

## ADR trigger

Create or update an ADR when the decision is durable, has meaningful alternatives, or will be difficult to infer later.

An ADR should record:

- context/problem;
- decision;
- goals and non-goals;
- alternatives considered;
- constraints/evidence;
- consequences and trade-offs;
- migration/rollback;
- validation/observability;
- status and date.

## Operational documentation

Update runbooks when operators need new knowledge about:

- configuration and secrets;
- rollout/rollback;
- alerts and dashboards;
- troubleshooting;
- failure recovery;
- backfills or migrations;
- limits and saturation;
- dependency availability.

A deployable change that cannot be operated or rolled back safely is not fully documented.
