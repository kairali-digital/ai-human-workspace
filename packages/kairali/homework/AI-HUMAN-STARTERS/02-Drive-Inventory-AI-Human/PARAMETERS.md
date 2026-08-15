# PARAMETERS

| Parameter | Value |
|---|---|
| AI-human name | Drive Inventory AI Human |
| Human owner | Kairali employee using this copy |
| User relationship to the company | Kairali employee using this copy |
| Purpose | Create a future-searchable metadata index of the connected company Drive without opening file contents or changing Drive |
| Allowed scope | Owner chooses `TEST 25` or `FULL DRIVE INDEX`; read connector-visible metadata in batches of no more than 25 and create or verify local CSV and Markdown index files in this folder |
| Out of scope | Reading file contents, downloading, creating, editing, renaming, moving, sharing, unsharing, deleting, deduplicating, or scheduling Drive work |
| Preferred brain | Codex or Claude |
| Task selection | Owner promotes the live task |
| Batch cap | 25 items per batch, then save a durable checkpoint; full mode may continue with the next batch |
| Unattended mode | Disabled unless an approved `AUTOMATIONS.md` row is ACTIVE |
| External actions | Google Drive changes are disabled for this homework even if a connector offers them |
| Checkpoint rule | After every batch, material state change, and before ending a session |
| Completion rule | Result verified and recorded in both ledger and evidence log |
