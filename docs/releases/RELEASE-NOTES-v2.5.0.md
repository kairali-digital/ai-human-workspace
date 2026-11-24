> PRIVATE WINDOWS 2.5 QA CANDIDATE — DO NOT INSTALL OR DISTRIBUTE.
> This is not a Windows release approval. Installation is blocked by LOCAL_BUILD_ONLY.
> Stable Windows remains v2.4.0. The Mac release instructions below are retained for comparison, not Windows authorization.

# AI-Human Workspace v2.5.0 for Mac

Mac users can use this version after the owner issues the matching release notice. Windows users should select v2.4.0. Existing workers need an idle checkpoint, a verified backup and the user's approval. Automatic updates are disabled for this release.

On the download page, select your edition and the version labeled for your computer. Open the existing worker and ask its Setup Helper to compare the signed v2.5.0 source commit and release checksums with the notice. Ask Setup Helper to match the employee or reusable edition ZIP to your installed worker, check the ZIP against the approved hash, and use the updater inside that ZIP’s workspace folder. Ask the helper to show the installed version, a passing validation result and the recovery location after the update.

Setup Helper reads the edition ZIP and manifest checksums from the approved signed commit, verifies the ZIP before running it, and supplies the approved manifest checksum to the updater. The Mac edition requires macOS.

## Included optional capabilities

- Adaptive work planning keeps the hard ceiling at 25 actions and lowers it for risk,
  evidence capacity, context or resource pressure. Missing signals remain unknown.
- Durable context checkpoints and identity-bound handoffs preserve the active task,
  gates and copied-file evidence. Read-first resource plans do not quit applications
  or close browser tabs.
- Addressed Worker Exchange messages require recipient acceptance and remain queued;
  messages do not replace the recipient's live task or grant authority.
- A consented private work map produces evidence-bound proposals, not activation.
- Off-by-default local memory and a separate read-only Chief of Staff provide sourced
  records, correction, expiry, conflict, forgetting and bounded changed-item pages.
  Fleet storage capacity is separate from the maximum action batch.
- Optional owner-chosen native update schedules verify owned task identity, exact
  definitions, interpreter and time-zone bindings, idle checkpoints and safe cleanup.
  Native Mac scheduling is restricted to the supported macOS build. On macOS 27.0.1
  (26A434), the job must be able to open its worker and logs. If macOS denies access,
  setup reports the failure and rolls back the attempted registration.
- Canonical receipt tree proofs check archived and restored bytes without rewriting
  historical receipts. The helper checks whether private state must be exported before an older runtime can open the worker.

## Boundaries and compatibility

All new optional capabilities start off. Automatic release eligibility is false. The
authority registry remains empty; external email/LinkedIn effects and managed skill
activation remain unavailable. A local record, attachment or model recommendation is
never permission for an external effect or a Gate 0 exception.

Configured Mac workers on stable v2.0.0, v2.0.2, v2.1.0, v2.2.0, v2.3.0 and v2.4.0 use the managed update path. The held v2.0.1 release is excluded. Pre-v2 workers need guided migration. New private-state
rollback now requires an export when crossing its first-supported-runtime boundary;
restoration requires an installed runtime that supports every archived root. Compatible
state stays in place, and genuine legacy archive bytes retain their original format.
Manual rollback refuses an active writer and requires explicit safe-checkpoint approval
when a task remains live, preserving that task. Private-state export still requires an
idle worker and reconciled governor, context, handoff, schedule and route state.

If a previous installation has automatic updates enabled, the helper checks the actual scheduler and records either the removed job or verified absence before suspension. Keep the update receipt. If a rollback is needed, give the helper the saved backup location and ask it to verify the previous version, the validator result and the worker's preserved files.
