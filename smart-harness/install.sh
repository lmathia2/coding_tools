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

copy_file() {
  local src="$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  if [[ -e "$dst" ]] && ! cmp -s "$src" "$dst"; then
    cp -p "$dst" "${dst}.bak.${STAMP}"
  fi
  cp "$src" "$dst"
  echo "installed ${dst#$TARGET/}"
}

copy_dir() {
  local src="$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  if [[ -d "$dst" ]]; then
    cp -R "$dst" "${dst}.bak.${STAMP}"
  fi
  rm -rf "$dst"
  cp -R "$src" "$dst"
  echo "installed ${dst#$TARGET/}"
}

# Shared skills are canonical and installed once for either/both harnesses.
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
  mkdir -p "$TARGET/.claude/agents"
  for f in "$ROOT"/claude-code/agents/*.md; do
    copy_file "$f" "$TARGET/.claude/agents/$(basename "$f")"
  done
  for d in "$ROOT"/claude-code/skills/*; do
    copy_dir "$d" "$TARGET/.claude/skills/$(basename "$d")"
  done
fi

if [[ ! -e "$TARGET/CLAUDE.md" ]]; then
  copy_file "$ROOT/templates/CLAUDE.md.example" "$TARGET/CLAUDE.md.example"
else
  echo "existing CLAUDE.md left untouched"
fi

mkdir -p "$TARGET/.agent-worktrees"
if [[ -f "$TARGET/.gitignore" ]]; then
  if ! grep -qxF '.agent-worktrees/' "$TARGET/.gitignore"; then
    printf '\n.agent-worktrees/\n.agent-state/\n' >> "$TARGET/.gitignore"
  fi
else
  printf '.agent-worktrees/\n.agent-state/\n' > "$TARGET/.gitignore"
fi

cat <<EOF

Done.
- Copilot: select Dev or ReviewPR in VS Code.
- Claude Code: use /dev or /review-pr.
- Shared skills live in .claude/skills and are used by both.
EOF
