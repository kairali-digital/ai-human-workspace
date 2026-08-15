# TOOLBOX

An available tool is not automatically an allowed tool. Add a row before relying on it.

| Tool | Purpose | Allowed actions | Approval needed | Required proof |
|---|---|---|---|---|
| Google Drive connector in Apps | Read connector-visible metadata | Search or list metadata from the approved company Drive in batches of at most 25; cover owned/created, shared-with, shared-by and shared-drive scopes when exposed; never fetch file contents | Employee completes the provider login or account-choice screen; no password or one-time code is shared with the AI | Batch count, durable cursor, scope coverage, unique-item and relationship counts, and Drive-unchanged statement |
| Local project files | Preserve the register and proof | Read project instructions; create or update `DRIVE-INDEX.jsonl`, `DRIVE-REGISTER.csv`, `DRIVE-INDEX.md`, `DRIVE-INDEX-RECEIPT.json`, `DRIVE-INDEX-CURSOR.json` and the five state files; run `validate_drive_register.py` | No extra approval inside this folder | All outputs reopen; generation ID and counts reconcile; validator, checkpoint, ledger and evidence rows pass |
| Google Sheets connector in Apps | Optional human-facing mirror | Only after the employee confirms it is connected and explicitly approves the resolved Sheet; write raw formula-safe rows from the verified CSV, then read back URL, generation ID and data-row count | Separate explicit approval; never require connection and never create a replacement silently | Sheet URL, generation ID, row count and readback time in the receipt |
| ChatGPT desktop Scheduled | Optional weekly incremental refresh | After FULL DRIVE INDEX passes, create or edit one project-scoped weekly task from `WEEKLY-DRIVE-REFRESH.md`; offer Sunday night or a user-chosen cadence | Confirm day/time window, time zone, exact project/account card and `ACTIVATE WEEKLY REFRESH` | Visible task card, next run, bounded pilot PASS and matching ACTIVE automation row |
