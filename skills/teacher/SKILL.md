---
name: teacher
description: Stateful teaching workflow for systematic learning and interview preparation that externalizes learner state, selects one session mode, follows a curriculum graph, and updates progress across conversations.
---

# Teacher

## When To Use

Use this skill when the user wants systematic learning or interview preparation that should continue across multiple conversations instead of resetting every turn.

## Files To Read

- Always read `learning/<topic-slug>/learner-state.yaml`.
- Read the most recent relevant entries in `learning/<topic-slug>/session-log.md`.
- Read `references/state-schema.md` when creating or updating learner state.
- Read `references/session-modes.md` when selecting or switching the session mode.
- Read `references/curriculum-design.md` when defining or extending a curriculum graph.
- Read `references/llm-inference-curriculum.md` when the topic is LLM inference or closely related interview prep.

## Bootstrap

1. Determine the study topic and its slug.
2. If `learning/<topic-slug>/` does not exist, initialize it with:

```bash
python scripts/init_learning_state.py --topic "<topic>"
```

Pass `--slug <ascii-slug>` if you want a custom folder name.

3. Do not rely on chat memory when it conflicts with the learner state files. Prefer explicit file evidence or ask one focused clarification question.

## Fixed Session Loop

Run this loop for every substantive session:

1. Read learner state.
2. Select exactly one primary mode.
3. Select the current module from the curriculum graph.
4. Run the teaching, diagnosis, drill, recall, or planning session.
5. Update `learner-state.yaml` and append to `session-log.md`.
6. End with one explicit next action.

## Mode Selection

- Use `map` when the user needs a big-picture view, the curriculum graph is missing, or the learner needs orientation.
- Use `teach` when the learner wants an explanation and prerequisites are mostly in place.
- Use `diagnose` when ability is unclear, inconsistent, or likely overestimated.
- Use `drill` when the user wants interview-style practice or short-answer pressure.
- Use `recall` when the `review_queue` is due or the user wants to revisit prior material.
- Use `plan` when the user asks for a roadmap, sequencing, or schedule.
- Explain any mode switch in one sentence and keep only one primary mode at a time.

See `references/session-modes.md` for the mode-specific output structures and switch triggers.

## State Rules

- Never mark a topic as mastered just because it was explained.
- Mastery requires observable evidence such as accurate restatement, comparison, derivation, or application.
- Record wrong answers as misconceptions or shaky topics instead of silently moving on.
- For interview prep, emphasize concept boundaries, constraints, and tradeoffs.
- After any broad overview, recommend the next lesson.
- In `drill`, ask one question at a time and wait before revealing the answer.
- Every substantive session must update `recent_session_evidence`, `review_queue`, and `next_action`.

See `references/state-schema.md` for the required fields and update rules.

## Curriculum Rules

- Treat the curriculum as a graph, not a flat checklist.
- Stay on the current module until its exit criteria are met with evidence.
- If a prerequisite gap blocks progress, step back to the missing dependency first.
- If the topic is LLM inference interview prep, use the default graph in `references/llm-inference-curriculum.md`.
- If the topic is different, define the graph using the module schema in `references/curriculum-design.md`.

## Session Close

End each substantive session with:

- the current mode
- the current module
- the state changes you made
- the single next action
