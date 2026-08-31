#!/usr/bin/env python3
"""Manage optional resumable WYSIWYShip work-unit lifecycle state."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any

import routing


STAGES = ("plan", "implement", "document", "simplify", "verify", "complete")
UNIT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,79}$")
DOC_IMPACTS = ("required", "generated", "none")
PLANNING_MODES = ("interactive", "auto", "imported")
PLANNING_GATES = ("pass", "user-override")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def repository_root(start: str) -> Path:
    completed = subprocess.run(
        ["git", "-C", str(Path(start).resolve()), "rev-parse", "--show-toplevel"],
        text=True, capture_output=True, check=False,
    )
    if completed.returncode != 0:
        raise ValueError(completed.stderr.strip() or f"not a Git repository: {start}")
    return Path(completed.stdout.strip()).resolve()


def state_root(root: Path) -> Path:
    return root / ".agent-state/work-units"


def unit_path(root: Path, unit_id: str) -> Path:
    if not UNIT_ID_RE.fullmatch(unit_id):
        raise ValueError("work-unit id must use 1-80 lowercase letters, digits, dots, underscores, or hyphens")
    return state_root(root) / f"{unit_id}.json"


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def load_unit(root: Path, unit_id: str) -> dict[str, Any]:
    path = unit_path(root, unit_id)
    if not path.exists():
        raise ValueError(f"unknown work unit {unit_id!r}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def load_all(root: Path) -> list[dict[str, Any]]:
    directory = state_root(root)
    if not directory.exists():
        return []
    units = []
    for path in sorted(directory.glob("*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError(f"{path}: expected a JSON object")
        units.append(value)
    return units


def new_unit(args: argparse.Namespace) -> dict[str, Any]:
    timestamp = now()
    return {
        "schema_version": 2,
        "id": args.unit_id,
        "title": args.title,
        "goal": args.goal,
        "acceptance_criteria": args.acceptance,
        "dependencies": args.depends_on,
        "owners": args.owner,
        "owned_paths": args.owns,
        "base_ref": args.base_ref,
        "stage": "plan",
        "planning": {
            "mode": args.planning_mode,
            "gate": args.planning_gate,
            "iterations": args.planning_iterations,
            "locked_at": timestamp,
            "decisions": args.decision,
            "in_scope": args.in_scope,
            "out_of_scope": args.out_of_scope,
            "assumptions": args.assumption,
            "open_questions": args.open_question,
            "ambiguity_assessment": args.ambiguity,
        },
        "evidence": {stage: [] for stage in STAGES[:-1]},
        "documentation": {"impact": args.docs_impact, "paths": args.doc_path, "reason": args.docs_reason},
        "verification": [],
        "source": {"framework": args.source_framework, "path": args.source_path},
        "commit_sha": None,
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def validation_errors(unit: dict[str, Any]) -> list[str]:
    errors = []
    required_strings = ("id", "title", "goal", "base_ref", "stage")
    errors.extend(f"missing non-empty {field}" for field in required_strings if not isinstance(unit.get(field), str) or not unit[field])
    if unit.get("schema_version") not in {1, 2}:
        errors.append("unsupported schema_version")
    if unit.get("schema_version") == 2:
        errors.extend(planning_errors(unit.get("planning")))
    if unit.get("stage") not in STAGES:
        errors.append(f"invalid stage {unit.get('stage')!r}")
    for field in ("acceptance_criteria", "dependencies", "owners", "owned_paths", "verification"):
        if not isinstance(unit.get(field), list):
            errors.append(f"{field} must be an array")
    errors.extend(documentation_errors(unit.get("documentation")))
    if not isinstance(unit.get("evidence"), dict):
        errors.append("evidence must be an object")
    if "routing" in unit:
        errors.extend(routing.bundle_errors(unit["routing"], started=unit.get("stage") != "plan",
                                            complete=unit.get("stage") == "complete"))
    return errors


def planning_errors(planning: object) -> list[str]:
    if not isinstance(planning, dict):
        return ["planning must be an object"]
    errors = []
    errors.extend(enum_errors(planning, "mode", PLANNING_MODES))
    errors.extend(enum_errors(planning, "gate", PLANNING_GATES))
    errors.extend(positive_integer_errors(planning, "iterations"))
    errors.extend(non_empty_string_errors(planning, "locked_at"))
    fields = ("decisions", "in_scope", "out_of_scope", "assumptions", "open_questions", "ambiguity_assessment")
    for field in fields:
        errors.extend(string_array_errors(planning, field))
    if isinstance(planning.get("decisions"), list) and not planning["decisions"]:
        errors.append("planning.decisions must record at least one key decision")
    return errors


def enum_errors(value: dict[str, Any], field: str, choices: tuple[str, ...]) -> list[str]:
    observed = value.get(field)
    return [] if observed in choices else [f"invalid planning {field} {observed!r}"]


def positive_integer_errors(value: dict[str, Any], field: str) -> list[str]:
    observed = value.get(field)
    return [] if isinstance(observed, int) and observed >= 1 else [f"planning.{field} must be a positive integer"]


def non_empty_string_errors(value: dict[str, Any], field: str) -> list[str]:
    observed = value.get(field)
    return [] if isinstance(observed, str) and observed else [f"planning.{field} must be a non-empty string"]


def string_array_errors(value: dict[str, Any], field: str) -> list[str]:
    observed = value.get(field)
    valid = isinstance(observed, list) and all(isinstance(item, str) and item.strip() for item in observed)
    return [] if valid else [f"planning.{field} must be an array of non-empty strings"]


def documentation_errors(documentation: object) -> list[str]:
    if not isinstance(documentation, dict):
        return ["documentation must be an object"]
    impact = documentation.get("impact")
    if impact not in DOC_IMPACTS:
        return [f"invalid documentation impact {impact!r}"]
    if impact in {"required", "generated"} and not documentation.get("paths"):
        return [f"documentation paths are required when impact is {impact}"]
    if impact == "none" and not documentation.get("reason"):
        return ["documentation reason is required when impact is none"]
    return []


def validate_all(root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    units = load_all(root)
    errors = []
    ids = {unit.get("id") for unit in units}
    for unit in units:
        errors.extend(f"{unit.get('id', '(unknown)')}: {error}" for error in validation_errors(unit))
        missing = [item for item in unit.get("dependencies", []) if item not in ids]
        errors.extend(f"{unit.get('id')}: missing dependency {item}" for item in missing)
    errors.extend(ownership_errors(units))
    return units, errors


def ownership_errors(units: list[dict[str, Any]]) -> list[str]:
    active = [unit for unit in units if unit.get("stage") not in {"plan", "complete"}]
    errors = []
    for index, left in enumerate(active):
        for right in active[index + 1:]:
            overlap = sorted(set(left.get("owned_paths", [])) & set(right.get("owned_paths", [])))
            if overlap:
                errors.append(f"ownership overlap: {left.get('id')} and {right.get('id')} both own {overlap}")
    return errors


def dependencies_complete(root: Path, unit: dict[str, Any]) -> list[str]:
    incomplete = []
    for dependency in unit.get("dependencies", []):
        if load_unit(root, dependency).get("stage") != "complete":
            incomplete.append(dependency)
    return incomplete


def active_pointer(root: Path) -> Path:
    return root / ".agent-state/active-work-unit"


def activate(root: Path, unit_id: str) -> None:
    load_unit(root, unit_id)
    path = active_pointer(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(unit_id + "\n", encoding="utf-8")


def active_unit(root: Path) -> dict[str, Any]:
    path = active_pointer(root)
    if not path.exists() or not path.read_text(encoding="utf-8").strip():
        raise ValueError("no active work unit; initialize or activate one first")
    return load_unit(root, path.read_text(encoding="utf-8").strip())


def initialize_command(args: argparse.Namespace) -> int:
    root = repository_root(args.root)
    path = unit_path(root, args.unit_id)
    if path.exists():
        raise ValueError(f"work unit {args.unit_id!r} already exists")
    args.base_ref = resolve_ref(root, args.base_ref)
    unit = new_unit(args)
    if getattr(args, "routing_plan", None):
        unit["routing"] = {"plan": routing.read_object(Path(args.routing_plan))}
        if unit["routing"]["plan"].get("task") != args.unit_id:
            raise ValueError("routing task must match the work-unit ID")
    errors = validation_errors(unit)
    if errors:
        raise ValueError("; ".join(errors))
    atomic_json(path, unit)
    if args.activate:
        activate(root, args.unit_id)
    print(json.dumps(unit, indent=2))
    return 0


def advance_command(args: argparse.Namespace) -> int:
    root = repository_root(args.root)
    unit = load_unit(root, args.unit_id)
    stage = unit.get("stage")
    if stage == "complete":
        raise ValueError(f"work unit {args.unit_id!r} is already complete")
    if getattr(args, "routing_receipt", None):
        if "routing" not in unit:
            raise ValueError("unit has no locked routing plan")
        unit["routing"]["receipt"] = routing.read_object(Path(args.routing_receipt))
    if "routing" in unit:
        errors = routing.bundle_errors(unit["routing"], started=True, complete=stage == "verify")
        if errors:
            raise ValueError("routing gate failed: " + "; ".join(errors))
    if stage == "plan":
        ensure_ready_to_implement(root, unit)
    if stage == "document":
        errors = documentation_errors(unit.get("documentation"))
        if errors:
            raise ValueError("; ".join(errors))
    unit["evidence"][stage].append(args.evidence)
    if stage == "verify":
        unit["verification"].append(args.evidence)
        unit["commit_sha"] = args.commit or git_head(root)
    unit["stage"] = STAGES[STAGES.index(stage) + 1]
    unit["updated_at"] = now()
    atomic_json(unit_path(root, args.unit_id), unit)
    print(json.dumps(unit, indent=2))
    return 0


def route_command(args: argparse.Namespace) -> int:
    """Attach a route to an imported plan or record an accepted routing-only change."""
    if not routing.has_text(args.reason):
        raise ValueError("rerouting requires a non-empty accepted decision reason")
    root = repository_root(args.root)
    unit = load_unit(root, args.unit_id)
    if unit.get("stage") == "complete":
        raise ValueError("cannot reroute a completed unit")
    plan = routing.read_object(Path(args.routing_plan))
    errors = routing.plan_errors(plan)
    if plan.get("task") != args.unit_id:
        errors.append("routing task must match the work-unit ID")
    previous = unit.get("routing")
    if previous and previous["plan"]["route_id"] == plan.get("route_id"):
        errors.append("rerouting requires a new route ID")
    if errors:
        raise ValueError("; ".join(errors))
    unit.setdefault("routing_history", []).append({"reason": args.reason, "previous": previous, "at": now()})
    unit["routing"] = {"plan": plan}
    unit["updated_at"] = now()
    atomic_json(unit_path(root, args.unit_id), unit)
    print(json.dumps(unit, indent=2))
    return 0


def ensure_ready_to_implement(root: Path, unit: dict[str, Any]) -> None:
    incomplete = dependencies_complete(root, unit)
    if incomplete:
        raise ValueError(f"dependencies are incomplete: {', '.join(incomplete)}")
    units, errors = validate_all(root)
    candidate = dict(unit)
    candidate["stage"] = "implement"
    others = [item for item in units if item.get("id") != unit.get("id")]
    errors.extend(ownership_errors([*others, candidate]))
    if errors:
        raise ValueError("ledger is invalid: " + "; ".join(errors))


def git_head(root: Path) -> str:
    completed = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise ValueError(completed.stderr.strip() or "could not resolve HEAD")
    return completed.stdout.strip()


def resolve_ref(root: Path, ref: str) -> str:
    completed = subprocess.run(["git", "rev-parse", "--verify", ref], cwd=root, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise ValueError(completed.stderr.strip() or f"could not resolve ref {ref!r}")
    return completed.stdout.strip()


def close_command(args: argparse.Namespace) -> int:
    root = repository_root(args.root)
    unit = active_unit(root) if args.unit_id is None else load_unit(root, args.unit_id)
    if unit.get("stage") != "complete":
        raise ValueError(f"work unit {unit.get('id')!r} cannot close at stage {unit.get('stage')!r}")
    errors = validation_errors(unit)
    if errors:
        raise ValueError("; ".join(errors))
    pointer = active_pointer(root)
    if pointer.exists() and pointer.read_text(encoding="utf-8").strip() == unit.get("id"):
        pointer.unlink()
    print(f"closed work unit: {unit.get('id')}")
    return 0


def show_command(args: argparse.Namespace) -> int:
    root = repository_root(args.root)
    unit = active_unit(root) if args.unit_id is None else load_unit(root, args.unit_id)
    print(json.dumps(unit, indent=2))
    return 0


def list_command(args: argparse.Namespace) -> int:
    units, errors = validate_all(repository_root(args.root))
    selected = [unit for unit in units if args.stage is None or unit.get("stage") == args.stage]
    print(json.dumps({"work_units": selected, "errors": errors}, indent=2))
    return 1 if errors else 0


def ready_command(args: argparse.Namespace) -> int:
    root = repository_root(args.root)
    units, errors = validate_all(root)
    if errors:
        print(json.dumps({"ready": [], "errors": errors}, indent=2))
        return 1
    ready = [unit for unit in units if unit.get("stage") == "plan" and not dependencies_complete(root, unit)]
    print(json.dumps({"ready": ready, "errors": []}, indent=2))
    return 0


def validate_command(args: argparse.Namespace) -> int:
    units, errors = validate_all(repository_root(args.root))
    print(json.dumps({"valid": not errors, "count": len(units), "errors": errors}, indent=2))
    return 1 if errors else 0


def activate_command(args: argparse.Namespace) -> int:
    root = repository_root(args.root)
    activate(root, args.unit_id)
    print(f"active work unit: {args.unit_id}")
    return 0


def add_root(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--root", default=".")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="action", required=True)
    initialized = subparsers.add_parser("init")
    initialized.add_argument("unit_id")
    initialized.add_argument("--title", required=True)
    initialized.add_argument("--goal", required=True)
    initialized.add_argument("--acceptance", action="append", required=True)
    initialized.add_argument("--depends-on", action="append", default=[])
    initialized.add_argument("--owner", action="append", default=[])
    initialized.add_argument("--owns", action="append", default=[])
    initialized.add_argument("--base-ref", default="HEAD")
    initialized.add_argument("--planning-mode", choices=PLANNING_MODES, required=True)
    initialized.add_argument("--planning-gate", choices=PLANNING_GATES, required=True)
    initialized.add_argument("--planning-iterations", type=int, default=1)
    initialized.add_argument("--decision", action="append", required=True)
    initialized.add_argument("--in-scope", action="append", default=[])
    initialized.add_argument("--out-of-scope", action="append", default=[])
    initialized.add_argument("--assumption", action="append", default=[])
    initialized.add_argument("--open-question", action="append", default=[])
    initialized.add_argument("--ambiguity", action="append", default=[])
    initialized.add_argument("--docs-impact", choices=DOC_IMPACTS, required=True)
    initialized.add_argument("--doc-path", action="append", default=[])
    initialized.add_argument("--docs-reason")
    initialized.add_argument("--source-framework")
    initialized.add_argument("--source-path")
    initialized.add_argument("--activate", action="store_true")
    initialized.add_argument("--routing-plan", help="freeze routing.py plan JSON into this unit")
    add_root(initialized)
    initialized.set_defaults(handler=initialize_command)
    advanced = subparsers.add_parser("advance")
    advanced.add_argument("unit_id")
    advanced.add_argument("--evidence", required=True)
    advanced.add_argument("--commit")
    advanced.add_argument("--routing-receipt", help="attach invocation evidence before advancing")
    add_root(advanced)
    advanced.set_defaults(handler=advance_command)
    routed = subparsers.add_parser("route", help="attach or replace a route after accepting a routing-only decision")
    routed.add_argument("unit_id")
    routed.add_argument("--routing-plan", required=True)
    routed.add_argument("--reason", required=True, help="accepted routing decision; does not grant execution permissions")
    add_root(routed)
    routed.set_defaults(handler=route_command)
    shown = subparsers.add_parser("show")
    shown.add_argument("unit_id", nargs="?")
    add_root(shown)
    shown.set_defaults(handler=show_command)
    listed = subparsers.add_parser("list")
    listed.add_argument("--stage", choices=STAGES)
    add_root(listed)
    listed.set_defaults(handler=list_command)
    ready = subparsers.add_parser("ready")
    add_root(ready)
    ready.set_defaults(handler=ready_command)
    validated = subparsers.add_parser("validate")
    add_root(validated)
    validated.set_defaults(handler=validate_command)
    activated = subparsers.add_parser("activate")
    activated.add_argument("unit_id")
    add_root(activated)
    activated.set_defaults(handler=activate_command)
    closed = subparsers.add_parser("close")
    closed.add_argument("unit_id", nargs="?")
    add_root(closed)
    closed.set_defaults(handler=close_command)
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
