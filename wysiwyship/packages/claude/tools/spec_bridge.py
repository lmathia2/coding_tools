#!/usr/bin/env python3
"""Preview or import accepted Spec Kit, OpenSpec, and BMAD tasks as work units."""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys
from typing import Any

import work_units


CHECKBOX_RE = re.compile(r"^\s*[-*]\s+\[([ xX])\]\s+(.+?)\s*$")
TASK_ID_RE = re.compile(r"^(?:\*\*)?([A-Za-z]*T?\d+(?:\.\d+)*)(?:\*\*)?\s+(.*)$")
TASK_TOKEN = r"[A-Za-z]*T?\d+(?:\.\d+)*"
DEPENDS_RE = re.compile(rf"(?i)\bdepends(?:\s+on)?\s*:\s*({TASK_TOKEN}(?:\s*,\s*{TASK_TOKEN})*)")
PATH_RE = re.compile(r"`([^`]+[/\\][^`]+|[^`]+\.[A-Za-z0-9]+)`|\b([A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.{}*-]+)+\.[A-Za-z0-9*{}-]+)\b")
FRAMEWORKS = ("spec-kit", "openspec", "bmad")


@dataclass(frozen=True)
class Artifact:
    framework: str
    path: str


@dataclass(frozen=True)
class ImportedTask:
    source_id: str
    title: str
    section: str | None
    completed: bool
    parallel: bool
    dependencies: list[str]
    owned_paths: list[str]
    line: int


def detect(root: Path) -> list[Artifact]:
    patterns = {
        "spec-kit": ("specs/*/tasks.md",),
        "openspec": ("openspec/changes/*/tasks.md",),
        "bmad": (
            "_bmad-output/implementation-artifacts/story-*.md",
            "_bmad-output/implementation-artifacts/spec-*.md",
            "_bmad-output/implementation-artifacts/stories/*.md",
        ),
    }
    artifacts = []
    for framework, globs in patterns.items():
        for pattern in globs:
            for path in sorted(root.glob(pattern)):
                if path.is_file() and "/archive/" not in path.as_posix():
                    artifacts.append(Artifact(framework, path.relative_to(root).as_posix()))
    return artifacts


def infer_framework(root: Path, path: Path) -> str:
    relative = path.resolve().relative_to(root.resolve()).as_posix()
    if relative.startswith("openspec/changes/"):
        return "openspec"
    if relative.startswith("_bmad-output/"):
        return "bmad"
    if relative.startswith("specs/"):
        return "spec-kit"
    raise ValueError(f"cannot infer framework from {relative}; pass --framework")


def parse_tasks(path: Path, include_complete: bool = False) -> list[ImportedTask]:
    tasks = []
    section: str | None = None
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.startswith("#"):
            section = line.lstrip("#").strip()
            continue
        match = CHECKBOX_RE.match(line)
        if not match:
            continue
        completed = match.group(1).lower() == "x"
        if completed and not include_complete:
            continue
        tasks.append(parse_task(match.group(2), section, completed, line_number))
    return tasks


def parse_task(text: str, section: str | None, completed: bool, line: int) -> ImportedTask:
    id_match = TASK_ID_RE.match(text)
    source_id = id_match.group(1) if id_match else f"L{line}"
    title = id_match.group(2) if id_match else text
    parallel = bool(re.search(r"(?i)(?:^|\s)\[P\](?:\s|$)", title))
    title = re.sub(r"(?i)(?:^|\s)\[P\](?=\s|$)", " ", title)
    title = re.sub(r"(?:^|\s)\[[A-Z]+\d+\](?=\s|$)", " ", title).strip()
    dependencies = dependency_ids(title)
    title = DEPENDS_RE.sub("", title).strip(" -;,")
    return ImportedTask(source_id, title, section, completed, parallel, dependencies, infer_paths(text), line)


def dependency_ids(text: str) -> list[str]:
    match = DEPENDS_RE.search(text)
    if not match:
        return []
    return [item for item in re.split(r"[\s,]+", match.group(1).strip()) if item]


def infer_paths(text: str) -> list[str]:
    paths = []
    for match in PATH_RE.finditer(text):
        value = match.group(1) or match.group(2)
        if value and not value.startswith(("http://", "https://")):
            paths.append(value.replace("\\", "/"))
    return sorted(set(paths))


def slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized[:32] or "task"


def unit_ids(framework: str, source: Path, tasks: list[ImportedTask]) -> dict[str, str]:
    prefix = slug(f"{framework}-{source.parent.name}")
    ids = {task.source_id: f"{prefix}-{slug(task.source_id)}-{slug(task.title)}"[:80].rstrip("-") for task in tasks}
    if len(ids) != len(tasks) or len(set(ids.values())) != len(tasks):
        raise ValueError("source task IDs do not translate to unique work-unit IDs")
    return ids


def preview(root: Path, framework: str, source: Path, include_complete: bool) -> dict[str, Any]:
    relative = source.resolve().relative_to(root.resolve()).as_posix()
    tasks = parse_tasks(source, include_complete)
    ids = unit_ids(framework, source, tasks)
    return {
        "framework": framework,
        "source": relative,
        "authoritative_source": True,
        "work_units": [unit_preview(task, ids, relative) for task in tasks],
    }


def unit_preview(task: ImportedTask, ids: dict[str, str], source: str) -> dict[str, Any]:
    unresolved = [item for item in task.dependencies if item not in ids]
    return {
        "id": ids[task.source_id],
        "source_id": task.source_id,
        "title": task.title,
        "section": task.section,
        "completed_in_source": task.completed,
        "parallel_hint": task.parallel,
        "dependencies": [ids[item] for item in task.dependencies if item in ids],
        "unresolved_dependencies": unresolved,
        "owned_paths": task.owned_paths,
        "documentation": {"impact": "required", "paths": [source]},
        "line": task.line,
    }


def import_preview(root: Path, plan: dict[str, Any], owner: str | None, activate_first: bool) -> list[dict[str, Any]]:
    units = plan["work_units"]
    if any(item["unresolved_dependencies"] for item in units):
        raise ValueError("source contains dependencies that do not resolve to imported task IDs")
    conflicts = [item["id"] for item in units if work_units.unit_path(root, item["id"]).exists()]
    if conflicts:
        raise ValueError(f"work units already exist: {', '.join(conflicts)}")
    created = [create_unit(root, plan, item, owner) for item in units]
    if activate_first and created:
        work_units.activate(root, created[0]["id"])
    return created


def create_unit(root: Path, plan: dict[str, Any], item: dict[str, Any], owner: str | None) -> dict[str, Any]:
    arguments = argparse.Namespace(
        unit_id=item["id"], title=item["title"], goal=item["title"],
        acceptance=[item["title"]], depends_on=item["dependencies"], owner=[owner] if owner else [],
        owns=item["owned_paths"], base_ref=work_units.resolve_ref(root, "HEAD"), docs_impact="required",
        doc_path=[plan["source"]], docs_reason=None, source_framework=plan["framework"], source_path=plan["source"],
        planning_mode="imported", planning_gate="pass", planning_iterations=1,
        decision=[f"Accepted {plan['framework']} artifact remains authoritative for {item['source_id']}."],
        in_scope=[item["title"]], out_of_scope=[], assumption=[], open_question=[],
        ambiguity=["Accepted upstream artifact supplies the executable planning contract."],
    )
    unit = work_units.new_unit(arguments)
    errors = work_units.validation_errors(unit)
    if errors:
        raise ValueError("; ".join(errors))
    work_units.atomic_json(work_units.unit_path(root, unit["id"]), unit)
    return unit


def resolve_source(args: argparse.Namespace, root: Path) -> tuple[str, Path]:
    source = (root / args.source).resolve()
    try:
        source.relative_to(root)
    except ValueError as exc:
        raise ValueError("source must stay within the repository") from exc
    if not source.is_file():
        raise ValueError(f"source artifact does not exist: {source}")
    return args.framework or infer_framework(root, source), source


def detect_command(args: argparse.Namespace) -> int:
    root = work_units.repository_root(args.root)
    print(json.dumps({"artifacts": [asdict(item) for item in detect(root)]}, indent=2))
    return 0


def preview_command(args: argparse.Namespace) -> int:
    root = work_units.repository_root(args.root)
    framework, source = resolve_source(args, root)
    print(json.dumps(preview(root, framework, source, args.include_complete), indent=2))
    return 0


def import_command(args: argparse.Namespace) -> int:
    if not args.accepted:
        raise ValueError("import requires --accepted to confirm the source artifact was reviewed and accepted")
    root = work_units.repository_root(args.root)
    framework, source = resolve_source(args, root)
    plan = preview(root, framework, source, args.include_complete)
    created = import_preview(root, plan, args.owner, args.activate_first)
    print(json.dumps({"created": [unit["id"] for unit in created], "source": plan["source"]}, indent=2))
    return 0


def add_source_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("source")
    parser.add_argument("--framework", choices=FRAMEWORKS)
    parser.add_argument("--include-complete", action="store_true")
    parser.add_argument("--root", default=".")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="action", required=True)
    detected = subparsers.add_parser("detect")
    detected.add_argument("--root", default=".")
    detected.set_defaults(handler=detect_command)
    shown = subparsers.add_parser("preview")
    add_source_arguments(shown)
    shown.set_defaults(handler=preview_command)
    imported = subparsers.add_parser("import")
    add_source_arguments(imported)
    imported.add_argument("--accepted", action="store_true")
    imported.add_argument("--owner")
    imported.add_argument("--activate-first", action="store_true")
    imported.set_defaults(handler=import_command)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return args.handler(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
