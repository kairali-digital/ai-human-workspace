# TOOLBOX

An available tool is not automatically an allowed tool. Add a row before relying on it.

| Tool | Purpose | Allowed actions | Approval needed | Required proof |
|---|---|---|---|---|
| Gmail connector in Apps — read | Build the pilot and daily importance brief | Verify profile; search the approved company Inbox; read message text and thread context in batches no larger than 25; never open attachments | Employee completes only the provider login or account-choice screen; no password or one-time code is shared | Account label, exact period/query, batch count, coverage gaps and concise report |
| Gmail connector in Apps — reversible filing | Organize clearly low-risk mail under ruled labels | Create or apply the exact `AI Triage/Reviewed` and `AI Filed/*` labels; preserve all existing labels; remove only `INBOX` and `UNREAD` from an exact approved low-risk match; restore `INBOX` and `UNREAD` after a proven false positive | Employee explicitly chooses `BRIEF + SAFE FILING`; rule exists in `EMAIL-TRIAGE-RULES.md`; automation row is ACTIVE | Counts by label, message IDs or connector evidence, before/after and recovery readback |
| Codex automation | Run the approved daily brief at the employee's chosen time | After the manual pilot, create or update one recurring automation against this exact project using `DAILY-TRIAGE-PROMPT.md`; view the card to verify it; never duplicate it | Employee supplies local time and confirms time zone and filing mode | Automation name, card, time, time zone, project, prompt, active status and matching `AUTOMATIONS.md` row |
| Local project files | Preserve rules, report, cursor and proof | Read instructions; create or update `EMAIL-TRIAGE-REPORT.md`, `EMAIL-TRIAGE-CURSOR.md`, `EMAIL-RULE-REVIEW.md` and the state files | No extra approval inside this folder | File readback plus cursor, ledger and evidence rows |

This connector does not authorize creating, editing or deleting permanent Gmail
filters. Proposals remain in `EMAIL-RULE-REVIEW.md` for human review.
