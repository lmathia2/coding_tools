#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:-}"
STAMP="$(date +%Y%m%d-%H%M%S)"
if [[ -z "$TARGET" || ! -d "$TARGET" ]]; then echo "Usage: ./install-workspace.sh /path/to/repository" >&2; exit 1; fi
TARGET="$(cd "$TARGET" && pwd)"
copy_file(){ src="$1"; dst="$2"; mkdir -p "$(dirname "$dst")"; if [[ -e "$dst" ]] && ! cmp -s "$src" "$dst"; then cp -p "$dst" "${dst}.bak.${STAMP}"; fi; cp "$src" "$dst"; }
copy_dir(){ src="$1"; dst="$2"; mkdir -p "$(dirname "$dst")"; if [[ -d "$dst" ]]; then cp -R "$dst" "${dst}.bak.${STAMP}"; fi; rm -rf "$dst"; cp -R "$src" "$dst"; }
for f in "$SCRIPT_DIR"/.github/agents/*.agent.md; do copy_file "$f" "$TARGET/.github/agents/$(basename "$f")"; done
for d in "$SCRIPT_DIR"/.claude/skills/*; do copy_dir "$d" "$TARGET/.claude/skills/$(basename "$d")"; done
for d in "$SCRIPT_DIR"/.github/skills/*; do copy_dir "$d" "$TARGET/.github/skills/$(basename "$d")"; done
copy_file "$SCRIPT_DIR/COPILOT_HARNESS_README.md" "$TARGET/COPILOT_HARNESS_README.md"
if [[ ! -e "$TARGET/CLAUDE.md" ]]; then copy_file "$SCRIPT_DIR/CLAUDE.md.example" "$TARGET/CLAUDE.md.example"; fi
echo "Installed. Use Dev or ReviewPR in VS Code."
