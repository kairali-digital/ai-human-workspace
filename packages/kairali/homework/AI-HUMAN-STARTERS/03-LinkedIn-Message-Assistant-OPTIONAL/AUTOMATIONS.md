# AUTOMATIONS

No scheduled job is authorized until the employee chooses the time, confirms the time
zone, sees the automation card, and approves it. A scheduled run may only open this
local project and present `SATURDAY-REVIEW-PROMPT.md`. It may never access LinkedIn.

| ID | Trigger | Task source | Allowed scope | Stop condition | Status | Last successful run |
|---|---|---|---|---|---|---|
| SATURDAY-LINKEDIN-REVIEW | Employee-chosen Saturday local time; time zone not set | `SATURDAY-REVIEW-PROMPT.md` | Open this local project; show one manual action at a time; process pasted text only | No pasted batch, more than 25 items, uncertainty, Gate 0, or employee unavailable | READY FOR SETUP | Never |
