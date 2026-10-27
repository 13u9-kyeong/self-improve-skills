#!/usr/bin/env bash
# Install /selfimprove as a standalone Claude Code skill (without the plugin system).
#
#   ./install.sh              -> ~/.claude/skills/selfimprove/     (all projects)
#   ./install.sh --project    -> ./.claude/skills/selfimprove/     (current project only)
#
# The skill directory carries the whole kit in kit/, so the skill can install the kit into
# any project the first time it runs there. Re-run after pulling to update; the installed
# copy is replaced completely.
#
# Exit: 0 installed · 2 cannot (source missing, empty result) · 3 usage.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/skills/selfimprove"
case "${1:-}" in
  "")          DEST="$HOME/.claude/skills/selfimprove" ;;
  --project)   DEST="$PWD/.claude/skills/selfimprove" ;;
  -h|--help)   sed -n '2,11p' "$0"; exit 0 ;;
  *)           echo "usage: $0 [--project]" >&2; exit 3 ;;
esac

[ -f "$SRC/SKILL.md" ] && [ -d "$SRC/kit" ] || { echo "skill source missing: $SRC" >&2; exit 2; }

rm -rf "$DEST"
mkdir -p "$DEST"
( cd "$SRC" && tar --exclude='__pycache__' --exclude='*.pyc' -cf - . ) | tar -xf - -C "$DEST"

n=$(find "$DEST/kit" -type f | wc -l | tr -d ' ')
[ -f "$DEST/SKILL.md" ] && [ "$n" -gt 0 ] || { echo "install produced an empty skill" >&2; exit 2; }
echo "installed: $DEST  (SKILL.md + install_kit.py + kit/, $n kit files)"
echo "invoke it in Claude Code as /selfimprove"
