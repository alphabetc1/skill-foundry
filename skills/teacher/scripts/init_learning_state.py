#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = SKILL_ROOT / "assets"
STATE_TEMPLATE = ASSETS_DIR / "learner-state-template.yaml"
LOG_TEMPLATE = ASSETS_DIR / "session-log-template.md"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    if not slug:
        digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:10]
        slug = f"topic-{digest}"
    return slug


def infer_bootstrap(topic: str) -> tuple[str, str, str]:
    lowered = topic.lower()
    if "llm" in lowered or "inference" in lowered:
        return (
            "request-lifecycle",
            "Start with the end-to-end serving path before drilling into isolated optimizations.",
            "Run a map session for request-lifecycle and calibrate the learner's baseline mental model.",
        )
    return (
        "curriculum-bootstrap",
        "No default curriculum graph has been selected yet.",
        "Run a map session to define the curriculum graph and choose the first real module.",
    )


def render_template(template: Path, replacements: dict[str, str]) -> str:
    content = template.read_text(encoding="utf-8")
    for key, value in replacements.items():
        content = content.replace(f"{{{{{key}}}}}", value)
    return content


def write_file(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")
    path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Initialize external learner state files for the teacher skill.",
    )
    parser.add_argument("--topic", required=True, help="Study topic, for example 'LLM inference interview prep'.")
    parser.add_argument("--slug", help="Optional topic slug. Defaults to a slugified topic.")
    parser.add_argument("--goal", default="TBD", help="Current learner goal.")
    parser.add_argument("--deadline", default="TBD", help="Interview date or deadline.")
    parser.add_argument("--background", default="TBD", help="Short learner background summary.")
    parser.add_argument(
        "--base-dir",
        default=str(SKILL_ROOT),
        help="Base directory that should contain the learning/ folder. Defaults to the skill root.",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing files.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not STATE_TEMPLATE.exists() or not LOG_TEMPLATE.exists():
        print("Error: required asset templates are missing.", file=sys.stderr)
        return 1

    try:
        slug = args.slug or slugify(args.topic)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        print("Error: slug must contain only lowercase letters, digits, and hyphens.", file=sys.stderr)
        return 1

    module_id, module_reason, next_action = infer_bootstrap(args.topic)
    date = "YYYY-MM-DD"

    target_dir = Path(args.base_dir).resolve() / "learning" / slug
    target_dir.mkdir(parents=True, exist_ok=True)

    replacements = {
        "TOPIC": args.topic,
        "GOAL": args.goal,
        "DEADLINE": args.deadline,
        "BACKGROUND": args.background,
        "INITIAL_MODULE_ID": module_id,
        "INITIAL_MODULE_REASON": module_reason,
        "NEXT_ACTION": next_action,
        "DATE": date,
        "MODE": "map",
        "MODULE": module_id,
        "SESSION_GOAL": "Orient the learner, confirm baseline knowledge, and choose the first study move.",
    }

    state_path = target_dir / "learner-state.yaml"
    log_path = target_dir / "session-log.md"

    try:
        write_file(state_path, render_template(STATE_TEMPLATE, replacements), args.force)
        write_file(log_path, render_template(LOG_TEMPLATE, replacements), args.force)
    except FileExistsError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Created {state_path}")
    print(f"Created {log_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
