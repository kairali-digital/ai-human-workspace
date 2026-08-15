# AUTOMATIONS

No unattended job is authorized until the owner marks a complete row `ACTIVE`.

| ID | Trigger | Task source | Allowed scope | Stop condition | Status | Last run UTC |
|---|---|---|---|---|---|---|
| SYSTEM-MONTHLY-UPDATE-001 | First calendar day at 10:00 AM in {{TIMEZONE}} | Latest approved release from the configured repository | Read-only version report; automatic managed-only update only when idle, released, hash-verified and backward-compatible | Live task; active writer; missing/mismatched worker; ineligible release; failed validator; rollback failure | {{AUTOMATIC_UPDATES}} | NOT RUN |
