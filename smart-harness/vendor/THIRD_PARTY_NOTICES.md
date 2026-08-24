# Third-Party Notices

The Smart Harness is self-contained but includes curated/adapted material from MIT-licensed projects.

## Superpowers

- Source: `obra/superpowers`
- Pinned source commit: `b36e0829c6d0140e93cfef2ca599b1b07d4a7797`
- Local adaptations: `shared/skills/superpowers-methodology/`, `shared/skills/superpowers-skill-authoring/`
- License: [`licenses/SUPERPOWERS-MIT.txt`](licenses/SUPERPOWERS-MIT.txt)

Only the methodology concepts needed by this harness are stored locally. The upstream plugin, hooks, telemetry, marketplaces, and scripts are not required or bundled.

## Ponytail

- Source: `DietrichGebert/ponytail`
- Pinned source commit: `2ed6c52c9d7e5e56942508591085fd45dea277d3`
- Local adaptations: `shared/skills/ponytail/`, `shared/skills/ponytail-review/`
- License: [`licenses/PONYTAIL-MIT.txt`](licenses/PONYTAIL-MIT.txt)

The local skills preserve the minimal-correct-solution philosophy while making Smart Harness documentation, tests, security, compatibility, and explicit requirements higher precedence.

## Pi Skills

- Source: `badlogic/pi-skills`
- Pinned source commit: `90bb51cae36515a648515b633a81c0c6efc8c74d`
- Local adaptation: `shared/skills/vscode/`
- License: [`licenses/PI-SKILLS-MIT.txt`](licenses/PI-SKILLS-MIT.txt)

The repository intentionally does not bundle upstream skills that require separate API keys, npm dependencies, Chrome setup, or additional CLIs.

Machine-readable provenance is in [`SOURCES.json`](SOURCES.json).
