# NATIVE UPDATE SCHEDULER

Native unattended updates are optional and off on a fresh install. Never infer a
cadence, day, time, IANA time zone, native operating-system time-zone identifier or
rollout lane. The owner must explicitly choose `WEEKLY` or `MONTHLY`, an exact local
time and day, and confirm that the host's native schedule zone represents the named
IANA zone. The owner must also choose `max_retry_attempts` from 1 through 25; this is
the maximum number of explicit retries after the first attempt, not an inferred
default.

The per-worker choice, native proof, rendered definition and pilot approval are
private state under `.ai-human/update-schedule/`; releases never replace them. macOS
renders a per-user LaunchAgent and Windows renders a per-user Task Scheduler
definition. The Windows boundary is a local wall-clock value, without a frozen UTC
offset, so the chosen clock time survives daylight-saving changes. Registration is
valid only after the adapter reads back the expected definition hash, status and
native time zone. Windows readback compares the canonical full task after
only documented non-executing registration metadata and the verified current-user SID
are normalized; extra triggers, actions, settings or attributes invalidate proof.
`update-schedule-show` labels disk evidence as stored proof, while
`update-schedule-show --verify-native` rereads the current host task and fails on drift.
The displayed next due time is computed from the internal rule after definition
readback; it is not presented as a native next-run query. Rendering on another
operating system is simulation, not proof that a task was registered. The macOS loaded
definition parser is restricted to tested macOS 27.0.1 build 26A434 because launchctl's
diagnostic format is not a stable API; other builds fail closed for activation. Exact
loaded command and calendar semantics must match even when the on-disk hash matches.
The renderer creates the private log directory before bootstrap, and pause removes
the login-time LaunchAgent copy so it remains paused after reboot; resume recreates it
from the private hash-verified definition. A Mac OS-build change or a Mac/Windows
time-zone change permits only exact-target safety cleanup, not activation. Cleanup
must prove the owned definition, native identity and absence; recovery must not
reinstall a schedule in an unconfirmed environment. Windows cleanup additionally
checks the loaded task's current-user SID. A failed readback is not proof of absence.

The chosen interpreter runs in isolated mode, ignoring inherited Python environment
and user-site paths. Configuration and resume first verify the installed runner hash,
load that actual runner and resolve the confirmed IANA zone with that interpreter.
Missing time-zone data, including a dependency visible only in user-site packages,
blocks activation instead of silently weakening isolation.

Every tick first validates the schedule identity, config hash, native proof and due
occurrence. A not-due or already-closed occurrence is quiet and performs no release
network check. A live task, writer lease or suspended system defers before checking
the network. One successful `CURRENT` or `UPDATED` report closes an occurrence;
`DEFERRED` and `FAILED` reports may be retried explicitly up to the owner's bound or
left for the next occurrence. Each native report is bound to the current schedule ID,
config hash and exact valid occurrence; malformed version-2 reports fail closed.

The existing release updater remains the only apply path: it accepts only the pinned
repository, owner-approved released manifests, exact hashes and backward-compatible
updates, then checkpoints, backs up, validates and rolls back on failure. Native
unattended discovery also requires the platform's explicit immutable-release flag;
an immutable commit alone is insufficient. Archives are fetched at the verified full
commit, not a mutable metadata download pointer. General-lane
automatic application additionally requires a verified artifact binding the exact
release to a passing Daily Email Triage fleet pilot. The pilot lane itself remains
`daily-email-triage`.

Configure, edit, pause, resume and remove are journaled. An interrupted transaction
blocks other work until schedule recovery restores and verifies the prior native and
local state. Suspend requires the native update schedule to be paused or removed;
uninstall and downgrade require verified removal so no operating-system task is
orphaned. A legacy worker with `automatic_updates: ACTIVE` but no private schedule is
never duplicated: the owner first removes the old external schedule, then records its
identifier and removal evidence with `update-schedule-legacy-disable`. That command
creates no native task and stores a self-hashed receipt bound to the current worker and
owner. A bare compatibility flag cannot bypass this migration.

Once a native schedule is configured, including PAUSED or REMOVED state, the legacy
monthly `automatic-update` and fleet entry points refuse before a release download and
never overwrite the native version-2 occurrence receipt. Owners use the native tick or
explicit bounded retry path for that worker.
