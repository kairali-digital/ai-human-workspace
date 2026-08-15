# SESSION END

1. Confirm this session owns the active writer lease and its expected-state hash still
   matches. A mismatch stops the close-out; do not overwrite the other state.
2. Prepare one compare-and-swap state commit containing the cursor, register, today,
   ledger and evidence changes required by this task.
3. Record detailed before state, after state, verification, result, artifact/readback
   and undo in `EVIDENCE_LOG.md`. If no state changed, say so explicitly. The automated
   check rejects obvious placeholders and weak phrases; it cannot prove a written claim
   is true. Read back the real artifact and leave proof a supervisor or Monitor can
   independently verify.
4. Add the completion-index row to `COMPLETED_LEDGER.md` only when it cites those
   passing evidence rows. Remove the closed task from `OPEN_REGISTER.md` and `TODAY.md`,
   then clear or advance `MASTER_CURSOR.md` in the same commit.
5. Run the installed worker validator. `Changed`, a saved file or a ledger row without
   evidence is not completion.
6. Release the writer lease only after the coherent commit and validator pass. Leave any
   deferred shared-system update open for the next fresh idle session.
