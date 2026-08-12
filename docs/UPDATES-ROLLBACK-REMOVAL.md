# Updates, rollback and removal

## Approved update flow

`RELEASE → CHECK → NO LIVE TASK OR CHECKPOINT → BACKUP → APPLY MANIFEST → VALIDATE → RECEIPT`

The lifecycle tool downloads only the configured repository's latest GitHub release,
verifies semantic version and every managed-file hash, and applies only manifest-listed
targets under `.ai-human/`.

Company, owner, role, purpose, facts, decisions, tools, gates, cursor, register, today,
ledger, evidence, automation records, credentials, browser sessions and personal files
are never managed by a release.

## Live-task protection

When a live task exists, an update is recorded in `OPEN_REGISTER.md` and deferred. The
owner reaches a checkpoint, clears or checkpoints the task, and then allows the update.

## Rollback

Before an update, the current managed files are copied to a unique
`.ai-human/backups/<old>-before-<new>-<UTC timestamp>/` folder. A failed local validation restores that backup
automatically. A deliberate rollback restores the named old version and verifies that
employee-state hashes did not change.

## Removal

Uninstall does not delete the worker. It moves the complete installed `.ai-human`
system to `.ai-human-removed-<UTC timestamp>` and writes a short notice. Company and
employee files remain where they were. Reinstall can restore the managed system later.

Deleting an entire worker folder is a separate destructive owner action and is not part
of the lifecycle tool.
