#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$SCRIPT_DIR/skills"
SKILL_SELECTION="all"
TARGET="both"

usage() {
  cat <<'EOF'
Install one skill or every skill in Skill Foundry.

Usage:
  ./install.sh [skill|all] [codex|claude|both] [child-installer args...]

Examples:
  ./install.sh forge
  ./install.sh teacher claude --scope project --project-dir /path/to/repo
  ./install.sh all both --mode link
  ./install.sh --list
EOF
}

die() {
  printf 'Error: %s\n' "$1" >&2
  exit 1
}

list_skills() {
  local dir
  for dir in "$SKILLS_DIR"/*; do
    [[ -d "$dir" && -x "$dir/install.sh" ]] || continue
    basename "$dir"
  done | sort
}

if [[ "${1:-}" == "--list" ]]; then
  list_skills
  exit 0
fi

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -gt 0 && "${1:-}" != --* ]]; then
  SKILL_SELECTION="$1"
  shift
fi

if [[ $# -gt 0 && "${1:-}" != --* ]]; then
  TARGET="$1"
  shift
fi

case "$TARGET" in
  codex|claude|both) ;;
  *)
    die "target must be codex, claude, or both"
    ;;
esac

mapfile -t AVAILABLE_SKILLS < <(list_skills)
[[ ${#AVAILABLE_SKILLS[@]} -gt 0 ]] || die "no installable skills found under $SKILLS_DIR"

if [[ "$SKILL_SELECTION" == "all" ]]; then
  SELECTED_SKILLS=("${AVAILABLE_SKILLS[@]}")
else
  [[ -x "$SKILLS_DIR/$SKILL_SELECTION/install.sh" ]] || die "unknown skill: $SKILL_SELECTION"
  SELECTED_SKILLS=("$SKILL_SELECTION")
fi

for skill in "${SELECTED_SKILLS[@]}"; do
  printf 'Installing %s\n' "$skill"
  "$SKILLS_DIR/$skill/install.sh" "$TARGET" "$@"
  printf '\n'
done
