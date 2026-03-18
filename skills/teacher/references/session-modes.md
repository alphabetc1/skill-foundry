# Session Modes

Use exactly one primary mode per substantive session.

## Selection Rules

- `map`: Choose this when the learner needs orientation, a graph overview, or a recommended starting point.
- `teach`: Choose this when the learner wants a focused explanation and prerequisites are mostly satisfied.
- `diagnose`: Choose this when the learner's real level is unclear or inconsistent.
- `drill`: Choose this for interview-style questioning and time pressure.
- `recall`: Choose this when the learner needs spaced retrieval from the `review_queue`.
- `plan`: Choose this for sequencing, pacing, or deadline-aware study planning.

If a session starts in the wrong mode, explain the switch in one sentence and continue with the better mode.

## `map`

Use when:

- the learner is new to the topic
- the curriculum graph is missing or unclear
- the learner asks for the big picture

Output structure:

1. Topic map or graph slice
2. Why the current module matters
3. Key dependencies and downstream modules
4. Recommended next lesson

Notes:

- End every `map` session with a recommended next lesson.
- Do not dive deep into every node. Prioritize orientation.

## `teach`

Use when:

- the learner asks to understand one module or tradeoff
- the learner needs a guided explanation after `map` or `diagnose`

Output structure:

1. Module goal
2. Core mechanism
3. Boundaries and tradeoffs
4. One quick understanding check
5. State update decision

Notes:

- Emphasize concept boundaries and design tradeoffs for interview prep.
- A teaching session alone does not justify moving a topic into `mastered`.

## `diagnose`

Use when:

- the learner says they "kind of know" a topic
- answers sound fluent but possibly shallow
- you need to place the learner on the graph

Output structure:

1. Diagnostic hypothesis
2. A short sequence of probing questions
3. Synthesis of strengths, gaps, and misconceptions
4. Recommended follow-up mode or module

Notes:

- Prefer short, high-signal probes over a long exam.
- Use the results to update `shaky`, `prerequisite_gaps`, and `misconceptions`.

## `drill`

Use when:

- the learner wants mock interview practice
- you want to pressure-test recall and tradeoff reasoning

Output structure:

1. One interview question
2. Wait for the learner answer
3. Brief assessment
4. Correction or better answer if needed
5. Next question or close

Notes:

- Ask one question at a time.
- Do not dump all answers up front.
- Convert wrong answers into state updates.

## `recall`

Use when:

- the `review_queue` has due items
- the learner wants to revisit older material
- you want to reduce forgetting before moving forward

Output structure:

1. Retrieval prompt
2. Wait for learner response
3. Compare with target reasoning
4. Repair gaps
5. Reschedule review if needed

Notes:

- Prefer active recall over re-explanation.
- Reinsert weak items into `review_queue` with a clearer next review condition.

## `plan`

Use when:

- the learner asks what to do next
- there is a deadline or interview date
- the graph needs to be turned into a schedule

Output structure:

1. Goal and constraints
2. Ordered module sequence
3. Session cadence or time boxes
4. Main risks and dependency bottlenecks
5. Single next action

Notes:

- Keep the plan tied to the current learner state.
- Do not output a generic checklist detached from the curriculum graph.
