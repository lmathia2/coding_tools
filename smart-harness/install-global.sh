#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM="${1:-all}"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="$HOME/.smart-harness-backups/$STAMP/global"

if [[ "$PLATFORM" != "copilot" && "$PLATFORM" != "claude" && "$PLATFORM" != "pi" && "$PLATFORM" != "both" && "$PLATFORM" != "all" ]]; then
  echo "Usage: $0 {copilot|claude|pi|both|all}" >&2
  exit 1
fi

selected() {
  local name="$1"
  case "$PLATFORM:$name" in
    copilot:copilot|claude:claude|pi:pi|both:copilot|both:claude|all:copilot|all:claude|all:pi) return 0 ;;
    *) return 1 ;;
  esac
}

copy_file() {
  local src="$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  if [[ -e "$dst" ]] && ! cmp -s "$src" "$dst"; then
    mkdir -p "$BACKUP"
    cp -p "$dst" "$BACKUP/$(basename "$dst")"
  fi
  cp "$src" "$dst"
  echo "installed $dst"
}

copy_dir() {
  local src="$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  if [[ -e "$dst" || -L "$dst" ]]; then
    if ! diff -qr "$src" "$dst" >/dev/null 2>&1; then
      mkdir -p "$BACKUP"
      cp -R "$dst" "$BACKUP/$(basename "$dst")"
    fi
  fi
  rm -rf "$dst"
  cp -R "$src" "$dst"
  echo "installed $dst"
}

merge_pi_settings() {
  local settings="$1" skill_path="$2"
  python3 - "$settings" "$skill_path" <<'PY'
import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
value = sys.argv[2]
data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
skills = data.setdefault("skills", [])
if value not in skills:
    skills.append(value)
data["enableSkillCommands"] = True
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
PY
}

# Shared personal skill library for Claude Code and VS Code Copilot; Pi references it through settings.
mkdir -p "$HOME/.claude/skills"
for dir in "$ROOT"/shared/skills/*; do
  copy_dir "$dir" "$HOME/.claude/skills/$(basename "$dir")"
done

if selected copilot; then
  mkdir -p "$HOME/.copilot/agents"
  for file in "$ROOT"/copilot/agents/*.agent.md; do
    copy_file "$file" "$HOME/.copilot/agents/$(basename "$file")"
  done
fi

if selected claude; then
  mkdir -p "$HOME/.claude/agents" "$HOME/.claude/commands"
  for file in "$ROOT"/claude-code/agents/*.md; do
    copy_file "$file" "$HOME/.claude/agents/$(basename "$file")"
  done
  for file in "$ROOT"/claude-code/commands/*.md; do
    copy_file "$file" "$HOME/.claude/commands/$(basename "$file")"
  done
fi

if selected pi; then
  mkdir -p "$HOME/.pi/agent/prompts"
  for file in "$ROOT"/pi/prompts/*.md; do
    copy_file "$file" "$HOME/.pi/agent/prompts/$(basename "$file")"
  done
  settings="$HOME/.pi/agent/settings.json"
  [[ -e "$settings" ]] && { mkdir -p "$BACKUP"; cp -p "$settings" "$BACKUP/pi-settings.json"; }
  merge_pi_settings "$settings" "$HOME/.claude/skills"
  echo "updated $settings"
fi

cat <<EOF

Global Smart Harness installation complete.
Shared skills: ~/.claude/skills
Copilot agents: ~/.copilot/agents (if selected)
Claude agents/commands: ~/.claude/agents and ~/.claude/commands (if selected)
Pi prompts/settings: ~/.pi/agent/prompts and ~/.pi/agent/settings.json (if selected)
EOF
