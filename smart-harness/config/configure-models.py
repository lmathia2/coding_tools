#!/usr/bin/env python3
"""Apply config/models.json to Copilot and Claude Code definitions.

Model identifiers are intentionally opaque strings. No third-party packages required.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CONFIG_PATH = HERE / "models.json"
ROLE_RE = re.compile(r"<!--\s*harness-role:\s*([a-z-]+)\s*-->")


def rewrite(path: Path, platform: str, config: dict, check: bool) -> bool:
    text = path.read_text(encoding="utf-8")
    match = ROLE_RE.search(text)
    if not match:
        return False
    role = match.group(1)
    spec = config[platform].get(role)
    if not spec:
        raise RuntimeError(f"{path}: role {role!r} missing from {platform} config")
    if not text.startswith("---\n"):
        raise RuntimeError(f"{path}: missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise RuntimeError(f"{path}: unclosed YAML frontmatter")

    front, body = text[4:end], text[end + 5 :]
    model = spec["model"]
    if re.search(r"(?m)^model:\s*.*$", front):
        front = re.sub(r"(?m)^model:\s*.*$", f"model: {model}", front)
    else:
        front += f"\nmodel: {model}"

    if platform == "claude_code":
        effort = spec.get("effort")
        if effort:
            if re.search(r"(?m)^effort:\s*.*$", front):
                front = re.sub(r"(?m)^effort:\s*.*$", f"effort: {effort}", front)
            else:
                front += f"\neffort: {effort}"
        else:
            front = re.sub(r"(?m)^effort:\s*.*\n?", "", front)

    updated = "---\n" + front.rstrip() + "\n---\n" + body
    if updated == text:
        return False
    if not check:
        path.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail when files need regeneration")
    args = parser.parse_args()

    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    files: list[tuple[Path, str]] = []
    files += [(p, "copilot") for p in (ROOT / "copilot" / "agents").glob("*.agent.md")]
    files += [(p, "claude_code") for p in (ROOT / "claude-code" / "agents").glob("*.md")]
    files += [(p, "claude_code") for p in (ROOT / "claude-code" / "commands").glob("*.md")]

    changed: list[Path] = []
    for path, platform in files:
        if rewrite(path, platform, config, args.check):
            changed.append(path.relative_to(ROOT))

    if changed:
        verb = "would update" if args.check else "updated"
        for path in changed:
            print(f"{verb}: {path}")
        return 1 if args.check else 0

    print("model configuration is current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
