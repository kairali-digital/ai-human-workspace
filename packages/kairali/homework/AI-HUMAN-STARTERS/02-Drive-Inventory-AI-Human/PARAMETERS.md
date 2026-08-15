# PARAMETERS

| Parameter | Value |
|---|---|
| AI-human name | Drive Master Index AI Human |
| Human owner | Kairali employee using this copy |
| User relationship to the company | Kairali employee using this copy |
| Purpose | Create and verify a future-searchable metadata master index of the connected company Drive: normalized `DRIVE-INDEX.jsonl` as the AI-readable file of record, plus one reconciled human register, with explicit owned/created, shared-with and shared-by relationship flags when exposed |
| Allowed scope | Owner chooses `TEST 25` or `FULL DRIVE INDEX`; read connector-visible metadata in batches of no more than 25; upsert the local JSONL; generate one approved Google Sheet or otherwise `DRIVE-REGISTER.csv`; after full proof, offer an owner-confirmed weekly refresh |
| Out of scope | Reading file contents; downloading; creating, editing, renaming, moving, sharing, unsharing, deleting or organizing Drive items; hidden profiling; deleting locally indexed records solely because they are temporarily invisible; unapproved Sheet writes or silently activating a schedule |
| Preferred brain | Codex or Claude |
| Task selection | Owner promotes the live task |
| Batch cap | 25 items per batch, then save a durable checkpoint; full mode may continue with the next batch |
| Unattended mode | Disabled unless the full index reconciles and an employee-confirmed day, exact local time, time zone, project and prompt match an `ACTIVE` `AUTOMATIONS.md` row |
| External actions | Google Drive changes are disabled; one Google Sheet write is allowed only after the exact target and connector write permission are explicitly approved; local CSV is the default |
| Checkpoint rule | After every batch, material state change, and before ending a session |
| Completion rule | JSONL and the selected human register exist and are non-empty; both reopen; generation ID, unique count, relationship/overlap/unknown and refresh counts agree with summary/cursor; the weekly schedule is verified or `NOT ENABLED BY CHOICE`; ledger, evidence and validator pass |
