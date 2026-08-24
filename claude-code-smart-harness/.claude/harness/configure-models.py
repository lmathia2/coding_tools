#!/usr/bin/env python3
"""Apply .claude/harness/model-config.json to harness skill/agent frontmatter.

No third-party packages required.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
CONFIG_PATH = HERE / "model-config.json"


def update_frontmatter(path: Path, role: str, model: str, effort: str | None) -> bool:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise RuntimeError(f"Missing YAML frontmatter: {path}")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise RuntimeError(f"Unclosed YAML frontmatter: {path}")

    front = text[4:end]
    body = text[end + 5:]

    # Replace or append model.
    if re.search(r"(?m)^model:\s*.*$", front):
        front = re.sub(r"(?m)^model:\s*.*$", f"model: {model}", front)
    else:
        front += f"\nmodel: {model}"

    # Replace/remove/append effort.
    if effort:
        if re.search(r"(?m)^effort:\s*.*$", front):
            front = re.sub(r"(?m)^effort:\s*.*$", f"effort: {effort}", front)
        else:
            front += f"\neffort: {effort}"
    else:
        front = re.sub(r"(?m)^effort:\s*.*\n?", "", front)

    new_text = "---\n" + front.rstrip() + "\n---\n" + body
    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> None:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    roles = config["roles"]

    candidates = list((PROJECT_ROOT / ".claude" / "agents").glob("*.md"))
    candidates += list((PROJECT_ROOT / ".claude" / "skills").glob("*/SKILL.md"))

    changed = []
    for path in candidates:
        text = path.read_text(encoding="utf-8")
        match = re.search(r"<!--\s*harness-role:\s*([a-z-]+)\s*-->", text)
        if not match:
            continue
        role = match.group(1)
        if role not in roles:
            raise RuntimeError(f"{path}: unknown harness role {role!r}")
        spec = roles[role]
        if update_frontmatter(path, role, spec["model"], spec.get("effort")):
            changed.append(path.relative_to(PROJECT_ROOT))

    print(f"Applied model configuration from {CONFIG_PATH.relative_to(PROJECT_ROOT)}")
    for path in changed:
        print(f"  updated {path}")
    if not changed:
        print("  no changes required")


if __name__ == "__main__":
    main()
