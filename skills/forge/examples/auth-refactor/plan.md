# Plan

## Background

Authorization logic is currently correct but duplicated. The goal is to centralize decisions without changing access semantics.

## Selected Solution

Create an auth policy layer with explicit functions for session validation, role checks, and tenant scope checks, then migrate controllers one group at a time.

Why this option:

- It makes security logic testable in isolation
- It reduces duplication without a full rewrite
- It supports a safer rollout than a one-shot middleware rewrite

## Planned Changes

- Add an `AuthPolicy` module with explicit decision helpers
- Update shared middleware to delegate to `AuthPolicy`
- Migrate the highest-traffic controllers first
- Add policy-focused tests for role and tenant combinations
- Keep critical route-level regression tests in place during migration

## Edge Cases

- Users with multiple roles across tenants
- Service accounts that bypass interactive session checks
- Controllers that currently perform partial auth checks in a non-standard order

## Verification

- Run auth and route regression tests
- Compare allowed and denied results before and after migration for critical flows
- Manually verify cross-tenant access remains blocked
