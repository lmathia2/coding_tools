#!/usr/bin/env python3
"""Resolve cross-host dispatch plans and check explicitly attributed receipts.

This checks evidence consistency, not its authenticity. It does not spawn agents
or prove an effective model from a prompt, agent name, or configured preference.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "config"))
from model_config import get_profile, load_config, resolve_spec


AGENTS = {
    "codex": {"normal": ("wysiwyship_worker",), "deep": ("wysiwyship_deep",),
              "fast": ("wysiwyship_fast",), "top": ("wysiwyship_reviewer",)},
    "claude_code": {"normal": ("smart-worker",), "deep": ("smart-deep-implementer", "smart-deep-reasoner"),
                    "fast": ("smart-fast",), "top": ("smart-top-reviewer",)},
    "copilot": {"normal": ("WorkerNormal",), "deep": ("WorkerDeep", "DeepReasoner"),
                "fast": ("FastLane",), "top": ("TopReviewer",)},
    "pi": {role: ("parallel-pi",) for role in ("normal", "deep", "fast", "top")},
}


def read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def has_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def default_config(root: Path) -> Path:
    installed = root / ".wysiwyship/config/models.json"
    return installed if installed.exists() else Path(__file__).resolve().parents[1] / "config/models.json"


def agent_name(host: str, role: str, workflow: str, selected: str | None, namespace: str) -> str:
    choices = AGENTS[host][role]
    default = choices[-1] if workflow == "review_pr" else choices[0]
    name = selected or default
    if name not in choices:
        raise ValueError(f"agent {name!r} does not implement {host}.{role}: choose {choices}")
    return f"{namespace}:{name}" if namespace else name


def resolve_route(config: Path, host: str, workflow: str, role: str, task: str,
                  execution: str = "delegated", reason: str = "", profile: str | None = None,
                  agent: str | None = None, namespace: str = "", require_confirmed: bool = False) -> dict[str, Any]:
    host = "claude_code" if host == "claude" else host
    if host not in AGENTS or workflow not in {"dev", "review_pr"}:
        raise ValueError("unknown host or workflow")
    if role not in AGENTS[host] or execution not in {"delegated", "inline"}:
        raise ValueError("unknown role or execution mode")
    if not has_text(task) or (execution == "inline" and not has_text(reason)):
        raise ValueError("task is required; inline execution also requires a reason")
    name, settings = get_profile(load_config(config), profile)
    spec = resolve_spec(settings, host, role)
    requested = {"model": spec["model"], "reasoning": spec["reasoning"]}
    if execution == "inline":
        requested = {"model": None, "reasoning": None}
    return {
        "schema_version": 1, "route_id": str(uuid.uuid4()), "task": task,
        "host": host, "workflow": workflow, "role": role, "execution": execution,
        "agent": agent_name(host, role, workflow, agent, namespace) if execution == "delegated" else "session",
        "profile": name, "configured": spec, "requested": requested,
        "reason": reason, "require_confirmed": require_confirmed,
    }


def plan_errors(plan: object) -> list[str]:
    if not isinstance(plan, dict) or plan.get("schema_version") != 1:
        return ["routing plan must be a schema_version 1 object"]
    errors = []
    for field in ("route_id", "task", "host", "workflow", "role", "execution", "agent", "profile"):
        if not has_text(plan.get(field)):
            errors.append(f"routing plan requires {field}")
    if errors:
        return errors
    errors.extend(selection_errors(plan))
    errors.extend(requested_errors(plan.get("requested")))
    if not isinstance(plan.get("require_confirmed"), bool):
        errors.append("require_confirmed must be a boolean")
    return errors


def requested_errors(requested: object) -> list[str]:
    if not isinstance(requested, dict) or set(requested) != {"model", "reasoning"}:
        return ["routing plan requires requested model and reasoning"]
    if any(value is not None and not has_text(value) for value in requested.values()):
        return ["requested settings must be non-empty strings or null"]
    return []


def selection_errors(plan: dict[str, Any]) -> list[str]:
    choices = {"host": AGENTS, "role": ("normal", "deep", "fast", "top"),
               "execution": ("delegated", "inline"), "workflow": ("dev", "review_pr")}
    errors = [f"routing plan has an unknown {field}" for field, allowed in choices.items() if plan[field] not in allowed]
    if errors:
        return errors
    if plan["execution"] == "inline":
        if not has_text(plan.get("reason")) or plan["agent"] != "session":
            errors.append("inline routing requires an explicit reason and session agent")
        if plan.get("requested") != {"model": None, "reasoning": None}:
            errors.append("inline routing must inherit session settings, not request a model switch")
    elif plan["agent"].split(":")[-1] not in AGENTS[plan["host"]][plan["role"]]:
        errors.append("agent does not implement the selected host role")
    return errors


def receipt_errors(plan: dict[str, Any], receipt: object, complete: bool) -> list[str]:
    if not isinstance(receipt, dict) or receipt.get("schema_version") != 1:
        return ["an invocation receipt is required; configuration is not execution"]
    errors = []
    for field in ("route_id", "agent", "requested"):
        if receipt.get(field) != plan[field]:
            errors.append(f"receipt {field} does not match the locked route")
    for field in ("invocation_id", "evidence_ref"):
        if not has_text(receipt.get(field)):
            errors.append(f"receipt requires {field}")
    if receipt.get("source") not in ("host", "launcher", "report"):
        errors.append("receipt source must be host, launcher, or report")
    allowed = ("completed",) if complete else ("started", "completed")
    if receipt.get("status") not in allowed:
        errors.append("invocation has not completed" if complete else "invocation did not start successfully")
    return errors


def model_evidence(plan: dict[str, Any], receipt: dict[str, Any]) -> tuple[str, list[str]]:
    observed = receipt.get("observed")
    if not isinstance(observed, dict):
        return "UNVERIFIED", []
    # Only host metadata can attest effective settings. Launcher argv and prose cannot.
    if receipt.get("source") != "host":
        return "UNVERIFIED", []
    errors = []
    for field, expected in plan["requested"].items():
        actual = observed.get(field)
        if expected is not None and actual is not None and expected != actual:
            errors.append(f"effective {field} differs from requested {expected!r}: {actual!r}")
    confirmed = all(has_text(observed.get(field)) for field in ("model", "reasoning"))
    return ("MISMATCH" if errors else "CONFIRMED" if confirmed else "UNVERIFIED"), errors


def check_route(plan: object, receipt: object = None, complete: bool = True) -> dict[str, Any]:
    errors = plan_errors(plan)
    if errors:
        return {"status": "FAIL", "model_status": "UNVERIFIED", "errors": errors}
    errors = receipt_errors(plan, receipt, complete)
    model_status = "UNVERIFIED"
    if not errors:
        model_status, errors = model_evidence(plan, receipt)
    if complete and plan["require_confirmed"] and model_status != "CONFIRMED":
        errors.append("this route requires host-confirmed model and reasoning evidence")
    return {"status": "FAIL" if errors else "PASS", "model_status": model_status,
            "errors": errors, "evidence_scope": "receipt consistency, not authenticity"}


def bundle_errors(bundle: object, started: bool, complete: bool) -> list[str]:
    if not isinstance(bundle, dict):
        return ["routing must contain a plan and optional receipt"]
    if not started:
        return plan_errors(bundle.get("plan"))
    return check_route(bundle.get("plan"), bundle.get("receipt"), complete)["errors"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    plan = commands.add_parser("plan", help="resolve a dispatch plan; does not invoke any model")
    plan.add_argument("--host", choices=sorted([*AGENTS, "claude"]), required=True)
    plan.add_argument("--workflow", choices=("dev", "review_pr"), default="dev")
    plan.add_argument("--role", choices=("normal", "deep", "fast", "top"), required=True)
    plan.add_argument("--task", required=True)
    plan.add_argument("--execution", choices=("delegated", "inline"), default="delegated")
    plan.add_argument("--reason", default="")
    plan.add_argument("--root", default=".")
    plan.add_argument("--config")
    plan.add_argument("--profile")
    plan.add_argument("--agent")
    plan.add_argument("--namespace", default="")
    plan.add_argument("--require-confirmed", action="store_true")
    check = commands.add_parser("check", help="validate a plan and an invocation receipt")
    check.add_argument("--plan", type=Path, required=True)
    check.add_argument("--receipt", type=Path, required=True)
    check.add_argument("--started", action="store_true", help="allow a started invocation instead of completion")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "check":
        result = check_route(read_object(args.plan), read_object(args.receipt), not args.started)
        print(json.dumps(result, indent=2))
        return 1 if result["status"] == "FAIL" else 0
    config = Path(args.config) if args.config else default_config(Path(args.root).resolve())
    # Native Claude plugins namespace their agents. Project installs do not.
    namespace = args.namespace
    if args.host in {"claude", "claude_code"} and (Path(__file__).resolve().parents[1] / ".claude-plugin/plugin.json").exists():
        namespace = namespace or "wysiwyship"
    result = resolve_route(config, args.host, args.workflow, args.role, args.task,
                           args.execution, args.reason, args.profile, args.agent,
                           namespace, args.require_confirmed)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
