#!/usr/bin/env python3
"""Apply local config/models.json to Copilot and Claude Code frontmatter."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CONFIG = json.loads((HERE / "models.json").read_text(encoding="utf-8"))
ROLE_RE = re.compile(r"<!--\s*harness-role:\s*([a-z-]+)\s*-->")
REQUIRED_PLATFORMS = {"copilot", "claude_code"}
REQUIRED_ROLES = {"coordinator", "normal", "deep", "fast", "top"}


def validate_config() -> None:
    if CONFIG.get("schema_version") != 1:
        raise RuntimeError("models.json schema_version must be 1")
    if set(CONFIG) - {"schema_version"} != REQUIRED_PLATFORMS:
        raise RuntimeError("models.json must define exactly copilot and claude_code")
    for platform in REQUIRED_PLATFORMS:
        validate_platform(platform, CONFIG.get(platform))


def validate_platform(platform: str, roles: object) -> None:
    if not isinstance(roles, dict) or set(roles) != REQUIRED_ROLES:
        raise RuntimeError(f"{platform} must define roles {sorted(REQUIRED_ROLES)}")
    for role, spec in roles.items():
        if not isinstance(spec, dict) or not isinstance(spec.get("model"), str) or not spec["model"].strip():
            raise RuntimeError(f"{platform}.{role} requires a non-empty model")


def replace_field(frontmatter: str, field: str, value: str | None) -> str:
    pattern = rf"(?m)^{re.escape(field)}:\s*.*$"
    if value is None:
        return re.sub(pattern + r"\n?", "", frontmatter)
    replacement = f"{field}: {value}"
    return re.sub(pattern, replacement, frontmatter) if re.search(pattern, frontmatter) else frontmatter + f"\n{replacement}"


def rewrite(path: Path, platform: str) -> str:
    text = path.read_text(encoding="utf-8")
    matches = ROLE_RE.findall(text)
    if len(matches) != 1:
        raise RuntimeError(f"{path}: expected exactly one harness-role marker, found {len(matches)}")
    spec = CONFIG[platform].get(matches[0])
    if not spec:
        raise RuntimeError(f"{path}: missing role {matches[0]!r}")
    end = text.find("\n---\n", 4)
    if not text.startswith("---\n") or end < 0:
        raise RuntimeError(f"{path}: invalid frontmatter")
    front, body = text[4:end], text[end + 5:]
    front = replace_field(front, "model", spec["model"])
    if platform == "claude_code":
        front = replace_field(front, "effort", spec.get("effort"))
    return "---\n" + front.rstrip() + "\n---\n" + body


def adapter_files() -> list[tuple[Path, str]]:
    return [
        *((path, "copilot") for path in (ROOT / "copilot/agents").glob("*.agent.md")),
        *((path, "claude_code") for path in (ROOT / "claude-code/agents").glob("*.md")),
        *((path, "claude_code") for path in (ROOT / "claude-code/commands").glob("*.md")),
    ]


def synchronize(check: bool) -> list[str]:
    stale = []
    for path, platform in adapter_files():
        current = path.read_text(encoding="utf-8")
        updated = rewrite(path, platform)
        if updated == current:
            continue
        stale.append(str(path.relative_to(ROOT)))
        if not check:
            path.write_text(updated, encoding="utf-8")
    return stale


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    validate_config()
    stale = synchronize(args.check)
    if args.check and stale:
        print("stale model frontmatter:")
        print("\n".join("  " + path for path in stale))
        return 1
    print("model configuration is current" if args.check or not stale else "updated model frontmatter")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
