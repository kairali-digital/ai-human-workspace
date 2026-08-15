# PARAMETERS

| Parameter | Value |
|---|---|
| AI-human name | Daily Email Triage AI Human |
| Human owner | Kairali employee using this copy |
| User relationship to the company | Kairali employee using this copy |
| Purpose | Deliver a concise daily company-email importance brief and, only when explicitly approved, file clearly low-risk mail under reversible rules with a monthly false-positive audit |
| Approved account label | NOT SET — verify the company Gmail account before reading mail |
| Daily local time | NOT SET — ask the employee in the first run |
| Time zone | NOT SET — detect locally and confirm only if wrong |
| Filing mode | NOT SET — choose BRIEF ONLY or BRIEF + SAFE FILING after the manual pilot |
| Allowed scope | Search and read the approved company Inbox; process connector-visible results in batches of no more than 25; read thread context; create and verify local reports, rules and cursor files; create one approved daily automation; when BRIEF + SAFE FILING is approved, apply only the exact AI labels and archive/mark read clearly low-risk matches |
| Out of scope | Personal mailboxes; sending, replying, forwarding or drafting; deleting, Trash, spam or unsubscribe; opening attachments; changing Gmail settings or permanent filters; filing sensitive, direct-human, consequential or ambiguous mail |
| Preferred brain | Codex or Claude |
| Task selection | Owner promotes the live task |
| Batch cap | 25 items, then checkpoint; a complete daily period may continue through additional checkpointed batches |
| Unattended mode | Disabled until the manual pilot passes, time/time zone are recorded, filing mode is ruled and the `AUTOMATIONS.md` row is ACTIVE |
| External actions | Read-only brief is allowed after account verification; reversible label/archive/read actions require BRIEF + SAFE FILING approval; every other Gmail write is disabled |
| Checkpoint rule | After every batch, material state change and before ending a session |
| Completion rule | Pilot report, schedule, automation card, cursor and evidence are verified; the workspace validator passes |
