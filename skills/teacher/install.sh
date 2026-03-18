#!/usr/bin/env bash

set -euo pipefail

SKILL_NAME="teacher"
MODE="copy"
TARGET="both"
CLAUDE_SCOPE="personal"
PROJECT_DIR=""
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_ITEMS=("SKILL.md" "README.md" "agents" "scripts" "references" "assets")

usage() {
  cat <<'EOF'
Install the teacher skill into Codex, Claude, or both.

Usage:
  ./install.sh [codex|claude|both] [--mode copy|link] [--scope personal|project] [--project-dir PATH]

Defaults:
  target       both
  mode         copy
  claude scope personal

Examples:
  ./install.sh
  ./install.sh codex
  ./install.sh claude --scope project --project-dir /path/to/repo
  ./install.sh both --mode link
EOF
}

die() {
  printf 'Error: %s\n' "$1" >&2
  exit 1
}

if [[ $# -gt 0 && "${1:-}" != --* ]]; then
  TARGET="$1"
  shift
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      [[ $# -ge 2 ]] || die "--mode requires a value"
      MODE="$2"
      shift 2
      ;;
    --scope)
      [[ $# -ge 2 ]] || die "--scope requires a value"
      CLAUDE_SCOPE="$2"
      shift 2
      ;;
    --project-dir)
      [[ $# -ge 2 ]] || die "--project-dir requires a value"
      PROJECT_DIR="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "unknown argument: $1"
      ;;
  esac
done

case "$TARGET" in
  codex|claude|both) ;;
  *)
    die "target must be codex, claude, or both"
    ;;
esac

case "$MODE" in
  copy|link) ;;
  *)
    die "mode must be copy or link"
    ;;
esac

case "$CLAUDE_SCOPE" in
  personal|project) ;;
  *)
    die "scope must be personal or project"
    ;;
esac

if [[ "$CLAUDE_SCOPE" == "project" && -z "$PROJECT_DIR" ]]; then
  PROJECT_DIR="$PWD"
fi

if [[ -n "$PROJECT_DIR" && ! -d "$PROJECT_DIR" ]]; then
  die "project directory does not exist: $PROJECT_DIR"
fi

install_copy() {
  local target_dir="$1"
  rm -rf "$target_dir"
  mkdir -p "$target_dir"

  local item
  for item in "${SOURCE_ITEMS[@]}"; do
    if [[ -e "$SCRIPT_DIR/$item" ]]; then
      cp -R "$SCRIPT_DIR/$item" "$target_dir/"
    fi
  done

  find "$target_dir" -type d -name "__pycache__" -prune -exec rm -rf {} +
  find "$target_dir" -type f -name "*.pyc" -delete
}

install_link() {
  local target_dir="$1"
  rm -rf "$target_dir"
  mkdir -p "$(dirname "$target_dir")"
  ln -s "$SCRIPT_DIR" "$target_dir"
}

install_target() {
  local label="$1"
  local target_dir="$2"

  mkdir -p "$(dirname "$target_dir")"
  if [[ "$MODE" == "copy" ]]; then
    install_copy "$target_dir"
  else
    install_link "$target_dir"
  fi

  printf 'Installed %-6s -> %s\n' "$label" "$target_dir"
}

CODEX_TARGET="${CODEX_HOME:-$HOME/.codex}/skills/$SKILL_NAME"
if [[ "$CLAUDE_SCOPE" == "project" ]]; then
  CLAUDE_TARGET="$PROJECT_DIR/.claude/skills/$SKILL_NAME"
else
  CLAUDE_TARGET="$HOME/.claude/skills/$SKILL_NAME"
fi

if [[ "$TARGET" == "codex" || "$TARGET" == "both" ]]; then
  install_target "Codex" "$CODEX_TARGET"
fi

if [[ "$TARGET" == "claude" || "$TARGET" == "both" ]]; then
  install_target "Claude" "$CLAUDE_TARGET"
fi

cat <<EOF

Next:
  Codex : start a new session, then invoke with \$teacher
  Claude: start a new session, then invoke with /teacher
EOF
