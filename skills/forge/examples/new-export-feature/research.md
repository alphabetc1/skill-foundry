# Research

## Current State

- The invoice list already accepts normalized filter parameters
- Admin actions use a shared permission guard
- Audit logging exists for refunds but not for exports

## Problem Background

The feature is user-facing, permission-sensitive, and potentially expensive for large datasets. The main design choice is whether to reuse the list query path directly or build a dedicated export query service.

## Recommended Options

1. Reuse the existing filtered invoice query and wrap it in a streaming export service.
2. Build a separate export query path only if the current list query cannot produce stable, pageless results.

## Recommended Test Strategy

1. Add service-level tests for CSV and JSON formatting with representative invoice rows.
2. Add authorization tests for finance admin and non-admin users.
3. Add an integration test that verifies filter parity between the list view and the export output.
