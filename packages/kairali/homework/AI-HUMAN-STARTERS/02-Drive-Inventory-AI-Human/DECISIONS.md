# DECISIONS

| Date UTC | Decision | Reason | Who | Supersedes |
|---|---|---|---|---|
| 2026-08-12 | `DRIVE-HW-001` is the compulsory second task for an attendee without a named homework plan | Give every otherwise-unmapped attendee a second safe, visible AI-human result | Abhilash - owner instruction | None |
| 2026-08-12 | The employee chooses `TEST 25` or `FULL DRIVE INDEX`; both remain metadata-only and process at most 25 items per checkpointed batch | Make the homework useful as a durable future-search index without an unsafe unbounded batch or any Drive mutation | Abhilash - owner instruction | The first-run 25-item-only decision |
| 2026-08-16 | Success requires a visible non-empty CSV reopened and row-count verified against summary and cursor, with explicit owned/created, shared-with and shared-by flags plus overlap/unknown totals | A witnessed run appeared to complete without leaving a usable dataset; overlapping relationship totals must not misstate unique files | Abhilash - owner instruction H-48 | File-exists-only proof |
| 2026-08-16 | `DRIVE-INDEX.jsonl` is the normalized AI-readable file of record; one approved Google Sheet or otherwise `DRIVE-REGISTER.csv` is generated from it, and all outputs share a generation ID and reconciled counts | A human register alone is not a durable machine lookup source, while dual independent registers can drift | Abhilash - owner instruction H-48 | CSV-only index design |
| 2026-08-16 | After the first reconciled full index, offer a weekly refresh with employee-confirmed day, exact local time and time zone; Sunday night is only a suggestion | A claimed schedule is not active until the employee chooses it and the visible card agrees | Abhilash - owner instruction H-48 | No refresh path |
