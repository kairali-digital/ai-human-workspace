# SESSION START

1. Read `COMPANY.md`, `PARAMETERS.md`, `ROLE.md`, `MASTER_CURSOR.md`,
   `OPEN_REGISTER.md` and `TODAY.md`.
2. Read the installed version from `.ai-human/VERSION`.
3. Ask the lifecycle tool to check the configured public repository for a newer
   approved release. This check is read-only; the employee does not run a command.
4. Report the installed version, latest approved version, plain-language changes and
   whether the core, reference pack or an explicitly installed skill is affected.
5. If a live task exists, record the available update and wait for a safe checkpoint.
6. If no live task exists, wait for the employee to approve `UPDATE NOW`. Never treat
   an available release or an empty cursor as permission to overwrite managed files.
7. After approval, back up the current managed copy, verify release and component
   hashes, and apply only the relevant manifest-listed targets.
8. Preserve all local company, role, fact, decision and task-state files. A reference
   pack update never rewrites a worker already copied from a starter.
9. Validate the worker. On failure, restore the backup and report the failed check.
10. On success, report the old version, new version, receipt location, preserved-state
    result and plain-language change summary. Attach that receipt to the employee's
    evidence log without rewriting unrelated state.
11. Name the live task, next action, exit evidence and blocker before changing state.
