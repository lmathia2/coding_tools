#!/usr/bin/env python3
"""Offline pilot validation and single-attempt Codex trials (Python 3.9+).

Same-user local measurement, not a security sandbox or anti-cheating boundary.
"""
import argparse
import difflib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
VERSION = 1
CACHES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
PRIVATE = {".git", ".agent-state", ".agent-worktrees", ".agents", ".codex",
           ".wysiwyship", ".wysiwyship-backups", ".venv", "venv", "node_modules"}
SOURCE_SUFFIXES = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java",
                   ".c", ".h", ".cpp", ".cs", ".rb", ".sh", ".sql"}
EFFORTS = ("low", "medium", "high", "xhigh")
TOKEN_KEYS = ("input_tokens", "cached_input_tokens", "output_tokens")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def safe_path(raw):
    """Reject symlinks, allowing only macOS's standard /tmp and /var aliases."""
    path = Path(os.path.abspath(raw))
    aliases = {Path("/tmp"): Path("/private/tmp"), Path("/var"): Path("/private/var")}
    for part in [path, *path.parents]:
        if part.is_symlink():
            require(part in aliases and part.resolve() == aliases[part],
                    "symlink forbidden: " + str(part))
    return path.resolve()


def read_json(path):
    value = json.loads(safe_path(path).read_text(encoding="utf-8"))
    require(isinstance(value, dict), "JSON object required: " + str(path))
    return value


def sync_directory(directory):
    if os.name == "posix":
        descriptor = os.open(str(directory), os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


def write_json(path, value):
    """Atomic, fsynced receipts; never follow a receipt symlink."""
    path = safe_path(path)
    descriptor, name = tempfile.mkstemp(prefix=".receipt-", dir=str(path.parent))
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        sync_directory(path.parent)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def files(root, excluded=CACHES, omit_tests=False):
    root = safe_path(root)
    require(root.is_dir(), "directory required: " + str(root))
    found = {}
    for directory, folders, names in os.walk(root):
        folders[:] = sorted(name for name in folders if name not in excluded)
        for name in [*folders, *sorted(names)]:
            if name in excluded:
                continue
            path = Path(directory) / name
            require(not path.is_symlink(), "symlink forbidden: " + str(path))
            if path.is_file() and not (omit_tests and name.startswith("test_")):
                found[path.relative_to(root).as_posix()] = path
            elif not path.is_dir():
                require(path.is_file(), "special file forbidden: " + str(path))
    return found


def tree_hash(root, excluded=CACHES):
    return digest({name: hashlib.sha256(path.read_bytes()).hexdigest()
                   for name, path in files(root, excluded).items()})


def copy_tree(source, destination, excluded=CACHES, omit_tests=False):
    members = files(source, excluded, omit_tests)
    destination.mkdir(parents=True, exist_ok=False)
    for name, path in members.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def catalog(root):
    data = read_json(root / "catalog.json")
    require(data.get("schema_version") == 1, "unsupported catalog schema")
    require(isinstance(data.get("suite_version"), str) and data["suite_version"], "suite_version required")
    require(isinstance(data.get("tasks"), list), "catalog tasks must be a list")
    identifiers = set()
    for task in data["tasks"]:
        require(isinstance(task, dict), "task must be an object")
        ident = task.get("id", "")
        require(isinstance(ident, str) and re.fullmatch(r"[a-z][a-z0-9-]*", ident), "unsafe task id")
        require(ident not in identifiers, "duplicate task id: " + ident)
        require(task.get("status") in ("pilot", "planned"), "invalid task status")
        if task["status"] == "pilot":
            require(isinstance(task.get("version"), str) and task["version"], "pilot task version required")
        identifiers.add(ident)
    return data


def fixture_revision(root, ident):
    data = catalog(root)
    task = next((item for item in data["tasks"] if item["id"] == ident), None)
    require(task is not None, "unknown task: " + str(ident))
    require(task["status"] == "pilot", "task is not a runnable pilot: " + ident)
    fixture = safe_path(root / "tasks" / ident)
    hashes = {name: tree_hash(fixture / name) for name in ("starter", "acceptance", "reference")}
    require(not any((fixture / "starter" / name).exists() for name in PRIVATE | {"TASK.md"}),
            "starter contains reserved harness/runtime paths")
    hashes["task.md"] = hashlib.sha256(safe_path(fixture / "task.md").read_bytes()).hexdigest()
    require((fixture / "starter/tests").is_dir(), "canonical regression tests missing")
    return {"suite_version": data["suite_version"], "task_version": task["version"],
            "catalog_hash": digest(data), "fixtures": hashes,
            "runner_version": VERSION, "grader_version": 1,
            "evaluator_hash": digest({name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                                      for name in ("runner.py", "grader.py")})}


def positive(raw):
    value = int(raw)
    if value <= 0:
        raise argparse.ArgumentTypeError("timeout must be positive")
    return value


def clean_environment():
    env = dict(os.environ)
    for key in list(env):
        if key.startswith("GIT_") or key in ("PYTHONPATH", "PYTHONHOME"):
            env.pop(key)
    env.update(PYTHONDONTWRITEBYTECODE="1", GIT_CONFIG_NOSYSTEM="1",
               GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT="0")
    return env


def stop_process(process):
    """Kill the whole group even when its leader exits immediately on TERM."""
    if os.name == "posix":
        for sig in (signal.SIGTERM, signal.SIGKILL):
            try:
                os.killpg(process.pid, sig)
            except ProcessLookupError:
                pass
            if sig == signal.SIGTERM:
                try:
                    process.wait(timeout=0.2)
                except subprocess.TimeoutExpired:
                    pass
    elif process.poll() is None:
        process.kill()
    process.wait()


def execute_process(argv, cwd, stdout, stderr, timeout, env=None):
    """File-backed output avoids deadlocks; elapsed time uses a monotonic clock."""
    started = time.monotonic()
    process = None
    code = None
    status = "launch_error"
    with safe_path(stdout).open("x") as output, safe_path(stderr).open("x") as errors:
        try:
            process = subprocess.Popen(argv, cwd=cwd, env=env, stdout=output, stderr=errors,
                                       start_new_session=os.name == "posix")
            try:
                code = process.wait(timeout=timeout)
                status = "completed" if code == 0 else "nonzero"
            except subprocess.TimeoutExpired:
                status = "timeout"
        except KeyboardInterrupt:
            status = "interrupted"
        except OSError as exc:
            errors.write(str(exc) + "\n")
        finally:
            if process is not None:
                stop_process(process)
                code = process.returncode
    return {"status": status, "returncode": code, "duration_seconds": time.monotonic() - started}


def valid_test_report(report):
    require(report.get("schema_version") == 1, "invalid grader schema")
    require(type(report.get("tests")) is int and report["tests"] >= 0, "invalid test count")
    for name in ("failures", "errors", "discovery_errors", "skips", "expected_failures", "unexpected_successes"):
        require(isinstance(report.get(name), list), "invalid grader field: " + name)
    require(type(report.get("successful")) is bool, "invalid grader success field")
    return report


def test_group(candidate, canonical, timeout):
    with tempfile.TemporaryDirectory(prefix="wysiwyship-grade-") as directory:
        root = safe_path(directory)
        work, tests = root / "candidate", root / "tests"
        copy_tree(candidate, work, CACHES | PRIVATE | {"tests"}, omit_tests=True)
        copy_tree(canonical, tests)
        env = clean_environment()
        env["PYTHONPATH"] = str(work)
        receipt = execute_process([sys.executable, str(HERE / "grader.py"), str(work),
                                   str(tests), str(root / "result.json")],
                                  work, root / "stdout", root / "stderr", timeout, env)
        try:
            report = valid_test_report(read_json(root / "result.json"))
            disallowed = ("failures", "errors", "discovery_errors", "skips", "expected_failures", "unexpected_successes")
            report["successful"] = (report["successful"] and report["tests"] > 0
                                    and not any(report[name] for name in disallowed)
                                    and receipt["status"] == "completed" and receipt["returncode"] == 0)
        except (ValueError, OSError) as exc:
            report = {"successful": False, "tests": None, "report_error": str(exc)}
        report.update(process=receipt, stdout=(root / "stdout").read_text(errors="replace"),
                      stderr=(root / "stderr").read_text(errors="replace"))
        return report


def grade(fixture, candidate, timeout):
    result = {"regression": test_group(candidate, fixture / "starter/tests", timeout),
              "acceptance": test_group(candidate, fixture / "acceptance", timeout)}
    result["correct"] = all(result[name]["successful"] for name in ("regression", "acceptance"))
    return result


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, "cannot load " + str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclasses resolves the module during import.
    original = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = original
    return module


def source_files(root):
    return {name: path for name, path in files(root, CACHES | PRIVATE | {"tests", "docs"}).items()
            if path.suffix in SOURCE_SUFFIXES and not path.name.startswith("test_")}


def complexity_delta(analyzer, name, before, after):
    previous = analyzer.analyze_code(before, name)
    current = analyzer.analyze_code(after, name)
    if "error" in previous or "error" in current:
        return {"file": name, "error": {"before": previous.get("error"), "after": current.get("error")}}
    analyzer.attach_baseline(current["functions"], previous["functions"])
    old = {item["qualified_name"]: item for item in previous["functions"]}
    new = {item["qualified_name"]: item for item in current["functions"]}
    changed = []
    for key in sorted(old.keys() | new.keys()):
        a, b = old.get(key), new.get(key)
        a_text = before.splitlines()[a["line"] - 1:a["end_line"]] if a else None
        b_text = after.splitlines()[b["line"] - 1:b["end_line"]] if b else None
        if a_text != b_text:
            changed.append({"qualified_name": key, "before": a["complexity_score"] if a else None,
                            "after": b["complexity_score"] if b else None,
                            "delta": b["delta"] if a and b else None,
                            "change": "modified" if a and b else ("added" if b else "deleted")})
    return {"file": name, "functions": changed}


def metrics(starter, candidate, analyzer_path):
    before, after = source_files(starter), source_files(candidate)
    changed, complexity = [], []
    added = deleted = 0
    analyzer = load_module(analyzer_path, "eval_complexity") if analyzer_path.is_file() else None
    for name in sorted(before.keys() | after.keys()):
        a = before[name].read_text() if name in before else ""
        b = after[name].read_text() if name in after else ""
        if a == b and (name in before) == (name in after):
            continue
        changed.append({"path": name, "change": "modified" if name in before and name in after
                        else ("added" if name in after else "deleted")})
        diff = list(difflib.ndiff(a.splitlines(), b.splitlines()))
        added += sum(line.startswith("+ ") for line in diff)
        deleted += sum(line.startswith("- ") for line in diff)
        if analyzer and Path(name).suffix == ".py":
            complexity.append(complexity_delta(analyzer, name, a, b))
    artifacts = files(candidate, CACHES | PRIVATE)
    return {"changed_source_files": changed, "added_source_loc": added, "deleted_source_loc": deleted,
            "changed_source_complexity": complexity if analyzer else None,
            "complexity_scope": "changed Python functions; added/deleted baselines are null",
            "documentation_artifacts": sorted(name for name in artifacts
                                              if name.lower().startswith("readme") or name.startswith("docs/")),
            "html_explainers": sorted(name for name in artifacts if name.endswith(".html")),
            "artifact_accuracy": "unassessed"}


def installed_snapshot(work):
    return {name: tree_hash(work / name) for name in (".agents", ".codex", ".wysiwyship")}


def harness_revision(harness):
    """Only Codex installer inputs, never the surrounding repository or evals."""
    names = ("config", "tools", "shared/skills", "codex/agents", "templates", "vendor",
             "scripts/install_harness.py", "VERSION")
    snapshot = {}
    for name in names:
        path = safe_path(harness / name)
        if path.is_dir():
            snapshot[name] = tree_hash(path)
        elif path.is_file():
            snapshot[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        else:
            snapshot[name] = None
    return snapshot


def install_workflow(work, harness, model, effort):
    log = work.parent / "installer.log"
    receipt = execute_process([sys.executable, str(harness / "scripts/install_harness.py"),
                               "project", "codex", str(work), "--no-model-discovery"],
                              work, log, work.parent / "installer.stderr", 120, clean_environment())
    require(receipt["status"] == "completed", "installer failed; see " + str(log))
    models_path = work / ".wysiwyship/config/models.json"
    models = read_json(models_path)
    profile = models["profiles"][models["active_profile"]]
    for group in ("roles", "workflows"):
        require(profile["codex"].get(group), "missing Codex " + group)
        for route in profile["codex"][group].values():
            route.update(model=model, reasoning=effort)
    write_json(models_path, models)
    sys.path.insert(0, str(harness / "config"))
    try:
        adapter = load_module(harness / "config/adapter_config.py", "eval_adapter")
        native = sorted((work / ".codex/agents").glob("*.toml"))
        require(native, "installer produced no native agents")
        for path in native:
            text = adapter.rewrite_text(path, path.read_text(), "codex", profile)
            require('model = "' + model + '"' in text, "native model not pinned")
            require('model_reasoning_effort = "' + effort + '"' in text, "native effort not pinned")
            path.write_text(text)
    finally:
        sys.path.pop(0)
    checks_path = work / ".wysiwyship/config/checks.json"
    checks = read_json(checks_path)
    checks["commands"] = [{"name": "regression", "argv": [sys.executable, "-m", "unittest",
                                                           "discover", "-s", "tests"]}]
    write_json(checks_path, checks)
    return {"snapshot": installed_snapshot(work), "installer": receipt,
            "native_agents": [path.relative_to(work).as_posix() for path in native]}


def prompt(condition):
    common = ("Complete TASK.md. Meet its public behavior and documentation requirements, including "
              "an ELI5 explanation. Preserve existing tests. Work noninteractively: choose documented "
              "defaults and record assumptions. Do not inspect evaluator/reference materials or use "
              "external lookups. Summarize implementation, verification, and limitations.")
    return ("$engineering-workflow auto\n\n" if condition == "workflow" else "") + common


def initialize_git(work):
    env = clean_environment()
    env.update(GIT_AUTHOR_NAME="Evaluation Runner", GIT_COMMITTER_NAME="Evaluation Runner",
               GIT_AUTHOR_EMAIL="eval@example.invalid", GIT_COMMITTER_EMAIL="eval@example.invalid")
    git = ["git", "-c", "core.hooksPath=" + os.devnull, "-c", "commit.gpgsign=false",
           "-c", "init.templateDir=", "-c", "core.attributesFile=" + os.devnull]
    for command in (["init", "-q", "--template="], ["add", "--all"], ["commit", "-qm", "evaluation starter"]):
        subprocess.run(git + command, cwd=work, env=env, check=True, capture_output=True)


def suite_root(args):
    return safe_path(args.suite_root) if args.suite_root else HERE


def prepare(args):
    root = suite_root(args)
    revision = fixture_revision(root, args.task)
    require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/+-]*", args.model), "invalid exact model name")
    require(Path(args.output).is_absolute(), "output must be absolute")
    output = safe_path(args.output)
    require(not output.exists(), "output already exists")
    harness = safe_path(args.harness_root) if args.harness_root else HERE.parent
    for protected in (root, harness):
        require(output != protected and protected not in output.parents and output not in protected.parents,
                "output must be outside suite and harness")
    output.mkdir(parents=True, exist_ok=False)
    work = output / "workspace"
    fixture = root / "tasks" / args.task
    copy_tree(fixture / "starter", work)
    require(not (work / "TASK.md").exists(), "starter contains reserved TASK.md")
    shutil.copy2(fixture / "task.md", work / "TASK.md")
    workflow = install_workflow(work, harness, args.model, args.reasoning) if args.condition == "workflow" else None
    initialize_git(work)
    analyzer = harness / "tools/complexity.py"
    analyzer_hash = hashlib.sha256(analyzer.read_bytes()).hexdigest() if analyzer.is_file() else None
    config = {"schema_version": VERSION, "task": args.task, "condition": args.condition,
              "requested_model": args.model, "reasoning_effort": args.reasoning,
              "timeout_seconds": args.timeout_seconds, "suite_root": str(root),
              "fixture_revision": revision, "workflow": workflow, "harness_root": str(harness),
              "harness_revision": harness_revision(harness),
              "analyzer_hash": analyzer_hash, "prompt": prompt(args.condition),
              "prepared_workspace_hash": tree_hash(work, CACHES | {".git"})}
    write_json(output / "trial.json", config)
    write_json(output / "PREPARED.json", {"config_hash": digest(config)})
    print(json.dumps({"trial": str(output), "config_hash": digest(config)}, indent=2))


def trial(raw):
    root = safe_path(raw)
    config = read_json(root / "trial.json")
    require(read_json(root / "PREPARED.json").get("config_hash") == digest(config), "prepared configuration changed")
    require(config.get("schema_version") == VERSION, "unsupported trial schema")
    require(config.get("condition") in ("baseline", "workflow"), "invalid trial condition")
    require(config.get("reasoning_effort") in EFFORTS, "invalid trial reasoning")
    require(type(config.get("timeout_seconds")) is int and config["timeout_seconds"] > 0, "invalid trial timeout")
    require(config.get("prompt") == prompt(config["condition"]), "trial prompt changed")
    require(fixture_revision(safe_path(config["suite_root"]), config["task"]) == config["fixture_revision"],
            "canonical fixture or evaluator changed since prepare")
    require(harness_revision(safe_path(config["harness_root"])) == config["harness_revision"],
            "harness inputs changed since prepare")
    analyzer = safe_path(config["harness_root"]) / "tools/complexity.py"
    current = hashlib.sha256(analyzer.read_bytes()).hexdigest() if analyzer.is_file() else None
    require(current == config["analyzer_hash"], "complexity analyzer changed since prepare")
    work = safe_path(root / "workspace")
    if config["condition"] == "workflow":
        require(installed_snapshot(work) == config["workflow"]["snapshot"], "installed harness changed")
    return root, work, config


def trace_summary(path):
    observations = []
    invalid = 0
    failed = False
    for line in safe_path(path).read_text(errors="replace").splitlines():
        try:
            event = json.loads(line)
            require(isinstance(event, dict), "not an event object")
        except ValueError:
            invalid += 1
            continue
        failed = failed or event.get("type") in ("turn.failed", "error")
        if event.get("type") == "turn.completed":
            observations.append(event.get("usage"))
    usage = {}
    for key in TOKEN_KEYS:
        values = [item.get(key) if isinstance(item, dict) else None for item in observations]
        usage[key] = sum(values) if values and all(type(x) is int and x >= 0 for x in values) else None
    return {"usage": usage, "turns_observed": len(observations), "invalid_json_lines": invalid,
            "model_execution_evidence": "turn event observed" if observations else "no completed turn observed",
            "failure_event": failed, "effective_model": "UNVERIFIED", "child_usage_coverage": "unknown",
            "workflow_invocation": "requires trace audit", "host_instruction_contamination": "unknown"}


def run(args):
    root, work, config = trial(args.trial)
    argv = [args.codex_executable, "exec", "--json", "--ephemeral", "--ignore-user-config",
            "-s", "workspace-write", "-C", str(work), "-m", config["requested_model"],
            "-c", 'model_reasoning_effort="' + config["reasoning_effort"] + '"',
            "-o", str(work / "final.txt"), config["prompt"]]
    if not args.execute:
        print(json.dumps({"execute": False, "network": False, "argv": argv}, indent=2))
        return 0
    require(tree_hash(work, CACHES | {".git"}) == config["prepared_workspace_hash"], "workspace changed before launch")
    # O_EXCL is the one-attempt claim; interruption never silently permits retry.
    with safe_path(root / "STARTED.json").open("x") as marker:
        json.dump({"config_hash": digest(config), "started_at": time.time(), "argv": argv}, marker)
        marker.flush()
        os.fsync(marker.fileno())
    sync_directory(root)
    receipt = {"status": "started", "config_hash": digest(config), "argv": argv,
               "effective_model": "UNVERIFIED", "child_usage_coverage": "unknown",
               "turns_observed": 0, "usage": {key: None for key in TOKEN_KEYS}}
    write_json(root / "run.json", receipt)
    try:
        receipt.update(execute_process(argv, work, root / "trace.jsonl", root / "stderr.txt",
                                       config["timeout_seconds"]))
    except (OSError, ValueError) as exc:
        receipt.update(status="launch_error", error=str(exc), returncode=None)
    if (root / "trace.jsonl").is_file() and not (root / "trace.jsonl").is_symlink():
        receipt.update(trace_summary(root / "trace.jsonl"))
    if receipt["status"] == "completed" and receipt.get("failure_event"):
        receipt["status"] = "event_error"
    write_json(root / "run.json", receipt)
    print(json.dumps(receipt, indent=2))
    return 0 if receipt["status"] == "completed" else 1


def grade_command(args):
    root, work, config = trial(args.trial)
    before = tree_hash(work, CACHES | {".git"})
    fixture = Path(config["suite_root"]) / "tasks" / config["task"]
    result = grade(fixture, work, args.timeout_seconds)
    require(before == tree_hash(work, CACHES | {".git"}), "candidate changed during grading")
    result.update(schema_version=1, config_hash=digest(config), workspace_hash=before,
                  fixture_revision=config["fixture_revision"], timeout_seconds=args.timeout_seconds,
                  metrics=metrics(fixture / "starter", work, Path(config["harness_root"]) / "tools/complexity.py"))
    write_json(root / "grade.json", result)
    print(json.dumps(result, indent=2))
    return 0 if result["correct"] else 1


def validate(args):
    root = suite_root(args)
    results = {}
    for entry in catalog(root)["tasks"]:
        ident = entry["id"]
        if entry["status"] == "planned":
            results[ident] = {"status": "skipped_planned"}
            continue
        fixture_revision(root, ident)
        fixture = root / "tasks" / ident
        starter = grade(fixture, fixture / "starter", args.timeout_seconds)
        with tempfile.TemporaryDirectory(prefix="wysiwyship-reference-") as directory:
            work = safe_path(directory) / "candidate"
            copy_tree(fixture / "starter", work)
            for name, source in files(fixture / "reference").items():
                target = work / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
            reference = grade(fixture, work, args.timeout_seconds)
        acceptance = starter["acceptance"]
        requirement_failures = len(acceptance.get("failures", [])) + len(acceptance.get("errors", []))
        valid_negative = (requirement_failures >= 2 and not acceptance.get("discovery_errors")
                          and acceptance.get("process", {}).get("status") == "nonzero")
        ok = starter["regression"]["successful"] and valid_negative and reference["correct"]
        results[ident] = {"status": "validated" if ok else "invalid", "starter": starter, "reference": reference}
    pilots = [row for row in results.values() if row["status"] != "skipped_planned"]
    print(json.dumps(results, indent=2))
    return 0 if pilots and all(row["status"] == "validated" for row in pilots) else 1


def comparison_row(raw):
    root, work, config = trial(raw)
    require((root / "grade.json").is_file(), "UNGRADED: " + str(root))
    grade_result = read_json(root / "grade.json")
    require(grade_result.get("schema_version") == 1 and type(grade_result.get("correct")) is bool,
            "malformed grade")
    require(grade_result.get("config_hash") == digest(config), "grade configuration changed")
    require(grade_result.get("fixture_revision") == config["fixture_revision"], "grade fixture changed")
    require(grade_result.get("workspace_hash") == tree_hash(work, CACHES | {".git"}), "STALE_GRADE: " + str(root))
    require((root / "run.json").is_file() and (root / "STARTED.json").is_file(), "UNEXECUTED: " + str(root))
    receipt = read_json(root / "run.json")
    require(read_json(root / "STARTED.json").get("config_hash") == digest(config), "launch marker configuration changed")
    require(receipt.get("config_hash") == digest(config), "run configuration changed")
    require(receipt.get("status") in ("completed", "nonzero", "timeout", "interrupted", "event_error", "launch_error"),
            "run did not execute to a terminal outcome")
    key = {name: config[name] for name in ("task", "requested_model", "reasoning_effort", "timeout_seconds",
                                         "fixture_revision", "harness_revision", "analyzer_hash")}
    key["grade_timeout_seconds"] = grade_result["timeout_seconds"]
    return key, {"trial": str(root), "condition": config["condition"], "correct": grade_result["correct"],
                 "run_status": receipt["status"], "duration_seconds": receipt.get("duration_seconds"),
                 "turns_observed": receipt.get("turns_observed", 0),
                 "usage": receipt.get("usage"), "metrics": grade_result["metrics"]}


def compare(args):
    groups = {}
    for raw in args.trials:
        key, row = comparison_row(raw)
        pair = groups.setdefault(digest(key), {"settings": key, "arms": {}})
        require(row["condition"] not in pair["arms"], "duplicate trial condition in pair")
        pair["arms"][row["condition"]] = row
    for pair in groups.values():
        require(set(pair["arms"]) == {"baseline", "workflow"}, "missing pair or mismatched settings/revision")
    pairs = []
    for pair in groups.values():
        baseline, workflow = pair["arms"]["baseline"], pair["arms"]["workflow"]
        comparable = all(arm["turns_observed"] > 0 and arm["run_status"] != "launch_error"
                         for arm in (baseline, workflow))
        pairs.append({**pair, "comparable": comparable,
                      "correctness_delta": int(workflow["correct"]) - int(baseline["correct"]) if comparable else None,
                      "duration_delta_seconds": workflow["duration_seconds"] - baseline["duration_seconds"] if comparable else None})
    print(json.dumps({"pairs": pairs, "interpretation": "paired observations, not a causal benefit claim"}, indent=2))
    return 0 if all(pair["comparable"] for pair in pairs) else 1


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--suite-root")
    commands = result.add_subparsers(dest="command", required=True)
    commands.add_parser("list")
    validate_parser = commands.add_parser("validate")
    validate_parser.add_argument("--timeout-seconds", type=positive, default=120)
    prepare_parser = commands.add_parser("prepare")
    prepare_parser.add_argument("task")
    prepare_parser.add_argument("--condition", choices=("baseline", "workflow"), required=True)
    prepare_parser.add_argument("--output", required=True)
    prepare_parser.add_argument("--model", required=True)
    prepare_parser.add_argument("--reasoning", choices=EFFORTS, required=True)
    prepare_parser.add_argument("--timeout-seconds", type=positive, default=7200)
    prepare_parser.add_argument("--harness-root")
    run_parser = commands.add_parser("run")
    run_parser.add_argument("trial")
    run_parser.add_argument("--execute", action="store_true")
    run_parser.add_argument("--codex-executable", default="codex", help="override for offline fake-CLI tests")
    grade_parser = commands.add_parser("grade")
    grade_parser.add_argument("trial")
    grade_parser.add_argument("--timeout-seconds", type=positive, default=120)
    commands.add_parser("compare").add_argument("trials", nargs="+")
    return result


def main(argv=None):
    try:
        args = parser().parse_args(argv)
        if args.command == "list":
            for task in catalog(suite_root(args))["tasks"]:
                print("\t".join((task["id"], task["status"], task.get("title", ""))))
            return 0
        return {"validate": validate, "prepare": prepare, "run": run,
                "grade": grade_command, "compare": compare}[args.command](args) or 0
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print("error: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
