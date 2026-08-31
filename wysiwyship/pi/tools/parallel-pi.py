#!/usr/bin/env python3
"""Run independent Pi child tasks concurrently without third-party extensions.

The only runtime requirement is the Pi executable itself. Input is a JSON array
from --tasks FILE or stdin. Each task supports: name, prompt, role, cwd, model,
thinking, tools, timeout_seconds. Explicit task settings override the selected
WYSIWYShip profile.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid
from typing import Any

PREFIX = """You are a bounded specialist child in a larger engineering workflow.
Complete only the delegated task. Do not delegate or spawn more agents.
Distinguish repository facts, inference, and recommendations. Return concise
evidence, commands actually run, limitations, and unresolved questions.

"""

READ_ONLY_TOOLS = {"read", "grep", "find", "ls"}
EXECUTE_TOOLS = READ_ONLY_TOOLS | {"bash"}
WRITE_TOOLS = EXECUTE_TOOLS | {"edit", "write"}
SAFE_ENV_KEYS = {"HOME", "LANG", "LOGNAME", "PATH", "SHELL", "TERM", "TMPDIR", "USER"}
MODEL_ROLES = {"coordinator", "normal", "deep", "fast", "top"}
WORKFLOWS = {"dev", "review_pr"}


def load_tasks(path: str | None) -> list[dict[str, Any]]:
    raw = Path(path).read_text(encoding="utf-8") if path else sys.stdin.read()
    data = json.loads(raw)
    if not isinstance(data, list) or not data:
        raise SystemExit("tasks must be a non-empty JSON array")
    for index, task in enumerate(data):
        if (
            not isinstance(task, dict)
            or not isinstance(task.get("name"), str)
            or not task["name"].strip()
            or not isinstance(task.get("prompt"), str)
            or not task["prompt"].strip()
        ):
            raise SystemExit(f"task {index} requires string name and prompt")
    return data


def decode_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value


def child_environment(inherit: bool) -> dict[str, str]:
    if inherit:
        return os.environ.copy()
    return {key: value for key, value in os.environ.items() if key in SAFE_ENV_KEYS or key.startswith("LC_")}


def load_pi_profile(path: Path, selected: str | None) -> tuple[str, dict[str, Any]] | None:
    if not path.exists():
        if selected:
            raise ValueError(f"model config does not exist: {path}")
        return None
    config = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError(f"{path}: model config must be an object")
    profiles = config.get("profiles")
    if config.get("schema_version") != 2 or not isinstance(profiles, dict):
        raise ValueError(f"{path}: unsupported model profile schema")
    name = selected or config.get("active_profile")
    profile = profiles.get(name) if isinstance(name, str) else None
    if not isinstance(profile, dict) or not isinstance(profile.get("pi"), dict):
        raise ValueError(f"{path}: unknown or invalid Pi profile {name!r}")
    return name, profile["pi"]


def apply_runtime_defaults(
    task: dict[str, Any],
    settings: dict[str, Any] | None,
    workflow: str,
) -> dict[str, Any]:
    resolved = dict(task)
    role = resolved.get("role", "fast")
    if not isinstance(role, str) or role not in MODEL_ROLES:
        raise ValueError(f"task {task['name']!r} has unknown model role {role!r}")
    resolved["role"] = role
    if settings is None:
        return resolved
    group = "workflows" if role == "coordinator" else "roles"
    key = workflow if role == "coordinator" else role
    spec = settings.get(group, {}).get(key)
    if not isinstance(spec, dict) or not isinstance(spec.get("reasoning"), str):
        raise ValueError(f"Pi profile is missing {group}.{key}")
    if "model" not in resolved:
        resolved["model"] = spec.get("model")
    if "thinking" not in resolved:
        resolved["thinking"] = spec["reasoning"]
    return resolved


def validate_routing(task: dict[str, Any], workflow: str | None = None) -> None:
    """Reject task settings that would silently change a locked Pi dispatch."""
    plan = task.get("routing")
    if plan is None:
        return
    if not isinstance(plan, dict) or plan.get("schema_version") != 1 or not plan.get("route_id"):
        raise ValueError("task routing must be a routing.py plan")
    if plan.get("require_confirmed"):
        raise ValueError("Pi print-mode launcher cannot confirm effective model/effort; this route cannot run here")
    expected = {"host": "pi", "execution": "delegated", "agent": "parallel-pi",
                "role": task.get("role", "fast"), "task": task["name"],
                "requested": {"model": task.get("model"), "reasoning": task.get("thinking")}}
    if workflow is not None:
        expected["workflow"] = workflow
    for field, value in expected.items():
        if plan.get(field) != value:
            raise ValueError(f"task {task['name']!r} conflicts with locked routing {field}")


def invocation_receipt(task: dict[str, Any], invocation_id: str, succeeded: bool) -> dict[str, Any]:
    """Argv is launch evidence, never a claim about the model that answered."""
    plan = task.get("routing") or {}
    return {
        "schema_version": 1, "route_id": plan.get("route_id", invocation_id),
        "agent": "parallel-pi", "invocation_id": invocation_id,
        "source": "launcher", "evidence_ref": f"parallel-pi:{invocation_id}",
        "status": "completed" if succeeded else "failed",
        "requested": {"model": task.get("model"), "reasoning": task.get("thinking")},
        "observed": None,
        "model_status": "UNVERIFIED",
        "model_selection": "explicit" if task.get("model") else "child-host-default",
    }


def default_model_config(cwd: str) -> Path:
    project = Path(cwd).resolve() / ".wysiwyship/config/models.json"
    return project if project.exists() else Path.home() / ".wysiwyship/config/models.json"


def resolve_tools(task: dict[str, Any], capability: str) -> str:
    allowed = {"read_only": READ_ONLY_TOOLS, "execute": EXECUTE_TOOLS, "write": WRITE_TOOLS}[capability]
    requested = task.get("tools")
    tools = allowed if requested is None else {item.strip() for item in str(requested).split(",") if item.strip()}
    unexpected = tools - allowed
    if unexpected:
        raise ValueError(f"task {task['name']!r} requests tools outside {capability}: {sorted(unexpected)}")
    return ",".join(sorted(tools))


def run_task(
    task: dict[str, Any],
    default_cwd: str,
    pi_bin: str,
    capability: str = "read_only",
    auto_approve: bool = False,
    inherit_env: bool = False,
) -> dict[str, Any]:
    validate_routing(task)
    invocation_id = str(uuid.uuid4())
    root = Path(default_cwd).resolve()
    cwd_path = Path(task.get("cwd") or root).resolve()
    if cwd_path != root and root not in cwd_path.parents:
        raise ValueError(f"task {task['name']!r} cwd escapes the configured root: {cwd_path}")
    cwd = str(cwd_path)
    cmd = [pi_bin, "-p", "--no-session"]
    if auto_approve:
        cmd.append("--approve")
    if task.get("model"):
        cmd += ["--model", str(task["model"])]
    if task.get("thinking"):
        cmd += ["--thinking", str(task["thinking"])]
    tools = resolve_tools(task, capability)
    if tools:
        cmd += ["--tools", str(tools)]
    lifecycle = "For implementation, run plan -> implement -> document -> simplify -> verify and return one commit-ready unit.\n\n" if capability == "write" else ""
    cmd.append(PREFIX + lifecycle + str(task["prompt"]))
    timeout = int(task.get("timeout_seconds", 900))
    started = time.monotonic()
    try:
        completed = subprocess.run(
            cmd,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=timeout,
            env=child_environment(inherit_env),
            check=False,
        )
        return {
            "name": task["name"],
            "role": task.get("role", "fast"),
            "model": task.get("model"),
            "thinking": task.get("thinking"),
            "cwd": cwd,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "timed_out": False,
            "duration_seconds": round(time.monotonic() - started, 6),
            "routing_receipt": invocation_receipt(task, invocation_id, completed.returncode == 0),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "name": task["name"],
            "role": task.get("role", "fast"),
            "model": task.get("model"),
            "thinking": task.get("thinking"),
            "cwd": cwd,
            "returncode": None,
            "stdout": decode_output(exc.stdout),
            "stderr": decode_output(exc.stderr),
            "timed_out": True,
            "duration_seconds": round(time.monotonic() - started, 6),
            "routing_receipt": invocation_receipt(task, invocation_id, False),
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", help="JSON task file; omit to read stdin")
    parser.add_argument("--cwd", default=".")
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--pi-bin", default=os.environ.get("WYSIWYSHIP_PI_BIN", "pi"))
    parser.add_argument("--model-config", help="models.json; defaults to <cwd>/.wysiwyship/config/models.json")
    parser.add_argument("--profile", help="model profile; defaults to active_profile")
    parser.add_argument("--workflow", choices=sorted(WORKFLOWS), default="dev")
    parser.add_argument("--capability", choices=("read_only", "execute", "write"), default="read_only")
    parser.add_argument("--auto-approve", action="store_true", help="Allow Pi to execute enabled tools without confirmation")
    parser.add_argument("--inherit-env", action="store_true", help="Pass the complete parent environment, including secrets")
    args = parser.parse_args()
    tasks = load_tasks(args.tasks)
    config_path = Path(args.model_config) if args.model_config else default_model_config(args.cwd)
    loaded = load_pi_profile(config_path.resolve(), args.profile)
    profile_name, settings = loaded if loaded else (None, None)
    tasks = [apply_runtime_defaults(task, settings, args.workflow) for task in tasks]
    # Validate the entire batch before any child starts, not after partial dispatch.
    for task in tasks:
        validate_routing(task, args.workflow)
    if profile_name:
        print(f"using Pi model profile {profile_name!r}", file=sys.stderr)
    workers = max(1, min(args.max_workers, len(tasks)))
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [
            pool.submit(
                run_task,
                task,
                args.cwd,
                args.pi_bin,
                args.capability,
                args.auto_approve,
                args.inherit_env,
            )
            for task in tasks
        ]
        results = [future.result() for future in futures]
    print(json.dumps(results, indent=2))
    return 1 if any(item["timed_out"] or item["returncode"] != 0 for item in results) else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
