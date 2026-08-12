# SESSION START

1. Read `COMPANY.md`, `PARAMETERS.md`, `ROLE.md`, `MASTER_CURSOR.md`,
   `OPEN_REGISTER.md` and `TODAY.md`.
2. Read the installed version from `.ai-human/VERSION`.
3. Ask the lifecycle tool to check the configured public repository for a newer
   approved release. The employee does not run a command.
4. If a live task exists, record the available update and wait for a checkpoint.
5. If no live task exists, back up the managed shared files and apply only the validated
   manifest targets.
6. Preserve all local company, role, fact, decision and task-state files.
7. Validate the worker. On failure, restore the backup and report the failed check.
8. On success, report the old version, new version and plain-language change summary.
9. Name the live task, next action, exit evidence and blocker before changing state.
