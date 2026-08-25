#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM="${1:-all}"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="$HOME/.smart-harness-backups/$STAMP"

case "$PLATFORM" in copilot|claude|pi|both|all) ;; *) echo "Usage: $0 {copilot|claude|pi|both|all}" >&2; exit 1;; esac
selected() { case "$PLATFORM:$1" in copilot:copilot|claude:claude|pi:pi|both:copilot|both:claude|all:copilot|all:claude|all:pi) return 0;; *) return 1;; esac; }

backup_existing() {
  local dst="$1"; [[ -e "$dst" || -L "$dst" ]] || return 0
  local rel="${dst#$HOME/}"; mkdir -p "$BACKUP_ROOT/$(dirname "$rel")"; cp -R "$dst" "$BACKUP_ROOT/$rel"
}
remove_legacy() { local dst="$1"; [[ -e "$dst" || -L "$dst" ]] || return 0; backup_existing "$dst"; rm -rf "$dst"; echo "removed legacy $dst"; }
copy_file() { local src="$1" dst="$2"; mkdir -p "$(dirname "$dst")"; if [[ -e "$dst" ]] && ! cmp -s "$src" "$dst"; then backup_existing "$dst"; fi; cp "$src" "$dst"; echo "installed $dst"; }
copy_dir() { local src="$1" dst="$2"; mkdir -p "$(dirname "$dst")"; if [[ -e "$dst" || -L "$dst" ]] && ! diff -qr "$src" "$dst" >/dev/null 2>&1; then backup_existing "$dst"; fi; rm -rf "$dst"; cp -R "$src" "$dst"; echo "installed $dst"; }

for name in codebase-map context-snapshot documentation-sync engineering-core parallel-work plan-first ponytail ponytail-review superpowers-methodology superpowers-skill-authoring task-ledger; do
  remove_legacy "$HOME/.claude/skills/$name"
done
mkdir -p "$HOME/.claude/skills"
for dir in "$ROOT"/shared/skills/*; do copy_dir "$dir" "$HOME/.claude/skills/$(basename "$dir")"; done

if selected copilot; then
  remove_legacy "$HOME/.copilot/agents/worker-terra.agent.md"
  mkdir -p "$HOME/.copilot/agents"
  for file in "$ROOT"/copilot/agents/*.agent.md; do copy_file "$file" "$HOME/.copilot/agents/$(basename "$file")"; done
fi

if selected claude; then
  for name in deep-worker.md fast-executor.md fast-verifier.md fast-worker.md; do remove_legacy "$HOME/.claude/agents/$name"; done
  mkdir -p "$HOME/.claude/agents" "$HOME/.claude/commands"
  for file in "$ROOT"/claude-code/agents/*.md; do copy_file "$file" "$HOME/.claude/agents/$(basename "$file")"; done
  for file in "$ROOT"/claude-code/commands/*.md; do copy_file "$file" "$HOME/.claude/commands/$(basename "$file")"; done
fi

if selected pi; then
  mkdir -p "$HOME/.pi/agent/prompts" "$HOME/.pi/agent/smart-harness"
  for file in "$ROOT"/pi/prompts/*.md; do copy_file "$file" "$HOME/.pi/agent/prompts/$(basename "$file")"; done
  for file in "$ROOT"/pi/tools/*.py "$ROOT"/pi/tools/*.md; do [[ -f "$file" ]] && copy_file "$file" "$HOME/.pi/agent/smart-harness/$(basename "$file")"; done
  python3 - "$HOME/.pi/agent/settings.json" "$HOME/.claude/skills" <<'PY'
import json,pathlib,sys
p=pathlib.Path(sys.argv[1]); skill=sys.argv[2]
data=json.loads(p.read_text()) if p.exists() else {}
skills=data.setdefault('skills',[])
if skill not in skills: skills.append(skill)
data['enableSkillCommands']=True
p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(data,indent=2)+'\n')
PY
fi

printf '\nSmart Harness v0.7 global installation complete. Legacy harness-managed skill/agent paths were backed up and removed.\n'
