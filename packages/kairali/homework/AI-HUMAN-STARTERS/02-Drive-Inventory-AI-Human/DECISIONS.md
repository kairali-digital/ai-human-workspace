# DECISIONS

| Date UTC | Decision | Reason | Who | Supersedes |
|---|---|---|---|---|
| 2026-08-12 | `DRIVE-HW-001` is the compulsory second task for an attendee without a named homework plan | Give every otherwise-unmapped attendee a second safe, visible AI-human result | Abhilash - owner instruction | None |
| 2026-08-12 | The employee chooses `TEST 25` or `FULL DRIVE INDEX`; both remain metadata-only and process at most 25 items per checkpointed batch | Make the homework useful as a durable future-search index without an unsafe unbounded batch or any Drive mutation | Abhilash - owner instruction | The first-run 25-item-only decision |
| 2026-08-16 | Maintain one AI-readable JSONL file of record and one matching human register; use an approved Google Sheet mirror when connected, otherwise CSV; offer a user-confirmed weekly incremental refresh after the first verified full index | Make the register reliable for humans and fast for Codex or Claude while preventing duplicate truth, silent scheduling, stale counts and personal profiling | Abhilash - owner instruction H-48 | CSV-only index output and no refresh offer |
