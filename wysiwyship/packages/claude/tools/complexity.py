#!/usr/bin/env python3
"""Measure Python function cyclomatic complexity without third-party packages.

The score is intentionally small and explainable: every function starts at one;
branches, loops, exception handlers, comprehension branches, match cases, and
short-circuit Boolean operators add decision points. Nested functions are scored
independently rather than inflating their parent.
"""
from __future__ import annotations

import argparse
import ast
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import subprocess
from typing import Iterable


EXCLUDED_PARTS = {".git", ".hg", ".mypy_cache", ".pytest_cache", ".tox", ".venv", "node_modules", "venv"}


def get_status(score: int) -> str:
    if score <= 5:
        return "Excellent"
    if score <= 10:
        return "Good"
    if score <= 20:
        return "Moderate Risk"
    return "High Risk / Refactor Required"


def get_recommendation(score: int) -> str:
    if score <= 10:
        return "No complexity-driven change is needed."
    if score <= 20:
        return "Consider guard clauses, extracting cohesive decisions, or simplifying nested loops and conditions."
    return "Refactor the decision structure: isolate responsibilities, flatten nesting, and replace repeated branching with data-driven dispatch where that improves clarity."


class ComplexityAnalyzer(ast.NodeVisitor):
    """Count decision points inside one function, excluding nested functions."""

    def __init__(self) -> None:
        self.complexity = 1

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        return

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        return

    def visit_Lambda(self, node: ast.Lambda) -> None:
        return

    def visit_If(self, node: ast.If) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        self.complexity += len(node.values) - 1
        self.generic_visit(node)

    def visit_match_case(self, node: ast.match_case) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_comprehension(self, node: ast.comprehension) -> None:
        self.complexity += 1 + len(node.ifs)
        self.generic_visit(node)


@dataclass(frozen=True)
class FunctionResult:
    file: str
    function_name: str
    qualified_name: str
    line: int
    end_line: int
    complexity_score: int
    status: str
    recommendation: str
    baseline_score: int | None = None
    delta: int | None = None


class FunctionCollector(ast.NodeVisitor):
    def __init__(self, file: str) -> None:
        self.file = file
        self.scope: list[str] = []
        self.results: list[FunctionResult] = []

    def _collect(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        analyzer = ComplexityAnalyzer()
        for statement in node.body:
            analyzer.visit(statement)
        qualified = ".".join([*self.scope, node.name])
        score = analyzer.complexity
        self.results.append(
            FunctionResult(
                file=self.file,
                function_name=node.name,
                qualified_name=qualified,
                line=node.lineno,
                end_line=getattr(node, "end_lineno", node.lineno),
                complexity_score=score,
                status=get_status(score),
                recommendation=get_recommendation(score),
            )
        )
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._collect(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._collect(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()


def analyze_code(source_code: str, file: str = "<memory>") -> dict[str, object]:
    try:
        tree = ast.parse(source_code, filename=file)
    except SyntaxError as exc:
        return {"file": file, "error": f"Invalid Python syntax: {exc}"}
    collector = FunctionCollector(file)
    collector.visit(tree)
    return {"file": file, "functions": [asdict(item) for item in collector.results]}


def discover_files(paths: Iterable[str]) -> list[Path]:
    files: set[Path] = set()
    for raw in paths:
        path = Path(raw)
        if path.is_file() and path.suffix == ".py":
            files.add(path)
        elif path.is_dir():
            files.update(
                child
                for child in path.rglob("*.py")
                if not any(part in EXCLUDED_PARTS for part in child.parts)
            )
    return sorted(files)


def read_git_version(ref: str, path: Path) -> str | None:
    root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        text=True,
        capture_output=True,
        check=False,
    )
    if root.returncode != 0:
        return None
    repository_root = Path(root.stdout.strip()).resolve()
    try:
        repository_path = path.resolve().relative_to(repository_root).as_posix()
    except ValueError:
        return None
    completed = subprocess.run(
        ["git", "-C", str(repository_root), "show", f"{ref}:{repository_path}"],
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.stdout if completed.returncode == 0 else None


def attach_baseline(current: list[dict[str, object]], baseline: list[dict[str, object]]) -> None:
    previous = {str(item["qualified_name"]): int(item["complexity_score"]) for item in baseline}
    for item in current:
        old = previous.get(str(item["qualified_name"]))
        item["baseline_score"] = old
        item["delta"] = int(item["complexity_score"]) - old if old is not None else None


def render_text(results: list[dict[str, object]], minimum: int) -> str:
    lines: list[str] = []
    for result in results:
        if "error" in result:
            lines.append(f"{result['file']}: ERROR {result['error']}")
            continue
        functions = [item for item in result["functions"] if int(item["complexity_score"]) >= minimum]
        for item in sorted(functions, key=lambda value: (-int(value["complexity_score"]), int(value["line"]))):
            delta = ""
            if item.get("delta") is not None:
                delta = f", delta {int(item['delta']):+d} from {item['baseline_score']}"
            lines.append(
                f"{item['file']}:{item['line']} {item['qualified_name']}: "
                f"{item['complexity_score']} ({item['status']}{delta})"
            )
            if int(item["complexity_score"]) > 10:
                lines.append(f"  {item['recommendation']}")
    return "\n".join(lines) if lines else "No functions matched the reporting threshold."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", default=["."], help="Python files or directories")
    parser.add_argument("--compare-ref", help="Git ref used to calculate per-function score deltas")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--min-score", type=int, default=1)
    parser.add_argument("--fail-above", type=int, help="Exit nonzero if a current score exceeds this value")
    return parser.parse_args()


def analyze_paths(paths: list[str], compare_ref: str | None) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for path in discover_files(paths):
        result = analyze_code(path.read_text(encoding="utf-8"), path.as_posix())
        if compare_ref and "functions" in result:
            baseline_source = read_git_version(compare_ref, path)
            if baseline_source is not None:
                baseline = analyze_code(baseline_source, path.as_posix()).get("functions", [])
                attach_baseline(result["functions"], baseline)
        results.append(result)
    return results


def exceeds_limit(results: list[dict[str, object]], limit: int | None) -> bool:
    return limit is not None and any(
        int(item["complexity_score"]) > limit
        for result in results
        for item in result.get("functions", [])
    )


def main() -> int:
    args = parse_args()
    results = analyze_paths(args.paths, args.compare_ref)

    if args.format == "json":
        print(json.dumps({"files": results}, indent=2))
    else:
        print(render_text(results, args.min_score))

    if any("error" in result for result in results):
        return 2
    if exceeds_limit(results, args.fail_above):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
