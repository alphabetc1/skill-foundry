# Curriculum Graph Design

Design the curriculum as a dependency graph, not a flat checklist.

## Required Module Schema

Each module must define:

- `id`: Stable slug for the module.
- `name`: Human-readable module name.
- `why_it_matters`: Why this node matters for the larger topic or interview performance.
- `prerequisites`: Upstream module ids or prerequisite concepts.
- `must_know_points`: Concepts the learner must be able to explain or apply.
- `interview_signals`: What a strong answer looks like in an interview.
- `exit_criteria`: Observable conditions for leaving the module.

## Example Shape

```yaml
- id: "request-lifecycle"
  name: "End-to-End Request Lifecycle"
  why_it_matters: "Provides the control-flow backbone for all later performance topics."
  prerequisites: []
  must_know_points:
    - "Request enters tokenizer, scheduler, model execution, detokenizer, and response path."
  interview_signals:
    - "Can describe latency contributors across the serving stack."
  exit_criteria:
    - "Explains the full serving path and locates batching, KV cache, and observability in it."
```

## Graph Rules

- Dependencies express what must already be understood, not merely what usually appears earlier.
- A module may have multiple downstream consumers.
- The current module should be the highest-value node whose prerequisites are mostly satisfied.
- If a blocking prerequisite gap appears, move backward in the graph before continuing forward.

## Module Selection Rules

Choose the current module in this order:

1. If the learner has a blocking prerequisite gap, select that missing dependency.
2. Else, if the current module has not met its exit criteria, stay on it.
3. Else, select the highest-priority downstream module that best supports the learner goal.
4. Else, if retention risk is high, switch to `recall` on a queued module before advancing.

## Exit Criteria Standard

Exit criteria should be performance-based. Good criteria include:

- can explain the mechanism without collapsing adjacent concepts
- can compare tradeoffs between two approaches
- can reason about a failure mode or bottleneck
- can answer an interview-style prompt with a coherent structure

Bad criteria include:

- "Saw the explanation once"
- "Read an article"
- "Feels comfortable"

## Curriculum Maintenance

- Add new modules only when they represent a distinct concept cluster or interview signal.
- Avoid splitting modules so finely that the graph becomes a checklist.
- When the user studies a new topic family, create a new graph rather than overloading an unrelated one.
