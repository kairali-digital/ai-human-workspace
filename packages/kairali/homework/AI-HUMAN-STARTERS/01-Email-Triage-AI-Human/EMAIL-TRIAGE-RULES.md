# EMAIL TRIAGE RULES

## Approval

`NOT SET` — the manual pilot must pass and the employee must choose `BRIEF ONLY` or
`BRIEF + SAFE FILING` before the daily automation is activated.

## Keep visible and unread

- Direct human requests, replies, approvals, decisions, deadlines and access requests.
- Account, security, legal, compliance, financial or failed-system alerts.
- Receipts, invoices, orders, travel and calendar messages.
- Starred, ambiguous or potentially consequential mail.
- Medical, dosage, certification, spend, credential, banking or personal HR mail.

## Approved low-risk filing labels

These rules apply only after `BRIEF + SAFE FILING` is explicitly approved.

| Label | Exact low-risk use | Never use when |
|---|---|---|
| `AI Filed/Promotions` | Clear bulk promotions or sales offers with no direct request | A human wrote directly, an account is involved or the message is ambiguous |
| `AI Filed/Newsletters` | Recurring newsletter or content digest with no action, deadline or account warning | The information is role-critical, requested or uncertain |
| `AI Filed/Routine Reports` | Routine automated report with no exception, failure or direct ask | The report shows an anomaly, missed target, failed workflow or required action |
| `AI Filed/Notifications` | No-action automated notification or expired login code | It concerns security, access, a deadline, calendar change or failed system |

For an approved match, add `AI Triage/Reviewed` and exactly one `AI Filed/*` label,
then archive and mark read. Preserve all existing labels. Never delete the message.

## Rule changes

No new sender, search query or permanent Gmail filter becomes active automatically.
Record the evidence and proposed action in `EMAIL-RULE-REVIEW.md`; a human approves or
rejects it first.

## EA learning

- Add concise candidate learning to `MEMORY-REVIEW-QUEUE.md`; do not copy full email
  text into memory.
- Learn tone only from replies the employee confirms as sent or approved.
- Learn importance, follow-up, filing and newsletter relevance only from explicit
  employee decisions, corrected outcomes or repeated source-backed observations.
- A proposed reply is local, clearly marked `NOT SENT`, and never becomes a Gmail
  draft or sent message without a separate approved action.
- Recommend unsubscribe only after repeated evidence shows a newsletter is not useful
  to the employee, company or role. Never unsubscribe automatically.
- Confirmed learning moves to `PERSONAL-WORK-MEMORY.md` with a source and date.
  Observed-only learning must remain labelled `OBSERVED — VERIFY`.
