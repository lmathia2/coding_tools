"""Evaluator-owned unittest process; stdout is diagnostic, result.json is data."""
import json
from pathlib import Path
import sys
import unittest


def pairs(items):
    return [[str(test), detail] for test, detail in items]


def main():
    candidate, tests, output = sys.argv[1:]
    sys.path.insert(0, candidate)
    report = {"schema_version": 1, "tests": 0, "failures": [], "errors": [], "discovery_errors": [],
              "skips": [], "expected_failures": [], "unexpected_successes": [], "successful": False}
    try:
        loader = unittest.TestLoader()
        suite = loader.discover(tests, pattern="test_*.py")
        result = unittest.TestResult()
        suite.run(result)
        report.update(tests=result.testsRun, failures=pairs(result.failures), errors=pairs(result.errors),
                      skips=pairs(result.skipped), expected_failures=pairs(result.expectedFailures),
                      unexpected_successes=[str(test) for test in result.unexpectedSuccesses])
        if loader.errors:
            report["discovery_errors"] = list(loader.errors)
        report["successful"] = (result.testsRun > 0 and result.wasSuccessful()
                                and not loader.errors and not result.skipped and not result.expectedFailures)
    except BaseException as exc:
        report["errors"].append(["grader", repr(exc)])
        report["discovery_errors"].append(repr(exc))
    Path(output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if report["successful"] else 1


if __name__ == "__main__":
    sys.exit(main())
