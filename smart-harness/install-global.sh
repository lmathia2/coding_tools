#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM="${1:-both}"
STAMP="$(date +%Y%m%d-%H%M%S)"

if [[ "$PLATFORM" != "copilot" && "$PLATFORM" != "claude" && "$PLATFORM" != "both" ]]; then
  echo "Usage: $0 {copilot|claude|both}" >&2
  exit 1
fi

BACKUP_ROOT="$HOME/.smart-harness-backups/$STAMP"

backup_copy_dir() {
  local src="$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  if [[ -d "$dst" ]] && ! diff -qr "$src" "$dst" >/dev/null 2>&1; then
    mkdir -p "$BACKUP_ROOT"
    cp -R "$dst" "$BACKUP_ROOT/$(basename "$dst")"
  fi
  rm -rf "$dst"
  cp -R "$src" "$dst"
  echo "installed $dst"
}

backup_copy_file() {
  local src="$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  if [[ -e "$dst" ]] && ! cmp -s "$src" "$dst"; then
    mkdir -p "$BACKUP_ROOT"
    cp -p "$dst" "$BACKUP_ROOT/$(basename "$dst")"
  fi
  cp "$src" "$dst"
  echo "installed $dst"
}

# Canonical shared personal skills. Both Claude Code and VS Code Copilot
# discover ~/.claude/skills, so install them once.
mkdir -p "$HOME/.claude/skills"
for d in "$ROOT"/shared/skills/*; do
  backup_copy_dir "$d" "$HOME/.claude/skills/$(basename "$d")"
done

if [[ "$PLATFORM" == "copilot" || "$PLATFORM" == "both" ]]; then
  mkdir -p "$HOME/.copilot/agents"
  for f in "$ROOT"/copilot/agents/*.agent.md; do
    backup_copy_file "$f" "$HOME/.copilot/agents/$(basename "$f")"
  done
fi

if [[ "$PLATFORM" == "claude" || "$PLATFORM" == "both" ]]; then
  mkdir -p "$HOME/.claude/agents" "$HOME/.claude/commands"
  for f in "$ROOT"/claude-code/agents/*.md; do
    backup_copy_file "$f" "$HOME/.claude/agents/$(basename "$f")"
  done
  for f in "$ROOT"/claude-code/commands/*.md; do
    backup_copy_file "$f" "$HOME/.claude/commands/$(basename "$f")"
  done
fi

cat <<EOF

Global installation complete.
Shared skills: ~/.claude/skills (used by BOTH harnesses)
Copilot agents: ~/.copilot/agents (if selected)
Claude agents: ~/.claude/agents (if selected)
Claude /dev + /review-pr: ~/.claude/commands (if selected)

Project-local customizations still take precedence where the platform defines precedence.
EOF
