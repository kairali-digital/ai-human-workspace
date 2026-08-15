# SESSION START

1. Read `COMPANY.md`, `PARAMETERS.md`, `ROLE.md`,
   `.ai-human/control/gate-profile.json`, `GATES.md`, `COMPLIANCE-SOURCES.md`,
   `WORK-GATES.md`, `MASTER_CURSOR.md`, `OPEN_REGISTER.md` and `TODAY.md`.
2. Read the installed version from `.ai-human/VERSION` and inspect the session-lease
   status. Stop if another writer owns the lease; never take over silently.
3. On the first calendar day at 10:00 AM, ask the approved scheduler adapter to supply
   this worker's confirmed offset-aware local time to the lifecycle tool and run the
   monthly read-only version check. Never substitute the lifecycle host's clock. At
   other times, use the last report and do not create a duplicate monthly check.
4. Report the installed version, latest approved version, plain-language changes and
   whether the core, reference pack or an explicitly installed skill is affected.
5. If a live task or writer lease exists, report `DEFERRED` and wait for a safe
   checkpoint. Do not alter controlled state behind the active writer.
6. If no live task or writer exists, an automatic update may continue only when the
   worker setting is ACTIVE and the release is owner-approved, immutable,
   hash-verified and explicitly backward-compatible. Otherwise wait for the existing
   approval path; an available release is not permission by itself.
7. Back up the current managed copy, apply only manifest-listed targets and preserve
   every user-owned state and setting. Automatically restore the backup on any
   failure.
8. Preserve all local company, role, fact, decision and task-state files. A reference
   pack update never rewrites a worker already copied from a starter.
9. Validate the worker. On failure, restore the backup and report the failed check.
10. On success, report the old version, new version, receipt location, preserved-state
    result and plain-language change summary. Attach that receipt to the user's
    evidence log without rewriting unrelated state.
11. Acquire one exclusive session lease. Name the live task, next action, exit evidence
    and blocker, then commit controlled state with the lease's expected-state hash.
