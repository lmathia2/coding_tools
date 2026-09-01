#!/usr/bin/env python3
"""Validate WYSIWYShip structure, simplicity budget, and core invariants."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT / "config"))
from model_config import get_profile, load_config, resolve_spec  # noqa: E402
from adapter_config import rewrite_text  # noqa: E402

EXPECTED_SKILLS = {
    "eli5",
    "engineering-workflow",
    "pr-review",
    "product-behavior-spec",
    "skill-authoring",
    "vscode",
}
DISTRIBUTED_SKILLS = {"eli5", "engineering-workflow", "pr-review", "product-behavior-spec"}
EXPECTED_CLAUDE_AGENTS = {
    "fast.md",
    "worker.md",
    "deep-reasoner.md",
    "deep-implementer.md",
    "top-reviewer.md",
}
EXPECTED_CLAUDE_COMMANDS = {"dev.md", "review-pr.md"}
EXPECTED_COPILOT_AGENTS = {
    "dev.agent.md",
    "review-pr.agent.md",
    "fast-lane.agent.md",
    "worker-normal.agent.md",
    "worker-deep.agent.md",
    "deep-reasoner.agent.md",
    "top-reviewer.agent.md",
}
EXPECTED_CODEX_AGENTS = {
    "wysiwyship-fast.toml", "wysiwyship-worker.toml",
    "wysiwyship-deep.toml", "wysiwyship-reviewer.toml",
}
EXPECTED_ADAPTER_TARGETS = {
    "copilot/agents/dev.agent.md": ("copilot", "coordinator", "dev"),
    "copilot/agents/review-pr.agent.md": ("copilot", "coordinator", "review_pr"),
    "copilot/agents/fast-lane.agent.md": ("copilot", "fast", None),
    "copilot/agents/worker-normal.agent.md": ("copilot", "normal", None),
    "copilot/agents/worker-deep.agent.md": ("copilot", "deep", None),
    "copilot/agents/deep-reasoner.agent.md": ("copilot", "deep", None),
    "copilot/agents/top-reviewer.agent.md": ("copilot", "top", None),
    "claude-code/commands/dev.md": ("claude_code", "coordinator", "dev"),
    "claude-code/commands/review-pr.md": ("claude_code", "coordinator", "review_pr"),
    "claude-code/agents/fast.md": ("claude_code", "fast", None),
    "claude-code/agents/worker.md": ("claude_code", "normal", None),
    "claude-code/agents/deep-reasoner.md": ("claude_code", "deep", None),
    "claude-code/agents/deep-implementer.md": ("claude_code", "deep", None),
    "claude-code/agents/top-reviewer.md": ("claude_code", "top", None),
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


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        fail(f"{path.relative_to(ROOT)} invalid frontmatter")
    block = text[4:text.find("\n---\n", 4)]
    values = {}
    for line in block.splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip().strip("'\"")
    return values


def validate_adapter_roles(profile: dict[str, object]) -> None:
    marker = re.compile(r"<!--\s*harness-role:\s*([a-z-]+)\s*-->")
    workflow_marker = re.compile(r"<!--\s*harness-workflow:\s*([a-z-]+)\s*-->")
    for relative, (platform, expected_role, workflow) in EXPECTED_ADAPTER_TARGETS.items():
        path = ROOT / relative
        text = path.read_text(encoding="utf-8")
        roles = marker.findall(text)
        if roles != [expected_role]:
            fail(f"{relative} expected one {expected_role!r} role marker, found {roles}")
        workflows = [item.replace("-", "_") for item in workflow_marker.findall(text)]
        expected_workflows = [workflow] if workflow else []
        if workflows != expected_workflows:
            fail(f"{relative} expected workflow markers {expected_workflows}, found {workflows}")
        metadata = frontmatter(path)
        spec = resolve_spec(profile, platform, expected_role, workflow)
        expected_model = spec["model"]
        if metadata.get("model") != expected_model:
            fail(f"{relative} model drift: expected {expected_model!r}, found {metadata.get('model')!r}")
        effort_field = "reasoningEffort" if platform == "copilot" else "effort"
        if metadata.get(effort_field) != spec["reasoning"]:
            fail(f"{relative} {effort_field} drift: expected {spec['reasoning']!r}, found {metadata.get(effort_field)!r}")
    for path in (ROOT / "codex/agents").glob("*.toml"):
        text = path.read_text(encoding="utf-8")
        if rewrite_text(path, text, "codex", profile) != text:
            fail(f"{path.relative_to(ROOT)} model or reasoning drift")


def validate_version_and_models() -> str:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", version):
        fail(f"VERSION must be semantic, found {version!r}")
    config = load_config(ROOT / "config/models.json")
    _, profile = get_profile(config)
    validate_adapter_roles(profile)
    return version


def validate_budgets() -> None:
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

    codex_agents = names(ROOT / "codex/agents", "*.toml")
    if codex_agents != EXPECTED_CODEX_AGENTS:
        fail(f"Codex agent budget drift: expected {sorted(EXPECTED_CODEX_AGENTS)}, found {sorted(codex_agents)}")


def validate_identities() -> None:
    # Catch duplicate Claude agent identities (the v0.6 fast-executor/fast-verifier bug).
    identities = {}
    for path in (ROOT / "claude-code/agents").glob("*.md"):
        identity = frontmatter_name(path)
        if identity in identities:
            fail(f"duplicate Claude agent name {identity}: {identities[identity]} and {path.name}")
        identities[identity] = path.name

    for path in (ROOT / "shared/skills").glob("*/SKILL.md"):
        frontmatter_name(path)


def validate_vendor() -> None:
    sources = json.loads((ROOT / "vendor/SOURCES.json").read_text(encoding="utf-8"))
    for item in sources["components"]:
        license_path = ROOT / item["license_file"]
        if not license_path.exists():
            fail(f"missing vendor license {item['license_file']}")
        for local in item["local_paths"]:
            if not (ROOT / local).exists():
                fail(f"vendor source points to missing local path {local}")


def validate_runtime_independence() -> None:
    # Runtime installers/helpers must not fetch or install third-party harness dependencies.
    runtime_files = [
        ROOT / "install.sh", ROOT / "install-global.sh", ROOT / "scripts/install_harness.py",
        ROOT / "config/model_discovery.py", *list((ROOT / "tools").glob("*.py")), *list((ROOT / "pi/tools").glob("*.py")),
    ]
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

    eli5_template = ROOT / "shared/skills/eli5/assets/project-eli5-template.html"
    template_text = eli5_template.read_text(encoding="utf-8").lower()
    for marker in ("http://", "https://", "<script src=", '<link rel="stylesheet"'):
        if marker in template_text:
            fail(f"ELI5 template contains external dependency marker {marker}")


def validate_removed_surfaces() -> None:
    # Old network-sync surfaces must stay gone.
    for rel in (
        "integrations/install-methodologies.sh", "integrations/upstreams.lock.json",
        "scripts/check-upstreams.py", "pi/install-extensions.sh", "pi/install-skills.sh",
        "pi/extensions.json", "pi/skills.json",
    ):
        if (ROOT / rel).exists():
            fail(f"legacy external-dependency surface remains: {rel}")
    if (REPO / ".github/workflows/wysiwyship-upstream-sync.yml").exists():
        fail("legacy upstream sync workflow remains")


def validate_required_refinements() -> None:
    for required in (ROOT / "tools/complexity.py", ROOT / "tools/commit_docs.py", ROOT / "tools/check.py", ROOT / "tools/work_units.py", ROOT / "tools/hook_check.py", ROOT / "tools/wiki.py", ROOT / "copilot/hooks/wysiwyship.json", ROOT / "codex/agents/wysiwyship-worker.toml", ROOT / "config/checks.json", ROOT / "config/model_discovery.py", ROOT / "tests/test_harness.py", ROOT / "templates/WORK_UNIT.md", ROOT / "shared/skills/engineering-workflow/references/planning-grill.md", ROOT / "shared/skills/eli5/scripts/render_explainer.py", ROOT / "shared/skills/eli5/assets/project-eli5-template.html"):
        if not required.exists():
            fail(f"missing required harness component {required.relative_to(ROOT)}")


def validate_native_packages(version: str) -> None:
    manifests = (
        ROOT / "packages/copilot/plugin.json",
        ROOT / "packages/claude/.claude-plugin/plugin.json",
        REPO / ".claude-plugin/marketplace.json",
    )
    for path in manifests:
        data = json.loads(path.read_text(encoding="utf-8"))
        observed = data.get("version") or data.get("metadata", {}).get("version")
        if observed != version:
            fail(f"{path.relative_to(REPO)} version drift: expected {version}, found {observed}")
    marketplace = json.loads((REPO / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    if marketplace.get("plugins", [{}])[0].get("version") != version:
        fail(".claude-plugin/marketplace.json plugin entry version drift")
    for package in ("copilot", "claude"):
        skills = {path.parent.name for path in (ROOT / "packages" / package / "skills").glob("*/SKILL.md")}
        if skills != DISTRIBUTED_SKILLS:
            fail(f"{package} package skills differ from the default set: {sorted(skills)}")


def main() -> int:
    version = validate_version_and_models()
    validate_budgets()
    validate_identities()
    validate_vendor()
    validate_runtime_independence()
    validate_removed_surfaces()
    validate_required_refinements()
    validate_native_packages(version)
    print(f"WYSIWYShip {version} validation: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
