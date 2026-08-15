# SESSION START

1. Read the mode, classify the requested effect, then use the proportional read set in
   `AGENT-RULES.md`. Do not perform the older blanket read of every identity,
   compliance and task-state file for an ordinary read-only or local reversible task.
2. Read the installed version from `.ai-human/VERSION`. The deterministic local task
   command checks the writer lease itself. Inspect the lease manually only when a live
   task, manual controlled-state change or consequential path makes it relevant.
3. Only on the first calendar day at 10:00 AM, ask the approved scheduler adapter to supply
   this worker's confirmed offset-aware local time to the lifecycle tool and run the
   monthly read-only version check. Never substitute the lifecycle host's clock. At
   other times, use the last report and do not create a duplicate monthly check.
4. Report update details only when an update check actually ran or the user asked.
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
11. Classify the user's request. For read-only work, answer directly without changing
    task state. For a clear local reversible request, run the deterministic task-start
    lifecycle path; it auto-generates an ID when needed and owns the lease and exact
    state format. Use the manual lease path only for consequential or other controlled
    changes the task command does not cover.
