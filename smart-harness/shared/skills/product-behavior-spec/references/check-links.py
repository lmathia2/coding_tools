#!/usr/bin/env python3
"""Validate local Markdown links and heading anchors in a behavior-spec tree.

Usage: python3 check-links.py [root]
No third-party packages are required.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
import re
import unicodedata

LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+[\"'][^\"']*[\"'])?\)")
HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def visible_lines(path: Path) -> list[str]:
    output: list[str] = []
    fenced = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if FENCE_RE.match(line):
            fenced = not fenced
            output.append("")
        else:
            output.append("" if fenced else line)
    return output


def github_slug(text: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[*_~]", "", text)
    text = unicodedata.normalize("NFKD", text).lower()
    text = "".join(ch for ch in text if ch.isalnum() or ch in " -_")
    return re.sub(r"\s+", "-", text.strip())


def anchors(path: Path) -> set[str]:
    counts: defaultdict[str, int] = defaultdict(int)
    result: set[str] = set()
    for line in visible_lines(path):
        match = HEADING_RE.match(line)
        if not match:
            continue
        base = github_slug(match.group(2))
        index = counts[base]
        counts[base] += 1
        result.add(base if index == 0 else f"{base}-{index}")
    return result


def markdown_files(root: Path) -> list[Path]:
    ignored = {".git", "node_modules", ".agent-worktrees", ".smart-harness-backups"}
    return sorted(path for path in root.rglob("*.md") if not ignored.intersection(path.parts))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    files = markdown_files(root)
    anchor_cache: dict[Path, set[str]] = {}
    problems: list[str] = []
    checked = 0

    for source in files:
        for line_number, line in enumerate(visible_lines(source), 1):
            for raw_target in LINK_RE.findall(line):
                target = raw_target.strip("<>")
                if SCHEME_RE.match(target) or target.startswith("//"):
                    continue
                checked += 1
                file_part, separator, anchor = target.partition("#")
                destination = (source.parent / file_part).resolve() if file_part else source.resolve()
                relative_source = source.relative_to(root)
                if not destination.exists():
                    problems.append(f"{relative_source}:{line_number}: missing target {target}")
                    continue
                if separator and anchor and destination.suffix.lower() == ".md":
                    available = anchor_cache.setdefault(destination, anchors(destination))
                    if anchor.lower() not in available:
                        problems.append(f"{relative_source}:{line_number}: missing anchor {target}")

    for problem in problems:
        print(problem)
    print(f"checked {len(files)} Markdown files and {checked} local links; {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
