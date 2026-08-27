#!/usr/bin/env python3
"""Select a model profile and synchronize adapter frontmatter."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

from model_config import get_profile, load_config, resolve_spec


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CONFIG_PATH = HERE / "models.json"
ROLE_RE = re.compile(r"<!--\s*harness-role:\s*([a-z-]+)\s*-->")
WORKFLOW_RE = re.compile(r"<!--\s*harness-workflow:\s*([a-z-]+)\s*-->")


def replace_field(frontmatter: str, field: str, value: str | None) -> str:
    pattern = rf"(?m)^{re.escape(field)}:\s*.*$"
    if value is None:
        return re.sub(pattern + r"\n?", "", frontmatter)
    replacement = f"{field}: {value}"
    return re.sub(pattern, replacement, frontmatter) if re.search(pattern, frontmatter) else frontmatter + f"\n{replacement}"


def adapter_target(path: Path, text: str) -> tuple[str, str | None]:
    roles = ROLE_RE.findall(text)
    workflows = WORKFLOW_RE.findall(text)
    if len(roles) != 1:
        raise RuntimeError(f"{path}: expected exactly one harness-role marker, found {len(roles)}")
    if roles[0] == "coordinator" and len(workflows) != 1:
        raise RuntimeError(f"{path}: coordinator requires exactly one harness-workflow marker")
    if roles[0] != "coordinator" and workflows:
        raise RuntimeError(f"{path}: specialist must not declare a harness-workflow marker")
    workflow = workflows[0].replace("-", "_") if workflows else None
    return roles[0], workflow


def rewrite(path: Path, platform: str, profile: dict[str, object]) -> str:
    text = path.read_text(encoding="utf-8")
    role, workflow = adapter_target(path, text)
    spec = resolve_spec(profile, platform, role, workflow)
    end = text.find("\n---\n", 4)
    if not text.startswith("---\n") or end < 0:
        raise RuntimeError(f"{path}: invalid frontmatter")
    front, body = text[4:end], text[end + 5:]
    front = replace_field(front, "model", spec.get("model"))
    front = replace_field(front, "reasoningEffort", spec["reasoning"] if platform == "copilot" else None)
    if platform == "claude_code":
        front = replace_field(front, "effort", spec["reasoning"])
    return "---\n" + front.rstrip() + "\n---\n" + body


def adapter_files() -> list[tuple[Path, str]]:
    return [
        *((path, "copilot") for path in (ROOT / "copilot/agents").glob("*.agent.md")),
        *((path, "claude_code") for path in (ROOT / "claude-code/agents").glob("*.md")),
        *((path, "claude_code") for path in (ROOT / "claude-code/commands").glob("*.md")),
    ]


def synchronize(profile: dict[str, object], check: bool) -> list[str]:
    updates = []
    for path, platform in adapter_files():
        current = path.read_text(encoding="utf-8")
        updated = rewrite(path, platform, profile)
        if updated == current:
            continue
        updates.append((path, updated))
    if not check:
        for path, updated in updates:
            path.write_text(updated, encoding="utf-8")
    return [str(path.relative_to(ROOT)) for path, _ in updates]


def write_active_profile(config: dict[str, object], name: str) -> None:
    if config["active_profile"] == name:
        return
    config["active_profile"] = name
    CONFIG_PATH.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")


def regenerate_reference() -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts/generate-reference.py")], check=True)


def display_selection(args: argparse.Namespace, config: dict[str, object], name: str, profile: dict[str, object]) -> bool:
    if args.list_profiles:
        for candidate in sorted(config["profiles"]):
            marker = "*" if candidate == config["active_profile"] else " "
            print(f"{marker} {candidate}")
        return True
    if args.show:
        print(json.dumps({"profile": name, **profile}, indent=2))
        return True
    return False


def report_sync(config: dict[str, object], name: str, stale: list[str], check: bool) -> int:
    if check and stale:
        print(f"stale model frontmatter for profile {name!r}:")
        print("\n".join("  " + path for path in stale))
        return 1
    if not check:
        write_active_profile(config, name)
        regenerate_reference()
    state = "current" if check or not stale else "updated"
    print(f"model profile {name!r} is {state}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--profile", help="profile to apply; persists as active unless --check is used")
    parser.add_argument("--list-profiles", action="store_true")
    parser.add_argument("--show", action="store_true", help="print the selected resolved profile")
    args = parser.parse_args()
    config = load_config(CONFIG_PATH)
    profile_name, profile = get_profile(config, args.profile)
    if display_selection(args, config, profile_name, profile):
        return 0
    stale = synchronize(profile, args.check)
    return report_sync(config, profile_name, stale, args.check)


if __name__ == "__main__":
    raise SystemExit(main())
