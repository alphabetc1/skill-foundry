---
name: forge
description: Explicit-invocation-only five-stage workflow for coding tasks. Use this skill only when the user explicitly invokes `forge` or `$forge` and wants a request turned into `prompt.md`, `research.md`, `plan.md`, implementation, `review.md`, and stage commits; do not trigger it from task shape alone.
license: Apache-2.0
---

# Forge

## Overview

Run this skill only when the current user request explicitly invokes `forge` or `$forge`. If the request merely resembles a staged coding task, do not use Forge.

Advance the work from the detected starting stage through stage 5 in one invocation unless the user explicitly asks to stop after a specific stage.

Do not implement code before stage 4.

Write `prompt.md`, `research.md`, `plan.md`, and `review.md` in the language of the current user request. Keep source code, identifiers, and code comments in English.

Create or update all stage files in the current working directory.

Forge requires subagent support for its intended stage 4 and stage 5 execution model. Do not silently collapse those stages back into a single-agent build-and-review flow.

## Detect the Stage

Treat a stage file as the starting-stage resume signal only when the current user request explicitly includes the literal filename.

- If the request does not explicitly mention `prompt.md`, `research.md`, `plan.md`, or `review.md`, start at stage 1.
- If the request explicitly mentions `prompt.md`, start at stage 2.
- If the request explicitly mentions `research.md`, start at stage 3.
- If the request explicitly mentions `plan.md`, start at stage 4.
- If the request explicitly mentions `review.md`, start at stage 5.

After choosing the starting stage, continue through all later stages by default.

If the user explicitly asks to stop after a particular stage, to only generate a specific artifact, or to skip a later stage such as review, honor that narrower stop point.

If the user mentions one stage file as the resume point and a later stage file as the requested stop point or final output, treat that as a valid start-and-stop pair instead of an ambiguity.

If the user explicitly mentions multiple stage filenames and the intended starting point is ambiguous, ask which file should be treated as authoritative before changing anything.

## Stage Announcement

Before starting each substantive stage, explicitly announce the active stage in one short line.

If an invocation runs multiple stages, emit one announcement before each stage begins.

Use this format:

- `Current stage: stage 1 - generate prompt.md`
- `Current stage: stage 2 - generate research.md`
- `Current stage: stage 3 - generate plan.md`
- `Current stage: stage 4 - implement plan.md`
- `Current stage: stage 5 - review implementation`

## Subagent Rules

- Stage 4 must run through exactly one dedicated implementation subagent.
- Spawn that implementation subagent only after `research.md` and `plan.md` are finalized for the current invocation.
- Pass both `research.md` and `plan.md` to the implementation subagent as explicit inputs or equivalent context attachments.
- The implementation subagent owns stage 4 code changes and the first pass of stage 4 validation.
- The main agent remains responsible for orchestration, integration of the implementation result into the main workspace when needed, and the final `stage4: implement plan.md` commit.
- If the execution environment uses isolated subagent workspaces, the implementation subagent should return a concrete patch, diff, or changed-file result that the main agent integrates before committing.
- Stage 5 must run as three parallel review tracks: the main agent plus exactly two independent review subagents.
- Review subagents are reviewers only. They must not create commits and should not be the agents that fix blocking issues.
- Give the two review subagents distinct review focus areas whenever practical, for example one focused on requirements and correctness, the other focused on regressions, tests, and edge cases.
- The main agent must aggregate the two review-subagent outputs together with its own review into the final `review.md`.
- If any blocking issue is found, only the main agent fixes it, reruns the relevant verification, relaunches both review subagents, reruns its own review, and repeats stage 5 until no blocking issue remains.

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

Create exactly one stage commit after finishing each stage that runs in the invocation.

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

Run stage 1 when the detected starting stage is stage 1.

Parse the user's request and rewrite it into a stronger model-ready brief saved as `prompt.md`.

Make `prompt.md` concrete and implementation-oriented. Include the user goal, relevant background, explicit requirements, constraints, expected deliverables, validation expectations, and any important assumptions that later stages must carry forward.

After writing `prompt.md`, create the commit `stage1: generate prompt.md`.

Continue to stage 2 unless the user explicitly asked to stop after stage 1 or after generating `prompt.md`.

## Stage 2

Run stage 2 when the detected starting stage is stage 2 or when stage 1 just completed and the workflow is continuing.

Require `prompt.md` to exist. If it is missing, say so and stop.

Use `prompt.md` as the primary brief for repository research. Generate `research.md` that briefly covers:

- the current state
- the problem background
- the requirements
- recommended implementation options, with multiple options allowed and ordered by priority
- test strategies, with multiple options allowed and ordered by priority

Keep `research.md` concise, decision-oriented, and grounded in the actual repository state.

After writing `research.md`, create the commit `stage2: generate research.md`.

Continue to stage 3 unless the user explicitly asked to stop after stage 2 or after generating `research.md`.

## Stage 3

Run stage 3 when the detected starting stage is stage 3 or when stage 2 just completed and the workflow is continuing.

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

After writing `plan.md`, create the commit `stage3: generate plan.md`.

Continue to stage 4 unless the user explicitly asked to stop after stage 3 or after generating `plan.md`.

## Stage 4

Run stage 4 when the detected starting stage is stage 4 or when stage 3 just completed and the workflow is continuing.

Require both `research.md` and `plan.md` to exist. If either file is missing, say exactly which file is missing and stop.

Spawn one dedicated implementation subagent for stage 4 and pass it `research.md` plus `plan.md`.

If `plan.md` was updated after an earlier implementation, revert the stale `stage4` commit first, then apply the new implementation.

Instruct the implementation subagent to implement the repository changes described in `plan.md`, follow `plan.md` closely, run the most relevant validation from `plan.md` when feasible, and report any material flaw or contradiction in `plan.md` instead of silently changing the plan.

After the implementation subagent finishes, inspect and integrate its result into the main workspace if needed.

If the implementation subagent reports a material flaw or contradiction in `plan.md`, stop and discuss the gap instead of silently changing the plan.

Run any missing or follow-up validation needed to confirm the integrated implementation. If a planned test cannot be run, say why.

After implementation, create the commit `stage4: implement plan.md`.

Continue to stage 5 unless the user explicitly asked to stop after stage 4, after implementation, or to skip review.

## Stage 5

Run stage 5 when the detected starting stage is stage 5 or when stage 4 just completed and the workflow is continuing.

Require `plan.md` to exist and require an active `stage4: implement plan.md` commit in the current repository history. If either prerequisite is missing, say so and stop.

Treat stage 5 as a fresh review pass that is separate from the implementation mindset used in stage 4. Launch two independent review subagents, perform the main-agent review in parallel, generate or overwrite `review.md`, and decide whether any blocking issue remains.

Blocking issues are defects that must be fixed before the workflow can be considered complete, such as incorrect behavior, unmet requirements, broken flows, failing required tests, data-loss risks, security problems, or severe regressions. Non-blocking concerns may stay documented in `review.md` without forcing another implementation loop.

Stage 5 is an internal loop inside one invocation:

- launch two review subagents with distinct review focus areas
- run the main-agent review in parallel with those review subagents
- aggregate all three review passes and write the current findings to `review.md`
- if blocking issues exist, fix them immediately in the main workspace without creating an intermediate commit
- rerun the relevant verification steps
- relaunch both review subagents and rerun the main-agent review
- update `review.md` to reflect the latest pass
- repeat until no blocking issue remains

Keep exactly one final stage 5 commit for the whole loop. Do not create intermediate commits for individual fixes discovered during review.

Make `review.md` concise and decision-oriented. Include the review scope, what was checked, a brief summary of the main-agent review plus the two review-subagent passes, any blocking issues that were found and fixed during the loop, any remaining non-blocking concerns, and an explicit final status stating whether blocking issues remain. The final saved `review.md` must state that no blocking issues remain before the workflow can end.

After the review loop finishes with no blocking issues remaining, create the commit `stage5: review and fix blocking issues`.

## Response Pattern

After each invocation, briefly report:

- which stage or stages ran
- which file was created or updated
- which commit or revert actions were created
- which implementation or review subagents were launched
- whether the workflow reached stage 5 or stopped early because the user explicitly asked it to
