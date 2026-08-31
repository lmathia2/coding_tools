#!/usr/bin/env python3
"""Run the deterministic WYSIWYShip lifecycle gate for a Git range."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

import commit_docs
import complexity
import work_units
import routing


HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")
DEFAULT_CONFIG = {
    "schema_version": 1,
    "documentation": {"enabled": True},
    "complexity": {"enabled": True, "fail_above": 20},
    "commands": [],
    "repository": {"require_clean": False},
    "work_units": {"enabled": True, "require_complete": False},
}


def run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=root, text=True, capture_output=True, check=False
    )


def git_output(root: Path, *args: str) -> str:
    completed = run_git(root, *args)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or f"git {' '.join(args)} failed")
    return completed.stdout


def repository_root(start: str | None) -> Path:
    requested = Path(start or ".").resolve()
    completed = subprocess.run(
        ["git", "-C", str(requested), "rev-parse", "--show-toplevel"],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or f"not a Git repository: {requested}")
    return Path(completed.stdout.strip()).resolve()


def default_config_path(root: Path) -> Path:
    installed = root / ".wysiwyship/config/checks.json"
    source = Path(__file__).resolve().parents[1] / "config/checks.json"
    return installed if installed.exists() else source


def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return dict(DEFAULT_CONFIG)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError(f"{path}: expected a schema_version 1 JSON object")
    for key in ("documentation", "complexity", "repository", "work_units"):
        if key in data and not isinstance(data[key], dict):
            raise ValueError(f"{path}: {key} must be an object")
    commands = data.get("commands", [])
    if not isinstance(commands, list):
        raise ValueError(f"{path}: commands must be an array")
    for command in commands:
        validate_command(command, path)
    return data


def validate_command(command: object, path: Path) -> None:
    if not isinstance(command, dict):
        raise ValueError(f"{path}: every command must be an object")
    name = command.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError(f"{path}: every command requires a non-empty name")
    validate_command_argv(command.get("argv"), name, path)
    validate_command_options(command, name, path)


def validate_command_argv(argv: object, name: str, path: Path) -> None:
    if not isinstance(argv, list) or not argv or not all(isinstance(item, str) and item for item in argv):
        raise ValueError(f"{path}: command {name!r} requires a non-empty string argv array")


def validate_command_options(command: dict[str, Any], name: str, path: Path) -> None:
    if "cwd" in command and not isinstance(command["cwd"], str):
        raise ValueError(f"{path}: command {name!r} cwd must be a string")
    timeout = command.get("timeout_seconds", 600)
    if not isinstance(timeout, int) or timeout < 1:
        raise ValueError(f"{path}: command {name!r} timeout_seconds must be a positive integer")


def result(name: str, status: str, summary: str, details: object | None = None) -> dict[str, object]:
    item: dict[str, object] = {"name": name, "status": status, "summary": summary}
    if details is not None:
        item["details"] = details
    return item


def documentation_check(root: Path, base: str, head: str) -> dict[str, object]:
    commits = commit_docs.inspect_range(base, head, str(root))
    failures = [item for item in commits if item["status"] == "FAIL"]
    if failures:
        return result("documentation", "FAIL", f"{len(failures)} commit(s) lack documentation evidence", commits)
    return result("documentation", "PASS", f"{len(commits)} commit(s) satisfy the documentation policy", commits)


def changed_python_paths(root: Path, base: str, head: str) -> list[str]:
    output = git_output(root, "diff", "--name-only", "--diff-filter=ACMR", f"{base}..{head}", "--", "*.py")
    return [path for path in output.splitlines() if path and (root / path).is_file()]


def changed_ranges(root: Path, base: str, head: str, path: str) -> list[tuple[int, int]]:
    patch = git_output(root, "diff", "--unified=0", f"{base}..{head}", "--", path)
    ranges = []
    for line in patch.splitlines():
        match = HUNK_RE.match(line)
        if not match:
            continue
        start = int(match.group(1))
        count = int(match.group(2) or 1)
        if count:
            ranges.append((start, start + count - 1))
    return ranges


def intersects(function: dict[str, object], ranges: list[tuple[int, int]]) -> bool:
    start, end = int(function["line"]), int(function["end_line"])
    return any(start <= changed_end and end >= changed_start for changed_start, changed_end in ranges)


def analyze_changed_file(root: Path, base: str, head: str, path: str) -> dict[str, object]:
    absolute = root / path
    current = complexity.analyze_code(absolute.read_text(encoding="utf-8"), path)
    if "error" in current:
        return current
    baseline = run_git(root, "show", f"{base}:{path}")
    if baseline.returncode == 0:
        previous = complexity.analyze_code(baseline.stdout, path).get("functions", [])
        complexity.attach_baseline(current["functions"], previous)
    ranges = changed_ranges(root, base, head, path)
    current["functions"] = [item for item in current["functions"] if intersects(item, ranges)]
    return current


def complexity_check(root: Path, base: str, head: str, limit: int) -> dict[str, object]:
    paths = changed_python_paths(root, base, head)
    files = [analyze_changed_file(root, base, head, path) for path in paths]
    syntax_errors = [item for item in files if "error" in item]
    functions = [function for item in files for function in item.get("functions", [])]
    failures = [item for item in functions if int(item["complexity_score"]) > limit]
    if syntax_errors:
        return result("complexity", "ERROR", f"{len(syntax_errors)} changed file(s) could not be parsed", files)
    if failures:
        return result("complexity", "FAIL", f"{len(failures)} changed function(s) exceed {limit}", files)
    return result("complexity", "PASS", f"{len(functions)} changed function(s) are at or below {limit}", files)


def safe_command_cwd(root: Path, configured: str) -> Path:
    root = root.resolve()
    candidate = (root / configured).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"configured command cwd escapes repository root: {configured}") from exc
    if not candidate.is_dir():
        raise ValueError(f"configured command cwd is not a directory: {configured}")
    return candidate


def command_check(root: Path, command: dict[str, Any]) -> dict[str, object]:
    cwd = safe_command_cwd(root, command.get("cwd", "."))
    argv = command["argv"]
    try:
        completed = subprocess.run(
            argv,
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,
            timeout=command.get("timeout_seconds", 600),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return result(command["name"], "ERROR", str(exc), {"argv": argv, "cwd": str(cwd)})
    details = {
        "argv": argv,
        "cwd": str(cwd),
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
    status = "PASS" if completed.returncode == 0 else "FAIL"
    return result(command["name"], status, f"exit {completed.returncode}: {' '.join(argv)}", details)


def cleanliness_check(root: Path) -> dict[str, object]:
    changes = git_output(root, "status", "--porcelain=v1", "--untracked-files=all").splitlines()
    status = "PASS" if not changes else "FAIL"
    summary = "repository is clean" if not changes else f"repository has {len(changes)} uncommitted path(s)"
    return result("repository-clean", status, summary, changes)


def work_unit_check(root: Path, require_complete: bool) -> dict[str, object]:
    units, errors = work_units.validate_all(root)
    incomplete = [unit.get("id") for unit in units if unit.get("stage") != "complete"]
    if require_complete and incomplete:
        errors.append(f"incomplete work units: {', '.join(str(item) for item in incomplete)}")
    status = "FAIL" if errors else "PASS"
    summary = f"{len(units)} work unit(s) valid" if not errors else f"{len(errors)} work-unit error(s)"
    return result("work-units", status, summary, {"errors": errors, "work_units": units})


def run_checks(root: Path, base: str, head: str, config: dict[str, Any], require_clean: bool) -> list[dict[str, object]]:
    checks = []
    if config.get("documentation", {}).get("enabled", True):
        checks.append(documentation_check(root, base, head))
    if config.get("complexity", {}).get("enabled", True):
        limit = config.get("complexity", {}).get("fail_above", 20)
        if not isinstance(limit, int) or limit < 1:
            raise ValueError("complexity.fail_above must be a positive integer")
        checks.append(complexity_check(root, base, head, limit))
    checks.extend(command_check(root, command) for command in config.get("commands", []))
    configured_clean = config.get("repository", {}).get("require_clean", False)
    if require_clean or configured_clean:
        checks.append(cleanliness_check(root))
    unit_config = config.get("work_units", {})
    if unit_config.get("enabled", True):
        checks.append(work_unit_check(root, bool(unit_config.get("require_complete", False))))
    return checks


def render_text(checks: list[dict[str, object]]) -> str:
    lines = [f"{item['status']:5} {item['name']}: {item['summary']}" for item in checks]
    failures = sum(item["status"] in {"FAIL", "ERROR"} for item in checks)
    lines.append(f"RESULT {'FAIL' if failures else 'PASS'}: {len(checks) - failures}/{len(checks)} checks passed")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", nargs="?", help="exclusive base Git ref")
    parser.add_argument("--active", action="store_true", help="use the active work unit's immutable base ref")
    parser.add_argument("--head", default="HEAD", help="inclusive head Git ref")
    parser.add_argument("--root", help="repository path; defaults to the current repository")
    parser.add_argument("--config", help="checks JSON; defaults to the installed or source configuration")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--require-clean", action="store_true", help="also fail on uncommitted changes")
    parser.add_argument("--routing-plan", type=Path, help="also check this unit or review lane's dispatch plan")
    parser.add_argument("--routing-receipt", type=Path, help="invocation receipt paired with --routing-plan")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if bool(args.routing_plan) != bool(args.routing_receipt):
        raise ValueError("provide both --routing-plan and --routing-receipt")
    root = repository_root(args.root)
    config_path = Path(args.config).resolve() if args.config else default_config_path(root)
    config = load_config(config_path)
    base = resolve_base(args, root)
    checks = run_checks(root, base, args.head, config, args.require_clean)
    if args.routing_plan:
        dispatch = routing.check_route(routing.read_object(args.routing_plan), routing.read_object(args.routing_receipt))
        checks.append(result("routing", dispatch["status"],
                             f"receipt checked; effective model: {dispatch['model_status']}", dispatch))
    payload = {"base": base, "head": args.head, "root": str(root), "checks": checks}
    print(json.dumps(payload, indent=2) if args.format == "json" else render_text(checks))
    return 1 if any(item["status"] in {"FAIL", "ERROR"} for item in checks) else 0


def resolve_base(args: argparse.Namespace, root: Path) -> str:
    if args.active and args.base:
        raise ValueError("provide either base or --active, not both")
    if args.active:
        return str(work_units.active_unit(root)["base_ref"])
    if not args.base:
        raise ValueError("base is required unless --active is used")
    return args.base


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (json.JSONDecodeError, OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
