#!/usr/bin/env python3
"""Run the active work-unit gate from Claude Code or Copilot stop hooks."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

import work_units


def hook_input() -> dict[str, object]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    value = json.loads(raw)
    return value if isinstance(value, dict) else {}


def block(reason: str) -> dict[str, str]:
    return {"decision": "block", "reason": reason[:8000]}


def evaluate(root: Path, payload: dict[str, object]) -> dict[str, str]:
    if payload.get("stop_hook_active") is True or payload.get("stopHookActive") is True:
        return {}
    pointer = work_units.active_pointer(root)
    if not pointer.exists():
        return {}
    unit = work_units.active_unit(root)
    if unit.get("stage") != "complete":
        stage = unit.get("stage")
        return block(f"Active work unit {unit.get('id')} is at {stage}; finish plan -> implement -> document -> simplify -> verify before stopping.")
    command = [sys.executable, str(Path(__file__).with_name("check.py")), "--active", "--root", str(root)]
    completed = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        evidence = "\n".join(item for item in (completed.stdout.strip(), completed.stderr.strip()) if item)
        return block(f"Smart Harness lifecycle gate failed for {unit.get('id')}:\n{evidence}")
    pointer.unlink()
    return {}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=("claude", "copilot"), required=True)
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = work_units.repository_root(args.root)
    print(json.dumps(evaluate(root, hook_input())))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        print(json.dumps(block(f"Smart Harness hook error: {exc}")))
        raise SystemExit(0)
