# Prompt

## User Goal

Add CSV and JSON export for invoices in the admin dashboard so finance admins can download filtered invoice data without manual copy-paste.

## Relevant Background

- The feature must reuse the existing invoice list filters
- Exports may include large result sets
- Finance data is sensitive and requires explicit permission checks
- Export actions should be auditable

## Requirements

- Add CSV export and JSON export from the invoice list flow
- Reuse the current filter parameters instead of introducing a second query path
- Restrict export access to finance admins only
- Record an audit log entry for every export request
- Keep the implementation safe for large datasets
- Add automated tests for authorization and output correctness

## Constraints

- Do not change the invoice data model
- Preserve existing invoice list behavior
- Prefer streaming or batched reads over loading the full dataset into memory

## Deliverables

- Backend export endpoint or service updates
- Admin UI trigger for export actions
- Permission checks and audit logging
- Tests covering CSV, JSON, and permission failures

## Validation

- Finance admins can export filtered invoices in CSV and JSON
- Non-admin users cannot access export actions
- Exported rows match the filtered invoice list
- Large exports complete without obvious memory spikes
