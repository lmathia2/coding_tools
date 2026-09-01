#!/usr/bin/env python3
"""Maintain a generated developer wiki on a simple commit cadence."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
from typing import Any


SCHEMA_VERSION = 1
WIKI_ROOT = Path("docs/wiki")
MANIFEST_PATH = WIKI_ROOT / "manifest.json"
INSTRUCTIONS_PATH = WIKI_ROOT / "INSTRUCTIONS.md"
REFRESH_PATH = WIKI_ROOT / ".refresh.json"
DEFAULT_PAGES = (
    ("quickstart.md", "How to install, invoke, and verify the project"),
    ("architecture.md", "Core components, ownership, and runtime flow"),
    ("development-lifecycle.md", "How a change moves from plan to verified result"),
    ("host-adapters.md", "Host integrations, capabilities, and limits"),
)
PLACEHOLDER = "<!-- wysiwyship:placeholder -->"


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def repository_root(start: str | None) -> Path:
    requested = Path(start or ".").resolve()
    completed = subprocess.run(
        ["git", "-C", str(requested), "rev-parse", "--show-toplevel"],
        text=True, capture_output=True, check=False,
    )
    if completed.returncode:
        raise ValueError(completed.stderr.strip() or f"not a Git repository: {requested}")
    return Path(completed.stdout.strip()).resolve()


def manifest_template() -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "pages": [
            {"path": str(WIKI_ROOT / name), "purpose": purpose}
            for name, purpose in DEFAULT_PAGES
        ],
    }


def page_template(name: str, purpose: str) -> str:
    title = Path(name).stem.replace("-", " ").title()
    return f"# {title}\n\n{PLACEHOLDER}\n\n{purpose}. Replace this page during the first full refresh.\n"


def starter_files(root: Path) -> dict[str, str]:
    files = {
        str(MANIFEST_PATH): json.dumps(manifest_template(), indent=2) + "\n",
        str(INSTRUCTIONS_PATH): (
            "# Wiki instructions\n\n"
            "Generated developer guide. Rebuild every manifest page when the configured commit cadence is due.\n"
        ),
        str(REFRESH_PATH): json.dumps({"schema_version": 1, "generation": 0, "source_head": None}, indent=2) + "\n",
    }
    for name, purpose in DEFAULT_PAGES:
        relative = str(WIKI_ROOT / name)
        if not (root / relative).exists():
            files[relative] = page_template(name, purpose)
    return files


def initialize(root: Path, dry_run: bool = False) -> dict[str, object]:
    created, preserved = [], []
    for relative, text in starter_files(root).items():
        path = root / relative
        if path.exists():
            preserved.append(relative)
        else:
            if not dry_run:
                atomic_write(path, text)
            created.append(relative)
    return {"status": "PASS", "created": created, "preserved": preserved, "dry_run": dry_run}


def read_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return data


def page_path(root: Path, raw: object) -> Path:
    if not isinstance(raw, str):
        raise ValueError("wiki page path must be a string")
    relative = PurePosixPath(raw)
    if relative.is_absolute() or ".." in relative.parts or not raw.startswith("docs/wiki/") or not raw.endswith(".md"):
        raise ValueError(f"invalid wiki page path: {raw}")
    path = (root / raw).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"wiki page escapes repository root: {raw}") from exc
    return path


def manifest(root: Path) -> dict[str, Any]:
    path = root / MANIFEST_PATH
    if not path.exists():
        raise ValueError(f"{MANIFEST_PATH} is missing; run wiki.py init")
    data = read_object(path)
    pages = data.get("pages")
    if data.get("schema_version") != SCHEMA_VERSION or not isinstance(pages, list) or not pages:
        raise ValueError(f"{MANIFEST_PATH}: expected schema_version 1 and a non-empty pages array")
    seen = set()
    for item in pages:
        if not isinstance(item, dict) or not isinstance(item.get("purpose"), str) or not item["purpose"].strip():
            raise ValueError(f"{MANIFEST_PATH}: every page requires path and purpose")
        raw = item.get("path")
        page_path(root, raw)
        if raw in seen:
            raise ValueError(f"{MANIFEST_PATH}: duplicate page {raw}")
        seen.add(raw)
    return data


def verify(root: Path) -> dict[str, object]:
    try:
        pages = []
        for item in manifest(root)["pages"]:
            path = page_path(root, item["path"])
            status = "PASS" if path.is_file() and path.read_text(encoding="utf-8").strip() else "FAIL"
            pages.append({"page": item["path"], "status": status})
        failures = [item for item in pages if item["status"] == "FAIL"]
        return {
            "status": "FAIL" if failures else "PASS",
            "summary": f"{len(pages) - len(failures)}/{len(pages)} wiki pages present",
            "pages": pages,
        }
    except (json.JSONDecodeError, OSError, UnicodeDecodeError, ValueError) as exc:
        return {"status": "ERROR", "summary": str(exc), "pages": []}


def read_refresh_marker(root: Path) -> dict[str, Any]:
    path = root / REFRESH_PATH
    if not path.exists():
        raise ValueError(f"{REFRESH_PATH} is missing; run wiki.py init")
    marker = read_object(path)
    generation = marker.get("generation")
    if marker.get("schema_version") != SCHEMA_VERSION or not isinstance(generation, int) or generation < 0:
        raise ValueError(f"{REFRESH_PATH}: invalid refresh marker")
    return marker


def git(root: Path, *args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
    if completed.returncode:
        raise ValueError(completed.stderr.strip() or f"git {' '.join(args)} failed")
    return completed.stdout.strip()


def cadence_check(root: Path, head: str, every: int) -> dict[str, object]:
    if not isinstance(every, int) or every < 1:
        raise ValueError("wiki.refresh_every_commits must be a positive integer")
    checked = verify(root)
    if checked["status"] != "PASS":
        return checked
    marker = read_refresh_marker(root)
    refresh_commit = git(root, "log", "-1", "--format=%H", head, "--", str(REFRESH_PATH))
    baseline = refresh_commit or marker.get("source_head")
    if marker["generation"] == 0 or not baseline:
        return {"status": "FAIL", "summary": "full wiki refresh is due", "pages": checked["pages"]}
    elapsed = int(git(root, "rev-list", "--count", f"{baseline}..{head}"))
    due = elapsed >= every
    return {
        "status": "FAIL" if due else "PASS",
        "summary": f"full wiki refresh is due after {elapsed} commit(s)" if due else f"wiki refresh current: {elapsed}/{every} commits",
        "last_refresh_commit": baseline,
        "commits_since_refresh": elapsed,
        "refresh_every_commits": every,
        "generation": marker["generation"],
        "pages": checked["pages"],
    }


def mark_refreshed(root: Path) -> dict[str, object]:
    checked = verify(root)
    if checked["status"] != "PASS":
        raise ValueError(str(checked["summary"]))
    placeholders = [
        item["page"] for item in checked["pages"]
        if PLACEHOLDER in page_path(root, item["page"]).read_text(encoding="utf-8")
    ]
    if placeholders:
        raise ValueError(f"replace every placeholder page before marking refresh: {', '.join(placeholders)}")
    generation = read_refresh_marker(root)["generation"] + 1
    try:
        source_head = git(root, "rev-parse", "HEAD")
    except ValueError:
        source_head = None
    marker = {"schema_version": 1, "generation": generation, "source_head": source_head}
    atomic_write(root / REFRESH_PATH, json.dumps(marker, indent=2) + "\n")
    return {"status": "PASS", "summary": f"recorded wiki generation {generation}", **marker}


def render(payload: dict[str, object], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(payload, indent=2)
    return f"{payload['status']}: {payload.get('summary', 'wiki')}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="repository root or a path inside it")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init")
    commands.add_parser("verify")
    due = commands.add_parser("due")
    due.add_argument("--head", default="HEAD")
    due.add_argument("--every", type=int, default=5)
    commands.add_parser("mark-refreshed")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repository_root(args.root)
    if args.command == "init":
        payload = initialize(root)
    elif args.command == "verify":
        payload = verify(root)
    elif args.command == "due":
        payload = cadence_check(root, args.head, args.every)
    else:
        payload = mark_refreshed(root)
    print(render(payload, args.format))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (json.JSONDecodeError, OSError, UnicodeDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
