#!/usr/bin/env python3
"""Validate v0.7 Smart Harness structure, simplicity budget, and core invariants."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent

EXPECTED_SKILLS = {
    "engineering-workflow",
    "pr-review",
    "product-behavior-spec",
    "skill-authoring",
    "vscode",
}
EXPECTED_CLAUDE_AGENTS = {
    "fast.md",
    "deep-reasoner.md",
    "deep-implementer.md",
    "top-reviewer.md",
}
EXPECTED_CLAUDE_COMMANDS = {"dev.md", "review-pr.md"}
EXPECTED_COPILOT_AGENTS = {
    "dev.agent.md",
    "review-pr.agent.md",
    "fast-terra.agent.md",
    "worker-sonnet.agent.md",
    "worker-sol.agent.md",
    "deep-sol.agent.md",
    "security-opus.agent.md",
}
LEGACY_SKILLS = {
    "codebase-map", "context-snapshot", "documentation-sync", "engineering-core",
    "parallel-work", "plan-first", "ponytail", "ponytail-review",
    "superpowers-methodology", "superpowers-skill-authoring", "task-ledger",
}
LEGACY_CLAUDE_AGENTS = {"deep-worker.md", "fast-executor.md", "fast-verifier.md", "fast-worker.md"}


def fail(message: str) -> None:
    raise AssertionError(message)


def names(path: Path, pattern: str) -> set[str]:
    return {p.name for p in path.glob(pattern)}


def require_terms(path: Path, terms: tuple[str, ...]) -> None:
    text = path.read_text(encoding="utf-8").lower()
    missing = [term for term in terms if term.lower() not in text]
    if missing:
        fail(f"{path.relative_to(ROOT)} missing required terms {missing}")


def frontmatter_name(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"{path.relative_to(ROOT)} missing frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        fail(f"{path.relative_to(ROOT)} invalid frontmatter")
    block = text[4:end]
    name = re.search(r"(?m)^name:\s*(\S.*)$", block)
    desc = re.search(r"(?m)^description:\s*(\S.*)$", block)
    if not name or not desc:
        fail(f"{path.relative_to(ROOT)} requires name and description")
    return name.group(1).strip().strip("'\"")


def main() -> int:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if version != "0.7.0":
        fail(f"VERSION must be 0.7.0, found {version}")

    skill_dirs = {p.parent.name for p in (ROOT / "shared/skills").glob("*/SKILL.md")}
    if skill_dirs != EXPECTED_SKILLS:
        fail(f"shared skill budget drift: expected {sorted(EXPECTED_SKILLS)}, found {sorted(skill_dirs)}")
    if skill_dirs & LEGACY_SKILLS:
        fail("legacy duplicate skills remain")

    claude_agents = names(ROOT / "claude-code/agents", "*.md")
    if claude_agents != EXPECTED_CLAUDE_AGENTS:
        fail(f"Claude agent budget drift: expected {sorted(EXPECTED_CLAUDE_AGENTS)}, found {sorted(claude_agents)}")
    if claude_agents & LEGACY_CLAUDE_AGENTS:
        fail("legacy Claude agents remain")

    claude_commands = names(ROOT / "claude-code/commands", "*.md")
    if claude_commands != EXPECTED_CLAUDE_COMMANDS:
        fail(f"Claude command surface drift: {sorted(claude_commands)}")

    copilot_agents = names(ROOT / "copilot/agents", "*.agent.md")
    if copilot_agents != EXPECTED_COPILOT_AGENTS:
        fail(f"Copilot agent budget drift: expected {sorted(EXPECTED_COPILOT_AGENTS)}, found {sorted(copilot_agents)}")

    # Catch duplicate Claude agent identities (the v0.6 fast-executor/fast-verifier bug).
    identities = {}
    for path in (ROOT / "claude-code/agents").glob("*.md"):
        identity = frontmatter_name(path)
        if identity in identities:
            fail(f"duplicate Claude agent name {identity}: {identities[identity]} and {path.name}")
        identities[identity] = path.name

    for path in (ROOT / "shared/skills").glob("*/SKILL.md"):
        frontmatter_name(path)

    require_terms(ROOT / "copilot/agents/dev.agent.md", ("engineering-workflow", "proportional plan", "verification", "documentation"))
    require_terms(ROOT / "claude-code/commands/dev.md", ("engineering-workflow", "verification", "documentation"))
    require_terms(ROOT / "pi/prompts/dev.md", ("engineering-workflow", "verification", "documentation"))

    for path in (
        ROOT / "copilot/agents/review-pr.agent.md",
        ROOT / "claude-code/commands/review-pr.md",
        ROOT / "pi/prompts/review-pr.md",
        ROOT / "shared/skills/pr-review/SKILL.md",
    ):
        require_terms(path, ("worktree", "unit", "integration", "semantic", "execution"))

    # Product behavior generation must remain specialist/conditional.
    require_terms(ROOT / "shared/skills/engineering-workflow/SKILL.md", ("do not create a product behavior specification unless the user asks" ,))
    require_terms(ROOT / "shared/skills/pr-review/SKILL.md", ("do not create one during review",))

    sources = json.loads((ROOT / "vendor/SOURCES.json").read_text(encoding="utf-8"))
    for item in sources["components"]:
        license_path = ROOT / item["license_file"]
        if not license_path.exists():
            fail(f"missing vendor license {item['license_file']}")
        for local in item["local_paths"]:
            if not (ROOT / local).exists():
                fail(f"vendor source points to missing local path {local}")

    # Runtime installers/helpers must not fetch or install third-party harness dependencies.
    runtime_files = [ROOT / "install.sh", ROOT / "install-global.sh", *list((ROOT / "pi/tools").glob("*.py"))]
    forbidden = [
        r"git\s+clone", r"gh\s+skill\s+install", r"/plugin\s+install",
        r"copilot\s+plugin\s+install", r"pi\s+install", r"npm\s+install",
        r"pip(?:3)?\s+install", r"curl\s+https?://", r"wget\s+https?://",
    ]
    for path in runtime_files:
        text = path.read_text(encoding="utf-8")
        for pattern in forbidden:
            if re.search(pattern, text, re.I):
                fail(f"{path.relative_to(ROOT)} contains forbidden runtime install/fetch pattern {pattern}")

    # Old network-sync surfaces must stay gone.
    for rel in (
        "integrations/install-methodologies.sh", "integrations/upstreams.lock.json",
        "scripts/check-upstreams.py", "pi/install-extensions.sh", "pi/install-skills.sh",
        "pi/extensions.json", "pi/skills.json",
    ):
        if (ROOT / rel).exists():
            fail(f"legacy external-dependency surface remains: {rel}")
    if (REPO / ".github/workflows/smart-harness-upstream-sync.yml").exists():
        fail("legacy upstream sync workflow remains")

    print("smart harness v0.7 validation: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
