---
name: forge
description: Five-stage workflow for coding tasks that progresses across separate invocations by generating `prompt.md`, then `research.md`, then `plan.md`, then implementing from `plan.md`, and finally reviewing the completed implementation into `review.md`. Use when Codex should refine a user's request into staged artifacts, keep each stage reviewable with dedicated git commits, and resume from an explicitly mentioned `prompt.md`, `research.md`, `plan.md`, or `review.md`.
---

# Forge

## Overview

Advance the work in exactly one stage per invocation.

Do not implement code before stage 4.

Write `prompt.md`, `research.md`, `plan.md`, and `review.md` in the language of the current user request. Keep source code, identifiers, and code comments in English.

Create or update all stage files in the current working directory.

## Detect the Stage

Treat a stage file as the resume signal only when the current user request explicitly includes the literal filename.

- If the request does not explicitly mention `prompt.md`, `research.md`, `plan.md`, or `review.md`, run stage 1 only.
- If the request explicitly mentions `prompt.md`, run stage 2 only.
- If the request explicitly mentions `research.md`, run stage 3 only.
- If the request explicitly mentions `plan.md`, run stage 4 only.
- If the request explicitly mentions `review.md`, run stage 5 only.

If the user explicitly mentions multiple stage filenames and the intended starting point is ambiguous, ask which file should be treated as authoritative before changing anything.

## Stage Announcement

Before doing any substantive work in an invocation, explicitly announce the active stage in one short line.

Use this format:

- `Current stage: stage 1 - generate prompt.md`
- `Current stage: stage 2 - generate research.md`
- `Current stage: stage 3 - generate plan.md`
- `Current stage: stage 4 - implement plan.md`
- `Current stage: stage 5 - review implementation`

## Git Rules

Require a git repository for this workflow. If the current directory is not inside a git repository, explain that the staged workflow needs git history and stop.

Inspect `git status --short` before changing anything. If uncommitted changes would make `git revert` unsafe or would mix unrelated edits into the current stage commit, explain the conflict and stop instead of forcing it.

For resume flows, prefer `scripts/revert_stage_commits.py` over hand-written `git log` and `git revert` sequences.

Use these exact stage commit messages:

- `stage1: generate prompt.md`
- `stage2: generate research.md`
- `stage3: generate plan.md`
- `stage4: implement plan.md`
- `stage5: review and fix blocking issues`

Create exactly one stage commit after finishing the active stage.

When the user resumes from an updated upstream artifact, revert stale downstream stage commits before generating the new output. Prefer this helper command while keeping the working directory at the user's repository root:

```bash
python scripts/revert_stage_commits.py prompt.md --apply
```

Resolve `scripts/revert_stage_commits.py` relative to this skill folder. Swap `prompt.md` for `research.md`, `plan.md`, or `review.md` as needed. The script resolves the latest active downstream stage commits and reverts them in the correct order with `git revert --no-edit`. Use the default dry run first if the history looks unusual. Never rewrite history with `git reset --hard`.

Use this downstream revert map:

- Resume from `prompt.md`: revert the latest active `stage5`, then `stage4`, then `stage3`, then `stage2` commit before regenerating `research.md`.
- Resume from `research.md`: revert the latest active `stage5`, then `stage4`, then `stage3` commit before regenerating `plan.md`.
- Resume from `plan.md`: revert the latest active `stage5`, then `stage4` commit before re-implementing.
- Resume from `review.md`: revert the latest active `stage5` commit before re-running the review.

If a downstream stage commit does not exist, continue without error.

Commit only the files relevant to the current stage and any revert commits created to remove stale downstream work.

## Stage 1

Run stage 1 when the user invokes this skill without explicitly naming any stage file.

Parse the user's request and rewrite it into a stronger model-ready brief saved as `prompt.md`.

Make `prompt.md` concrete and implementation-oriented. Include the user goal, relevant background, explicit requirements, constraints, expected deliverables, validation expectations, and any important assumptions that later stages must carry forward.

After writing `prompt.md`, create the commit `stage1: generate prompt.md` and stop. Do not create `research.md`, do not create `plan.md`, and do not implement code in this invocation.

## Stage 2

Run stage 2 only when the user explicitly mentions `prompt.md`.

Require `prompt.md` to exist. If it is missing, say so and stop.

Use `prompt.md` as the primary brief for repository research. Generate `research.md` that briefly covers:

- the current state
- the problem background
- the requirements
- recommended implementation options, with multiple options allowed and ordered by priority
- test strategies, with multiple options allowed and ordered by priority

Keep `research.md` concise, decision-oriented, and grounded in the actual repository state.

After writing `research.md`, create the commit `stage2: generate research.md` and stop. Do not create `plan.md`, and do not implement code in this invocation.

## Stage 3

Run stage 3 only when the user explicitly mentions `research.md`.

Require both `prompt.md` and `research.md` to exist. If either file is missing, say exactly which file is missing and stop.

Use `prompt.md` and `research.md` together, choose the best recommended option unless the user explicitly directs another option, and generate an implementation-ready `plan.md`.

Make `plan.md` detailed enough that stage 4 can execute it without redoing the design work. Include:

- the full problem background
- the current state
- the requirements
- the selected solution and why it was chosen
- the planned code and file changes
- edge cases or migration concerns
- the verification and testing plan

After writing `plan.md`, create the commit `stage3: generate plan.md` and stop. Do not implement code in this invocation.

## Stage 4

Run stage 4 only when the user explicitly mentions `plan.md`.

Require `plan.md` to exist. If it is missing, say so and stop.

Implement the repository changes described in `plan.md`.

If `plan.md` was updated after an earlier implementation, revert the stale `stage4` commit first, then apply the new implementation.

Follow `plan.md` closely. If implementation reveals a material flaw or contradiction in `plan.md`, stop and discuss the gap instead of silently changing the plan.

Run the most relevant validation or tests from `plan.md` when feasible. If a planned test cannot be run, say why.

After implementation, create the commit `stage4: implement plan.md` and stop. Do not generate `review.md` in this invocation.

## Stage 5

Run stage 5 only when the user explicitly mentions `review.md`.

Require `plan.md` to exist and require an active `stage4: implement plan.md` commit in the current repository history. If either prerequisite is missing, say so and stop.

Treat stage 5 as a fresh review pass that is separate from the implementation mindset used in stage 4. Review the completed functionality end to end, generate or overwrite `review.md`, and decide whether any blocking issue remains.

Blocking issues are defects that must be fixed before the workflow can be considered complete, such as incorrect behavior, unmet requirements, broken flows, failing required tests, data-loss risks, security problems, or severe regressions. Non-blocking concerns may stay documented in `review.md` without forcing another implementation loop.

Stage 5 is an internal loop inside one invocation:

- review the current implementation and write the current findings to `review.md`
- if blocking issues exist, fix them immediately without creating an intermediate commit
- rerun the relevant review and verification steps
- update `review.md` to reflect the latest pass
- repeat until no blocking issue remains

Keep exactly one final stage 5 commit for the whole loop. Do not create intermediate commits for individual fixes discovered during review.

Make `review.md` concise and decision-oriented. Include the review scope, what was checked, any blocking issues that were found and fixed during the loop, any remaining non-blocking concerns, and an explicit final status stating whether blocking issues remain. The final saved `review.md` must state that no blocking issues remain before the workflow can end.

After the review loop finishes with no blocking issues remaining, create the commit `stage5: review and fix blocking issues`.

## Response Pattern

After each invocation, briefly report:

- which stage ran
- which file was created or updated
- which commit or revert actions were created
- what explicit next invocation should mention to continue, if another stage remains
