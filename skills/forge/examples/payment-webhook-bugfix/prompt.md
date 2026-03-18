# Prompt

## User Goal

Fix duplicate payment webhook processing that can mark the same order as paid twice.

## Relevant Background

- The issue is intermittent and likely tied to webhook retries
- Payment webhooks are externally triggered and must be idempotent
- Incorrect duplicate handling can corrupt order state and financial reporting

## Requirements

- Identify the most likely duplicate-processing path
- Make webhook handling idempotent
- Preserve the current successful path for first-time events
- Add automated coverage for retry and duplicate delivery behavior

## Constraints

- Do not break existing payment provider signature validation
- Avoid schema changes unless they are necessary for idempotency
- Favor targeted fixes over a broad payments rewrite

## Deliverables

- Root-cause analysis in repository context
- Idempotent webhook processing changes
- Tests for first delivery, retry delivery, and out-of-order duplicate delivery

## Validation

- Duplicate deliveries no longer create duplicate paid transitions
- Valid first deliveries still complete successfully
- Existing signature validation remains intact
