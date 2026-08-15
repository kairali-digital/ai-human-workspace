# WEEKLY DRIVE REFRESH

Offer this only after `FULL DRIVE INDEX` and `validate_drive_register.py` pass. Do not
activate it silently.

Ask one question at a time:

1. “Would you like a weekly Drive refresh?” Wait for Yes or No.
2. If Yes: “Which day and local-time window should it run? Sunday night is suggested,
   or choose another convenient time.” Wait.
3. “Which time zone should I use?” Read the answer back and wait for confirmation.
4. Show the complete scheduled-task card: approved account label, project folder,
   cadence, time/time window, time zone, metadata-only scope and notification choice.
   Wait for `ACTIVATE WEEKLY REFRESH`.

Create the task in ChatGPT desktop Scheduled, attached to this exact local project.
The computer must be on, ChatGPT desktop must be running and this project folder must
remain available. Connector approval or a workspace restriction may pause a run. Never
claim the automation is active until the card and next-run time are visible and one
bounded pilot refresh passes.

## Scheduled run prompt

```text
This is the approved weekly refresh for DRIVE-HW-001.

Read AGENTS.md, AI-HUMAN.md, PARAMETERS.md, TOOLBOX.md, GATES.md, WORK-GATES.md,
DRIVE-REGISTER-SCHEMA.md, DRIVE-INDEX-CURSOR.json and DRIVE-INDEX-RECEIPT.json.
Verify this exact project, the approved Drive account label, the confirmed schedule and
time zone, and an ACTIVE matching row in AUTOMATIONS.md. If any check fails, change no
register and report the exact blocker.

Read connector-visible Drive metadata only. Never open or download file contents and
never change Drive. Check for items added or metadata changed since the last successful
checkpoint. Process at most 25 items, save and validate a checkpoint, then continue in
another batch only inside this approved run.

Upsert by stable item_id into DRIVE-INDEX.jsonl. Never delete or mark an item deleted
merely because it is temporarily invisible. If a saved cursor or change feed is
unavailable, record that gap and rescan the affected connector-visible scope in batches
of at most 25, skipping stable IDs already indexed.

Generate a new generation_id. Rebuild DRIVE-REGISTER.csv from the complete JSONL. If
the approved human-register mode is GOOGLE_SHEET, update the existing approved Sheet
with raw, formula-safe values and read back its generation ID and row count. Never
create a replacement Sheet silently. Update DRIVE-INDEX.md,
DRIVE-INDEX-RECEIPT.json and DRIVE-INDEX-CURSOR.json.

Report unique added, updated, unchanged and unknown counts. Run
validate_drive_register.py. Advance last_successful_refresh_utc only after the JSONL,
CSV, optional Sheet, receipt, summary and cursor reopen with the same generation ID and
counts. Otherwise keep the prior successful cursor and report FAILED — REGISTER NOT
ADVANCED.
```

The employee can open Scheduled to pause, edit or delete the task. Deleting the task
does not delete either local register or the approved Google Sheet. A missed run uses
the same incremental check from the last successful checkpoint; it is never guessed to
have run.
