# Self-Contained Distribution Contract

## Function

Make the WYSIWYShip usable from one reviewed repository without runtime dependency fetching.

## Intent

A reviewed commit in `coding_tools` should completely determine the harness behavior. Corporate users can audit one repository, install from local files, and reproduce the same agents and skills across machines.

## Contract

The project/global installers copy files from `wysiwyship/` into project or user configuration directories without fetching code or dependencies. Native Copilot/Claude plugin installation may fetch this repository through the host's normal trusted plugin mechanism; the installed bundle itself must not fetch dependencies or helper repositories.

Default model discovery invokes installed host control surfaces and reads local host configuration. Codex may refresh authenticated catalog metadata while serving `model/list`; disable all host discovery with `--no-model-discovery` for a strictly offline static-profile install. Discovery never runs an inference request, installs a package, or reads VS Code private extension storage.

Runtime code must not:

- run `git clone`, `gh skill install`, plugin/marketplace install commands, `pi install`, npm/pip package installation, curl/wget downloads, or remote execution;
- silently fetch newer third-party content;
- require optional external MCP servers or hooks.

Host products are prerequisites: Codex, VS Code/GitHub Copilot, Claude Code, or Pi. The target project retains its own normal language/build/test dependencies.

Installation is preflighted and transactional. Replaced paths are backed up, failure triggers rollback, settings and manifests use atomic writes, and `--dry-run` / `--status` expose intended or installed state. Generated native packages carry the same agents, skills, tools, configuration, provenance, and notices; CI rejects package drift.

## Vendored content

All third-party-derived skill text, renderer assets, and scripts are stored in `shared/skills/`, with pinned provenance and licenses under `vendor/`. The ELI5 visual renderer emits a single offline HTML file and never loads a CDN, remote font, package, analytics endpoint, or source repository.

Updates are deliberate code changes: review upstream, copy/adapt the required material, update `vendor/SOURCES.json`, docs/changelog, regenerate the reference, and run CI.

## Verification

CI scans executable harness scripts for forbidden external-install patterns, checks notices/licenses, validates generated documentation and model routing, parses shell/Python, and smoke-tests a local all-platform installation.
