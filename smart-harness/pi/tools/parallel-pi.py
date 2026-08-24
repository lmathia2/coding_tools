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


def load_tasks(path: str | None) -> list[dict[str, Any]]:
    raw = Path(path).read_text(encoding="utf-8") if path else sys.stdin.read()
    data = json.loads(raw)
    if not isinstance(data, list) or not data:
        raise SystemExit("tasks must be a non-empty JSON array")
    for index, task in enumerate(data):
        if not isinstance(task, dict) or not task.get("name") or not task.get("prompt"):
            raise SystemExit(f"task {index} requires string name and prompt")
    return data


def run_task(task: dict[str, Any], default_cwd: str, pi_bin: str) -> dict[str, Any]:
    cwd = str(Path(task.get("cwd") or default_cwd).resolve())
    cmd = [pi_bin, "-p", "--no-session", "--approve"]
    if task.get("model"):
        cmd += ["--model", str(task["model"])]
    if task.get("thinking"):
        cmd += ["--thinking", str(task["thinking"])]
    tools = task.get("tools", "read,grep,find,ls,bash")
    if tools:
        cmd += ["--tools", str(tools)]
    cmd.append(PREFIX + str(task["prompt"]))
    timeout = int(task.get("timeout_seconds", 900))
    try:
        completed = subprocess.run(
            cmd,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=timeout,
            env=os.environ.copy(),
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
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "timed_out": True,
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", help="JSON task file; omit to read stdin")
    parser.add_argument("--cwd", default=".")
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--pi-bin", default=os.environ.get("SMART_HARNESS_PI_BIN", "pi"))
    args = parser.parse_args()
    tasks = load_tasks(args.tasks)
    workers = max(1, min(args.max_workers, len(tasks)))
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(run_task, task, args.cwd, args.pi_bin) for task in tasks]
        results = [future.result() for future in futures]
    print(json.dumps(results, indent=2))
    return 1 if any(item["timed_out"] or item["returncode"] != 0 for item in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
