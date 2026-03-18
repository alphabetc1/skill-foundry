# Prompt

## User Goal

Refactor authentication and authorization logic so session validation, role checks, and tenant checks are centralized instead of duplicated across controllers.

## Relevant Background

- The current auth flow works but has drifted into repeated checks
- Refactors in auth code are high risk because failures can silently broaden access
- The user wants a safer internal structure, not new product behavior

## Requirements

- Preserve existing access behavior
- Reduce repeated auth logic in controllers
- Create a clearer surface for role and tenant checks
- Make the rules easier to test
- Sequence changes so the rewrite is incremental rather than disruptive

## Constraints

- No user-visible auth behavior changes
- No flag day migration
- Favor adapter layers if they reduce rollout risk

## Deliverables

- Centralized auth service or policy layer
- Controller updates to use the new auth entry points
- Regression tests for role and tenant combinations

## Validation

- Existing allowed flows still work
- Existing denied flows still fail
- Authorization tests are easier to read and maintain than before
