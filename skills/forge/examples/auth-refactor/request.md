# Request

Refactor the authentication flow so session checks, role checks, and tenant checks are no longer spread across controllers.

Requirements:

- Keep behavior backward compatible
- Reduce duplicate middleware logic
- Make authorization rules easier to test
- Avoid a risky all-at-once rewrite
