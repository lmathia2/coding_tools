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
work_units = load_module("work_units", HARNESS / "tools/work_units.py")
check_gate = load_module("check_gate", HARNESS / "tools/check.py")
experiments = load_module("experiments", HARNESS / "tools/experiments.py")
hook_check = load_module("hook_check", HARNESS / "tools/hook_check.py")
spec_bridge = load_module("spec_bridge", HARNESS / "tools/spec_bridge.py")
model_config = load_module("model_config", HARNESS / "config/model_config.py")
configure_models = load_module("configure_models", HARNESS / "config/configure-models.py")
package_builder = load_module("build_packages", HARNESS / "scripts/build_packages.py")
eli5_renderer = load_module("eli5_renderer", HARNESS / "shared/skills/eli5/scripts/render_explainer.py")


class Eli5RendererTests(unittest.TestCase):
    def story(self) -> dict[str, object]:
        return {
            "title": "A safer release gate",
            "subtitle": "What changed and why it helps",
            "audience": "Curious developer",
            "summary": "The project checks the important promises before a release is called complete.",
            "slides": [
                {"title": "The old problem", "bullets": ["Checks could be scattered"], "accent": "coral"},
                {
                    "title": "Think of a preflight checklist",
                    "analogy": {"title": "A pilot's checklist", "body": "One ordered list catches omissions.", "boundary": "Software checks can be automated."},
                    "accent": "mint",
                },
                {
                    "title": "Proof",
                    "metrics": [{"value": "8/8", "label": "checks passed", "detail": "Clean repository"}],
                    "accent": "gold",
                },
            ],
            "closing": {"title": "The takeaway", "body": "The release evidence is now repeatable.", "next_steps": ["Keep project checks current"]},
        }

    def test_renders_offline_fixed_stage_document(self) -> None:
        story = self.story()
        story["summary"] = "Safe even with </script><script>alert('no')</script> text."
        document = eli5_renderer.render_document(story)
        self.assertIn('class="deck-stage"', document)
        self.assertIn("prefers-reduced-motion", document)
        self.assertIn("\\u003c/script\\u003e", document)
        self.assertNotIn("https://", document.lower())
        self.assertNotIn("<script src=", document.lower())

    def test_rejects_overloaded_slides(self) -> None:
        story = self.story()
        story["slides"][0]["bullets"] = [str(index) for index in range(6)]
        with self.assertRaisesRegex(ValueError, "at most 5"):
            eli5_renderer.render_document(story)

    def test_defaults_to_curious_developer_audience(self) -> None:
        story = self.story()
        del story["audience"]
        document = eli5_renderer.render_document(story)
        self.assertIn('"audience":"Curious developer"', document)


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
            global_config = home / ".wysiwyship/config/models.json"
            global_config.parent.mkdir(parents=True)
            global_config.write_text("{}", encoding="utf-8")
            with mock.patch.object(parallel_pi.Path, "home", return_value=home):
                self.assertEqual(parallel_pi.default_model_config(str(project)), global_config)
                project_config = project / ".wysiwyship/config/models.json"
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
            self.assertEqual([item["status"] for item in results], ["PASS", "PASS", "PASS", "PASS"])

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


class WorkUnitTests(unittest.TestCase):
    def initialize_repository(self, root: Path) -> str:
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Harness Test"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "harness@example.invalid"], cwd=root, check=True)
        (root / "README.md").write_text("# Test\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "baseline"], cwd=root, check=True)
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True, check=True).stdout.strip()

    def unit_args(self, root: Path, unit_id: str = "api-contract") -> argparse.Namespace:
        return argparse.Namespace(
            root=str(root), unit_id=unit_id, title="API contract", goal="Add the contract",
            acceptance=["contract is tested"], depends_on=[], owner=["worker-a"], owns=["src/api.py"],
            base_ref="HEAD", docs_impact="required", doc_path=["docs/api.md"], docs_reason=None,
            source_framework=None, source_path=None, activate=True,
        )

    def test_lifecycle_resolves_base_and_requires_ordered_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            base = self.initialize_repository(root)
            args = self.unit_args(root)
            with mock.patch("builtins.print"):
                work_units.initialize_command(args)
            unit = work_units.load_unit(root, args.unit_id)
            self.assertEqual(unit["base_ref"], base)
            for stage in work_units.STAGES[:-1]:
                advance = argparse.Namespace(root=str(root), unit_id=args.unit_id, evidence=f"{stage} evidence", commit=None)
                with mock.patch("builtins.print"):
                    work_units.advance_command(advance)
            self.assertEqual(work_units.active_unit(root)["stage"], "complete")
            self.assertEqual(hook_check.evaluate(root, {}), {})
            self.assertFalse(work_units.active_pointer(root).exists())

    def test_dependency_blocks_implementation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.initialize_repository(root)
            dependency = self.unit_args(root, "dependency")
            dependent = self.unit_args(root, "dependent")
            dependent.depends_on = ["dependency"]
            dependent.owns = ["src/other.py"]
            with mock.patch("builtins.print"):
                work_units.initialize_command(dependency)
                work_units.initialize_command(dependent)
            advance = argparse.Namespace(root=str(root), unit_id="dependent", evidence="plan", commit=None)
            with self.assertRaisesRegex(ValueError, "dependencies are incomplete"):
                work_units.advance_command(advance)

    def test_stop_hook_blocks_an_incomplete_active_unit(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.initialize_repository(root)
            with mock.patch("builtins.print"):
                work_units.initialize_command(self.unit_args(root))
            decision = hook_check.evaluate(root, {})
            self.assertEqual(decision["decision"], "block")
            self.assertEqual(hook_check.evaluate(root, {"stop_hook_active": True}), {})


class SpecBridgeTests(unittest.TestCase):
    def test_detects_supported_artifact_locations(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            paths = [
                root / "specs/001-auth/tasks.md",
                root / "openspec/changes/add-auth/tasks.md",
                root / "_bmad-output/implementation-artifacts/story-auth.md",
            ]
            for path in paths:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("- [ ] task\n", encoding="utf-8")
            detected = {(item.framework, item.path) for item in spec_bridge.detect(root)}
            self.assertEqual(len(detected), 3)

    def test_parses_ids_parallel_hints_dependencies_and_paths(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "tasks.md"
            path.write_text(
                "## User Story 1\n- [ ] T001 [P] Add `src/api.py`\n- [ ] T002 Test contract depends: T001\n- [x] T003 Already done\n",
                encoding="utf-8",
            )
            tasks = spec_bridge.parse_tasks(path)
        self.assertEqual([task.source_id for task in tasks], ["T001", "T002"])
        self.assertTrue(tasks[0].parallel)
        self.assertEqual(tasks[0].owned_paths, ["src/api.py"])
        self.assertEqual(tasks[1].dependencies, ["T001"])
        self.assertEqual(tasks[1].section, "User Story 1")

    def test_import_preserves_source_and_resolved_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Harness Test"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "harness@example.invalid"], cwd=root, check=True)
            source = root / "specs/001-auth/tasks.md"
            source.parent.mkdir(parents=True)
            source.write_text("- [ ] T001 Add `src/api.py`\n- [ ] T002 Add tests depends: T001\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "accepted spec"], cwd=root, check=True)
            plan = spec_bridge.preview(root, "spec-kit", source, False)
            created = spec_bridge.import_preview(root, plan, "worker-a", True)
            self.assertEqual(created[1]["dependencies"], [created[0]["id"]])
            self.assertEqual(created[0]["source"], {"framework": "spec-kit", "path": "specs/001-auth/tasks.md"})
            self.assertEqual(work_units.active_unit(root)["id"], created[0]["id"])


class PackageBuilderTests(unittest.TestCase):
    def test_builds_native_manifests_and_rewrites_runtime_paths(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw) / "packages"
            package_builder.build(output)
            copilot = json.loads((output / "copilot/plugin.json").read_text(encoding="utf-8"))
            claude = json.loads((output / "claude/.claude-plugin/plugin.json").read_text(encoding="utf-8"))
            skill = (output / "claude/skills/engineering-workflow/SKILL.md").read_text(encoding="utf-8")
        self.assertEqual(copilot["version"], package_builder.VERSION)
        self.assertEqual(claude["version"], package_builder.VERSION)
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/tools/check.py", skill)
        self.assertNotIn(".wysiwyship/tools/check.py", skill)

    def test_committed_packages_match_canonical_sources(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            expected = Path(raw) / "packages"
            package_builder.build(expected)
            self.assertEqual(package_builder.compare_directories(expected, HARNESS / "packages"), [])


class InstallerTests(unittest.TestCase):
    def test_install_migrates_previous_brand_without_removing_other_hooks(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw)
            old_support = target / ".smart-harness/config/models.json"
            old_support.parent.mkdir(parents=True)
            old_support.write_text('{"old": true}\n', encoding="utf-8")
            old_copilot_hook = target / ".github/hooks/smart-harness.json"
            old_copilot_hook.parent.mkdir(parents=True)
            old_copilot_hook.write_text("{}\n", encoding="utf-8")
            settings = target / ".claude/settings.json"
            settings.parent.mkdir(parents=True)
            settings.write_text(json.dumps({"hooks": {"Stop": [{"hooks": [
                {"type": "command", "command": installer.PREVIOUS_CLAUDE_HOOK_COMMAND},
                {"type": "command", "command": "python3 keep-me.py"},
            ]}]}}), encoding="utf-8")

            installer.Installer("project", "all", target, False).run()

            self.assertFalse((target / ".smart-harness").exists())
            self.assertFalse(old_copilot_hook.exists())
            self.assertTrue((target / ".wysiwyship/install-manifest.json").exists())
            installed = json.loads(settings.read_text(encoding="utf-8"))
            commands = [handler["command"] for group in installed["hooks"]["Stop"] for handler in group["hooks"]]
            self.assertNotIn(installer.PREVIOUS_CLAUDE_HOOK_COMMAND, commands)
            self.assertIn("python3 keep-me.py", commands)
            self.assertIn(installer.CLAUDE_HOOK_COMMAND, commands)

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
            manifest = target / ".wysiwyship/install-manifest.json"
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
            manifest_path = target / ".wysiwyship/install-manifest.json"
            first = json.loads(manifest_path.read_text(encoding="utf-8"))
            installer.Installer("project", "all", target, False).run()
            second = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(first["outputs"], second["outputs"])
            self.assertEqual(installer.print_status(target), 0)
            self.assertTrue((target / ".wysiwyship/vendor/licenses/SUPERPOWERS-MIT.txt").exists())
            self.assertTrue((target / ".wysiwyship/tools/complexity.py").exists())
            self.assertTrue((target / ".wysiwyship/tools/commit_docs.py").exists())
            self.assertTrue((target / ".wysiwyship/tools/check.py").exists())
            self.assertTrue((target / ".wysiwyship/tools/experiments.py").exists())
            self.assertTrue((target / ".wysiwyship/tools/work_units.py").exists())
            self.assertTrue((target / ".wysiwyship/tools/hook_check.py").exists())
            self.assertTrue((target / ".wysiwyship/tools/spec_bridge.py").exists())
            self.assertTrue((target / ".wysiwyship/config/models.json").exists())
            self.assertTrue((target / ".wysiwyship/config/checks.json").exists())
            self.assertTrue((target / ".github/hooks/wysiwyship.json").exists())
            settings = json.loads((target / ".claude/settings.json").read_text(encoding="utf-8"))
            self.assertEqual(settings["hooks"]["Stop"][0]["hooks"][0]["command"], installer.CLAUDE_HOOK_COMMAND)

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
            first = json.loads((target / ".wysiwyship/install-manifest.json").read_text(encoding="utf-8"))
            installer.Installer("project", "claude", target, False).run()
            second = json.loads((target / ".wysiwyship/install-manifest.json").read_text(encoding="utf-8"))
            self.assertTrue(first["backup_history"])
            self.assertEqual(second["backup_history"][: len(first["backup_history"])], first["backup_history"])
            self.assertEqual(len(second["backup_history"]), len(first["backup_history"]) + 1)
            self.assertEqual(second["platforms"], ["claude", "copilot"])

    def test_global_layout_uses_shared_installer(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw)
            installer.Installer("global", "pi", target, False).run()
            manifest = json.loads((target / ".wysiwyship/install-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["scope"], "global")
            self.assertTrue((target / ".pi/agent/prompts/dev.md").exists())
            self.assertTrue((target / ".pi/agent/wysiwyship/parallel-pi.py").exists())
            self.assertTrue((target / ".claude/skills/engineering-workflow/SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
