# MASTER CURSOR

## LIVE TASK

**DRIVE-HW-001** - choose `TEST 25` or build a complete connector-visible Google Drive metadata index in checkpointed batches.

## NEXT ACTION

Personalize the human owner, confirm the Google Drive app is connected to the
approved company account, then ask the owner to choose `TEST 25` or `FULL DRIVE INDEX`.

## EXIT EVIDENCE

`DRIVE-INDEX.csv`, `DRIVE-INDEX.md` and `DRIVE-INDEX-CURSOR.md` exist and are read back.
Every batch is at most 25 and checkpointed; item IDs prevent duplicates; supported
owned/created, shared-with, shared-by and shared-drive scopes are recorded; unknowns and
coverage gaps are explicit; sensitive titles are flagged without opening files; and no
Drive action was taken. Full mode is complete only when every supported scope has no
next page. Test mode says the full Drive was not indexed.

## LAST CHECKPOINT

Workspace created and owner-rules preloaded. No Google Drive was accessed while building the starter.
