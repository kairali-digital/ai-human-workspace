# SESSION END

1. If the request was read-only, return the useful answer; there is no task-state close.
2. For local reversible work, read back each declared artifact and run the deterministic
   task-complete lifecycle path with the concrete outcome, verification and undo. Do not
   manually format cursor, register, today, ledger or evidence. The validator rejects
   obvious placeholders; it cannot prove a written claim is true, so use a real readback.
   Keep that proof to one concrete sentence; do not compute hashes, byte counts or
   transaction detail unless the user requested an integrity check. Describe undo for
   the requested artifact; do not say no other files changed because lifecycle state
   and internal receipts change by design.
3. The command writes an exact `PASS` result, keeps explanation in the verification
   field, removes the closed ID from open/today, clears the cursor, validates the whole
   worker and releases its temporary writer lease as one controlled operation. If any
   check fails, report the task as still open; never say done.
4. For consequential or unsupported controlled changes, use the existing explicit
   compare-and-swap lease path and full evidence/rollback controls.
5. Put the requested result first in the user-facing answer. For a normal success, stop
   after the result plus any narrow withheld-item explanation and next safe step. Do
   not narrate the task ID, lifecycle path, receipts, hashes, internal state changes,
   tool counts or routine validation housekeeping unless the requested exit proof or a
   failure makes one of them relevant. Those details stay available to Monitor and
   recovery.
