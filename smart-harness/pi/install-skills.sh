#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILE="${1:-useful}"
shift || true
PROJECT=""
WITH_DEPS=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project)
      PROJECT="${2:-}"
      shift 2
      ;;
    --with-deps)
      WITH_DEPS=1
      shift
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -n "$PROJECT" ]]; then
  [[ -d "$PROJECT" ]] || { echo "project directory does not exist: $PROJECT" >&2; exit 1; }
  PROJECT="$(cd "$PROJECT" && pwd)"
  TARGET="$PROJECT/.pi/skills"
else
  TARGET="$HOME/.pi/agent/skills"
fi

CONFIG="$ROOT/skills.json"
readarray_compat() {
  python3 - "$CONFIG" "$PROFILE" <<'PY'
import json, sys
path, profile = sys.argv[1:]
data = json.load(open(path, encoding="utf-8"))
profiles = data["profiles"]
if profile == "all":
    names = list(profiles)
else:
    if profile not in profiles:
        raise SystemExit(f"unknown profile: {profile}")
    names = [profile]
seen = set()
for name in names:
    for skill in profiles[name]:
        if skill not in seen:
            seen.add(skill)
            print(skill)
PY
}

REPO="$(python3 - "$CONFIG" <<'PY'
import json, sys
print(json.load(open(sys.argv[1], encoding="utf-8"))["source"]["repository"])
PY
)"
SHA="$(python3 - "$CONFIG" <<'PY'
import json, sys
print(json.load(open(sys.argv[1], encoding="utf-8"))["source"]["commit"])
PY
)"
CACHE="$HOME/.smart-harness/upstreams/pi-skills"

if [[ ! -d "$CACHE/.git" ]]; then
  mkdir -p "$(dirname "$CACHE")"
  git clone --filter=blob:none --no-checkout "https://github.com/$REPO.git" "$CACHE"
fi
git -C "$CACHE" fetch --depth 1 origin "$SHA"
git -C "$CACHE" checkout --detach -f "$SHA"
git -C "$CACHE" clean -fdx

mkdir -p "$TARGET"
while IFS= read -r skill; do
  [[ -n "$skill" ]] || continue
  src="$CACHE/$skill"
  [[ -d "$src" ]] || { echo "missing upstream skill: $skill" >&2; exit 1; }
  dst="$TARGET/$skill"
  if [[ -e "$dst" && ! -L "$dst" ]]; then
    backup="$HOME/.smart-harness-backups/$(date +%Y%m%d-%H%M%S)/pi-skills"
    mkdir -p "$backup"
    cp -R "$dst" "$backup/$skill"
    rm -rf "$dst"
  fi
  ln -sfn "$src" "$dst"
  if [[ "$WITH_DEPS" -eq 1 && -f "$src/package.json" ]]; then
    command -v npm >/dev/null || { echo "npm required for --with-deps" >&2; exit 1; }
    (cd "$src" && npm install --omit=dev)
  fi
  echo "installed skill $skill"
done < <(readarray_compat)

cat <<EOF

Installed Pi skill profile: $PROFILE
Target: $TARGET
Some skills require Chrome, API credentials, or additional CLIs; see each skill's SKILL.md.
EOF
