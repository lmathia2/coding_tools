# Grounded repository wiki

The repository wiki is on by default. It is a derived developer-learning layer,
not an authority for product requirements, API contracts, or accepted decisions.
When facts conflict, use this precedence:

1. locked requirements and decisions;
2. implementation, tests, schemas, and configuration;
3. authoritative project documentation;
4. `docs/wiki/`;
5. the post-completion ELI5 artifact.

## Document-stage protocol

1. Ensure the wiki exists:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/tools/wiki.py" init
   ```

2. Update authoritative documentation for the current change; generated wiki
   pages never satisfy that requirement.
3. Read `wiki.refresh_every_commits` from the checks config:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/tools/wiki.py" due --every <N>
   ```

4. If it passes, stop. If due, use the active host to rewrite every manifest
   page from current source, tests, configuration, and authoritative docs.
5. Verify and record the full refresh:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/tools/wiki.py" verify
   python3 "${CLAUDE_PLUGIN_ROOT}/tools/wiki.py" mark-refreshed
   ```

Commit the refreshed Markdown and `.refresh.json` with the code unit that reached
the cadence. `INSTRUCTIONS.md` is user-owned.

## Boundaries

- The default cadence is five commits. Set it to `1` for an every-commit wiki or
  another positive integer for a different cost/freshness bound.
- The tool checks only structure, page presence, and commit cadence. It does not
  guess semantic staleness or call a model.
- Do not install OpenWiki, Node, a provider SDK, a connector, telemetry, a CI bot,
  a graph viewer, or a CDN. WYSIWYShip carries the required policy and standard-
  library implementation locally.
- ELI5 may use the wiki as a map, but it must verify facts against repository
  source before repeating them.
