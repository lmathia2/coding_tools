#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM="${1:-}"
TARGET="${2:-}"
STAMP="$(date +%Y%m%d-%H%M%S)"

if [[ "$PLATFORM" != "copilot" && "$PLATFORM" != "claude" && "$PLATFORM" != "both" ]]; then
  echo "Usage: $0 {copilot|claude|both} /path/to/project" >&2
  exit 1
fi
if [[ -z "$TARGET" || ! -d "$TARGET" ]]; then
  echo "Target project directory does not exist: $TARGET" >&2
  exit 1
fi
TARGET="$(cd "$TARGET" && pwd)"
BACKUP_ROOT="$TARGET/.smart-harness-backups/$STAMP"

rel_to_target() {
  local p="$1"
  printf '%s' "${p#$TARGET/}"
}

backup_existing() {
  local dst="$1"
  [[ -e "$dst" ]] || return 0
  local rel
  rel="$(rel_to_target "$dst")"
  local out="$BACKUP_ROOT/$rel"
  mkdir -p "$(dirname "$out")"
  cp -R "$dst" "$out"
}

copy_file() {
  local src="$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  if [[ -e "$dst" ]] && ! cmp -s "$src" "$dst"; then
    backup_existing "$dst"
  fi
  cp "$src" "$dst"
  echo "installed $(rel_to_target "$dst")"
}

copy_dir() {
  local src="$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  if [[ -d "$dst" ]] && ! diff -qr "$src" "$dst" >/dev/null 2>&1; then
    backup_existing "$dst"
  fi
  rm -rf "$dst"
  cp -R "$src" "$dst"
  echo "installed $(rel_to_target "$dst")"
}

# Canonical shared skills: copied once. Both Claude Code and VS Code Copilot
# discover .claude/skills, so a "both" install does not duplicate them.
mkdir -p "$TARGET/.claude/skills"
for d in "$ROOT"/shared/skills/*; do
  copy_dir "$d" "$TARGET/.claude/skills/$(basename "$d")"
done

if [[ "$PLATFORM" == "copilot" || "$PLATFORM" == "both" ]]; then
  mkdir -p "$TARGET/.github/agents" "$TARGET/.github/skills"
  for f in "$ROOT"/copilot/agents/*.agent.md; do
    copy_file "$f" "$TARGET/.github/agents/$(basename "$f")"
  done
  copy_dir "$ROOT/copilot/github-skills/code-review" "$TARGET/.github/skills/code-review"
fi

if [[ "$PLATFORM" == "claude" || "$PLATFORM" == "both" ]]; then
  mkdir -p "$TARGET/.claude/agents" "$TARGET/.claude/commands"
  for f in "$ROOT"/claude-code/agents/*.md; do
    copy_file "$f" "$TARGET/.claude/agents/$(basename "$f")"
  done
  for f in "$ROOT"/claude-code/commands/*.md; do
    copy_file "$f" "$TARGET/.claude/commands/$(basename "$f")"
  done
fi

if [[ ! -e "$TARGET/CLAUDE.md" ]]; then
  copy_file "$ROOT/templates/CLAUDE.md.example" "$TARGET/CLAUDE.md.example"
else
  echo "existing CLAUDE.md left untouched"
fi

mkdir -p "$TARGET/.agent-worktrees" "$TARGET/.agent-state"
touch "$TARGET/.gitignore"
for entry in '.agent-worktrees/' '.agent-state/' '.smart-harness-backups/'; do
  if ! grep -qxF "$entry" "$TARGET/.gitignore"; then
    printf '%s\n' "$entry" >> "$TARGET/.gitignore"
  fi
done

cat <<EOF

Done.
- Copilot: select Dev or ReviewPR in VS Code.
- Claude Code: use /dev or /review-pr.
- Shared skills live once in .claude/skills and are used by both.
- Claude-only entry points live in .claude/commands, so they do not duplicate shared skills.
- Re-running this installer syncs updates; replaced files are backed up under .smart-harness-backups/.
EOF
