#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILE="${1:-core}"
SCOPE="${2:-}"
CONFIG="$ROOT/extensions.json"

command -v pi >/dev/null || { echo "pi is not installed" >&2; exit 1; }

if [[ "$SCOPE" != "" && "$SCOPE" != "--project" ]]; then
  echo "Usage: $0 [core|methodology|testing|observability|productivity|all] [--project]" >&2
  exit 1
fi

packages="$(python3 - "$CONFIG" "$PROFILE" <<'PY'
import json, sys
path, profile = sys.argv[1:]
data = json.load(open(path, encoding="utf-8"))["profiles"]
if profile == "all":
    names = list(data)
else:
    if profile not in data:
        raise SystemExit(f"unknown profile: {profile}")
    names = [profile]
seen = set()
for name in names:
    for package in data[name]:
        if package not in seen:
            seen.add(package)
            print(package)
PY
)"

flag=()
[[ "$SCOPE" == "--project" ]] && flag=(-l)

while IFS= read -r package; do
  [[ -n "$package" ]] || continue
  echo "Installing $package"
  pi install "${flag[@]}" "$package"
done <<< "$packages"

cat <<EOF

Installed Pi profile: $PROFILE
Review third-party source before updates. Use 'pi update --extensions' only when you intend to reconcile unpinned packages.
EOF
