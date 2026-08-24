#!/usr/bin/env python3
"""Check or update pinned GitHub upstream commits and synchronized manifests."""
from __future__ import annotations

import argparse
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCK = ROOT / "integrations" / "upstreams.lock.json"
EXTENSIONS = ROOT / "pi" / "extensions.json"
SKILLS = ROOT / "pi" / "skills.json"


def latest_commit(repository: str, ref: str) -> str:
    url = f"https://api.github.com/repos/{repository}/commits/{urllib.parse.quote(ref, safe='')}"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "smart-harness-upstream-check"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)["sha"]


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def synchronize_manifests(lock: dict) -> None:
    by_name = {item["name"]: item for item in lock["upstreams"]}

    extensions = json.loads(EXTENSIONS.read_text(encoding="utf-8"))
    extensions["profiles"]["methodology"] = [
        f"git:github.com/{by_name['superpowers']['repository']}@{by_name['superpowers']['commit']}",
        f"git:github.com/{by_name['ponytail']['repository']}@{by_name['ponytail']['commit']}",
    ]
    write_json(EXTENSIONS, extensions)

    skills = json.loads(SKILLS.read_text(encoding="utf-8"))
    skills["source"]["repository"] = by_name["pi-skills"]["repository"]
    skills["source"]["commit"] = by_name["pi-skills"]["commit"]
    write_json(SKILLS, skills)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--update", action="store_true")
    args = parser.parse_args()

    data = json.loads(LOCK.read_text(encoding="utf-8"))
    changed = False
    for item in data["upstreams"]:
        latest = latest_commit(item["repository"], item["ref"])
        locked = item["commit"]
        if latest != locked:
            changed = True
            print(f"{item['name']}: {locked[:12]} -> {latest[:12]}")
            if args.update:
                item["commit"] = latest
        else:
            print(f"{item['name']}: current ({locked[:12]})")

    if args.update:
        if changed:
            write_json(LOCK, data)
        synchronize_manifests(data)
        return 0
    return 1 if changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
