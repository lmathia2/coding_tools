#!/usr/bin/env python3
"""Transactional, self-contained Smart Harness installer."""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import sys
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
PLATFORMS = {"copilot", "claude", "pi", "both", "all"}
LEGACY_SKILLS = (
    "codebase-map", "context-snapshot", "documentation-sync", "engineering-core",
    "parallel-work", "plan-first", "ponytail", "ponytail-review",
    "superpowers-methodology", "superpowers-skill-authoring", "task-ledger",
)
LEGACY_CLAUDE_AGENTS = ("deep-worker.md", "fast-executor.md", "fast-verifier.md", "fast-worker.md")
LEGACY_COPILOT_AGENTS = (
    "worker-terra.agent.md", "fast-terra.agent.md", "worker-sonnet.agent.md",
    "worker-sol.agent.md", "deep-sol.agent.md", "security-opus.agent.md",
)


def exists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def remove_path(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    elif exists(path):
        path.unlink()


def copy_path(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_symlink():
        destination.symlink_to(os.readlink(source))
    elif source.is_dir():
        shutil.copytree(source, destination, symlinks=True)
    else:
        shutil.copy2(source, destination)


def path_digest(path: Path) -> str:
    digest = hashlib.sha256()
    if path.is_symlink():
        digest.update(b"link\0" + os.readlink(path).encode())
    elif path.is_file():
        digest.update(b"file\0" + path.read_bytes())
    elif path.is_dir():
        digest.update(b"dir\0")
        for child in sorted(path.rglob("*")):
            relative = child.relative_to(path).as_posix().encode()
            digest.update(relative + b"\0")
            if child.is_symlink():
                digest.update(b"link\0" + os.readlink(child).encode())
            elif child.is_file():
                digest.update(b"file\0" + child.read_bytes())
            else:
                digest.update(b"dir\0")
    else:
        return "missing"
    return digest.hexdigest()


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        if path.exists():
            shutil.copymode(path, temporary_path)
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def load_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def validate_manifest_data(data: dict[str, Any], path: Path) -> None:
    if data.get("schema_version") != 1:
        raise ValueError(f"{path}: unsupported or missing schema_version")
    if not isinstance(data.get("platforms"), list) or not all(item in {"copilot", "claude", "pi"} for item in data["platforms"]):
        raise ValueError(f"{path}: platforms must contain only copilot, claude, or pi")
    if not isinstance(data.get("backup_history"), list) or not all(isinstance(item, str) for item in data["backup_history"]):
        raise ValueError(f"{path}: backup_history must be an array of paths")
    outputs = data.get("outputs")
    if not isinstance(outputs, list):
        raise ValueError(f"{path}: outputs must be an array")
    for output in outputs:
        validate_manifest_output(output, path)


def validate_manifest_output(output: object, manifest: Path) -> None:
    if not isinstance(output, dict) or not isinstance(output.get("path"), str) or not isinstance(output.get("sha256"), str):
        raise ValueError(f"{manifest}: each output requires string path and sha256")
    path = PurePosixPath(output["path"])
    if str(path) == "." or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{manifest}: output path must stay within the install root: {path}")


class Installer:
    def __init__(self, scope: str, platform: str, target: Path, dry_run: bool) -> None:
        self.scope = scope
        self.platform = platform
        self.target = target.resolve()
        self.dry_run = dry_run
        self.snapshots: list[tuple[Path, bool, Path | None]] = []
        self.snapshot_paths: set[Path] = set()
        self.outputs: set[Path] = set()
        self.backup_root: Path | None = None

    def selected(self, platform: str) -> bool:
        return self.platform == platform or self.platform == "all" or (self.platform == "both" and platform in {"copilot", "claude"})

    def relative(self, path: Path) -> str:
        return path.relative_to(self.target).as_posix()

    def log(self, action: str, path: Path) -> None:
        print(f"{action} {self.relative(path)}")

    def ensure_backup_root(self) -> Path:
        if self.backup_root is None:
            base = self.target / ".smart-harness-backups"
            base.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S-")
            self.backup_root = Path(tempfile.mkdtemp(prefix=stamp, dir=base))
        return self.backup_root

    def snapshot(self, destination: Path) -> None:
        if destination in self.snapshot_paths or self.dry_run:
            return
        self.snapshot_paths.add(destination)
        present = exists(destination)
        backup: Path | None = None
        if present:
            backup = self.ensure_backup_root() / self.relative(destination)
            copy_path(destination, backup)
        self.snapshots.append((destination, present, backup))

    def replace(self, source: Path, destination: Path) -> None:
        if exists(destination) and path_digest(source) == path_digest(destination):
            self.outputs.add(destination)
            return
        self.log("would install" if self.dry_run else "installed", destination)
        if self.dry_run:
            return
        self.snapshot(destination)
        remove_path(destination)
        copy_path(source, destination)
        self.outputs.add(destination)

    def remove_legacy(self, destination: Path) -> None:
        if not exists(destination):
            return
        self.log("would remove legacy" if self.dry_run else "removed legacy", destination)
        if self.dry_run:
            return
        self.snapshot(destination)
        remove_path(destination)

    def write_text(self, destination: Path, text: str) -> None:
        if destination.exists() and destination.read_text(encoding="utf-8") == text:
            self.outputs.add(destination)
            return
        self.log("would update" if self.dry_run else "updated", destination)
        if self.dry_run:
            return
        self.snapshot(destination)
        atomic_write(destination, text)
        self.outputs.add(destination)

    def preflight(self) -> None:
        if self.scope not in {"project", "global"}:
            raise ValueError(f"unknown scope {self.scope!r}")
        if self.platform not in PLATFORMS:
            raise ValueError(f"unknown platform {self.platform!r}")
        self.validate_target()
        self.validate_sources()
        self.validate_pi_settings()
        self.validate_manifest()

    def validate_target(self) -> None:
        if not self.target.is_dir():
            raise ValueError(f"target directory does not exist: {self.target}")
        if not os.access(self.target, os.W_OK):
            raise PermissionError(f"target directory is not writable: {self.target}")

    def validate_sources(self) -> None:
        required = [ROOT / "VERSION", ROOT / "config/models.json", ROOT / "shared/skills", ROOT / "templates", ROOT / "tools/complexity.py", ROOT / "tools/commit_docs.py", ROOT / "vendor/SOURCES.json"]
        missing = [str(path) for path in required if not path.exists()]
        if missing:
            raise FileNotFoundError(f"installer source is incomplete: {missing}")

    def validate_pi_settings(self) -> None:
        if not self.selected("pi"):
            return
        settings = self.pi_settings_path()
        data = load_json_object(settings)
        skills = data.get("skills", [])
        if not isinstance(skills, list) or not all(isinstance(item, str) for item in skills):
            raise ValueError(f"{settings}: skills must be an array of strings")

    def validate_manifest(self) -> None:
        manifest = self.target / ".smart-harness/install-manifest.json"
        if manifest.exists():
            validate_manifest_data(load_json_object(manifest), manifest)

    def pi_settings_path(self) -> Path:
        return self.target / (".pi/settings.json" if self.scope == "project" else ".pi/agent/settings.json")

    def install_shared(self) -> None:
        skill_root = self.target / ".claude/skills"
        for name in LEGACY_SKILLS:
            self.remove_legacy(skill_root / name)
        for source in sorted((ROOT / "shared/skills").iterdir()):
            if source.is_dir():
                self.replace(source, skill_root / source.name)

    def install_copilot(self) -> None:
        base = self.target / (".github/agents" if self.scope == "project" else ".copilot/agents")
        for name in LEGACY_COPILOT_AGENTS:
            self.remove_legacy(base / name)
        for source in sorted((ROOT / "copilot/agents").glob("*.agent.md")):
            self.replace(source, base / source.name)
        if self.scope == "project":
            self.replace(ROOT / "copilot/github-skills/code-review", self.target / ".github/skills/code-review")

    def install_claude(self) -> None:
        agent_root = self.target / ".claude/agents"
        for name in LEGACY_CLAUDE_AGENTS:
            self.remove_legacy(agent_root / name)
        for source in sorted((ROOT / "claude-code/agents").glob("*.md")):
            self.replace(source, agent_root / source.name)
        for source in sorted((ROOT / "claude-code/commands").glob("*.md")):
            self.replace(source, self.target / ".claude/commands" / source.name)

    def install_pi(self) -> None:
        if self.scope == "project":
            prompt_root = self.target / ".pi/prompts"
            tool_root = self.target / ".pi/tools"
            skill_path = "../.claude/skills"
        else:
            prompt_root = self.target / ".pi/agent/prompts"
            tool_root = self.target / ".pi/agent/smart-harness"
            skill_path = str(self.target / ".claude/skills")
        for source in sorted((ROOT / "pi/prompts").glob("*.md")):
            self.replace(source, prompt_root / source.name)
        for pattern in ("*.py", "*.md"):
            for source in sorted((ROOT / "pi/tools").glob(pattern)):
                self.replace(source, tool_root / source.name)
        settings_path = self.pi_settings_path()
        data = load_json_object(settings_path)
        skills = data.setdefault("skills", [])
        if skill_path not in skills:
            skills.append(skill_path)
        data["enableSkillCommands"] = True
        self.write_text(settings_path, json.dumps(data, indent=2) + "\n")

    def install_support_files(self) -> None:
        support_root = self.target / ".smart-harness"
        self.replace(ROOT / "config/models.json", support_root / "config/models.json")
        for source in sorted((ROOT / "tools").glob("*.py")):
            self.replace(source, support_root / "tools" / source.name)
        self.replace(ROOT / "vendor/SOURCES.json", support_root / "vendor/SOURCES.json")
        self.replace(ROOT / "vendor/THIRD_PARTY_NOTICES.md", support_root / "vendor/THIRD_PARTY_NOTICES.md")
        self.replace(ROOT / "vendor/licenses", support_root / "vendor/licenses")
        if self.scope == "project":
            self.install_project_support_files(support_root)

    def install_project_support_files(self, support_root: Path) -> None:
        for source in sorted((ROOT / "templates").iterdir()):
            if source.is_file():
                self.replace(source, support_root / "templates" / source.name)
        if not (self.target / "CLAUDE.md").exists():
            self.replace(ROOT / "templates/CLAUDE.md.example", self.target / "CLAUDE.md.example")
        self.ensure_project_directories()
        self.update_gitignore()

    def ensure_project_directories(self) -> None:
        for directory in (self.target / ".agent-worktrees", self.target / ".agent-state"):
            if not directory.exists() and not self.dry_run:
                self.snapshot(directory)
                directory.mkdir(parents=True)

    def update_gitignore(self) -> None:
        gitignore = self.target / ".gitignore"
        text = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
        lines = text.splitlines()
        for entry in (".agent-worktrees/", ".agent-state/", ".smart-harness-backups/"):
            if entry not in lines:
                lines.append(entry)
        self.write_text(gitignore, "\n".join(lines) + "\n")

    def manifest_outputs(self, previous: dict[str, Any]) -> dict[str, str]:
        outputs = {
            item["path"]: item["sha256"]
            for item in previous.get("outputs", [])
            if isinstance(item, dict) and "path" in item and "sha256" in item
        }
        outputs.update(
            {
                self.relative(path): path_digest(path)
                for path in self.outputs
                if exists(path)
            }
        )
        return outputs

    def manifest_platforms(self, previous: dict[str, Any]) -> list[str]:
        selected = {"copilot", "claude", "pi"} if self.platform == "all" else ({"copilot", "claude"} if self.platform == "both" else {self.platform})
        selected.update(previous.get("platforms", []))
        return sorted(selected)

    def manifest_data(self, previous: dict[str, Any], outputs: dict[str, str], platforms: list[str]) -> dict[str, Any]:
        backup_history = list(previous.get("backup_history", []))
        if self.backup_root and str(self.backup_root) not in backup_history:
            backup_history.append(str(self.backup_root))
        return {
            "schema_version": 1,
            "version": VERSION,
            "scope": self.scope,
            "platforms": platforms,
            "backup_history": backup_history,
            "outputs": [{"path": path, "sha256": digest} for path, digest in sorted(outputs.items())],
        }

    def write_manifest(self) -> None:
        manifest = self.target / ".smart-harness/install-manifest.json"
        previous = load_json_object(manifest) if manifest.exists() else {}
        outputs = self.manifest_outputs(previous)
        platforms = self.manifest_platforms(previous)

        candidate = json.dumps(self.manifest_data(previous, outputs, platforms), indent=2) + "\n"
        if manifest.exists() and manifest.read_text(encoding="utf-8") == candidate:
            return
        self.snapshot(manifest)
        candidate = json.dumps(self.manifest_data(previous, outputs, platforms), indent=2) + "\n"
        self.log("wrote manifest", manifest)
        atomic_write(manifest, candidate)

    def rollback(self) -> None:
        print("installation failed; rolling back touched paths", file=sys.stderr)
        for destination, present, backup in reversed(self.snapshots):
            try:
                remove_path(destination)
                if present and backup is not None:
                    copy_path(backup, destination)
            except OSError as exc:
                print(f"rollback failed for {destination}: {exc}", file=sys.stderr)

    def run(self) -> None:
        self.preflight()
        try:
            self.install_shared()
            if self.selected("copilot"):
                self.install_copilot()
            if self.selected("claude"):
                self.install_claude()
            if self.selected("pi"):
                self.install_pi()
            self.install_support_files()
            if not self.dry_run:
                self.write_manifest()
        except Exception:
            if not self.dry_run:
                self.rollback()
            raise


def print_status(target: Path) -> int:
    manifest_path = target / ".smart-harness/install-manifest.json"
    if not manifest_path.exists():
        print("Smart Harness is not installed (manifest missing).")
        return 1
    manifest = load_json_object(manifest_path)
    validate_manifest_data(manifest, manifest_path)
    drift: list[str] = []
    if manifest.get("version") != VERSION:
        drift.append(f"manifest version {manifest.get('version', 'unknown')} != installer version {VERSION}")
    for output in manifest.get("outputs", []):
        path = target / output["path"]
        if path_digest(path) != output["sha256"]:
            drift.append(output["path"])
    platforms = ",".join(manifest.get("platforms", [])) or "unknown"
    print(f"Smart Harness {manifest.get('version', 'unknown')} ({platforms}, {manifest.get('scope', 'unknown')})")
    if drift:
        print("Drifted or missing paths:")
        for path in drift:
            print(f"  {path}")
        return 1
    print("Installed files match the manifest.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("scope", choices=("project", "global"))
    parser.add_argument("platform", choices=sorted(PLATFORMS), nargs="?", default="all")
    parser.add_argument("target", nargs="?")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--status", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.scope == "project":
        if not args.target:
            raise SystemExit("project installation requires /path/to/project")
        target = Path(args.target)
    else:
        if args.target:
            raise SystemExit("global installation does not accept a target path")
        target = Path.home()
    if args.status:
        return print_status(target.resolve())
    installer = Installer(args.scope, args.platform, target, args.dry_run)
    installer.run()
    mode = "dry run complete" if args.dry_run else "installation complete"
    print(f"\nSmart Harness {VERSION} {mode} ({args.scope}, {args.platform}).")
    if installer.backup_root:
        print(f"Backup: {installer.backup_root}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
