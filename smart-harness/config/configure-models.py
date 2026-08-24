#!/usr/bin/env python3
"""Apply smart-harness/config/models.json to Copilot and Claude Code definitions.

Model identifiers are opaque strings: edit models.json when providers/models change.
No third-party packages required.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CONFIG = json.loads((HERE / "models.json").read_text(encoding="utf-8"))

ROLE_RE = re.compile(r"<!--\s*harness-role:\s*([a-z-]+)\s*-->")


def rewrite(path: Path, platform: str) -> bool:
    text = path.read_text(encoding="utf-8")
    role_match = ROLE_RE.search(text)
    if not role_match:
        return False
    role = role_match.group(1)
    spec = CONFIG[platform].get(role)
    if not spec:
        raise RuntimeError(f"{path}: role {role!r} missing from {platform} model config")
    if not text.startswith("---\n"):
        raise RuntimeError(f"{path}: missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise RuntimeError(f"{path}: unclosed YAML frontmatter")
    front, body = text[4:end], text[end + 5:]
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

    new = "---\n" + front.rstrip() + "\n---\n" + body
    if new == text:
        return False
    path.write_text(new, encoding="utf-8")
    return True


def main() -> None:
    files: list[tuple[Path, str]] = []
    files += [(p, "copilot") for p in (ROOT / "copilot" / "agents").glob("*.agent.md")]
    files += [(p, "claude_code") for p in (ROOT / "claude-code" / "agents").glob("*.md")]
    files += [(p, "claude_code") for p in (ROOT / "claude-code" / "commands").glob("*.md")]

    changed = []
    for path, platform in files:
        if rewrite(path, platform):
            changed.append(path.relative_to(ROOT))

    print("Applied model config:")
    for p in changed:
        print(f"  updated {p}")
    if not changed:
        print("  no changes required")


if __name__ == "__main__":
    main()
