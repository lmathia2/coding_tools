#!/usr/bin/env python3
"""Select a model profile and synchronize adapter frontmatter."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

from adapter_config import rewrite_text
from model_config import get_profile, load_config


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CONFIG_PATH = HERE / "models.json"


def adapter_files() -> list[tuple[Path, str]]:
    return [
        *((path, "copilot") for path in (ROOT / "copilot/agents").glob("*.agent.md")),
        *((path, "claude_code") for path in (ROOT / "claude-code/agents").glob("*.md")),
        *((path, "claude_code") for path in (ROOT / "claude-code/commands").glob("*.md")),
        *((path, "codex") for path in (ROOT / "codex/agents").glob("*.toml")),
    ]


def synchronize(profile: dict[str, object], check: bool) -> list[str]:
    updates = []
    for path, platform in adapter_files():
        current = path.read_text(encoding="utf-8")
        updated = rewrite_text(path, current, platform, profile)
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
        subprocess.run([sys.executable, str(ROOT / "scripts/generate-reference.py")], check=True)
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
