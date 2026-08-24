#!/usr/bin/env python3
"""Validate Smart Harness structure, workflow invariants, docs, links, and generated files."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = ROOT.parent

REQUIRED = [
    "shared/skills/plan-first/SKILL.md",
    "shared/skills/parallel-work/SKILL.md",
    "shared/skills/engineering-core/SKILL.md",
    "shared/skills/documentation-sync/SKILL.md",
    "shared/skills/pr-review/SKILL.md",
    "copilot/agents/dev.agent.md",
    "copilot/agents/review-pr.agent.md",
    "claude-code/commands/dev.md",
    "claude-code/commands/review-pr.md",
    "pi/prompts/dev.md",
    "pi/prompts/review-pr.md",
    "config/models.json",
    "integrations/upstreams.lock.json",
    "docs/ARCHITECTURE.md",
    "docs/WORKFLOW_CONTRACTS.md",
    "docs/DOCUMENTATION_POLICY.md",
]

ENTRY_POINTS = [
    "copilot/agents/dev.agent.md",
    "claude-code/commands/dev.md",
    "pi/prompts/dev.md",
]
PR_POINTS = [
    "copilot/agents/review-pr.agent.md",
    "claude-code/commands/review-pr.md",
    "pi/prompts/review-pr.md",
]
EDITORS = [
    "copilot/agents/worker-terra.agent.md",
    "copilot/agents/worker-sonnet.agent.md",
    "copilot/agents/worker-sol.agent.md",
    "claude-code/agents/fast-worker.md",
    "claude-code/agents/deep-implementer.md",
]


def require_text(path: str, needles: list[str]) -> None:
    text = (ROOT / path).read_text(encoding="utf-8").lower()
    missing = [needle for needle in needles if needle.lower() not in text]
    if missing:
        raise AssertionError(f"{path}: missing required workflow terms {missing}")


def validate_frontmatter() -> None:
    candidates = list(ROOT.glob("shared/skills/*/SKILL.md"))
    candidates += list(ROOT.glob("copilot/agents/*.agent.md"))
    candidates += list(ROOT.glob("claude-code/agents/*.md"))
    candidates += list(ROOT.glob("claude-code/commands/*.md"))
    for path in candidates:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n") or "\n---\n" not in text[4:]:
            raise AssertionError(f"invalid frontmatter: {path.relative_to(ROOT)}")


def validate_links() -> None:
    pattern = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
    for path in ROOT.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for raw in pattern.findall(text):
            target = raw.strip().split()[0].strip("<>")
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = target.split("#", 1)[0]
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                raise AssertionError(f"broken local link in {path.relative_to(ROOT)}: {raw}")


def validate_manifest_sync() -> None:
    lock = json.loads((ROOT / "integrations/upstreams.lock.json").read_text(encoding="utf-8"))
    by_name = {item["name"]: item for item in lock["upstreams"]}
    extensions = json.loads((ROOT / "pi/extensions.json").read_text(encoding="utf-8"))
    expected_methodology = [
        f"git:github.com/{by_name['superpowers']['repository']}@{by_name['superpowers']['commit']}",
        f"git:github.com/{by_name['ponytail']['repository']}@{by_name['ponytail']['commit']}",
    ]
    if extensions["profiles"]["methodology"] != expected_methodology:
        raise AssertionError("Pi methodology profile is out of sync with upstream lock")

    skills = json.loads((ROOT / "pi/skills.json").read_text(encoding="utf-8"))
    if skills["source"]["repository"] != by_name["pi-skills"]["repository"] or skills["source"]["commit"] != by_name["pi-skills"]["commit"]:
        raise AssertionError("Pi skills source is out of sync with upstream lock")


def main() -> int:
    for rel in REQUIRED:
        if not (ROOT / rel).exists():
            raise AssertionError(f"missing required file: {rel}")

    for workflow in [
        REPO_ROOT / ".github/workflows/smart-harness-ci.yml",
        REPO_ROOT / ".github/workflows/smart-harness-upstream-sync.yml",
    ]:
        if not workflow.exists():
            raise AssertionError(f"missing repository workflow: {workflow.relative_to(REPO_ROOT)}")

    for json_path in [
        "config/models.json",
        "integrations/upstreams.lock.json",
        "pi/extensions.json",
        "pi/skills.json",
    ]:
        json.loads((ROOT / json_path).read_text(encoding="utf-8"))

    validate_frontmatter()
    validate_manifest_sync()

    for path in ENTRY_POINTS:
        require_text(path, ["plan", "documentation", "parallel", "verify"])
    for path in PR_POINTS:
        require_text(path, ["plan", "worktree", "unit", "integration", "documentation", "not executed"])
    for path in EDITORS:
        require_text(path, ["documentation-sync", "verification"])

    extensions = (ROOT / "pi/extensions.json").read_text(encoding="utf-8")
    if "pi-retry" in extensions:
        raise AssertionError("deprecated pi-retry must not be configured")

    subprocess.run([sys.executable, str(ROOT / "config/configure-models.py"), "--check"], check=True)
    subprocess.run([sys.executable, str(ROOT / "scripts/generate-reference.py"), "--check"], check=True)
    validate_links()

    print("Smart Harness validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
