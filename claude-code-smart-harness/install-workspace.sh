#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:-}"
STAMP="$(date +%Y%m%d-%H%M%S)"

if [[ -z "$TARGET" || ! -d "$TARGET" ]]; then
  echo "Usage: bash install-workspace.sh /path/to/repository" >&2
  exit 1
fi
TARGET="$(cd "$TARGET" && pwd)"

copy_file() {
  local src="$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  if [[ -e "$dst" ]] && ! cmp -s "$src" "$dst"; then
    cp -p "$dst" "${dst}.bak.${STAMP}"
    echo "Backed up: $dst"
  fi
  cp "$src" "$dst"
  echo "Installed: $dst"
}

for f in "$SCRIPT_DIR"/.claude/agents/*.md; do
  copy_file "$f" "$TARGET/.claude/agents/$(basename "$f")"
done

for d in "$SCRIPT_DIR"/.claude/skills/*; do
  name="$(basename "$d")"
  mkdir -p "$TARGET/.claude/skills/$name"
  for f in "$d"/*; do
    [[ -f "$f" ]] && copy_file "$f" "$TARGET/.claude/skills/$name/$(basename "$f")"
  done
done

mkdir -p "$TARGET/.claude/harness"
for f in "$SCRIPT_DIR"/.claude/harness/*; do
  [[ -f "$f" ]] && copy_file "$f" "$TARGET/.claude/harness/$(basename "$f")"
done

if [[ ! -e "$TARGET/CLAUDE.md" ]]; then
  copy_file "$SCRIPT_DIR/CLAUDE.md.example" "$TARGET/CLAUDE.md.example"
else
  echo "Existing CLAUDE.md left untouched."
fi

if command -v python3 >/dev/null 2>&1; then
  (cd "$TARGET" && python3 .claude/harness/configure-models.py)
else
  echo "python3 not found; model defaults are already preconfigured."
  echo "If you later edit .claude/harness/model-config.json, apply it manually to agent/skill frontmatter."
fi

echo
echo "Done. Restart Claude Code so project subagents reload."
echo "Daily interface: /dev <task>   or   /review-pr <base ref / intent>"
