#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM="${1:-}"
TARGET="${2:-}"
STAMP="$(date +%Y%m%d-%H%M%S)"

case "$PLATFORM" in copilot|claude|pi|both|all) ;; *) echo "Usage: $0 {copilot|claude|pi|both|all} /path/to/project" >&2; exit 1;; esac
[[ -n "$TARGET" && -d "$TARGET" ]] || { echo "Target project directory does not exist: $TARGET" >&2; exit 1; }
TARGET="$(cd "$TARGET" && pwd)"
BACKUP_ROOT="$TARGET/.smart-harness-backups/$STAMP"

selected() {
  case "$PLATFORM:$1" in copilot:copilot|claude:claude|pi:pi|both:copilot|both:claude|all:copilot|all:claude|all:pi) return 0;; *) return 1;; esac
}
backup_existing() { local dst="$1"; [[ -e "$dst" || -L "$dst" ]] || return 0; local rel="${dst#$TARGET/}"; mkdir -p "$BACKUP_ROOT/$(dirname "$rel")"; cp -R "$dst" "$BACKUP_ROOT/$rel"; }
copy_file() { local src="$1" dst="$2"; mkdir -p "$(dirname "$dst")"; if [[ -e "$dst" ]] && ! cmp -s "$src" "$dst"; then backup_existing "$dst"; fi; cp "$src" "$dst"; echo "installed ${dst#$TARGET/}"; }
copy_dir() { local src="$1" dst="$2"; mkdir -p "$(dirname "$dst")"; if [[ -e "$dst" || -L "$dst" ]] && ! diff -qr "$src" "$dst" >/dev/null 2>&1; then backup_existing "$dst"; fi; rm -rf "$dst"; cp -R "$src" "$dst"; echo "installed ${dst#$TARGET/}"; }

merge_pi_settings() {
  python3 - "$1" "$2" <<'PY_SETTINGS'
import json, pathlib, sys
path=pathlib.Path(sys.argv[1]); skill_path=sys.argv[2]
data=json.loads(path.read_text()) if path.exists() else {}
skills=data.setdefault("skills",[])
if skill_path not in skills: skills.append(skill_path)
data["enableSkillCommands"]=True
path.parent.mkdir(parents=True,exist_ok=True)
path.write_text(json.dumps(data,indent=2)+"\n")
PY_SETTINGS
}

# Canonical local shared skills. No network operation occurs.
mkdir -p "$TARGET/.claude/skills"
for dir in "$ROOT"/shared/skills/*; do copy_dir "$dir" "$TARGET/.claude/skills/$(basename "$dir")"; done

if selected copilot; then
  mkdir -p "$TARGET/.github/agents" "$TARGET/.github/skills"
  for file in "$ROOT"/copilot/agents/*.agent.md; do copy_file "$file" "$TARGET/.github/agents/$(basename "$file")"; done
  copy_dir "$ROOT/copilot/github-skills/code-review" "$TARGET/.github/skills/code-review"
fi
if selected claude; then
  mkdir -p "$TARGET/.claude/agents" "$TARGET/.claude/commands"
  for file in "$ROOT"/claude-code/agents/*.md; do copy_file "$file" "$TARGET/.claude/agents/$(basename "$file")"; done
  for file in "$ROOT"/claude-code/commands/*.md; do copy_file "$file" "$TARGET/.claude/commands/$(basename "$file")"; done
fi
if selected pi; then
  mkdir -p "$TARGET/.pi/prompts" "$TARGET/.pi/tools"
  for file in "$ROOT"/pi/prompts/*.md; do copy_file "$file" "$TARGET/.pi/prompts/$(basename "$file")"; done
  for file in "$ROOT"/pi/tools/*.py "$ROOT"/pi/tools/*.md; do [[ -f "$file" ]] && copy_file "$file" "$TARGET/.pi/tools/$(basename "$file")"; done
  [[ -e "$TARGET/.pi/settings.json" ]] && backup_existing "$TARGET/.pi/settings.json"
  merge_pi_settings "$TARGET/.pi/settings.json" "../.claude/skills"
  echo "updated .pi/settings.json"
fi

mkdir -p "$TARGET/.smart-harness/templates"
for file in "$ROOT"/templates/*; do copy_file "$file" "$TARGET/.smart-harness/templates/$(basename "$file")"; done
[[ -e "$TARGET/CLAUDE.md" ]] || copy_file "$ROOT/templates/CLAUDE.md.example" "$TARGET/CLAUDE.md.example"

mkdir -p "$TARGET/.agent-worktrees" "$TARGET/.agent-state"
touch "$TARGET/.gitignore"
for entry in '.agent-worktrees/' '.agent-state/' '.smart-harness-backups/'; do grep -qxF "$entry" "$TARGET/.gitignore" || printf '%s\n' "$entry" >> "$TARGET/.gitignore"; done

cat <<EOF_DONE

Done. All installed content came from this checkout; no external plugin, package, skill, or repository was downloaded.
- Copilot: Dev / ReviewPR
- Claude Code: /dev /review-pr
- Pi: /dev /review-pr
EOF_DONE
