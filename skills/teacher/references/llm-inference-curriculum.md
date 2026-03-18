# LLM Inference Interview Prep Curriculum

Use this as the default curriculum graph for LLM inference interview preparation.

## Default Start Path

Recommended starting path:

1. `request-lifecycle`
2. `prefill-decode`
3. `batching-scheduling`
4. `kv-cache`
5. `kernels-hardware`
6. `decode-optimizations`
7. `quantization`
8. `parallelism-distributed-serving`
9. `serving-architecture`
10. `reliability-observability`

The graph is not a strict linear syllabus. Follow dependencies when the learner exposes gaps.

## Modules

### `request-lifecycle`

- Why it matters: Establishes the end-to-end serving path so later optimizations have context.
- Prerequisites: None.
- Must-know points:
  - Request path from tokenization through scheduling, model execution, detokenization, and response assembly.
  - Main latency buckets and where queueing shows up.
  - Where batching, KV cache, routing, and observability fit.
- Interview signals:
  - Can narrate the serving path cleanly.
  - Can locate likely latency contributors without hand-waving.
- Exit criteria:
  - Explains the full path and can place at least three optimization levers on it.

### `prefill-decode`

- Why it matters: Many inference tradeoffs only make sense after separating prompt processing from token-by-token generation.
- Prerequisites:
  - `request-lifecycle`
- Must-know points:
  - Different compute patterns in prefill and decode.
  - Why decode often becomes memory-bound.
  - How sequence length changes cost in each phase.
- Interview signals:
  - Can compare latency and throughput implications of prefill vs decode.
  - Can explain why optimizations often target one phase more than the other.
- Exit criteria:
  - Correctly reasons about performance differences between the two phases in a new scenario.

### `batching-scheduling`

- Why it matters: Real serving systems win or lose on how requests share model execution time.
- Prerequisites:
  - `prefill-decode`
- Must-know points:
  - Static batching vs continuous batching.
  - Queueing, fairness, and tail-latency tradeoffs.
  - Interaction between request mix and scheduler behavior.
- Interview signals:
  - Can explain why naive batching hurts latency for some workloads.
  - Can discuss throughput vs responsiveness tradeoffs.
- Exit criteria:
  - Compares at least two scheduling approaches and their tradeoffs coherently.

### `kv-cache`

- Why it matters: KV cache drives both decode efficiency and memory pressure.
- Prerequisites:
  - `prefill-decode`
- Must-know points:
  - Why KV cache exists.
  - How it changes decode complexity and memory footprint.
  - Tradeoffs around cache layout, eviction, and reuse.
- Interview signals:
  - Can explain why KV cache helps decode.
  - Can reason about when KV cache becomes the bottleneck.
- Exit criteria:
  - Correctly explains performance benefits and memory costs of KV cache in one answer.

### `kernels-hardware`

- Why it matters: Inference performance is constrained by hardware utilization, memory movement, and kernel efficiency.
- Prerequisites:
  - `prefill-decode`
- Must-know points:
  - Compute-bound vs memory-bound behavior.
  - GPU bandwidth, occupancy, and launch-overhead intuition.
  - Why fused kernels and optimized attention implementations matter.
- Interview signals:
  - Can connect workload shape to hardware bottlenecks.
  - Can explain why "more FLOPs" does not guarantee better inference speed.
- Exit criteria:
  - Diagnoses a bottleneck as primarily compute, bandwidth, or overhead limited with defensible reasoning.

### `decode-optimizations`

- Why it matters: This is where many practical serving improvements show up in interviews.
- Prerequisites:
  - `batching-scheduling`
  - `kv-cache`
  - `kernels-hardware`
- Must-know points:
  - Speculative decoding basics and acceptance-rate tradeoffs.
  - Prefix caching and reuse patterns.
  - Early stopping, paged attention, and token selection overheads.
- Interview signals:
  - Can compare at least two decode optimizations without treating them as universally good.
  - Can state when an optimization backfires.
- Exit criteria:
  - Chooses an optimization for a scenario and defends the tradeoff.

### `quantization`

- Why it matters: Quantization is a major lever for memory footprint, throughput, and deployment cost.
- Prerequisites:
  - `prefill-decode`
  - `kernels-hardware`
- Must-know points:
  - Weight-only vs activation-aware quantization.
  - Accuracy, calibration, and hardware support tradeoffs.
  - Why lower precision helps memory bandwidth and capacity.
- Interview signals:
  - Can explain when quantization helps and what risks it introduces.
  - Can compare serving impact beyond just model size reduction.
- Exit criteria:
  - Gives a balanced answer on performance gains, quality risk, and deployment constraints.

### `parallelism-distributed-serving`

- Why it matters: Large models and large traffic both force distribution choices.
- Prerequisites:
  - `request-lifecycle`
  - `kernels-hardware`
- Must-know points:
  - Tensor, pipeline, and data parallelism roles in serving.
  - Communication costs and topology sensitivity.
  - Routing and replica-level scaling tradeoffs.
- Interview signals:
  - Can explain why one form of parallelism fits a serving constraint better than another.
  - Can mention communication overhead, memory fit, and utilization together.
- Exit criteria:
  - Recommends a parallelism strategy for a deployment scenario and justifies it.

### `serving-architecture`

- Why it matters: Interviews often expect system-level thinking beyond isolated kernels.
- Prerequisites:
  - `batching-scheduling`
  - `parallelism-distributed-serving`
  - `quantization`
- Must-know points:
  - Frontend/router, scheduler, worker, cache, and model runtime responsibilities.
  - Multi-model and multi-tenant serving considerations.
  - Where autoscaling and admission control fit.
- Interview signals:
  - Can sketch a serving stack and identify key control points.
  - Can reason about isolation, efficiency, and complexity together.
- Exit criteria:
  - Produces a coherent serving architecture and explains why each layer exists.

### `reliability-observability`

- Why it matters: Production inference work is incomplete without debugging, SLOs, and failure handling.
- Prerequisites:
  - `serving-architecture`
- Must-know points:
  - Latency, throughput, and error metrics.
  - Queue depth, cache hit rate, token-level metrics, and saturation signals.
  - Fallbacks, retries, overload handling, and deployment safety.
- Interview signals:
  - Can say what to measure and why.
  - Can connect symptoms to likely root causes.
- Exit criteria:
  - Defines a minimal observability set and uses it to reason about a concrete failure or regression.
