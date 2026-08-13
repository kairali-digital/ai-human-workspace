# DAILY TRIAGE PROMPT

Run `EMAIL-DAILY-001` inside this Email Triage project.

1. Read `PARAMETERS.md`, `MASTER_CURSOR.md`, `AUTOMATIONS.md`,
   `EMAIL-TRIAGE-RULES.md`, `EMAIL-TRIAGE-CURSOR.md`, `TOOLBOX.md` and `GATES.md`.
   Stop without reading mail if the automation row is not `ACTIVE`, the approved
   company account cannot be verified, the project differs from the recorded project,
   or another task is changing the same state files.
2. Search the approved company Inbox after the last successful UTC cursor, excluding
   Spam and Trash. On the first daily run, start after the manual pilot checkpoint.
   Cover every connector-visible result in batches of no more than 25. After each
   batch, save the cursor, state and evidence before continuing. If the connector
   cannot expose a complete time window or next page, record the exact coverage gap;
   never claim the whole period was checked.
3. Inspect each message and read thread context when needed. Do not open attachments
   and do not rely on Gmail's Important marker alone. Compare with the previous brief
   so an unchanged item is repeated only when it remains urgent, becomes overdue or
   has new information.
4. Classify every reviewed message as `NEEDS ACTION`, `WAITING / FOLLOW UP`,
   `WORTH READING`, `LOW-RISK FILING` or `HUMAN REVIEW`. Put critical account,
   security, broken-system and direct-human messages first. Gate 0 and highly
   sensitive mail is `HUMAN REVIEW`; show sender, subject and date only and give no
   advice.
5. Replace `EMAIL-TRIAGE-REPORT.md` with a concise brief containing exactly:
   `NEEDS ACTION`, `WAITING / FOLLOW UP`, `WORTH READING`, `HUMAN REVIEW`,
   `FILTER HEALTH` and `RUN SUMMARY`. Include every important item, a direct Gmail
   link when available, why it matters, any deadline or age and one next human action.
   If nothing is actionable, say `No action required`. End with bucket counts, period
   covered, batches completed, coverage gaps, what changed since the previous brief
   and the next cursor.
6. If `PARAMETERS.md` says `BRIEF + SAFE FILING` and the matching automation row is
   `ACTIVE`, apply only the exact approved rules in `EMAIL-TRIAGE-RULES.md`. Preserve
   every existing label. For a clearly low-risk match, add `AI Triage/Reviewed` and
   the single matching `AI Filed/*` label, remove `INBOX` and remove `UNREAD`. Never
   file a starred, direct-human, ambiguous, financial, security, legal, compliance,
   medical, dosage, certification, spend, credential, banking, personal HR, receipt,
   invoice, order, travel, calendar, deadline, access-request or failed-system item.
   Keep uncertain mail in Inbox and unread. If the mode is `BRIEF ONLY`, make no Gmail
   change.
7. On the first successful daily run in a new calendar month, audit up to one batch of
   25 recent messages from each active `AI Filed/*` label. If a filed message is
   clearly important, restore `INBOX` and `UNREAD` while preserving all labels and
   report it. If uncertain, make no change and report it for human review.
8. When a recurring sender or rule appears wrong, append one evidence-backed proposal
   to `EMAIL-RULE-REVIEW.md`. Do not change a permanent Gmail filter and do not activate
   a new filing rule. A human must review and approve the exact sender or query first.
9. Never send, reply, forward, draft, delete, Trash, mark spam, unsubscribe, open an
   attachment, change a Gmail setting or create, edit or delete a permanent Gmail
   filter. Never copy a full private email into local files.
10. Update `EMAIL-TRIAGE-CURSOR.md`, the project state files and evidence only after
    the report and any authorized reversible filing actions are read back. Validate
    the workspace. A failed or partial run does not advance the last-success cursor.
