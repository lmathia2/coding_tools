from __future__ import annotations

import argparse
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


HARNESS = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


complexity = load_module("complexity", HARNESS / "tools/complexity.py")
parallel_pi = load_module("parallel_pi", HARNESS / "pi/tools/parallel-pi.py")
installer = load_module("install_harness", HARNESS / "scripts/install_harness.py")
commit_docs = load_module("commit_docs", HARNESS / "tools/commit_docs.py")
check_gate = load_module("check_gate", HARNESS / "tools/check.py")
experiments = load_module("experiments", HARNESS / "tools/experiments.py")
model_config = load_module("model_config", HARNESS / "config/model_config.py")
configure_models = load_module("configure_models", HARNESS / "config/configure-models.py")


class ComplexityTests(unittest.TestCase):
    def test_counts_decisions_and_boolean_operators(self) -> None:
        result = complexity.analyze_code(
            """
def decide(items, enabled):
    for item in items:
        if enabled and item.ready:
            return True
    return False
"""
        )
        function = result["functions"][0]
        self.assertEqual(function["complexity_score"], 4)
        self.assertEqual(function["status"], "Excellent")

    def test_nested_function_is_scored_independently(self) -> None:
        result = complexity.analyze_code(
            """
def outer():
    def inner(value):
        if value:
            return 1
        return 0
    return inner
"""
        )
        scores = {item["qualified_name"]: item["complexity_score"] for item in result["functions"]}
        self.assertEqual(scores, {"outer": 1, "outer.inner": 2})

    def test_invalid_python_is_reported(self) -> None:
        result = complexity.analyze_code("def broken(:\n")
        self.assertIn("Invalid Python syntax", result["error"])

    @unittest.skipUnless(sys.version_info >= (3, 10), "match syntax requires Python 3.10+")
    def test_match_cases_each_add_a_decision(self) -> None:
        result = complexity.analyze_code(
            """
def classify(value):
    match value:
        case 1:
            return "one"
        case _:
            return "other"
"""
        )
        self.assertEqual(result["functions"][0]["complexity_score"], 3)

    def test_attaches_baseline_delta_by_qualified_name(self) -> None:
        current = [{"qualified_name": "Service.run", "complexity_score": 7}]
        baseline = [{"qualified_name": "Service.run", "complexity_score": 5}]
        complexity.attach_baseline(current, baseline)
        self.assertEqual(current[0]["baseline_score"], 5)
        self.assertEqual(current[0]["delta"], 2)


class ParallelPiTests(unittest.TestCase):
    def test_timeout_bytes_are_json_serializable(self) -> None:
        timeout = subprocess.TimeoutExpired("pi", 1, output=b"partial stdout", stderr=b"partial stderr")
        with mock.patch.object(parallel_pi.subprocess, "run", side_effect=timeout):
            result = parallel_pi.run_task({"name": "probe", "prompt": "probe"}, ".", "pi")
        self.assertEqual(result["stdout"], "partial stdout")
        self.assertEqual(result["stderr"], "partial stderr")
        self.assertGreaterEqual(result["duration_seconds"], 0)
        json.dumps(result)

    def test_read_only_capability_rejects_bash(self) -> None:
        with self.assertRaisesRegex(ValueError, "outside read_only"):
            parallel_pi.resolve_tools({"name": "probe", "tools": "read,bash"}, "read_only")

    def test_execute_capability_enables_bash_by_default(self) -> None:
        tools = set(parallel_pi.resolve_tools({"name": "probe"}, "execute").split(","))
        self.assertEqual(tools, parallel_pi.EXECUTE_TOOLS)

    def test_task_cwd_must_stay_under_root(self) -> None:
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as outside:
            task = {"name": "probe", "prompt": "probe", "cwd": outside}
            with self.assertRaisesRegex(ValueError, "escapes the configured root"):
                parallel_pi.run_task(task, root, "pi")

    def test_task_name_and_prompt_must_be_strings(self) -> None:
        with mock.patch.object(parallel_pi.sys, "stdin", io.StringIO('[{"name": ["bad"], "prompt": "x"}]')):
            with self.assertRaises(SystemExit):
                parallel_pi.load_tasks(None)

    def test_profile_supplies_model_and_thinking_by_role(self) -> None:
        settings = {
            "workflows": {"dev": {"model": "coordinator-model", "reasoning": "high"}},
            "roles": {"fast": {"model": "fast-model", "reasoning": "low"}},
        }
        task = parallel_pi.apply_runtime_defaults({"name": "probe", "prompt": "probe"}, settings, "dev")
        self.assertEqual(task["role"], "fast")
        self.assertEqual(task["model"], "fast-model")
        self.assertEqual(task["thinking"], "low")

    def test_explicit_task_runtime_overrides_profile(self) -> None:
        settings = {
            "workflows": {},
            "roles": {"deep": {"model": "profile-model", "reasoning": "high"}},
        }
        task = {"name": "probe", "prompt": "probe", "role": "deep", "model": "experiment", "thinking": "medium"}
        resolved = parallel_pi.apply_runtime_defaults(task, settings, "review_pr")
        self.assertEqual(resolved["model"], "experiment")
        self.assertEqual(resolved["thinking"], "medium")

    def test_model_config_prefers_project_then_global(self) -> None:
        with tempfile.TemporaryDirectory() as project_raw, tempfile.TemporaryDirectory() as home_raw:
            project = Path(project_raw)
            home = Path(home_raw)
            global_config = home / ".smart-harness/config/models.json"
            global_config.parent.mkdir(parents=True)
            global_config.write_text("{}", encoding="utf-8")
            with mock.patch.object(parallel_pi.Path, "home", return_value=home):
                self.assertEqual(parallel_pi.default_model_config(str(project)), global_config)
                project_config = project / ".smart-harness/config/models.json"
                project_config.parent.mkdir(parents=True)
                project_config.write_text("{}", encoding="utf-8")
                self.assertEqual(parallel_pi.default_model_config(str(project)), project_config.resolve())


class ModelConfigurationTests(unittest.TestCase):
    def test_repository_profiles_are_valid_and_resolvable(self) -> None:
        config = model_config.load_config(HARNESS / "config/models.json")
        self.assertEqual(set(config["profiles"]), {"balanced", "economy", "quality"})
        _, balanced = model_config.get_profile(config, "balanced")
        self.assertEqual(model_config.resolve_spec(balanced, "copilot", "coordinator", "dev")["reasoning"], "high")
        self.assertEqual(model_config.resolve_spec(balanced, "pi", "fast")["reasoning"], "low")

    def test_copilot_rewrite_translates_canonical_reasoning(self) -> None:
        profile = {
            "copilot": {
                "workflows": {"dev": {"model": "Test Model", "reasoning": "medium"}},
                "roles": {},
            }
        }
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "dev.agent.md"
            path.write_text("---\nname: Test\nmodel: Old\n---\n<!-- harness-role: coordinator -->\n<!-- harness-workflow: dev -->\n", encoding="utf-8")
            updated = configure_models.rewrite(path, "copilot", profile)
        self.assertIn("model: Test Model", updated)
        self.assertIn("reasoningEffort: medium", updated)


class CommitDocumentationTests(unittest.TestCase):
    def test_code_and_documentation_in_same_commit_pass(self) -> None:
        result = commit_docs.evaluate_commit("abc", "change", "change", ["src/app.py", "docs/api.md"])
        self.assertEqual(result["status"], "PASS")

    def test_concrete_no_impact_trailer_passes(self) -> None:
        message = "Refactor parser\n\nDocs-Impact: none — behavior and contracts are unchanged"
        result = commit_docs.evaluate_commit("abc", "change", message, ["src/parser.py"])
        self.assertEqual(result["status"], "PASS")

    def test_code_only_commit_without_reason_fails(self) -> None:
        result = commit_docs.evaluate_commit("abc", "change", "change", ["src/app.py", "tests/test_app.py"])
        self.assertEqual(result["status"], "FAIL")

    def test_git_range_inspection(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw)
            subprocess.run(["git", "init", "-q"], cwd=target, check=True)
            subprocess.run(["git", "config", "user.name", "Harness Test"], cwd=target, check=True)
            subprocess.run(["git", "config", "user.email", "harness@example.invalid"], cwd=target, check=True)
            (target / "README.md").write_text("# Test\n", encoding="utf-8")
            subprocess.run(["git", "add", "README.md"], cwd=target, check=True)
            subprocess.run(["git", "commit", "-qm", "baseline"], cwd=target, check=True)
            base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=target, text=True, capture_output=True, check=True).stdout.strip()
            (target / "app.py").write_text("value = 1\n", encoding="utf-8")
            subprocess.run(["git", "add", "app.py"], cwd=target, check=True)
            subprocess.run(["git", "commit", "-qm", "Add app"], cwd=target, check=True)
            results = commit_docs.inspect_range(base, "HEAD", str(target))
            self.assertEqual([result["status"] for result in results], ["FAIL"])


class LifecycleGateTests(unittest.TestCase):
    def make_repository(self, root: Path) -> str:
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Harness Test"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "harness@example.invalid"], cwd=root, check=True)
        (root / "README.md").write_text("# Test\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "baseline"], cwd=root, check=True)
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True, check=True).stdout.strip()

    def test_changed_function_complexity_ignores_untouched_functions(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            base = self.make_repository(root)
            source = "def old(a, b, c):\n    if a and b and c:\n        return 1\n    return 0\n\ndef changed():\n    return 1\n"
            (root / "app.py").write_text(source, encoding="utf-8")
            (root / "docs.md").write_text("# App\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "Add app and docs"], cwd=root, check=True)
            base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True, check=True).stdout.strip()
            (root / "app.py").write_text(source.replace("return 1\n", "return 2\n", 1), encoding="utf-8")
            subprocess.run(["git", "add", "app.py"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "Change old\n\nDocs-Impact: none — return value only"], cwd=root, check=True)
            item = check_gate.complexity_check(root, base, "HEAD", 20)
            names = [function["qualified_name"] for file in item["details"] for function in file.get("functions", [])]
            self.assertEqual(names, ["old"])

    def test_gate_composes_docs_complexity_and_commands(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            base = self.make_repository(root)
            (root / "app.py").write_text("def run():\n    return 1\n", encoding="utf-8")
            (root / "docs.md").write_text("# Contract\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "Add app contract"], cwd=root, check=True)
            config = {
                "documentation": {"enabled": True},
                "complexity": {"enabled": True, "fail_above": 20},
                "commands": [{"name": "probe", "argv": [sys.executable, "-c", "print('ok')"]}],
                "repository": {"require_clean": False},
            }
            results = check_gate.run_checks(root, base, "HEAD", config, False)
            self.assertEqual([item["status"] for item in results], ["PASS", "PASS", "PASS"])

    def test_command_cwd_cannot_escape_repository(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            with self.assertRaisesRegex(ValueError, "escapes repository root"):
                check_gate.safe_command_cwd(Path(raw), "../outside")


class ExperimentTests(unittest.TestCase):
    def test_profile_resolves_model_and_reasoning(self) -> None:
        profile, spec = experiments.read_profile(
            HARNESS / "config/models.json", "quality", "pi", "deep", "dev"
        )
        self.assertEqual(profile, "quality")
        self.assertIn("model", spec)
        self.assertEqual(spec["reasoning"], "xhigh")

    def test_append_and_load_preserve_optional_measurements(self) -> None:
        metadata = {
            "workflow": "dev", "role": "normal", "platform": "pi",
            "profile": "balanced", "model": None, "reasoning": "medium",
        }
        record = experiments.make_record(
            metadata,
            status="pass",
            verification="pass",
            duration_seconds=2.5,
            complexity_before=9,
            complexity_after=6,
        )
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "experiments.jsonl"
            experiments.append_records(path, [record])
            loaded = experiments.load_records(path)
        self.assertEqual(loaded[0]["complexity_delta"], -3)
        self.assertIsNone(loaded[0]["cost_usd"])

    def test_comparison_reports_observed_sample_counts(self) -> None:
        records = [
            {"profile": "quality", "status": "pass", "verification": "pass", "duration_seconds": 10},
            {"profile": "quality", "status": "fail", "verification": "unknown", "duration_seconds": None},
        ]
        summary = experiments.summarize(records, "profile")[0]
        self.assertEqual(summary["outcome"], {"reported": 2, "rate": 0.5})
        self.assertEqual(summary["verification"], {"reported": 1, "rate": 1.0})
        self.assertEqual(summary["metrics"]["duration_seconds"], {"reported": 1, "average": 10.0})

    def test_pi_result_import_uses_measured_duration(self) -> None:
        args = argparse.Namespace(workflow="dev", profile="economy")
        record = experiments.pi_record(
            args,
            {
                "name": "probe", "role": "fast", "model": "test", "thinking": "low",
                "returncode": 0, "timed_out": False, "duration_seconds": 1.25,
            },
        )
        self.assertEqual(record["status"], "pass")
        self.assertEqual(record["duration_seconds"], 1.25)


class InstallerTests(unittest.TestCase):
    def test_invalid_pi_settings_fail_before_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw)
            settings = target / ".pi/settings.json"
            settings.parent.mkdir(parents=True)
            settings.write_text("not-json", encoding="utf-8")
            instance = installer.Installer("project", "all", target, False)
            with self.assertRaises(json.JSONDecodeError):
                instance.run()
            self.assertFalse((target / ".claude").exists())
            self.assertEqual(settings.read_text(encoding="utf-8"), "not-json")

    def test_invalid_manifest_fails_before_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw)
            manifest = target / ".smart-harness/install-manifest.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text('{"schema_version": 1, "platforms": [], "backup_history": [], "outputs": [{"path": "../../escape", "sha256": "x"}]}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "stay within the install root"):
                installer.Installer("project", "claude", target, False).run()
            self.assertFalse((target / ".claude").exists())

    def test_failure_rolls_back_removed_legacy_content(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw)
            legacy = target / ".claude/skills/plan-first/SKILL.md"
            legacy.parent.mkdir(parents=True)
            legacy.write_text("user content", encoding="utf-8")
            instance = installer.Installer("project", "all", target, False)
            with mock.patch.object(instance, "install_pi", side_effect=RuntimeError("probe failure")):
                with self.assertRaisesRegex(RuntimeError, "probe failure"):
                    instance.run()
            self.assertEqual(legacy.read_text(encoding="utf-8"), "user content")
            self.assertFalse((target / ".github/agents/dev.agent.md").exists())

    def test_install_is_idempotent_and_manifest_is_current(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw)
            installer.Installer("project", "all", target, False).run()
            manifest_path = target / ".smart-harness/install-manifest.json"
            first = json.loads(manifest_path.read_text(encoding="utf-8"))
            installer.Installer("project", "all", target, False).run()
            second = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(first["outputs"], second["outputs"])
            self.assertEqual(installer.print_status(target), 0)
            self.assertTrue((target / ".smart-harness/vendor/licenses/SUPERPOWERS-MIT.txt").exists())
            self.assertTrue((target / ".smart-harness/tools/complexity.py").exists())
            self.assertTrue((target / ".smart-harness/tools/commit_docs.py").exists())
            self.assertTrue((target / ".smart-harness/tools/check.py").exists())
            self.assertTrue((target / ".smart-harness/tools/experiments.py").exists())
            self.assertTrue((target / ".smart-harness/config/models.json").exists())
            self.assertTrue((target / ".smart-harness/config/checks.json").exists())

    def test_dry_run_does_not_mutate_target(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw)
            installer.Installer("project", "all", target, True).run()
            self.assertEqual(list(target.iterdir()), [])

    def test_manifest_preserves_backup_history_and_other_platforms(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw)
            existing = target / ".claude/skills/engineering-workflow/SKILL.md"
            existing.parent.mkdir(parents=True)
            existing.write_text("old", encoding="utf-8")
            installer.Installer("project", "copilot", target, False).run()
            first = json.loads((target / ".smart-harness/install-manifest.json").read_text(encoding="utf-8"))
            installer.Installer("project", "claude", target, False).run()
            second = json.loads((target / ".smart-harness/install-manifest.json").read_text(encoding="utf-8"))
            self.assertTrue(first["backup_history"])
            self.assertEqual(second["backup_history"][: len(first["backup_history"])], first["backup_history"])
            self.assertEqual(len(second["backup_history"]), len(first["backup_history"]) + 1)
            self.assertEqual(second["platforms"], ["claude", "copilot"])

    def test_global_layout_uses_shared_installer(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw)
            installer.Installer("global", "pi", target, False).run()
            manifest = json.loads((target / ".smart-harness/install-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["scope"], "global")
            self.assertTrue((target / ".pi/agent/prompts/dev.md").exists())
            self.assertTrue((target / ".pi/agent/smart-harness/parallel-pi.py").exists())
            self.assertTrue((target / ".claude/skills/engineering-workflow/SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
