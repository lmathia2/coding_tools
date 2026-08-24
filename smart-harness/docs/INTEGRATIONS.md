# Integrations

See [the optional-integration guide](../integrations/README.md) for Superpowers and Ponytail.

See [the Pi guide](../pi/README.md) for the curated Pi extension profiles.

## Selection principles

- keep the default workflow small;
- add an integration only when it solves a demonstrated need;
- prefer narrow packages over broad bundles;
- review executable extensions because they run with user permissions;
- pin/track upstream state;
- use provider-native update mechanisms;
- avoid duplicate planners, reviewers, and task systems unless deliberately replacing the default.

## Recommended Pi core

The core profile was selected because it maps directly to Smart Harness needs:

- subagent parallelism;
- safe worktrees;
- language-server diagnostics;
- PR status visibility;
- provider retry resilience.

Broad productivity or observability packages remain optional.
