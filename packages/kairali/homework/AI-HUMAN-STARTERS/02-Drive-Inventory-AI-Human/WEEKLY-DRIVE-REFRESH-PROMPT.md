# WEEKLY DRIVE REFRESH PROMPT

Run `DRIVE-WEEKLY-001` inside this Drive Master Index project.

1. Read `PARAMETERS.md`, `MASTER_CURSOR.md`, `AUTOMATIONS.md`,
   `DRIVE-REGISTER-SCHEMA.md`, `DRIVE-INDEX-CURSOR.json`,
   `DRIVE-INDEX-RECEIPT.json`, `TOOLBOX.md`, `GATES.md` and `WORK-GATES.md`. Stop before
   Drive access if the automation row is not `ACTIVE`, the approved company account
   or exact project cannot be verified, a writer holds the state lease, or the last
   successful full-index generation is missing or unreconciled.
2. Search connector-visible metadata added or changed since the last successful
   checkpoint. Work in batches of no more than 25. If a cursor expired or a supported
   change feed is unavailable, rescan the affected source scope in bounded batches
   and deduplicate by stable item ID.
3. Upsert stable IDs into `DRIVE-INDEX.jsonl`. Never delete a record merely because it
   is temporarily invisible; retain it as `NOT SEEN THIS RUN — VERIFY`. Use `UNKNOWN`
   for unavailable fields and `HUMAN REVIEW` for sensitive titles or metadata. Never
   open or download file content and never change Drive.
4. Start a new generation ID for the proposed refreshed dataset. Regenerate or update
   the one approved human register from the exact JSONL data. Do not switch between a
   Google Sheet and `DRIVE-REGISTER.csv` without separate employee approval.
5. Reopen and parse every non-empty JSONL line; reject malformed JSON or duplicate
   item IDs. Reopen the exact Google Sheet range or CSV and count data rows. Require
   JSONL, the selected human register, receipt, summary and cursor to agree on generation ID, unique count,
   relationship/overlap/unknown totals and added/updated/unchanged/unknown counts.
6. Advance the last-success cursor only after both register readbacks reconcile.
   Otherwise leave the prior successful cursor unchanged, record the exact failure and
   one recovery action, and keep the task open.
7. Replace `DRIVE-INDEX.md` with the new coverage, freshness, generation, counts,
   human-register locator, any connector gaps and the Drive-unchanged sentence. Update
   `DRIVE-INDEX-RECEIPT.json`, `DRIVE-INDEX-CURSOR.json`, state and evidence. Run
   `validate_drive_register.py`, then validate the workspace.

If a scheduled run was missed because the computer, ChatGPT, folder or connector was
unavailable, do not pretend it ran. The employee may say `RUN DRIVE REFRESH NOW` for a
supervised recovery run; resume from the last successful cursor and follow this same
contract. Pause, edit or remove the job only through the visible automation card, then
make `AUTOMATIONS.md` match the verified card state.
