# Research

## Current State

- Controllers combine session presence, role checks, and tenant checks inline
- Some checks already call shared helpers, but the boundary is inconsistent
- Test coverage exists around top-level routes, not around reusable policy decisions

## Problem Background

The refactor is risky because auth bugs create security regressions. The best path is one that centralizes policy decisions while keeping rollout scope small.

## Recommended Options

1. Introduce an auth policy layer and migrate controllers to it incrementally.
2. Consolidate current middleware into a single large middleware chain if policy extraction is too expensive.

## Recommended Test Strategy

1. Add policy-level tests for session, role, and tenant combinations.
2. Keep route-level regression tests for critical admin and cross-tenant flows.
3. Add one migration-focused test proving the old and new paths reject the same invalid request.
