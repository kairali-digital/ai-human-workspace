# AUTOMATIONS

No unattended job is authorized until a complete row is marked `ACTIVE` by the owner.

| ID | Trigger | Task source | Allowed scope | Stop condition | Status | Last run UTC |
|---|---|---|---|---|---|---|
| DRIVE-WEEKLY-REFRESH | Employee-confirmed weekly local day/time window/time zone; Sunday night is suggested, never assumed | `WEEKLY-DRIVE-REFRESH.md` plus last successful `DRIVE-INDEX-CURSOR.json` | Connector-visible metadata additions and changes only; batches at most 25; update JSONL file of record, human CSV and the already approved Sheet mirror if selected | Account/project/schedule mismatch; approval needed; register generation/count mismatch; expired cursor without bounded rescan; validation failure | NOT ACTIVE — offer only after FULL DRIVE INDEX passes | NEVER |
