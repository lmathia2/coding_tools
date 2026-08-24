#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:-}"
TARGET="${2:-}"
STAMP="$(date +%Y%m%d-%H%M%S)"
CACHE="$HOME/.smart-harness/upstreams"
LOCK="$ROOT/integrations/upstreams.lock.json"

usage() {
  cat <<'EOF'
Usage:
  install-methodologies.sh project /path/to/project
  install-methodologies.sh global
  install-methodologies.sh pi [--project]

project/global installs a curated skill-only subset.
pi installs the full pinned Pi packages.
EOF
}

if [[ "$MODE" != "project" && "$MODE" != "global" && "$MODE" != "pi" ]]; then
  usage >&2
  exit 1
fi

read_lock() {
  python3 - "$LOCK" "$1" "$2" <<'PY'
import json, sys
p, name, field = sys.argv[1:]
data = json.load(open(p, encoding="utf-8"))
item = next(x for x in data["upstreams"] if x["name"] == name)
print(item[field])
PY
}

SUPER_REPO="$(read_lock superpowers repository)"
SUPER_SHA="$(read_lock superpowers commit)"
PONY_REPO="$(read_lock ponytail repository)"
PONY_SHA="$(read_lock ponytail commit)"

if [[ "$MODE" == "pi" ]]; then
  command -v pi >/dev/null || { echo "pi is not installed" >&2; exit 1; }
  local_flag=()
  [[ "$TARGET" == "--project" ]] && local_flag=(-l)
  pi install "${local_flag[@]}" "git:github.com/$SUPER_REPO@$SUPER_SHA"
  pi install "${local_flag[@]}" "git:github.com/$PONY_REPO@$PONY_SHA"
  exit 0
fi

if [[ "$MODE" == "project" ]]; then
  [[ -n "$TARGET" && -d "$TARGET" ]] || { echo "project directory required" >&2; exit 1; }
  TARGET="$(cd "$TARGET" && pwd)"
  SKILL_TARGET="$TARGET/.claude/skills"
  LICENSE_TARGET="$TARGET/.smart-harness/licenses"
  BACKUP="$TARGET/.smart-harness-backups/$STAMP/methodologies"
else
  SKILL_TARGET="$HOME/.claude/skills"
  LICENSE_TARGET="$HOME/.smart-harness/licenses"
  BACKUP="$HOME/.smart-harness-backups/$STAMP/methodologies"
fi

checkout() {
  local repo="$1" sha="$2" dst="$3"
  mkdir -p "$(dirname "$dst")"
  if [[ ! -d "$dst/.git" ]]; then
    git clone --filter=blob:none --no-checkout "https://github.com/$repo.git" "$dst"
  fi
  git -C "$dst" fetch --depth 1 origin "$sha"
  git -C "$dst" checkout --detach -f "$sha"
  git -C "$dst" clean -fdx
}

install_skill() {
  local src="$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  if [[ -e "$dst" ]]; then
    mkdir -p "$BACKUP"
    cp -R "$dst" "$BACKUP/$(basename "$dst")"
  fi
  rm -rf "$dst"
  cp -R "$src" "$dst"
  echo "installed $(basename "$dst")"
}

SUPER_DIR="$CACHE/superpowers"
PONY_DIR="$CACHE/ponytail"
checkout "$SUPER_REPO" "$SUPER_SHA" "$SUPER_DIR"
checkout "$PONY_REPO" "$PONY_SHA" "$PONY_DIR"

mkdir -p "$SKILL_TARGET" "$LICENSE_TARGET"

super_skills=(
  brainstorming writing-plans executing-plans dispatching-parallel-agents
  systematic-debugging test-driven-development verification-before-completion
  using-git-worktrees requesting-code-review receiving-code-review
  finishing-a-development-branch subagent-driven-development
)
pony_skills=(ponytail ponytail-review ponytail-audit)

for name in "${super_skills[@]}"; do
  install_skill "$SUPER_DIR/skills/$name" "$SKILL_TARGET/$name"
done
for name in "${pony_skills[@]}"; do
  install_skill "$PONY_DIR/skills/$name" "$SKILL_TARGET/$name"
done

cp "$SUPER_DIR/LICENSE" "$LICENSE_TARGET/superpowers-MIT.txt"
cp "$PONY_DIR/LICENSE" "$LICENSE_TARGET/ponytail-MIT.txt"

cat <<EOF

Curated methodology skills installed from pinned commits.
The forceful Superpowers bootstrap was intentionally not installed.
Smart Harness planning, documentation, test, and safety invariants remain authoritative.
EOF
