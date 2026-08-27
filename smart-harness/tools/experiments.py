#!/usr/bin/env python3
"""Record and compare model-profile experiment evidence as append-only JSONL."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Iterable
import uuid


ROLES = ("coordinator", "normal", "deep", "fast", "top")
WORKFLOWS = ("dev", "review_pr")
PLATFORMS = ("copilot", "claude_code", "pi")
STATUSES = ("pass", "fail", "blocked", "unknown")
VERIFICATIONS = ("pass", "fail", "not_run", "unknown")
METRICS = (
    "duration_seconds", "input_tokens", "output_tokens", "cost_usd",
    "complexity_delta", "review_defects", "rework_count",
)


def git_root(start: Path) -> Path | None:
    completed = subprocess.run(
        ["git", "-C", str(start.resolve()), "rev-parse", "--show-toplevel"],
        text=True,
        capture_output=True,
        check=False,
    )
    return Path(completed.stdout.strip()).resolve() if completed.returncode == 0 else None


def default_log_path(cwd: Path) -> Path:
    root = git_root(cwd)
    return (root or cwd.resolve()) / ".agent-state/model-experiments.jsonl"


def default_model_config(cwd: Path) -> Path:
    root = git_root(cwd)
    installed = (root or cwd.resolve()) / ".smart-harness/config/models.json"
    source = Path(__file__).resolve().parents[1] / "config/models.json"
    return installed if installed.exists() else source


def read_profile(path: Path, requested: str | None, platform: str, role: str, workflow: str) -> tuple[str | None, dict[str, Any]]:
    if not path.exists():
        return requested, {}
    data, profiles = load_profiles(path)
    profile_name, profile = select_profile(path, data, profiles, requested)
    platform_config = profile.get(platform)
    if not isinstance(platform_config, dict):
        raise ValueError(f"{path}: profile {profile_name!r} lacks platform {platform!r}")
    group, key = ("workflows", workflow) if role == "coordinator" else ("roles", role)
    spec = platform_config.get(group, {}).get(key)
    if not isinstance(spec, dict):
        raise ValueError(f"{path}: profile {profile_name!r} lacks {platform}.{group}.{key}")
    return profile_name, spec


def load_profiles(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    profiles = data.get("profiles") if isinstance(data, dict) else None
    if not isinstance(data, dict) or data.get("schema_version") != 2 or not isinstance(profiles, dict):
        raise ValueError(f"{path}: expected model-profile schema version 2")
    return data, profiles


def select_profile(path: Path, data: dict[str, Any], profiles: dict[str, Any], requested: str | None) -> tuple[str, dict[str, Any]]:
    profile_name = requested or data.get("active_profile")
    profile = profiles.get(profile_name) if isinstance(profile_name, str) else None
    if not isinstance(profile, dict):
        raise ValueError(f"{path}: unknown model profile {profile_name!r}")
    return profile_name, profile


def resolve_metadata(args: argparse.Namespace) -> dict[str, Any]:
    cwd = Path(args.cwd).resolve()
    config = Path(args.config).resolve() if args.config else default_model_config(cwd)
    profile, spec = read_profile(config, args.profile, args.platform, args.role, args.workflow)
    return {
        "workflow": args.workflow,
        "role": args.role,
        "platform": args.platform,
        "profile": profile,
        "model": args.model if args.model is not None else spec.get("model"),
        "reasoning": args.reasoning if args.reasoning is not None else spec.get("reasoning"),
    }


def require_non_negative(name: str, value: int | float | None) -> None:
    if value is not None and value < 0:
        raise ValueError(f"{name} cannot be negative")


def make_record(metadata: dict[str, Any], **evidence: Any) -> dict[str, Any]:
    numeric_fields = (
        "duration_seconds", "input_tokens", "output_tokens", "cost_usd",
        "complexity_before", "complexity_after", "review_defects", "rework_count",
    )
    for name in numeric_fields:
        require_non_negative(name, evidence.get(name))
    before, after = evidence.get("complexity_before"), evidence.get("complexity_after")
    delta = after - before if before is not None and after is not None else None
    return {
        "schema_version": 1,
        "id": str(uuid.uuid4()),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        **metadata,
        "status": evidence.get("status", "unknown"),
        "verification": evidence.get("verification", "unknown"),
        "duration_seconds": evidence.get("duration_seconds"),
        "input_tokens": evidence.get("input_tokens"),
        "output_tokens": evidence.get("output_tokens"),
        "cost_usd": evidence.get("cost_usd"),
        "complexity_before": before,
        "complexity_after": after,
        "complexity_delta": delta,
        "review_defects": evidence.get("review_defects"),
        "rework_count": evidence.get("rework_count"),
        "notes": evidence.get("notes"),
        "source": evidence.get("source", "manual"),
    }


def append_records(path: Path, records: Iterable[dict[str, Any]]) -> None:
    payload = "".join(json.dumps(record, sort_keys=True) + "\n" for record in records).encode("utf-8")
    if not payload:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        write_all(descriptor, payload)
    finally:
        os.close(descriptor)


def write_all(descriptor: int, payload: bytes) -> None:
    offset = 0
    while offset < len(payload):
        offset += os.write(descriptor, payload[offset:])


def load_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        record = json.loads(line)
        if not isinstance(record, dict) or record.get("schema_version") != 1:
            raise ValueError(f"{path}:{line_number}: expected an experiment schema_version 1 object")
        records.append(record)
    return records


def average(records: list[dict[str, Any]], field: str) -> dict[str, int | float | None]:
    values = [float(record[field]) for record in records if isinstance(record.get(field), (int, float))]
    return {"reported": len(values), "average": round(sum(values) / len(values), 4) if values else None}


def rate(records: list[dict[str, Any]], field: str, success: str, excluded: set[object]) -> dict[str, int | float | None]:
    values = [record.get(field) for record in records if record.get(field) not in excluded]
    passed = sum(value == success for value in values)
    return {"reported": len(values), "rate": round(passed / len(values), 4) if values else None}


def summarize(records: list[dict[str, Any]], group_by: str) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        key = str(record.get(group_by) or "(unreported)")
        groups.setdefault(key, []).append(record)
    summaries = []
    for key, grouped in sorted(groups.items()):
        summaries.append({
            group_by: key,
            "runs": len(grouped),
            "outcome": rate(grouped, "status", "pass", {"unknown", None}),
            "verification": rate(grouped, "verification", "pass", {"unknown", "not_run", None}),
            "metrics": {field: average(grouped, field) for field in METRICS},
        })
    return summaries


def format_rate(value: float | None) -> str:
    return f"{value * 100:.1f}%" if value is not None else "n/a"


def render_comparison(summaries: list[dict[str, Any]], group_by: str) -> str:
    lines = []
    for summary in summaries:
        outcome = summary["outcome"]["rate"]
        verification = summary["verification"]["rate"]
        duration = summary["metrics"]["duration_seconds"]["average"]
        lines.append(
            f"{summary[group_by]}: runs={summary['runs']} outcome={format_rate(outcome)} "
            f"verification={format_rate(verification)} avg_duration={duration if duration is not None else 'n/a'}"
        )
    return "\n".join(lines) if lines else "No experiment records found."


def evidence_from_args(args: argparse.Namespace, source: str = "manual") -> dict[str, Any]:
    return {
        "status": args.status,
        "verification": args.verification,
        "duration_seconds": args.duration_seconds,
        "input_tokens": args.input_tokens,
        "output_tokens": args.output_tokens,
        "cost_usd": args.cost_usd,
        "complexity_before": args.complexity_before,
        "complexity_after": args.complexity_after,
        "review_defects": args.review_defects,
        "rework_count": args.rework_count,
        "notes": args.notes,
        "source": source,
    }


def record_command(args: argparse.Namespace) -> int:
    record = make_record(resolve_metadata(args), **evidence_from_args(args))
    append_records(Path(args.log), [record])
    print(json.dumps(record, indent=2))
    return 0


def run_command(args: argparse.Namespace) -> int:
    command = args.command[1:] if args.command and args.command[0] == "--" else args.command
    if not command:
        raise ValueError("run requires a command after --")
    started = time.monotonic()
    completed = subprocess.run(command, cwd=Path(args.cwd).resolve(), check=False)
    args.status = "pass" if completed.returncode == 0 else "fail"
    args.duration_seconds = round(time.monotonic() - started, 6)
    record = make_record(resolve_metadata(args), **evidence_from_args(args, "command-wrapper"))
    append_records(Path(args.log), [record])
    print(f"experiment {record['id']} recorded in {args.log}", file=sys.stderr)
    return completed.returncode


def import_pi_command(args: argparse.Namespace) -> int:
    raw = Path(args.results).read_text(encoding="utf-8") if args.results != "-" else sys.stdin.read()
    results = json.loads(raw)
    if not isinstance(results, list):
        raise ValueError("Pi results must be a JSON array")
    records = [pi_record(args, item) for item in results]
    append_records(Path(args.log), records)
    print(json.dumps({"recorded": len(records), "log": args.log}, indent=2))
    return 0


def pi_record(args: argparse.Namespace, item: object) -> dict[str, Any]:
    if not isinstance(item, dict) or not isinstance(item.get("role"), str):
        raise ValueError("each Pi result requires an object with a role")
    metadata = {
        "workflow": args.workflow,
        "role": item["role"],
        "platform": "pi",
        "profile": args.profile,
        "model": item.get("model"),
        "reasoning": item.get("thinking"),
    }
    passed = not item.get("timed_out") and item.get("returncode") == 0
    return make_record(
        metadata,
        status="pass" if passed else "fail",
        verification="unknown",
        duration_seconds=item.get("duration_seconds"),
        notes=f"Pi child task: {item.get('name', '(unnamed)')}",
        source="parallel-pi",
    )


def compare_command(args: argparse.Namespace) -> int:
    summaries = summarize(load_records(Path(args.log)), args.group_by)
    payload = {"group_by": args.group_by, "groups": summaries}
    print(json.dumps(payload, indent=2) if args.format == "json" else render_comparison(summaries, args.group_by))
    return 0


def list_command(args: argparse.Namespace) -> int:
    records = load_records(Path(args.log))[-args.limit:]
    print(json.dumps({"records": records}, indent=2))
    return 0


def add_metadata_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workflow", choices=WORKFLOWS, required=True)
    parser.add_argument("--role", choices=ROLES, required=True)
    parser.add_argument("--platform", choices=PLATFORMS, required=True)
    parser.add_argument("--profile")
    parser.add_argument("--model")
    parser.add_argument("--reasoning")
    parser.add_argument("--config", help="model profile config; defaults to the installed config")
    parser.add_argument("--cwd", default=".")


def add_evidence_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--status", choices=STATUSES, default="unknown")
    parser.add_argument("--verification", choices=VERIFICATIONS, default="unknown")
    parser.add_argument("--duration-seconds", type=float)
    parser.add_argument("--input-tokens", type=int)
    parser.add_argument("--output-tokens", type=int)
    parser.add_argument("--cost-usd", type=float)
    parser.add_argument("--complexity-before", type=int)
    parser.add_argument("--complexity-after", type=int)
    parser.add_argument("--review-defects", type=int)
    parser.add_argument("--rework-count", type=int)
    parser.add_argument("--notes")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", help="JSONL path; defaults to .agent-state/model-experiments.jsonl")
    subparsers = parser.add_subparsers(dest="action", required=True)
    record = subparsers.add_parser("record")
    add_metadata_arguments(record)
    add_evidence_arguments(record)
    record.set_defaults(handler=record_command)
    run = subparsers.add_parser("run")
    add_metadata_arguments(run)
    add_evidence_arguments(run)
    run.add_argument("command", nargs=argparse.REMAINDER)
    run.set_defaults(handler=run_command)
    imported = subparsers.add_parser("import-pi")
    imported.add_argument("results", help="parallel-pi JSON results file, or - for stdin")
    imported.add_argument("--workflow", choices=WORKFLOWS, required=True)
    imported.add_argument("--profile")
    imported.set_defaults(handler=import_pi_command)
    compare = subparsers.add_parser("compare")
    compare.add_argument("--group-by", choices=("profile", "model", "reasoning", "role", "workflow", "platform"), default="profile")
    compare.add_argument("--format", choices=("text", "json"), default="text")
    compare.set_defaults(handler=compare_command)
    listed = subparsers.add_parser("list")
    listed.add_argument("--limit", type=int, default=20)
    listed.set_defaults(handler=list_command)
    args = parser.parse_args()
    args.log = args.log or str(default_log_path(Path(getattr(args, "cwd", "."))))
    return args


def main() -> int:
    args = parse_args()
    return args.handler(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
