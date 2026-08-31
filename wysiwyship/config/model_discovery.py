#!/usr/bin/env python3
"""Discover local coding hosts and derive conservative model routing."""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import selectors
import shutil
import subprocess
import time
from typing import Any, Callable


Run = Callable[..., subprocess.CompletedProcess[str]]
ROLE_PREFERENCES = {
    "fast": ("luna", "spark", "haiku", "mini", "terra"),
    "normal": ("terra", "sonnet", "sol", "opus"),
    "deep": ("sol", "opus", "sonnet", "terra"),
    "top": ("sol", "opus", "sonnet", "terra"),
}
WORKFLOW_ROLE = {"dev": "deep", "review_pr": "top"}


def command(executable: str, *args: str, run: Run = subprocess.run, timeout: int = 8) -> subprocess.CompletedProcess[str]:
    return run([executable, *args], text=True, capture_output=True, timeout=timeout, check=False)


def executable_version(executable: str, run: Run) -> str | None:
    try:
        result = command(executable, "--version", run=run)
    except (OSError, subprocess.TimeoutExpired):
        return None
    text = (result.stdout or result.stderr).strip()
    return text.splitlines()[0] if text else None


def unavailable(host: str, note: str) -> dict[str, Any]:
    return {
        "host": host, "installed": False, "version": None, "evidence": "not-installed",
        "models": [], "current_model": None, "notes": [note],
    }


def read_rpc(stream: Any, request_id: int, timeout: float = 10) -> dict[str, Any]:
    selector = selectors.DefaultSelector()
    selector.register(stream, selectors.EVENT_READ)
    deadline = time.monotonic() + timeout
    try:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not selector.select(remaining):
                raise RuntimeError(f"timed out waiting for app-server response id {request_id}")
            line = stream.readline()
            if not line:
                raise RuntimeError(f"app-server closed before response id {request_id}")
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                continue
            if message.get("id") != request_id:
                continue
            if "error" in message:
                raise RuntimeError(str(message["error"]))
            return message.get("result", {})
    finally:
        selector.close()


def codex_model_catalog(executable: str) -> list[dict[str, Any]]:
    process = subprocess.Popen(
        [executable, "app-server"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL, text=True,
    )
    if process.stdin is None or process.stdout is None:
        raise RuntimeError("could not open Codex app-server pipes")
    try:
        initialize = {"method": "initialize", "id": 0, "params": {"clientInfo": {
            "name": "wysiwyship", "title": "WYSIWYShip installer", "version": "1",
        }}}
        process.stdin.write(json.dumps(initialize) + "\n")
        process.stdin.flush()
        read_rpc(process.stdout, 0)
        process.stdin.write(json.dumps({"method": "initialized", "params": {}}) + "\n")
        process.stdin.write(json.dumps({
            "method": "model/list", "id": 1,
            "params": {"limit": 100, "includeHidden": False},
        }) + "\n")
        process.stdin.flush()
        return read_rpc(process.stdout, 1).get("data", [])
    finally:
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=2)


def discover_codex(
    which: Callable[[str], str | None] = shutil.which,
    run: Run = subprocess.run,
    model_list: Callable[[str], list[dict[str, Any]]] = codex_model_catalog,
) -> dict[str, Any]:
    executable = which("codex")
    if not executable:
        return unavailable("codex", "Codex CLI was not found on PATH.")
    result: dict[str, Any] = {
        "host": "codex", "installed": True, "version": executable_version(executable, run),
        "evidence": "session-inheritance", "models": [], "current_model": None, "notes": [],
    }
    try:
        entries = model_list(executable)
        result["models"] = [
            {
                "id": item["model"],
                "default": bool(item.get("isDefault")),
                "reasoning": [effort["reasoningEffort"] for effort in item.get("supportedReasoningEfforts", [])],
            }
            for item in entries if isinstance(item, dict) and isinstance(item.get("model"), str)
        ]
        result["evidence"] = "account-visible"
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        result["notes"].append(f"Exact model discovery failed; workflows inherit the Codex session: {exc}")
    return result


def json_model_restrictions(paths: list[Path]) -> list[str]:
    models: list[str] = []
    for path in paths:
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        values = data.get("availableModels") if isinstance(data, dict) else None
        if isinstance(values, list):
            models.extend(value for value in values if isinstance(value, str) and value.strip())
    return list(dict.fromkeys(models))


def discover_claude(target: Path, home: Path, which: Callable[[str], str | None] = shutil.which, run: Run = subprocess.run) -> dict[str, Any]:
    executable = which("claude")
    if not executable:
        return unavailable("claude_code", "Claude Code was not found on PATH.")
    paths = [
        home / ".claude/settings.json", target / ".claude/settings.json",
        Path("/Library/Application Support/ClaudeCode/managed-settings.json"),
    ]
    models = json_model_restrictions(paths)
    evidence = "configured-restriction" if models else "session-inheritance"
    notes = [] if models else ["Claude Code has no supported non-interactive entitlement list; using the active session model."]
    return {
        "host": "claude_code", "installed": True, "version": executable_version(executable, run),
        "evidence": evidence, "models": [{"id": model, "default": model == "default", "reasoning": []} for model in models],
        "current_model": None, "notes": notes,
    }


def vscode_extensions(home: Path, code: str | None, run: Run) -> list[str]:
    if code:
        try:
            response = command(code, "--list-extensions", "--show-versions", run=run)
            if response.returncode == 0:
                return [line.strip() for line in response.stdout.splitlines() if line.strip()]
        except (OSError, subprocess.TimeoutExpired):
            pass
    roots = (home / ".vscode/extensions", home / ".vscode-insiders/extensions")
    return [path.name for root in roots if root.is_dir() for path in root.iterdir()]


def discover_copilot(home: Path, which: Callable[[str], str | None] = shutil.which, run: Run = subprocess.run) -> dict[str, Any]:
    executable = which("copilot")
    code = which("code")
    extensions = vscode_extensions(home, code, run)
    extension = next((item for item in extensions if item.lower().startswith("github.copilot")), None)
    if not executable and not extension:
        return unavailable("copilot", "Neither Copilot CLI nor a VS Code Copilot extension was detected.")
    version = executable_version(executable, run) if executable else extension
    return {
        "host": "copilot", "installed": True, "version": version,
        "evidence": "session-inheritance", "models": [], "current_model": None,
        "notes": ["Copilot does not expose the signed-in VS Code model picker through a supported installer API; custom agents inherit the session model."],
    }


def discover_pi(which: Callable[[str], str | None] = shutil.which, run: Run = subprocess.run) -> dict[str, Any]:
    executable = which("pi")
    if not executable:
        return unavailable("pi", "Pi was not found on PATH.")
    return {
        "host": "pi", "installed": True, "version": executable_version(executable, run),
        "evidence": "session-inheritance", "models": [], "current_model": None,
        "notes": ["Pi's coordinator retains its active session; a child without --model uses its own host default, not the parent's interactive selection. Explicit task overrides must match any locked route."],
    }


def discover(target: Path, home: Path | None = None, which: Callable[[str], str | None] = shutil.which, run: Run = subprocess.run) -> dict[str, Any]:
    actual_home = home or Path.home()
    hosts = [
        discover_copilot(actual_home, which, run),
        discover_claude(target, actual_home, which, run),
        discover_codex(which, run),
        discover_pi(which, run),
    ]
    return {"schema_version": 1, "hosts": {host["host"]: host for host in hosts}}


def preferred_model(models: list[dict[str, Any]], role: str) -> dict[str, Any] | None:
    if not models:
        return None
    for token in ROLE_PREFERENCES[role]:
        match = next((model for model in models if token in model["id"].lower()), None)
        if match:
            return match
    return next((model for model in models if model.get("default")), models[0])


def clamp_reasoning(requested: str, supported: list[str]) -> str:
    if not supported or requested in supported:
        return requested
    order = ("minimal", "low", "medium", "high", "xhigh", "max", "ultra")
    eligible = [value for value in order if value in supported and order.index(value) <= order.index(requested)]
    return eligible[-1] if eligible else supported[0]


def configure_spec(spec: dict[str, Any], selected: dict[str, Any] | None, evidence: str, note: str = "") -> None:
    spec["model"] = selected["id"] if selected else None
    if selected:
        spec["reasoning"] = clamp_reasoning(spec["reasoning"], selected.get("reasoning", []))
    spec["notes"] = f"Installer evidence: {evidence}.{note}"


def configure_platform(settings: dict[str, Any], discovery: dict[str, Any], platform: str) -> None:
    exact = discovery["evidence"] in {"account-visible", "configured-restriction"}
    for role, spec in settings["roles"].items():
        selected = preferred_model(discovery["models"], role) if exact else None
        configure_spec(spec, selected, discovery["evidence"])
    for workflow, spec in settings["workflows"].items():
        selected = preferred_model(discovery["models"], WORKFLOW_ROLE[workflow]) if exact and platform != "codex" else None
        note = " Coordinator inherits the active Codex session." if platform == "codex" else ""
        configure_spec(spec, selected, discovery["evidence"], note)


def adaptive_profile(base: dict[str, Any], report: dict[str, Any]) -> dict[str, Any]:
    profile = deepcopy(base)
    for platform, settings in profile.items():
        discovery = report["hosts"].get(platform, unavailable(platform, "Host was not scanned."))
        configure_platform(settings, discovery, platform)
    return profile


def route_line(routes: dict[str, Any]) -> str:
    resolved = {
        **{f"{key}.coordinator": value.get("model") or "inherit" for key, value in routes["workflows"].items()},
        **{key: value.get("model") or "inherit" for key, value in routes["roles"].items()},
    }
    return "    routes: " + ", ".join(f"{key}={value}" for key, value in resolved.items())


def host_report_lines(name: str, host: dict[str, Any], routes: dict[str, Any] | None) -> list[str]:
    state = host["version"] or ("detected" if host["installed"] else "not installed")
    models = ", ".join(model["id"] for model in host["models"]) or "session/default inheritance"
    lines = [f"  {name}: {state}; {host['evidence']}; {models}"]
    lines.extend(f"    note: {note}" for note in host["notes"])
    if routes:
        lines.append(route_line(routes))
    return lines


def report_lines(report: dict[str, Any], profile: dict[str, Any] | None = None) -> list[str]:
    lines = ["Model capability discovery:"]
    for name, host in report["hosts"].items():
        lines.extend(host_report_lines(name, host, profile.get(name) if profile else None))
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = discover(Path(args.target).resolve())
    print(json.dumps(result, indent=2) if args.json else "\n".join(report_lines(result)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
