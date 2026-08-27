#!/usr/bin/env python3
"""Generate docs/REFERENCE.md from repository-local WYSIWYShip sources."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "config"))
from model_config import get_profile, load_config  # noqa: E402


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


def collect_skills() -> list[tuple[str, str, str]]:
    skills: list[tuple[str, str, str]] = []
    for path in sorted((ROOT / "shared/skills").glob("*/SKILL.md")):
        fm = frontmatter(path)
        skills.append((fm.get("name", path.parent.name), fm.get("description", ""), str(path.parent.relative_to(ROOT))))
    return skills


def header_lines(version: str, skills: list[tuple[str, str, str]], codex_agents: list[str], copilot_files: list[str], claude_agents: list[str], claude_commands: list[str]) -> list[str]:
    return [
        "# Generated WYSIWYShip Reference",
        "",
        "*What you spec is what you ship. Plan it. Prove it. Just ship.*",
        "",
        f"> Generated from repository-local files for version `{version}`. Do not edit by hand.",
        "",
        "## Simplicity budget",
        "",
        f"- Shared discoverable skills: **{len(skills)}** (budget: 6)",
        f"- Codex specialist definitions: **{len(codex_agents)}** (budget: 4)",
        f"- Copilot agent definitions: **{len(copilot_files)}** (2 visible + 5 hidden)",
        f"- Claude Code hidden agents: **{len(claude_agents)}** (budget: 5)",
        f"- Claude Code visible commands: **{len(claude_commands)}** (budget: 2)",
        "",
        "## Work-unit lifecycle",
        "",
        "Every development request starts with an evidence-first planning grill and an explicit human or auto plan lock. After lock, execution is rapid and low-interruption unless a material decision is invalidated or new authority is required.",
        "",
        "Every implementation unit is coherent and independently committable, with explicit planning decisions, dependencies, and ownership:",
        "",
        "```text",
        "plan -> implement -> document -> simplify -> verify",
        "```",
        "",
        "Live authoritative documentation travels in the same logical commit as code. Changed Python functions can be scored with `.wysiwyship/tools/complexity.py`; other languages use repository-native analyzers.",
        "",
        "## Model routing",
        "",
    ]


def model_lines(config: dict[str, object]) -> list[str]:
    active, profile = get_profile(config)
    available = ", ".join(f"`{name}`" for name in sorted(config["profiles"]))
    lines = [f"Active profile: **`{active}`**. Available profiles: {available}.", ""]
    for platform in ("codex", "copilot", "claude_code", "pi"):
        lines += [
            f"### {platform.replace('_', ' ').title()}",
            "",
            "| Target | Model | Reasoning |",
            "|---|---|---|",
        ]
        settings = profile[platform]
        for workflow, spec in settings["workflows"].items():
            lines.append(f"| `{workflow}.coordinator` | `{spec.get('model') or 'inherit'}` | `{spec['reasoning']}` |")
        for role, spec in settings["roles"].items():
            lines.append(f"| `{role}` | `{spec.get('model') or 'inherit'}` | `{spec['reasoning']}` |")
        lines.append("")
    return lines


def skill_lines(skills: list[tuple[str, str, str]]) -> list[str]:
    lines = ["## Shared skills", "", "| Skill | Description | Local path |", "|---|---|---|"]
    for name, desc, path in skills:
        safe_desc = desc.replace("|", "\\|")
        lines.append(f"| `{name}` | {safe_desc} | `{path}` |")
    return lines


def adapter_lines(codex_agents: list[str], copilot_files: list[str], claude_agents: list[str], claude_commands: list[str]) -> list[str]:
    lines = ["", "## Adapter files", "", "### Codex specialists", ""]
    lines += [f"- `{name}`" for name in codex_agents]
    lines += ["", "### Copilot", ""]
    lines += [f"- `{name}`" for name in copilot_files]
    lines += ["", "### Claude Code hidden agents", ""]
    lines += [f"- `{name}`" for name in claude_agents]
    lines += ["", "### Claude Code commands", ""]
    lines += [f"- `{name}`" for name in claude_commands]
    return lines


def vendor_lines(sources: dict[str, object]) -> list[str]:
    lines = ["", "## Vendored sources", "", "| Component | Pinned commit | License | Local integration |", "|---|---|---|---|"]
    for item in sources["components"]:
        paths = ", ".join(f"`{p}`" for p in item["local_paths"])
        lines.append(f"| {item['name']} | `{item['commit']}` | {item['license']} | {paths} |")
    return lines


def footer_lines() -> list[str]:
    return [
        "",
        "## Installed support tools",
        "",
        "- `.wysiwyship/tools/complexity.py` — dependency-free Python function cyclomatic complexity and baseline deltas.",
        "- `.wysiwyship/tools/commit_docs.py` — commit-range documentation synchronization checks.",
        "- `.wysiwyship/config/models.json` — installed active profile and model/reasoning routes for every host.",
        "- `.wysiwyship/model-discovery.json` — installer evidence, account-visible capabilities, fallbacks, and limitations when discovery is enabled.",
        "- `.wysiwyship/install-manifest.json` — installed paths, checksums, platforms, version, and backup history.",
        "- `.wysiwyship/vendor/` — pinned provenance and license notices carried with installed artifacts.",
        "",
        "Installation is preflighted and transactional, uses atomic settings/manifest writes, rolls back touched paths on failure, and supports `--dry-run`, `--status`, and `--no-model-discovery`.",
        "",
        "## Runtime network dependency",
        "",
        "None. Installers copy repository-local files only. Host applications and target-project dependencies are prerequisites, not downloaded by this harness.",
        "",
    ]


def generate() -> str:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    models = load_config(ROOT / "config/models.json")
    sources = json.loads((ROOT / "vendor/SOURCES.json").read_text(encoding="utf-8"))
    skills = collect_skills()
    codex_agents = sorted(p.name for p in (ROOT / "codex/agents").glob("*.toml"))
    copilot_files = sorted(p.name for p in (ROOT / "copilot/agents").glob("*.agent.md"))
    claude_agents = sorted(p.name for p in (ROOT / "claude-code/agents").glob("*.md"))
    claude_commands = sorted(p.name for p in (ROOT / "claude-code/commands").glob("*.md"))
    lines = header_lines(version, skills, codex_agents, copilot_files, claude_agents, claude_commands)
    lines += model_lines(models)
    lines += skill_lines(skills)
    lines += adapter_lines(codex_agents, copilot_files, claude_agents, claude_commands)
    lines += vendor_lines(sources)
    lines += footer_lines()
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
