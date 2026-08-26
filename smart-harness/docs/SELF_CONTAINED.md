# Self-Contained Distribution Contract

## Function

Make the Smart Harness usable from one repository without downloading skills, plugins, extensions, MCP servers, or helper repositories at runtime.

## Intent

A reviewed commit in `coding_tools` should completely determine the harness behavior. Corporate users can audit one repository, install from local files, and reproduce the same agents and skills across machines.

## Contract

Runtime installers may copy files from `smart-harness/` into project or user configuration directories. They must not:

- run `git clone`, `gh skill install`, plugin/marketplace install commands, `pi install`, npm/pip package installation, curl/wget downloads, or remote execution;
- silently fetch newer third-party content;
- require optional external MCP servers or hooks.

Host products are prerequisites: VS Code/GitHub Copilot, Claude Code, or Pi. The target project retains its own normal language/build/test dependencies.

Installation is preflighted and transactional. Replaced paths are backed up, failure triggers rollback, settings and manifests use atomic writes, and `--dry-run` / `--status` expose intended or installed state. The installed support directory includes the complexity analyzer plus pinned third-party provenance and license notices.

## Vendored content

All third-party-derived skill text is stored in `shared/skills/`, with pinned provenance and licenses under `vendor/`.

Updates are deliberate code changes: review upstream, copy/adapt the required material, update `vendor/SOURCES.json`, docs/changelog, regenerate the reference, and run CI.

## Verification

CI scans executable harness scripts for forbidden external-install patterns, checks notices/licenses, validates generated documentation and model routing, parses shell/Python, and smoke-tests a local all-platform installation.
