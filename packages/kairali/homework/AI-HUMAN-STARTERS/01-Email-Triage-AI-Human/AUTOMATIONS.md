# AUTOMATIONS

No unattended job is authorized until the manual pilot passes, the employee rules the
filing mode and a complete row is marked `ACTIVE`. The automation runs only while the
computer is awake, ChatGPT is running and this exact project remains available.

| ID | Trigger | Task source | Allowed scope | Stop condition | Status | Last run UTC |
|---|---|---|---|---|---|---|
| EMAIL-DAILY-001 | Every day at employee-approved local time and time zone — NOT SET | `DAILY-TRIAGE-PROMPT.md` | Approved company Inbox; batches no larger than 25; concise report; only ruled reversible filing; first successful run of each month includes safety audit | Wrong account/project; inactive row; concurrent writer; connector coverage failure; Gate 0; any unapproved Gmail write | DRAFT — pilot and approval required | NOT RUN |
