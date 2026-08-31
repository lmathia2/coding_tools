"""Offline boundaries; fake executables only. No model/auth/network calls."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("eval_runner", ROOT / "runner.py")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)
HARNESS = Path(os.environ.get("EVAL_TEST_HARNESS_ROOT", str(ROOT.parent)))


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text).lstrip())


def fixture(base):
    runner.write_json(base / "catalog.json", {
        "schema_version": 1, "suite_version": "0.1.0-pilot",
        "tasks": [{"id": "durable-jobs", "status": "pilot", "version": "1", "title": "pilot"},
                  {"id": "future-task", "status": "planned", "title": "planned"}]})
    root = base / "tasks/durable-jobs"
    write(root / "task.md", "Implement answer() and preserve the public CLI. Add documentation.")
    write(root / "starter/pkg/__init__.py", "def answer():\n    return 0\n")
    write(root / "starter/pkg/__main__.py", "from . import answer\nprint(answer())\n")
    write(root / "starter/tests/test_original.py", """
        from pathlib import Path
        import unittest
        from pkg import answer
        class Original(unittest.TestCase):
            def test_contract(self):
                self.assertIn(answer(), (0, 1))
                self.assertFalse(Path('contamination').exists())
                Path('contamination').write_text('regression mutation')
    """)
    write(root / "starter/docs/README.md", "Original documentation.")
    write(root / "reference/pkg/__init__.py", "def answer():\n    return 1\n")
    write(root / "acceptance/helper.py", "EXPECTED = 1\n")
    write(root / "acceptance/legacy_v1.sql", "SELECT 1;\n")
    write(root / "acceptance/test_acceptance.py", """
        import subprocess
        import sys
        import unittest
        from pathlib import Path
        from helper import EXPECTED
        from pkg import answer
        class Acceptance(unittest.TestCase):
            def test_value(self):
                self.assertEqual(answer(), EXPECTED)
            def test_cli(self):
                output = subprocess.check_output([sys.executable, '-m', 'pkg'], text=True)
                self.assertEqual(output.strip(), str(EXPECTED))
            def test_fresh_copy_and_helpers(self):
                self.assertFalse(Path('contamination').exists())
                self.assertFalse(Path('tests').exists())
                self.assertTrue(Path(__file__).with_name('legacy_v1.sql').exists())
    """)
    return root


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="runner-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.suite = self.root / "evals"
        self.suite.mkdir()
        self.fixture = fixture(self.suite)
        self.counter = 0

    def cli(self, *args):
        output, error = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            code = runner.main(list(args))
        return code, output.getvalue(), error.getvalue()

    def prepare(self, condition="baseline", timeout=2, model="exact-test-model"):
        self.counter += 1
        trial = self.root / ("trial-" + str(self.counter))
        args = ["--suite-root", str(self.suite), "prepare", "durable-jobs", "--condition", condition,
                "--output", str(trial), "--model", model, "--reasoning", "high",
                "--timeout-seconds", str(timeout), "--harness-root", str(HARNESS)]
        result = self.cli(*args)
        self.assertEqual(result[0], 0, result)
        return trial

    def fake(self, body):
        path = self.root / ("fake-codex-" + str(self.counter))
        write(path, "#!" + sys.executable + "\n" + textwrap.dedent(body).lstrip())
        path.chmod(0o700)
        return str(path)

    def execute(self, trial, body="print('{\"type\": \"turn.completed\", \"usage\": {\"input_tokens\": 2, \"output_tokens\": 1}}')"):
        return self.cli("run", str(trial), "--execute", "--codex-executable", self.fake(body))

    def test_validate_requires_real_failures_and_skips_planned(self):
        code, output, error = self.cli("--suite-root", str(self.suite), "validate")
        self.assertEqual(code, 0, error)
        result = json.loads(output)
        self.assertEqual(result["future-task"]["status"], "skipped_planned")
        self.assertEqual(len(result["durable-jobs"]["starter"]["acceptance"]["failures"]), 2)
        self.assertTrue(result["durable-jobs"]["reference"]["correct"])
        catalog = runner.read_json(self.suite / "catalog.json")
        catalog["tasks"] = catalog["tasks"][1:]
        runner.write_json(self.suite / "catalog.json", catalog)
        self.assertNotEqual(self.cli("--suite-root", str(self.suite), "validate")[0], 0)

    def test_prepare_pins_revision_copies_no_solution_and_commits(self):
        trial = self.prepare()
        config = runner.read_json(trial / "trial.json")
        self.assertEqual(config["fixture_revision"]["suite_version"], "0.1.0-pilot")
        self.assertIn("return 0", (trial / "workspace/pkg/__init__.py").read_text())
        self.assertFalse((trial / "workspace/reference").exists())
        self.assertFalse((trial / "workspace/acceptance").exists())
        status = subprocess.check_output(["git", "status", "--porcelain"], cwd=trial / "workspace", text=True)
        self.assertEqual(status, "")

    def test_no_overwrite_and_unsafe_destinations(self):
        trial = self.prepare()
        common = ["--suite-root", str(self.suite), "prepare", "durable-jobs", "--condition", "baseline",
                  "--model", "m", "--reasoning", "low"]
        for output in (trial, self.suite / "nested", self.root, Path("relative")):
            with self.subTest(output=output):
                self.assertNotEqual(self.cli(*common, "--output", str(output))[0], 0)
        alias = self.root / "alias"
        alias.symlink_to(self.root, target_is_directory=True)
        self.assertNotEqual(self.cli(*common, "--output", str(alias / "new"))[0], 0)
        target = self.root / "dangling"
        target.symlink_to(self.root / "nonexistent")
        self.assertNotEqual(self.cli(*common, "--output", str(target))[0], 0)

    def test_planned_bad_catalog_and_bad_timeout(self):
        common = ["--suite-root", str(self.suite), "prepare", "future-task", "--condition", "baseline",
                  "--model", "m", "--reasoning", "low", "--output", str(self.root / "new")]
        self.assertNotEqual(self.cli(*common)[0], 0)
        with self.assertRaises(SystemExit):
            self.cli(*common, "--timeout-seconds", "0")
        catalog = runner.read_json(self.suite / "catalog.json")
        for bad in ("../escape", "duplicate"):
            changed = dict(catalog)
            changed["tasks"] = [dict(catalog["tasks"][0], id=bad)]
            if bad == "duplicate":
                changed["tasks"] *= 2
            runner.write_json(self.suite / "catalog.json", changed)
            self.assertNotEqual(self.cli("--suite-root", str(self.suite), "list")[0], 0)

    def test_fixture_symlinks_and_caches(self):
        revision = runner.fixture_revision(self.suite, "durable-jobs")
        write(self.fixture / "starter/__pycache__/ignored.pyc", "cache")
        self.assertEqual(revision, runner.fixture_revision(self.suite, "durable-jobs"))
        (self.fixture / "starter/link").symlink_to(self.fixture / "task.md")
        with self.assertRaisesRegex(ValueError, "symlink"):
            runner.fixture_revision(self.suite, "durable-jobs")

    def test_fixture_and_config_mutations_rejected(self):
        trial = self.prepare()
        original = (self.fixture / "starter/tests/test_original.py").read_text()
        write(self.fixture / "starter/tests/test_original.py", "# changed canonical tests")
        for args in (("run", str(trial)), ("grade", str(trial)), ("compare", str(trial))):
            self.assertNotEqual(self.cli(*args)[0], 0)
        write(self.fixture / "starter/tests/test_original.py", original)
        config = runner.read_json(trial / "trial.json")
        config["requested_model"] = "changed"
        runner.write_json(trial / "trial.json", config)
        self.assertIn("prepared configuration changed", self.cli("run", str(trial))[2])

    def test_agent_tests_cannot_replace_canonical_tests(self):
        trial = self.prepare()
        write(trial / "workspace/pkg/__init__.py", "def answer():\n    return 7\n")
        write(trial / "workspace/tests/test_original.py", "# maliciously remove regression")
        write(trial / "workspace/test_agent.py", "raise RuntimeError('must not import agent tests')")
        result = self.cli("grade", str(trial))
        self.assertEqual(result[0], 1, result)
        grade = runner.read_json(trial / "grade.json")
        self.assertEqual(grade["regression"]["tests"], 1)
        self.assertEqual(len(grade["regression"]["failures"]), 1)
        self.assertFalse((trial / "workspace/contamination").exists())

    def test_zero_discovery_skip_expected_failure_and_fake_stdout_fail(self):
        cases = {
            "zero": "# no tests\n",
            "discovery": "raise RuntimeError('discovery failure')\n",
            "skip": "import unittest\n@unittest.skip('no')\nclass T(unittest.TestCase):\n def test_x(self): pass\n",
            "expected": "import unittest\nclass T(unittest.TestCase):\n @unittest.expectedFailure\n def test_x(self): self.fail()\n",
            "fake_stdout": "print('{\"successful\": true, \"tests\": 42}')\n",
        }
        for name, body in cases.items():
            with self.subTest(name=name):
                tests = self.root / name
                write(tests / "test_case.py", body)
                report = runner.test_group(self.fixture / "starter", tests, 2)
                self.assertFalse(report["successful"], report)

    def test_malformed_grader_report_and_false_exit_zero_fail(self):
        valid = {"schema_version": 1, "successful": True, "tests": 1, "failures": [], "errors": [],
                 "discovery_errors": [], "skips": [], "expected_failures": [], "unexpected_successes": []}
        cases = ["not json", "[]", '{"schema_version": 1, "successful": true}',
                 json.dumps(dict(valid, tests=0)), json.dumps(dict(valid, skips=[["test", "skip"]]))]
        for payload in cases:
            def fake_process(argv, cwd, stdout, stderr, timeout, env):
                Path(stdout).write_text("")
                Path(stderr).write_text("")
                Path(argv[-1]).write_text(payload)
                return {"status": "completed", "returncode": 0}
            with self.subTest(payload=payload), mock.patch.object(runner, "execute_process", side_effect=fake_process):
                report = runner.test_group(self.fixture / "starter", self.fixture / "acceptance", 2)
            self.assertFalse(report["successful"])

    def test_validation_allows_missing_api_errors_but_not_discovery_failure(self):
        write(self.fixture / "reference/pkg/__init__.py", "def answer():\n return 1\ndef added_api():\n return 1\n")
        write(self.fixture / "acceptance/test_acceptance.py", """
            import unittest
            import pkg
            class Requirements(unittest.TestCase):
                def test_api(self): self.assertEqual(pkg.added_api(), 1)
                def test_api_again(self): self.assertGreater(pkg.added_api(), 0)
        """)
        self.assertEqual(self.cli("--suite-root", str(self.suite), "validate")[0], 0)
        write(self.fixture / "acceptance/test_acceptance.py", "from pkg import added_api\n")
        result = self.cli("--suite-root", str(self.suite), "validate")
        self.assertEqual(result[0], 1, result)

    def test_grader_timeout_is_not_a_pass(self):
        tests = self.root / "hanging-tests"
        write(tests / "test_timeout.py", "import time\ntime.sleep(30)\n")
        result = runner.test_group(self.fixture / "starter", tests, 0.1)
        self.assertFalse(result["successful"])
        self.assertEqual(result["process"]["status"], "timeout")

    def test_grading_excludes_private_runtime_and_agent_tests(self):
        candidate = self.root / "private-candidate"
        runner.copy_tree(self.fixture / "starter", candidate)
        for name in runner.PRIVATE - {".git"}:
            write(candidate / name / "secret", "runtime")
        write(candidate / "test_agent.py", "raise RuntimeError('not canonical')")
        tests = self.root / "private-tests"
        write(tests / "test_private.py", """
            from pathlib import Path
            import unittest
            class Private(unittest.TestCase):
                def test_fresh(self):
                    self.assertFalse(any(path.name.startswith('.') for path in Path.cwd().iterdir()))
                    self.assertFalse(Path('test_agent.py').exists())
                    self.assertFalse(Path('tests').exists())
        """)
        self.assertTrue(runner.test_group(candidate, tests, 2)["successful"])

    def test_preview_and_prelaunch_mutation_never_execute(self):
        trial = self.prepare()
        with mock.patch.object(runner.subprocess, "Popen", side_effect=AssertionError("launch forbidden")):
            code, output, error = self.cli("run", str(trial))
            self.assertEqual(code, 0, error)
            argv = json.loads(output)["argv"]
            self.assertIn("--ignore-user-config", argv)
            self.assertIn('model_reasoning_effort="high"', argv)
        self.assertFalse((trial / "STARTED.json").exists())
        write(trial / "workspace/new.py", "# edited")
        self.assertIn("workspace changed before launch", self.execute(trial)[2])

    def test_fake_success_nested_usage_and_no_rerun(self):
        trial = self.prepare()
        code, output, error = self.execute(trial, """
            import json
            print(json.dumps({'type': 'turn.completed', 'usage': {'input_tokens': 3, 'cached_input_tokens': 1, 'output_tokens': 4}}))
            print('invalid json')
            print(json.dumps({'type': 'turn.completed', 'usage': {'input_tokens': 5, 'output_tokens': 2}}))
        """)
        self.assertEqual(code, 0, error)
        receipt = json.loads(output)
        self.assertEqual(receipt["usage"], {"input_tokens": 8, "cached_input_tokens": None, "output_tokens": 6})
        self.assertEqual(receipt["invalid_json_lines"], 1)
        self.assertEqual(receipt["effective_model"], "UNVERIFIED")
        self.assertNotEqual(self.execute(trial)[0], 0)

    def test_fake_nonzero_event_error_timeout_and_launch_error(self):
        cases = [("nonzero", "raise SystemExit(3)"),
                 ("event_error", "print('{\"type\": \"turn.failed\"}')"),
                 ("timeout", "import time\ntime.sleep(20)")]
        for status, body in cases:
            with self.subTest(status=status):
                trial = self.prepare(timeout=1)
                self.assertEqual(self.execute(trial, body)[0], 1)
                self.assertEqual(runner.read_json(trial / "run.json")["status"], status)
                self.assertNotEqual(self.execute(trial)[0], 0)
        trial = self.prepare()
        result = self.cli("run", str(trial), "--execute", "--codex-executable", str(self.root / "missing"))
        self.assertEqual(result[0], 1, result)
        self.assertEqual(runner.read_json(trial / "run.json")["status"], "launch_error")
        linked_trial = self.prepare()
        sentinel = self.root / "private-sentinel"
        sentinel.write_text("do not read or overwrite")
        (linked_trial / "trace.jsonl").symlink_to(sentinel)
        self.assertEqual(self.execute(linked_trial)[0], 1)
        self.assertEqual(runner.read_json(linked_trial / "run.json")["status"], "launch_error")
        self.assertEqual(sentinel.read_text(), "do not read or overwrite")

    @unittest.skipUnless(os.name == "posix", "process-group semantics are POSIX")
    def test_timeout_kills_term_ignoring_descendant(self):
        trial = self.prepare(timeout=1)
        pidfile = self.root / "child.pid"
        heartbeat = self.root / "heartbeat"
        child_code = ("import signal,time\nfrom pathlib import Path\n"
                      "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
                      "while True:\n Path(%r).write_text(str(time.monotonic()))\n time.sleep(0.03)\n") % str(heartbeat)
        body = """
            import subprocess, sys, time
            child = subprocess.Popen([sys.executable, '-c', %r])
            open(%r, 'w').write(str(child.pid))
            time.sleep(60)
        """ % (child_code, str(pidfile))
        self.assertEqual(self.execute(trial, body)[0], 1)
        pid = int(pidfile.read_text())
        final_heartbeat = heartbeat.read_text()
        time.sleep(0.2)
        if heartbeat.read_text() != final_heartbeat:
            os.kill(pid, signal.SIGKILL)
            self.fail("descendant survived runner timeout")

    def test_interrupt_cleans_up_and_records(self):
        process = mock.Mock()
        process.wait.side_effect = [KeyboardInterrupt(), 0, 0]
        process.returncode = -9
        process.pid = 12345
        trial = self.prepare()
        with mock.patch.object(runner.subprocess, "Popen", return_value=process), mock.patch.object(runner.os, "killpg") as kill:
            result = self.cli("run", str(trial), "--execute")
        self.assertEqual(result[0], 1, result)
        self.assertEqual(runner.read_json(trial / "run.json")["status"], "interrupted")
        self.assertIn(mock.call(12345, signal.SIGKILL), kill.call_args_list)

    @unittest.skipUnless((HARNESS / "scripts/install_harness.py").is_file(), "set EVAL_TEST_HARNESS_ROOT for installer integration")
    def test_actual_installer_pins_all_routes_native_agents_and_checks(self):
        trial = self.prepare("workflow")
        work = trial / "workspace"
        models = runner.read_json(work / ".wysiwyship/config/models.json")
        profile = models["profiles"][models["active_profile"]]["codex"]
        for group in ("roles", "workflows"):
            for route in profile[group].values():
                self.assertEqual(route["model"], "exact-test-model")
                self.assertEqual(route["reasoning"], "high")
        for path in (work / ".codex/agents").glob("*.toml"):
            self.assertIn('model = "exact-test-model"', path.read_text())
            self.assertIn('model_reasoning_effort = "high"', path.read_text())
        commands = runner.read_json(work / ".wysiwyship/config/checks.json")["commands"]
        self.assertEqual(commands[0]["name"], "regression")
        self.assertIsInstance(commands[0]["argv"], list)
        self.assertTrue((trial / "installer.log").exists())
        self.assertTrue((work / ".agents/skills/engineering-workflow/SKILL.md").exists())
        (work / ".codex/agents/extra.toml").write_text("# mutation")
        self.assertIn("installed harness changed", self.cli("run", str(trial))[2])

    @unittest.skipUnless((HARNESS / "scripts/install_harness.py").is_file(), "set EVAL_TEST_HARNESS_ROOT for paired integration")
    def test_pair_success_duplicates_mismatch_staleness_and_unexecuted(self):
        baseline, workflow = self.prepare(), self.prepare("workflow")
        for trial in (baseline, workflow):
            self.assertEqual(self.execute(trial)[0], 0)
            self.assertEqual(self.cli("grade", str(trial))[0], 1)
        code, output, error = self.cli("compare", str(baseline), str(workflow))
        self.assertEqual(code, 0, error)
        pair = json.loads(output)["pairs"][0]
        self.assertEqual(pair["correctness_delta"], 0)
        self.assertEqual(pair["arms"]["baseline"]["run_status"], "completed")
        self.assertIn("duplicate", self.cli("compare", str(baseline), str(workflow), str(baseline))[2])
        mismatch = self.prepare(model="different")
        self.execute(mismatch)
        self.cli("grade", str(mismatch))
        self.assertIn("mismatched", self.cli("compare", str(mismatch), str(workflow))[2])
        unexecuted = self.prepare()
        self.assertIn("UNGRADED", self.cli("compare", str(unexecuted), str(workflow))[2])
        self.cli("grade", str(unexecuted))
        self.assertIn("UNEXECUTED", self.cli("compare", str(unexecuted), str(workflow))[2])
        write(baseline / "workspace/docs/new.md", "changed after grade")
        self.assertIn("STALE_GRADE", self.cli("compare", str(baseline), str(workflow))[2])

    @unittest.skipUnless((HARNESS / "scripts/install_harness.py").is_file(), "set EVAL_TEST_HARNESS_ROOT for paired integration")
    def test_comparison_keeps_infrastructure_failures_without_delta(self):
        baseline, workflow = self.prepare(), self.prepare("workflow")
        self.cli("run", str(baseline), "--execute", "--codex-executable", str(self.root / "missing"))
        self.execute(workflow)
        for trial in (baseline, workflow):
            self.cli("grade", str(trial))
        code, output, error = self.cli("compare", str(baseline), str(workflow))
        self.assertEqual(code, 1, error)
        pair = json.loads(output)["pairs"][0]
        self.assertIsNone(pair["correctness_delta"])
        self.assertIsNone(pair["duration_delta_seconds"])
        self.assertEqual(pair["arms"]["baseline"]["run_status"], "launch_error")
        empty = self.prepare()
        self.assertEqual(self.execute(empty, "print('{}')")[0], 0)
        self.cli("grade", str(empty))
        code, output, error = self.cli("compare", str(empty), str(workflow))
        self.assertEqual(code, 1, error)
        self.assertIsNone(json.loads(output)["pairs"][0]["correctness_delta"])

    @unittest.skipUnless((HARNESS / "scripts/install_harness.py").is_file(), "set EVAL_TEST_HARNESS_ROOT for paired integration")
    def test_comparison_different_fixture_hashes_rejected(self):
        baseline = self.prepare()
        self.execute(baseline)
        self.cli("grade", str(baseline))
        second_suite = self.root / "other-evals"
        runner.copy_tree(self.suite, second_suite)
        write(second_suite / "tasks/durable-jobs/task.md", "different revision")
        self.suite = second_suite
        workflow = self.prepare("workflow")
        self.execute(workflow)
        self.cli("grade", str(workflow))
        self.assertIn("mismatched", self.cli("compare", str(baseline), str(workflow))[2])

    @unittest.skipUnless((HARNESS / "tools/complexity.py").is_file(), "set EVAL_TEST_HARNESS_ROOT for analyzer integration")
    def test_metrics_changed_function_deltas_deleted_source_and_exclusions(self):
        candidate = self.root / "candidate"
        runner.copy_tree(self.fixture / "starter", candidate)
        write(candidate / "pkg/__init__.py", "def answer():\n    if True:\n        return 1\n    return 0\n")
        (candidate / "pkg/__main__.py").unlink()
        write(candidate / "new.py", "def new():\n    return 2\n")
        write(candidate / "docs/example.py", "# excluded")
        write(candidate / "tests/test_added.py", "# excluded")
        write(candidate / ".wysiwyship/tools/new.py", "# excluded")
        report = runner.metrics(self.fixture / "starter", candidate, HARNESS / "tools/complexity.py")
        self.assertEqual([item["path"] for item in report["changed_source_files"]],
                         ["new.py", "pkg/__init__.py", "pkg/__main__.py"])
        self.assertEqual(report["added_source_loc"], 4)
        self.assertEqual(report["deleted_source_loc"], 2)
        function = next(item for item in report["changed_source_complexity"] if item["file"] == "pkg/__init__.py")["functions"][0]
        self.assertEqual((function["before"], function["after"], function["delta"]), (1, 2, 1))
        missing = runner.metrics(self.fixture / "starter", candidate, self.root / "missing.py")
        self.assertIsNone(missing["changed_source_complexity"])


if __name__ == "__main__":
    unittest.main()
