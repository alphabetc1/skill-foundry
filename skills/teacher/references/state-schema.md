# Learner State Schema

The learner state lives at `learning/<topic-slug>/learner-state.yaml`. It is the durable source of truth for progress across conversations.

## Required Top-Level Fields

- `topic`: Human-readable study topic.
- `goal`: Current target outcome.
- `deadline`: Interview date, deadline, or `TBD`.
- `background`: Short description of prior experience.
- `current_module`: The active curriculum module.
- `mastered`: Verified strengths with evidence.
- `shaky`: Topics the learner can partly use but cannot yet trust under pressure.
- `prerequisite_gaps`: Missing dependencies that block progress.
- `misconceptions`: Incorrect beliefs observed from learner output.
- `review_queue`: Topics to revisit later.
- `recent_session_evidence`: The most recent session-level evidence records.
- `next_action`: The single highest-priority next step.

## Field Shapes

`current_module`

```yaml
current_module:
  id: "request-lifecycle"
  status: "in-progress"
  why_now: "Needed before batching and KV cache tradeoffs will make sense."
```

`mastered[]`

```yaml
- module: "prefill-decode"
  topic: "Decode is memory-bound for large KV footprints"
  evidence: "Learner contrasted arithmetic intensity in prefill vs decode and applied it to latency expectations."
  verified_on: "2026-03-14"
```

`shaky[]`

```yaml
- module: "batching-scheduling"
  topic: "Continuous batching fairness tradeoffs"
  signal: "Learner described throughput benefits but missed tail-latency impact."
  next_check: "Ask for a scheduler design comparison."
```

`prerequisite_gaps[]`

```yaml
- module: "kernels-hardware"
  topic: "GPU memory hierarchy"
  impact: "Cannot reason about bandwidth bottlenecks yet."
```

`misconceptions[]`

```yaml
- module: "kv-cache"
  belief: "KV cache only matters during prefill"
  correction: "KV cache primarily matters for decode reuse and memory footprint."
  observed_in: "diagnose session on 2026-03-14"
```

`review_queue[]`

```yaml
- module: "decode-optimizations"
  topic: "Speculative decoding acceptance-rate tradeoffs"
  reason: "Previously shaky under comparison questions"
  priority: "medium"
  next_review: "2026-03-18"
```

`recent_session_evidence[]`

```yaml
- date: "2026-03-14"
  mode: "diagnose"
  module: "prefill-decode"
  learner_output: "Explained why decode scales differently from prefill."
  assessment: "Understands the split but still confuses compute-bound and memory-bound cases."
  resulting_updates: "Added one misconception and one shaky topic."
```

## Update Rules

- Keep `current_module` aligned with the module the learner is actively working on now.
- Only add an item to `mastered` after a verifiable learner performance signal.
- Move a topic out of `shaky` only when a later session provides stronger evidence.
- Keep `misconceptions` concrete. Store the incorrect claim, not a vague label.
- Use `review_queue` for future retrieval practice, not as a generic backlog.
- Keep `recent_session_evidence` short and evidence-based. Prefer the newest 5 to 8 entries.
- Keep `next_action` to one imperative sentence. It should be specific enough to start the next session immediately.

## Evidence Standard

Count mastery evidence only when the learner demonstrates at least one of these:

- accurate restatement in their own words
- comparison between similar concepts or design choices
- step-by-step derivation or causal explanation
- application to a new scenario, failure mode, or interview question

Explaining a concept to the learner is not evidence.
