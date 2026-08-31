#!/usr/bin/env python3
"""Build reproducible Copilot and Claude Code plugins from canonical harness sources."""
from __future__ import annotations

import argparse
import filecmp
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ROOT / "packages"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
PLUGIN_NAME = "wysiwyship"
DESCRIPTION = "What you spec is what you ship: plan, implement, document, simplify, verify, and explain with deterministic evidence."


def write_json(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def copy_files(source: Path, destination: Path, pattern: str = "*") -> None:
    for path in sorted(source.glob(pattern)):
        target = destination / path.name
        if path.is_dir():
            shutil.copytree(path, target)
        elif path.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def rewrite_runtime_paths(root: Path, placeholder: str) -> None:
    for path in root.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"python3 (\.wysiwyship/(?:tools|config)/[^\s`]+)", lambda match: f'python3 "{placeholder}/{match.group(1).split("/", 1)[1]}"', text)
        text = text.replace(".wysiwyship/", f"{placeholder}/")
        path.write_text(text, encoding="utf-8")


def copy_runtime(destination: Path) -> None:
    copy_files(ROOT / "tools", destination / "tools", "*.py")
    for name in ("checks.json", "models.json"):
        target = destination / "config" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "config" / name, target)
    shutil.copy2(ROOT / "config/model_config.py", destination / "config/model_config.py")
    copy_files(ROOT / "shared/skills", destination / "skills")
    copy_files(ROOT / "vendor", destination / "vendor")


def plugin_metadata() -> dict[str, object]:
    return {
        "name": PLUGIN_NAME,
        "description": DESCRIPTION,
        "version": VERSION,
        "author": {"name": "lmathia2"},
        "repository": "https://github.com/lmathia2/coding_tools",
        "keywords": ["sdlc", "coding-workflow", "code-review", "complexity", "documentation", "eli5"],
    }


def build_copilot(destination: Path) -> None:
    copy_runtime(destination)
    copy_files(ROOT / "copilot/agents", destination / "agents", "*.agent.md")
    manifest = {**plugin_metadata(), "agents": "agents/", "skills": "skills/", "hooks": "hooks.json"}
    write_json(destination / "plugin.json", manifest)
    hooks = json.loads((ROOT / "copilot/hooks/wysiwyship.json").read_text(encoding="utf-8"))
    entry = hooks["hooks"]["agentStop"][0]
    entry["bash"] = 'python3 "${PLUGIN_ROOT}/tools/hook_check.py" --host copilot'
    entry["powershell"] = 'python "${PLUGIN_ROOT}/tools/hook_check.py" --host copilot'
    write_json(destination / "hooks.json", hooks)
    rewrite_runtime_paths(destination, "${PLUGIN_ROOT}")
    write_package_readme(destination, "copilot")


def build_claude(destination: Path) -> None:
    copy_runtime(destination)
    copy_files(ROOT / "claude-code/agents", destination / "agents", "*.md")
    copy_files(ROOT / "claude-code/commands", destination / "commands", "*.md")
    manifest = {
        "$schema": "https://json.schemastore.org/claude-code-plugin-manifest.json",
        "displayName": "WYSIWYShip",
        **plugin_metadata(),
    }
    write_json(destination / ".claude-plugin/plugin.json", manifest)
    hooks = {
        "description": "Verify an explicitly active WYSIWYShip work unit before stopping.",
        "hooks": {"Stop": [{"hooks": [{
            "type": "command", "command": "python3",
            "args": ["${CLAUDE_PLUGIN_ROOT}/tools/hook_check.py", "--host", "claude"], "timeout": 600,
        }]}]},
    }
    write_json(destination / "hooks/hooks.json", hooks)
    rewrite_runtime_paths(destination, "${CLAUDE_PLUGIN_ROOT}")
    namespace_claude_commands(destination / "commands")
    write_package_readme(destination, "claude")


def namespace_claude_commands(commands: Path) -> None:
    names = (
        "eli5", "engineering-workflow", "pr-review", "product-behavior-spec",
        "smart-fast", "smart-worker", "smart-deep-reasoner", "smart-deep-implementer", "smart-top-reviewer",
    )
    for path in commands.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        for name in names:
            text = text.replace(f"`{name}`", f"`{PLUGIN_NAME}:{name}`")
        path.write_text(text, encoding="utf-8")


def write_package_readme(destination: Path, platform: str) -> None:
    install = (
        "`copilot plugin install lmathia2/coding_tools:wysiwyship/packages/copilot`"
        if platform == "copilot"
        else "add `lmathia2/coding_tools` as a Claude marketplace, then install `wysiwyship@coding-tools`"
    )
    destination.joinpath("README.md").write_text(
        f"# WYSIWYShip {platform.title()} plugin\n\nGenerated from canonical WYSIWYShip v{VERSION} sources. Install with {install}.\n\n"
        "Plugin installation supplies host workflows, specialists, skills, tools, and the inactive-by-default stop hook. "
        "Use the repository installer instead when the workflow/configuration files should be versioned with a project.\n",
        encoding="utf-8",
    )


def build(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    build_copilot(output / "copilot")
    build_claude(output / "claude")


def compare_directories(expected: Path, actual: Path) -> list[str]:
    comparison = filecmp.dircmp(expected, actual)
    errors = [f"missing generated path: {expected / name}" for name in comparison.left_only]
    errors.extend(f"unexpected generated path: {actual / name}" for name in comparison.right_only)
    errors.extend(
        f"generated content differs: {actual / name}"
        for name in comparison.common_files
        if (expected / name).read_bytes() != (actual / name).read_bytes()
    )
    for name in comparison.common_dirs:
        errors.extend(compare_directories(expected / name, actual / name))
    return errors


def validate_output(output: Path) -> None:
    protected = {Path("/").resolve(), Path.home().resolve(), ROOT.resolve(), ROOT.parent.resolve()}
    if output in protected:
        raise ValueError(f"refusing to replace broad output path: {output}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=str(PACKAGES))
    args = parser.parse_args()
    output = Path(args.output).resolve()
    validate_output(output)
    if args.check:
        with tempfile.TemporaryDirectory() as raw:
            expected = Path(raw) / "packages"
            build(expected)
            errors = compare_directories(expected, output)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        print("native plugin packages are current")
        return 0
    if output.exists():
        shutil.rmtree(output)
    build(output)
    print(f"built native plugin packages in {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
