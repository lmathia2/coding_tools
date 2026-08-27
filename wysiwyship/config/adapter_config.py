#!/usr/bin/env python3
"""Render host adapter model and reasoning settings from a profile."""
from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from model_config import resolve_spec


ROLE_RE = re.compile(r"<!--\s*harness-role:\s*([a-z-]+)\s*-->")
WORKFLOW_RE = re.compile(r"<!--\s*harness-workflow:\s*([a-z-]+)\s*-->")
TOML_ROLE_RE = re.compile(r"(?m)^#\s*harness-role:\s*([a-z-]+)\s*$")


def replace_field(frontmatter: str, field: str, value: str | None) -> str:
    pattern = rf"(?m)^{re.escape(field)}:\s*.*$"
    if value is None:
        return re.sub(pattern + r"\n?", "", frontmatter)
    replacement = f"{field}: {value}"
    return re.sub(pattern, replacement, frontmatter) if re.search(pattern, frontmatter) else frontmatter + f"\n{replacement}"


def markdown_target(path: Path, text: str) -> tuple[str, str | None]:
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


def rewrite_markdown(path: Path, text: str, platform: str, profile: dict[str, Any]) -> str:
    role, workflow = markdown_target(path, text)
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


def replace_toml(text: str, field: str, value: str | None) -> str:
    pattern = rf'(?m)^{re.escape(field)}\s*=\s*"[^"]*"\n?'
    if value is None:
        return re.sub(pattern, "", text)
    replacement = f'{field} = "{value}"\n'
    return re.sub(pattern, replacement, text) if re.search(pattern, text) else replacement + text


def rewrite_codex(path: Path, text: str, profile: dict[str, Any]) -> str:
    roles = TOML_ROLE_RE.findall(text)
    if len(roles) != 1:
        raise RuntimeError(f"{path}: expected exactly one harness-role marker, found {len(roles)}")
    spec = resolve_spec(profile, "codex", roles[0])
    text = replace_toml(text, "model", spec.get("model"))
    return replace_toml(text, "model_reasoning_effort", spec["reasoning"])


def rewrite_text(path: Path, text: str, platform: str, profile: dict[str, Any]) -> str:
    return rewrite_codex(path, text, profile) if platform == "codex" else rewrite_markdown(path, text, platform, profile)
