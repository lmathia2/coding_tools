#!/usr/bin/env python3
"""Generate docs/REFERENCE.md from repository-local Smart Harness sources."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    out: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line or line.startswith((" ", "\t")):
            continue
        key, value = line.split(":", 1)
        out[key.strip()] = value.strip().strip("'\"")
    return out


def generate() -> str:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    models = json.loads((ROOT / "config/models.json").read_text(encoding="utf-8"))
    sources = json.loads((ROOT / "vendor/SOURCES.json").read_text(encoding="utf-8"))

    skills = []
    for path in sorted((ROOT / "shared/skills").glob("*/SKILL.md")):
        fm = frontmatter(path)
        skills.append((fm.get("name", path.parent.name), fm.get("description", ""), str(path.parent.relative_to(ROOT))))

    copilot_files = sorted(p.name for p in (ROOT / "copilot/agents").glob("*.agent.md"))
    claude_agents = sorted(p.name for p in (ROOT / "claude-code/agents").glob("*.md"))
    claude_commands = sorted(p.name for p in (ROOT / "claude-code/commands").glob("*.md"))

    lines = [
        "# Generated Smart Harness Reference",
        "",
        f"> Generated from repository-local files for version `{version}`. Do not edit by hand.",
        "",
        "## Simplicity budget",
        "",
        f"- Shared discoverable skills: **{len(skills)}** (budget: 5)",
        f"- Copilot agent definitions: **{len(copilot_files)}** (2 visible + 5 hidden)",
        f"- Claude Code hidden agents: **{len(claude_agents)}** (budget: 4)",
        f"- Claude Code visible commands: **{len(claude_commands)}** (budget: 2)",
        "",
        "## Model routing",
        "",
    ]

    for platform in ("copilot", "claude_code"):
        lines += [
            f"### {platform.replace('_', ' ').title()}",
            "",
            "| Role | Model | Effort |",
            "|---|---|---|",
        ]
        for role, spec in models[platform].items():
            lines.append(f"| `{role}` | `{spec['model']}` | `{spec.get('effort', '')}` |")
        lines.append("")

    lines += ["## Shared skills", "", "| Skill | Description | Local path |", "|---|---|---|"]
    for name, desc, path in skills:
        safe_desc = desc.replace("|", "\\|")
        lines.append(f"| `{name}` | {safe_desc} | `{path}` |")

    lines += ["", "## Adapter files", "", "### Copilot", ""]
    lines += [f"- `{name}`" for name in copilot_files]
    lines += ["", "### Claude Code hidden agents", ""]
    lines += [f"- `{name}`" for name in claude_agents]
    lines += ["", "### Claude Code commands", ""]
    lines += [f"- `{name}`" for name in claude_commands]

    lines += ["", "## Vendored sources", "", "| Component | Pinned commit | License | Local integration |", "|---|---|---|---|"]
    for item in sources["components"]:
        paths = ", ".join(f"`{p}`" for p in item["local_paths"])
        lines.append(f"| {item['name']} | `{item['commit']}` | {item['license']} | {paths} |")

    lines += [
        "",
        "## Runtime network dependency",
        "",
        "None. Installers copy repository-local files only. Host applications and target-project dependencies are prerequisites, not downloaded by this harness.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = ROOT / "docs/REFERENCE.md"
    new = generate()
    if args.check:
        if not path.exists() or path.read_text(encoding="utf-8") != new:
            print("generated reference is stale")
            return 1
        print("generated reference is current")
        return 0
    path.write_text(new, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
