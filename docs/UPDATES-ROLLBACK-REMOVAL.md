# Updates, rollback and removal

## Approved update flow

`RELEASE → ANNOUNCE → READ-ONLY CHECK → EMPLOYEE APPROVAL → NO LIVE TASK OR CHECKPOINT → BACKUP → APPLY MANIFEST → VALIDATE → RECEIPT → MONITOR PROOF`

The lifecycle tool downloads only the configured repository's latest GitHub release,
verifies semantic version and every managed-file hash, and applies only manifest-listed
targets under `.ai-human/`.

Company, owner, role, purpose, facts, decisions, tools, gates, cursor, register, today,
ledger, evidence, automation records, credentials, browser sessions and personal files
are never managed by a release.

Checking may happen automatically at session start when the public release is
reachable. For Kairali, the employee may start it with the exact `CHECK FOR KAIRALI
UPDATE` prompt. Applying never happens silently. The lifecycle waits for the employee to
approve `UPDATE NOW` at a safe checkpoint. Company components are checked and applied
separately, so an optional role skill is never installed or upgraded merely because a
core release exists.

## GitHub Desktop is not the installer

`Fetch origin` checks the selected repository for commits. `Pull origin` copies those
commits into that repository checkout. These buttons are the beginner-safe sync path
for an assigned shared Kairali repository, but they do not update `.ai-human` inside a
separate employee worker, a separately installed company reference kit, or an opt-in
skill. The Setup Helper performs those lifecycle actions from the tagged release.

Technical employees may keep a public source checkout current with Git or GitHub
Desktop, but installed workers still change only through the manifest lifecycle.

## Live-task protection

When a live task exists, an update is recorded in `OPEN_REGISTER.md` and deferred. The
owner reaches a checkpoint, clears or checkpoints the task, and then allows the update.

## Rollout proof

The release owner publishes one semantic-version release and the stable portal must
show the same version. The company announcement names the version, change summary,
affected managed layers, stable portal and exact check prompt. Each updated worker
provides `.ai-human/VERSION`, validation `PASS`, an update/component receipt and an
evidence-log reference. A Monitor reads those proofs for the announced employee batch
and reports any missing, deferred or mismatched worker; it never rewrites worker state.

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

## Optional components

Company role packs, homework reference kits and governed skills are listed in
`component-manifest.json`. They are never silently installed with a core update.

- fresh component install verifies the complete source tree;
- component upgrade requires a declared checkpoint and preserves the previous copy;
- component removal requires a checkpoint and moves the full copy to
  `.ai-human-component-archive`;
- employee workers created from a homework template are outside component management.
