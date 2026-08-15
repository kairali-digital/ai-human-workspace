# AUTOMATIONS

No unattended job is authorized until the manual pilot passes, the employee rules the
filing mode and a complete row is marked `ACTIVE`. The automation runs only while the
computer is awake, ChatGPT is running and this exact project remains available.

| ID | Trigger | Task source | Allowed scope | Stop condition | Status | Last run UTC |
|---|---|---|---|---|---|---|
| EMAIL-DAILY-001 | Every day at employee-approved fixed local time and time zone — NOT SET | `DAILY-TRIAGE-PROMPT.md` | Approved company Inbox; batches no larger than 25; neat EA notification; local proposed replies marked NOT SENT; sourced memory candidates; only ruled reversible filing; first successful run of each month includes safety audit | Wrong account/project; inactive row; concurrent writer; connector coverage failure; Gate 0; sensitive memory; any unapproved Gmail write | DRAFT — pilot, memory baseline and approval required | NOT RUN |
| SYSTEM-MONTHLY-UPDATE-001 | First calendar day at 10:00 AM in the employee-confirmed time zone — NOT SET | Latest approved `kairali-digital/ai-human-workspace` release | Read-only version report; automatic managed-only update only when idle, released, hash-verified and backward-compatible | Live email or other task; active writer; wrong worker ID/time zone; invalid release; failed validator; rollback failure | DRAFT — v2.0 rollout is not active | NOT RUN |
