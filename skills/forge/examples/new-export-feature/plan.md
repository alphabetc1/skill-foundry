# Plan

## Background

The invoice admin list already supports filtering. Export should be an extension of that flow, not a parallel implementation with separate business rules.

## Selected Solution

Use the existing invoice filter builder, add an export service that iterates over the filtered query in batches, and expose CSV and JSON downloads behind the existing finance admin guard.

Why this option:

- It keeps filter behavior consistent with the current list
- It avoids duplicate query logic
- It supports large exports better than building one large in-memory payload

## Planned Changes

- Add an `InvoiceExportService` that accepts normalized filters and output format
- Add admin controller or route handlers for CSV and JSON export
- Add audit log calls on export start and completion
- Add export buttons to the invoice admin UI
- Reuse the existing finance admin permission guard
- Add tests for format correctness, auth failures, and filter parity

## Edge Cases

- Empty exports should still return headers for CSV
- Invalid format values should return a validation error
- Long-running exports should fail cleanly if permissions or filters are invalid

## Verification

- Run backend tests for the invoice domain
- Run UI tests for export button visibility
- Manually verify CSV and JSON output with a filtered invoice set
