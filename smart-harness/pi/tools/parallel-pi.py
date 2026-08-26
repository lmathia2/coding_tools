#!/usr/bin/env python3
"""Run independent Pi child tasks concurrently without third-party extensions.

The only runtime requirement is the Pi executable itself. Input is a JSON array
from --tasks FILE or stdin. Each task supports: name, prompt, cwd, model,
thinking, tools, timeout_seconds.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys
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
            "cwd": cwd,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "name": task["name"],
            "cwd": cwd,
            "returncode": None,
            "stdout": decode_output(exc.stdout),
            "stderr": decode_output(exc.stderr),
            "timed_out": True,
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", help="JSON task file; omit to read stdin")
    parser.add_argument("--cwd", default=".")
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--pi-bin", default=os.environ.get("SMART_HARNESS_PI_BIN", "pi"))
    parser.add_argument("--capability", choices=("read_only", "execute", "write"), default="read_only")
    parser.add_argument("--auto-approve", action="store_true", help="Allow Pi to execute enabled tools without confirmation")
    parser.add_argument("--inherit-env", action="store_true", help="Pass the complete parent environment, including secrets")
    args = parser.parse_args()
    tasks = load_tasks(args.tasks)
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
