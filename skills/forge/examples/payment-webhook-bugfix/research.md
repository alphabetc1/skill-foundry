# Research

## Current State

- Signature validation happens before order updates
- Order payment state changes occur in the webhook handler
- Event identifiers are logged but not used as a hard idempotency key

## Problem Background

Webhook providers retry on timeout or transient failure. If the handler treats every delivery as new, duplicate state transitions become possible.

## Recommended Options

1. Add an idempotency check keyed by provider event ID before the order paid transition.
2. Fall back to checking whether the order is already paid only if provider event IDs are unavailable.

## Recommended Test Strategy

1. Add handler tests for first delivery, exact duplicate delivery, and replay after success.
2. Add a regression test that proves duplicate deliveries do not emit duplicate side effects such as email or audit events.
