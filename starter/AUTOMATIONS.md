# AUTOMATIONS

No unattended job is authorized until the owner marks a complete row `ACTIVE`.

| ID | Trigger | Task source | Allowed scope | Stop condition | Status | Last run UTC |
|---|---|---|---|---|---|---|
| SYSTEM-MONTHLY-UPDATE-001 | First calendar day at 10:00 AM in {{TIMEZONE}} | Latest approved release from the configured repository | Read-only version report; automatic managed-only update only when idle, released, hash-verified and backward-compatible | Live task; active writer; missing/mismatched worker; ineligible release; failed validator; rollback failure | {{AUTOMATIC_UPDATES}} | NOT RUN |
| USER-QUARTERLY-IMPROVEMENT-001 | User-confirmed monthly or quarterly local date and time | Only source categories and research channels approved in private improvement config | Active approved-channel research, evidence scan, derived recommendations, dated `PROPOSE` / `LATER` / `REJECT` history and owner-supplied time measurement; every external and skill effect is unavailable in v2.4 | Declined, paused, removed, missing visible Scheduled card or exact prompt hash, missing next run, unavailable host, stale schedule proof, permission denial, Gate 0, hostile source or failed validator | NOT ENABLED BY CHOICE | NOT RUN |
| USER-SILENT-AUTONOMY-001 | Future trusted effect runtime only | No external broker or trusted skill loader is shipped in v2.4 | Policy/schema preview only; no email, LinkedIn or silent skill effect can execute | Always stop with the explicit unavailable-runtime reason | UNAVAILABLE IN v2.4 | NOT RUN |
