# Verification scope — v2.5.0 local candidate

Status: LOCAL_BUILD_ONLY / PENDING_FINAL_AUDITS_AND_GO.
Verdict: DO NOT SHIP.

Earlier development commit a498da0 passed216 lifecycle tests, candidate validation,
compilation and a scoped history-secret scan. This is prior-source evidence, not a
pass for the subsequently changed v2.5 bytes. Bounded synthetic Mac runner checks
proved not-due quietness, live-task deferral and repeated-deferral suppression, with
the exact temporary native task removed; that is not a full updater/platform pass.

Actual original-v2.4/v2.3 probes exposed orphaned new private state and a minimum
restore-runtime gap. The development correction has narrow regression and interrupted
transaction coverage. Complete post-edit combined tests and real old-runtime retesting
are pending. No data loss was observed in those probes; preserved bytes alone did not
provide the older runtime's missing controls.

Before publication: freeze one exact commit/tree and all assets; pass the full builder,
compatibility, security, package, beginner and real-platform journeys; verify required
independent recovery copies and offline restore/rollback; obtain independent Claude
and Monitor passes against identical bytes; then request the owner's exact-candidate
GO. Existing same-device recovery copies do not satisfy independence. Windows remains
unproven until an approved real test host is exercised.

No final CheckA, CheckB, CheckC, GO, public release or employee update is asserted here.
Any later candidate-byte change requires a fresh freeze and all applicable checks.
