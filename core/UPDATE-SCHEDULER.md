# NATIVE UPDATE SCHEDULER

Native unattended updates are optional and off on a fresh install. Never infer a
cadence, day, time, IANA time zone, native operating-system time-zone identifier or
rollout lane. The owner must explicitly choose `WEEKLY` or `MONTHLY`, an exact local
time and day, and confirm that the host's native schedule zone represents the named
IANA zone.

The per-worker choice, native proof, rendered definition and pilot approval are
private state under `.ai-human/update-schedule/`; releases never replace them. macOS
uses a per-user LaunchAgent and Windows uses a per-user Task Scheduler definition.
Registration is valid only after the adapter reads back the expected definition hash,
status and native time zone. Rendering on another operating system is simulation, not
proof that a task was registered.

Every tick first validates the schedule identity, config hash, native proof and due
occurrence. A not-due or already-closed occurrence is quiet and performs no release
network check. A live task, writer lease or suspended system defers before checking
the network. One successful `CURRENT` or `UPDATED` report closes an occurrence;
`DEFERRED` and `FAILED` reports may be retried explicitly or at the next occurrence.

The existing release updater remains the only apply path: it accepts only the pinned
repository, owner-approved released manifests, exact hashes and backward-compatible
updates, then checkpoints, backs up, validates and rolls back on failure. General-lane
automatic application additionally requires a verified artifact binding the exact
release to a passing Daily Email Triage fleet pilot. The pilot lane itself remains
`daily-email-triage`.

Configure, edit, pause, resume and remove are journaled. An interrupted transaction
blocks other work until schedule recovery restores and verifies the prior native and
local state. Suspend requires the native update schedule to be paused or removed;
uninstall and downgrade require verified removal so no operating-system task is
orphaned. A legacy worker with `automatic_updates: ACTIVE` but no private schedule is
never duplicated: the owner must first verify removal of the old external schedule.
