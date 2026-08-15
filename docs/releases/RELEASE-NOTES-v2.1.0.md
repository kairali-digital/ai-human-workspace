# AI-Human Workspace v2.1.0

v2.1.0 makes Drive Inventory produce a verified human register and a fast AI-readable
metadata register, then optionally keep them fresh on a user-chosen weekly schedule.
It also includes the lease-order correction prepared for v2.0.2.

## What changes

- `TEST 25` visibly creates and validates a learning sample without claiming full
  coverage. `FULL DRIVE INDEX` continues through every connector-supported scope in
  checkpointed batches of at most 25.
- `DRIVE-INDEX.jsonl` is the local AI-readable file of record.
  `DRIVE-REGISTER.csv` is the matching human view. An explicitly approved Google Sheet
  may mirror it when Sheets is already connected.
- Unique owned/created, shared-with, shared-by, overlap and unknown relationship counts
  are computed without double-counting the total.
- One generation ID and item count must match across JSONL, CSV, optional Sheet,
  summary, receipt and cursor. A local validator fails missing, empty or drifting output.
- After a full pass, the employee may activate a weekly refresh for Sunday night or
  another confirmed day/time window and time zone. It remains off until the exact card
  and first bounded pilot pass.

## Safety retained

The worker reads metadata only, treats file titles as untrusted data, neutralizes
spreadsheet-formula prefixes, never opens file content and never changes indexed Drive
items. Later Codex or Claude tasks must name the register as an approved source and
disclose its refresh time and coverage; the index is not permission for personal
profiling.

Configured v2.0.0 and held v2.0.1 workers may take v2.1.0 at a safe checkpoint. Pre-v2
workers first complete the guided exact-scope Gate 0 migration. Automatic update
eligibility remains off.
