#!/usr/bin/env python3
"""
Resolve and optionally revert active downstream workflow stage commits.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

STAGE_MESSAGES = {
    1: "stage1: generate prompt.md",
    2: "stage2: generate research.md",
    3: "stage3: generate plan.md",
    4: "stage4: implement plan.md",
    5: "stage5: review and fix blocking issues",
}

REVERT_MAP = {
    "prompt.md": [5, 4, 3, 2],
    "research.md": [5, 4, 3],
    "plan.md": [5, 4],
    "review.md": [5],
}

REVERT_BODY_RE = re.compile(r"^This reverts commit ([0-9a-f]{7,40})\.$", re.MULTILINE)


@dataclass
class CommitNode:
    commit_hash: str
    subject: str
    kind: str
    stage: int | None = None
    target: "CommitNode | None" = None
    active: bool = False


def run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def ensure_git_repo(cwd: Path) -> None:
    result = run_git(["rev-parse", "--show-toplevel"], cwd)
    if result.returncode != 0:
        raise RuntimeError("Current directory is not inside a git repository.")


def ensure_clean_worktree(cwd: Path) -> None:
    result = run_git(["status", "--porcelain"], cwd)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Failed to inspect git status.")
    if result.stdout.strip():
        raise RuntimeError("Working tree is not clean. Commit or stash changes before applying reverts.")


def resolve_tracked_hash(prefix: str, tracked: dict[str, CommitNode]) -> CommitNode | None:
    matches = [node for commit_hash, node in tracked.items() if commit_hash.startswith(prefix)]
    if len(matches) == 1:
        return matches[0]
    return None


def set_active(node: CommitNode, active: bool) -> None:
    if node.active == active:
        return
    node.active = active
    if node.kind == "revert" and node.target is not None:
        set_active(node.target, not node.target.active)


def load_active_stage_commits(cwd: Path) -> dict[int, CommitNode]:
    result = run_git(["log", "--reverse", "--format=%H%x1f%s%x1f%b%x1e"], cwd)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Failed to read git history.")

    tracked: dict[str, CommitNode] = {}
    stage_nodes: dict[int, list[CommitNode]] = {stage: [] for stage in STAGE_MESSAGES}

    for raw_record in result.stdout.split("\x1e"):
        record = raw_record.strip("\n")
        if not record.strip():
            continue

        parts = record.split("\x1f")
        if len(parts) != 3:
            continue

        commit_hash, subject, body = parts
        stage = next((stage for stage, message in STAGE_MESSAGES.items() if subject == message), None)
        if stage is not None:
            node = CommitNode(commit_hash=commit_hash, subject=subject, kind="stage", stage=stage)
            tracked[commit_hash] = node
            stage_nodes[stage].append(node)
            set_active(node, True)
            continue

        match = REVERT_BODY_RE.search(body)
        if not match:
            continue

        target = resolve_tracked_hash(match.group(1), tracked)
        if target is None:
            continue

        node = CommitNode(commit_hash=commit_hash, subject=subject, kind="revert", target=target)
        tracked[commit_hash] = node
        set_active(node, True)

    active_commits: dict[int, CommitNode] = {}
    for stage, nodes in stage_nodes.items():
        for node in reversed(nodes):
            if node.active:
                active_commits[stage] = node
                break
    return active_commits


def describe_targets(resume_from: str, active_commits: dict[int, CommitNode]) -> list[CommitNode]:
    targets = []
    for stage in REVERT_MAP[resume_from]:
        node = active_commits.get(stage)
        if node is not None:
            targets.append(node)
    return targets


def apply_reverts(cwd: Path, targets: list[CommitNode]) -> None:
    for node in targets:
        result = run_git(["revert", "--no-edit", node.commit_hash], cwd)
        if result.returncode != 0:
            stderr = result.stderr.strip()
            stdout = result.stdout.strip()
            details = stderr or stdout or f"git revert failed for {node.commit_hash}"
            raise RuntimeError(details)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Show or revert active downstream workflow stage commits.",
    )
    parser.add_argument(
        "resume_from",
        choices=sorted(REVERT_MAP),
        help="Explicit stage file mentioned by the user.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Execute git revert --no-edit for the resolved downstream stage commits.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    cwd = Path.cwd()

    try:
        ensure_git_repo(cwd)
        if args.apply:
            ensure_clean_worktree(cwd)
        active_commits = load_active_stage_commits(cwd)
        targets = describe_targets(args.resume_from, active_commits)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if not targets:
        print(f"No active downstream stage commits to revert for {args.resume_from}.")
        return 0

    print(f"Resolved downstream stage commits for {args.resume_from}:")
    for node in targets:
        print(f"- {node.subject} [{node.commit_hash[:12]}]")

    if not args.apply:
        print("Dry run only. Re-run with --apply to execute the reverts.")
        return 0

    try:
        apply_reverts(cwd, targets)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print("Created revert commits in the order listed above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
