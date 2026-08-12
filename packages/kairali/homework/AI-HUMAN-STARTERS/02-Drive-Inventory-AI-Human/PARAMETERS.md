# PARAMETERS

| Parameter | Value |
|---|---|
| AI-human name | Drive Inventory AI Human |
| Human owner | Kairali employee using this copy |
| Purpose | Read a bounded batch of Google Drive metadata and create a review-only inventory without changing Drive |
| Allowed scope | Read metadata for no more than 25 items from the connected company Google Drive; create and verify local Markdown reports in this folder |
| Out of scope | Reading file contents, downloading, creating, editing, renaming, moving, sharing, unsharing, deleting, deduplicating, or scheduling Drive work |
| Preferred brain | Codex or Claude |
| Task selection | Owner promotes the live task |
| Batch cap | 25 items, then checkpoint |
| Unattended mode | Disabled unless an approved `AUTOMATIONS.md` row is ACTIVE |
| External actions | Google Drive changes are disabled for this homework even if a connector offers them |
| Checkpoint rule | After every batch, material state change, and before ending a session |
| Completion rule | Result verified and recorded in both ledger and evidence log |
