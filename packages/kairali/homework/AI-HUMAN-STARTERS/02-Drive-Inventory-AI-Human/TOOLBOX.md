# TOOLBOX

An available tool is not automatically an allowed tool. Add a row before relying on it.

| Tool | Purpose | Allowed actions | Approval needed | Required proof |
|---|---|---|---|---|
| Google Drive plugin | Read connector-visible metadata | Search or list metadata from the approved company Drive in batches of at most 25; cover owned/created, shared-with, shared-by and shared-drive scopes when exposed; never fetch file contents | Employee completes the provider login or account-choice screen; no password or one-time code is shared with the AI | Batch count, durable cursor, scope coverage, unique-item count and Drive-unchanged statement |
| Local project files | Preserve the index and proof | Read project instructions; create or update `DRIVE-INDEX.csv`, `DRIVE-INDEX.md`, `DRIVE-INDEX-CURSOR.md` and the five state files | No extra approval inside this folder | File readback plus checkpoint, ledger and evidence rows |
