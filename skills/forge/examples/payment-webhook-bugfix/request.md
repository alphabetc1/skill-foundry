# Request

Investigate why some payment webhooks mark the same order as paid twice.

Requirements:

- Find the most likely cause
- Fix the duplicate-processing path
- Preserve existing successful webhook handling
- Add tests so the bug does not return
