# AUTOMATIONS

No unattended job is authorized until the owner marks a complete row `ACTIVE`.

| ID | Trigger | Task source | Allowed scope | Stop condition | Status | Last run UTC |
|---|---|---|---|---|---|---|
| SYSTEM-MONTHLY-UPDATE-001 | First calendar day at 10:00 AM in {{TIMEZONE}} | Latest approved release from the configured repository | Read-only version report; automatic managed-only update only when idle, released, hash-verified and backward-compatible | Live task; active writer; missing/mismatched worker; ineligible release; failed validator; rollback failure | {{AUTOMATIC_UPDATES}} | NOT RUN |
| USER-QUARTERLY-IMPROVEMENT-001 | User-confirmed quarterly local date and time | Only source categories approved in private improvement config | Read-only evidence scan and recommendations awaiting `PROPOSE` / `LATER` / `REJECT`; no automatic skill activation or external effect | Declined, paused, removed, missing visible Scheduled card, missing next run, unavailable host, stale schedule proof, permission denial, Gate 0, hostile source or failed validator | NOT ENABLED BY CHOICE | NOT RUN |
