# Plan

## Background

Webhook handling must be idempotent because retries are expected. The bug most likely comes from logging provider event IDs without enforcing them as a deduplication boundary.

## Selected Solution

Store or check processed provider event IDs before applying the paid transition, and short-circuit duplicate deliveries while still returning a success response to the provider.

Why this option:

- It matches normal webhook retry behavior
- It protects both order state and downstream side effects
- It is smaller and safer than rewriting the whole payment flow

## Planned Changes

- Add an idempotency guard around webhook event processing
- Ensure duplicate deliveries do not emit duplicate side effects
- Keep signature validation as the first gate
- Add regression tests for duplicate deliveries and replay behavior

## Edge Cases

- Duplicate events arriving after a successful first processing
- Event replay after partial downstream failure
- Providers sending the same business event under different transport timings

## Verification

- Run payment webhook tests
- Manually replay the same payload twice in a local environment
- Confirm only one paid transition and one notification are emitted
