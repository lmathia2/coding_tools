#!/usr/bin/env python3
"""Check that each code commit carries documentation or a no-impact reason."""
from __future__ import annotations

import argparse
import json
from pathlib import PurePosixPath
import re
import subprocess
import sys


CODE_SUFFIXES = {
    ".c", ".cc", ".cpp", ".cs", ".css", ".go", ".h", ".hpp", ".html", ".java",
    ".js", ".jsx", ".kt", ".kts", ".php", ".py", ".rb", ".rs", ".sh", ".sql",
    ".swift", ".ts", ".tsx", ".vue",
}
DOC_SUFFIXES = {".adoc", ".md", ".mdx", ".rst"}
DOC_DIRECTORIES = {"doc", "docs", "documentation"}
DOC_BASENAMES = {"architecture", "changelog", "contributing", "readme", "runbook"}
NO_IMPACT_RE = re.compile(r"(?im)^Docs-Impact:\s*none\s*(?:—|-)\s*\S.+$")


def git(*args: str, cwd: str | None = None) -> str:
    completed = subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or f"git {' '.join(args)} failed")
    return completed.stdout


def is_documentation(path: str) -> bool:
    parsed = PurePosixPath(path)
    stem = parsed.stem.lower()
    return (
        parsed.suffix.lower() in DOC_SUFFIXES
        or any(part.lower() in DOC_DIRECTORIES for part in parsed.parts)
        or any(stem.startswith(name) for name in DOC_BASENAMES)
    )


def is_code(path: str) -> bool:
    return PurePosixPath(path).suffix.lower() in CODE_SUFFIXES and not is_documentation(path)


def evaluate_commit(commit: str, subject: str, message: str, files: list[str]) -> dict[str, object]:
    code_paths = [path for path in files if is_code(path)]
    documentation_paths = [path for path in files if is_documentation(path)]
    no_impact = bool(NO_IMPACT_RE.search(message))
    passed = not code_paths or bool(documentation_paths) or no_impact
    return {
        "commit": commit,
        "subject": subject,
        "status": "PASS" if passed else "FAIL",
        "code_paths": code_paths,
        "documentation_paths": documentation_paths,
        "docs_impact_none": no_impact,
        "reason": None if passed else "code changed without documentation or a concrete Docs-Impact: none — <reason>",
    }


def inspect_range(base: str, head: str, cwd: str | None = None) -> list[dict[str, object]]:
    commits = [line for line in git("rev-list", "--reverse", f"{base}..{head}", cwd=cwd).splitlines() if line]
    results = []
    for commit in commits:
        files = [line for line in git("diff-tree", "--root", "--no-commit-id", "--name-only", "-r", commit, cwd=cwd).splitlines() if line]
        message = git("show", "-s", "--format=%B", commit, cwd=cwd)
        subject = message.splitlines()[0] if message.splitlines() else ""
        results.append(evaluate_commit(commit, subject, message, files))
    return results


def render_text(results: list[dict[str, object]]) -> str:
    if not results:
        return "No commits found in the requested range."
    lines = []
    for result in results:
        lines.append(f"{result['status']} {str(result['commit'])[:12]} {result['subject']}")
        if result["reason"]:
            lines.append(f"  {result['reason']}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", help="exclusive base ref")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    results = inspect_range(args.base, args.head)
    print(json.dumps({"commits": results}, indent=2) if args.format == "json" else render_text(results))
    return 1 if any(result["status"] == "FAIL" for result in results) else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
