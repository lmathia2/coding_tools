#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM="${1:-}"
TARGET="${2:-}"
STAMP="$(date +%Y%m%d-%H%M%S)"

if [[ "$PLATFORM" != "copilot" && "$PLATFORM" != "claude" && "$PLATFORM" != "pi" && "$PLATFORM" != "both" && "$PLATFORM" != "all" ]]; then
  echo "Usage: $0 {copilot|claude|pi|both|all} /path/to/project" >&2
  exit 1
fi
[[ -n "$TARGET" && -d "$TARGET" ]] || { echo "Target project directory does not exist: $TARGET" >&2; exit 1; }
TARGET="$(cd "$TARGET" && pwd)"
BACKUP_ROOT="$TARGET/.smart-harness-backups/$STAMP"

selected() {
  local name="$1"
  case "$PLATFORM:$name" in
    copilot:copilot|claude:claude|pi:pi|both:copilot|both:claude|all:copilot|all:claude|all:pi) return 0 ;;
    *) return 1 ;;
  esac
}

backup_existing() {
  local dst="$1"
  [[ -e "$dst" || -L "$dst" ]] || return 0
  local rel="${dst#$TARGET/}"
  local out="$BACKUP_ROOT/$rel"
  mkdir -p "$(dirname "$out")"
  cp -R "$dst" "$out"
}

copy_file() {
  local src="$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  if [[ -e "$dst" ]] && ! cmp -s "$src" "$dst"; then backup_existing "$dst"; fi
  cp "$src" "$dst"
  echo "installed ${dst#$TARGET/}"
}

copy_dir() {
  local src="$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  if [[ -e "$dst" || -L "$dst" ]]; then
    if ! diff -qr "$src" "$dst" >/dev/null 2>&1; then backup_existing "$dst"; fi
  fi
  rm -rf "$dst"
  cp -R "$src" "$dst"
  echo "installed ${dst#$TARGET/}"
}

merge_pi_settings() {
  local settings="$1" skill_path="$2"
  python3 - "$settings" "$skill_path" <<'PY'
import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
skill_path = sys.argv[2]
if path.exists():
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"invalid existing Pi settings {path}: {exc}")
else:
    data = {}
skills = data.setdefault("skills", [])
if skill_path not in skills:
    skills.append(skill_path)
data["enableSkillCommands"] = True
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
PY
}

# One canonical shared skill library for all selected platforms.
mkdir -p "$TARGET/.claude/skills"
for dir in "$ROOT"/shared/skills/*; do
  copy_dir "$dir" "$TARGET/.claude/skills/$(basename "$dir")"
done

if selected copilot; then
  mkdir -p "$TARGET/.github/agents" "$TARGET/.github/skills"
  for file in "$ROOT"/copilot/agents/*.agent.md; do
    copy_file "$file" "$TARGET/.github/agents/$(basename "$file")"
  done
  copy_dir "$ROOT/copilot/github-skills/code-review" "$TARGET/.github/skills/code-review"
fi

if selected claude; then
  mkdir -p "$TARGET/.claude/agents" "$TARGET/.claude/commands"
  for file in "$ROOT"/claude-code/agents/*.md; do
    copy_file "$file" "$TARGET/.claude/agents/$(basename "$file")"
  done
  for file in "$ROOT"/claude-code/commands/*.md; do
    copy_file "$file" "$TARGET/.claude/commands/$(basename "$file")"
  done
fi

if selected pi; then
  mkdir -p "$TARGET/.pi/prompts"
  for file in "$ROOT"/pi/prompts/*.md; do
    copy_file "$file" "$TARGET/.pi/prompts/$(basename "$file")"
  done
  if [[ -e "$TARGET/.pi/settings.json" ]]; then backup_existing "$TARGET/.pi/settings.json"; fi
  merge_pi_settings "$TARGET/.pi/settings.json" "../.claude/skills"
  echo "updated .pi/settings.json"
fi

mkdir -p "$TARGET/.smart-harness/templates"
copy_file "$ROOT/templates/ADR.md" "$TARGET/.smart-harness/templates/ADR.md"
copy_file "$ROOT/templates/MODULE_README.md" "$TARGET/.smart-harness/templates/MODULE_README.md"

if [[ ! -e "$TARGET/CLAUDE.md" ]]; then
  copy_file "$ROOT/templates/CLAUDE.md.example" "$TARGET/CLAUDE.md.example"
else
  echo "existing CLAUDE.md left untouched"
fi

mkdir -p "$TARGET/.agent-worktrees" "$TARGET/.agent-state"
touch "$TARGET/.gitignore"
for entry in '.agent-worktrees/' '.agent-state/' '.smart-harness-backups/'; do
  grep -qxF "$entry" "$TARGET/.gitignore" || printf '%s\n' "$entry" >> "$TARGET/.gitignore"
done

cat <<EOF

Done.
- Copilot: select Dev or ReviewPR in VS Code.
- Claude Code: use /dev or /review-pr.
- Pi: use /dev or /review-pr.
- Shared skills, including mandatory documentation-sync, live in .claude/skills.
- Re-running this installer syncs updates; replaced files are backed up under .smart-harness-backups/.
EOF
