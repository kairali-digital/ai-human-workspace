# DAILY TRIAGE PROMPT

Run `EMAIL-DAILY-001` inside this Email Triage project.

1. Read `PARAMETERS.md`, `MASTER_CURSOR.md`, `AUTOMATIONS.md`,
   `EMAIL-TRIAGE-RULES.md`, `EMAIL-TRIAGE-CURSOR.md`, `PERSONAL-WORK-MEMORY.md`,
   `MEMORY-REVIEW-QUEUE.md`, `MEMORY-SOURCES.md`, `TOOLBOX.md`, `GATES.md` and `WORK-GATES.md`.
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
4. Classify every reviewed message as `NEEDS ACTION`, `PROPOSED REPLY`,
   `WAITING / FOLLOW UP`, `WORTH READING`, `LOW-RISK FILING`, `NEWSLETTER REVIEW`,
   `MEMORY CANDIDATE` or `HUMAN REVIEW`. Put critical account,
   security, broken-system and direct-human messages first. Gate 0 and highly
   sensitive mail is `HUMAN REVIEW`; show sender, subject and date only and give no
   advice.
5. Replace `EMAIL-TRIAGE-REPORT.md` with a clean notification brief containing exactly:
   `TODAY AT A GLANCE`, `NEEDS ACTION`, `PROPOSED REPLIES`,
   `WAITING / FOLLOW UP`, `WORTH READING`, `HUMAN REVIEW`,
   `NEWSLETTERS TO REVIEW`, `MEMORY LEARNED OR NEEDS CONFIRMATION`, `FILTER HEALTH`
   and `RUN SUMMARY`. Include every important item, a direct Gmail
   link when available, why it matters, any deadline or age and one next human action.
   For a non-sensitive message that merits a reply, include concise local wording based
   only on confirmed facts and evidenced tone, visibly labelled `NOT SENT`. Never draft
   wording for Gate 0 or highly sensitive mail.
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
8. Add concise source-backed learning candidates to `MEMORY-REVIEW-QUEUE.md`. Promote
   an item to `PERSONAL-WORK-MEMORY.md` only after an explicit employee ruling, except
   that repeated evidence may remain `OBSERVED — VERIFY`. Record source, date,
   freshness and review point. Never store full message text, sensitive content,
   inferred traits, private relationships, authority or intent. Apply correction,
   exclusion and forget requests before using that memory again.
9. When a recurring sender or rule appears wrong, append one evidence-backed proposal
   to `EMAIL-RULE-REVIEW.md`, including exact sender/query, proposed action, examples
   and undo. For a consistently irrelevant newsletter, add an unsubscribe proposal
   with relevance evidence. Do not unsubscribe or create/change a permanent Gmail
   filter during the daily run. The employee must separately approve the exact action.
10. Never send, reply, forward, create a Gmail draft, delete, Trash, mark spam,
   unsubscribe, open an attachment, change a Gmail setting or create, edit or delete a
   permanent Gmail filter during an unattended run. Local proposed-reply text is
   allowed and is never represented as sent or saved in Gmail. Never copy a full
   private email into local files.
11. Update `EMAIL-TRIAGE-CURSOR.md`, the project state files and evidence only after
    the report and any authorized reversible filing actions are read back. Validate
    the workspace. A failed or partial run does not advance the last-success cursor.
