# AUTOMATIONS

No unattended job is authorized until the first `FULL DRIVE INDEX` has reconciled and
the employee confirms the day, exact local time, time zone, project and task prompt.
The job runs only while the computer is awake, ChatGPT is running, this folder remains
available and connector approvals remain valid.

| ID | Trigger | Task source | Allowed scope | Stop condition | Status | Last run UTC |
|---|---|---|---|---|---|---|
| DRIVE-WEEKLY-001 | Employee-chosen day and exact local time in confirmed time zone — NOT SET; Sunday night may be suggested but no time is assumed | `WEEKLY-DRIVE-REFRESH-PROMPT.md` | Connector-visible metadata since the last successful checkpoint; batches no larger than 25; stable-ID upsert into JSONL; regenerate or update the one approved human register | Wrong account/project; inactive or mismatched card; concurrent writer; unreconciled prior generation; connector or Sheet readback failure; Gate 0; any Drive mutation | DRAFT — offer only after full index proof | NOT RUN |

The employee may pause, edit or remove the visible automation card. Verify the card and
make this row match. A missed run is not silently marked successful; use `RUN DRIVE
REFRESH NOW` to recover from the last successful cursor.
