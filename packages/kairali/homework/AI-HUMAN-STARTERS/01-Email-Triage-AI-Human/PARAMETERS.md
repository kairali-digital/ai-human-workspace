# PARAMETERS

| Parameter | Value |
|---|---|
| AI-human name | Email Triage AI Human |
| Human owner | Kairali employee using this copy |
| Purpose | Read a bounded batch of company email and create a review-only triage report without changing the mailbox |
| Allowed scope | Search and read no more than 25 messages from the connected company inbox; create and verify local Markdown reports in this folder |
| Out of scope | Sending, replying, drafting in Gmail, archiving, labelling, deleting, changing read state, opening attachments, scheduling, or using another mailbox |
| Preferred brain | Codex or Claude |
| Task selection | Owner promotes the live task |
| Batch cap | 25 items, then checkpoint |
| Unattended mode | Disabled unless an approved `AUTOMATIONS.md` row is ACTIVE |
| External actions | Mailbox changes are disabled for this homework even if a connector offers them |
| Checkpoint rule | After every batch, material state change, and before ending a session |
| Completion rule | Result verified and recorded in both ledger and evidence log |
