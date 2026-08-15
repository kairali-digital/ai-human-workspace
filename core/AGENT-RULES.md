# SHARED AGENT RULES

0. Read `.ai-human/control/mode.json` first when it exists. If its status is
   `SUSPENDED`, say that the AI-human system is off, do not load or apply the remaining
   AI-human rules or state, do not run its managed automations or updates, and defer to
   the user's current request plus any other project instructions. Only the lifecycle
   `resume`, `uninstall`, `status`, `validate` and state-verification paths remain active.
1. When mode is `ACTIVE`, read the local `COMPANY.md`, `PARAMETERS.md`, `ROLE.md`,
   `.ai-human/control/gate-profile.json`, `GATES.md`, `COMPLIANCE-SOURCES.md` and task
   state first. Read `WORK-GATES.md` for task-specific operating locks. Stop regulated or consequential work if the profile is missing,
   unconfirmed, overdue, mismatched or fails validation.
2. Work on one named task ID at a time.
3. Name the independent batch unit before applying the local batch cap. The cap applies
   to separately executed items, separately processed people/workers/artifacts and
   repeated external writes. Entries embedded in one authorized artifact or assignment
   intake are not separate batch units: preserve the complete artifact and never
   truncate or partially upload it. If entries become separate records or actions,
   each one is a batch unit. Stop each execution batch at the cap and checkpoint.
4. A change is not complete until the result is verified and recorded.
5. Capture new ideas in `OPEN_REGISTER.md`; do not interrupt the live task.
6. Never invent a number, fact, source, permission, approval or completion.
7. An available tool is not permission; check `TOOLBOX.md`, `GATES.md` and
   `WORK-GATES.md`.
8. Stop for access, publishing, sending, deletion, security changes and human gates.
   When mode is `ACTIVE` and a request crosses one of these or another declared
   boundary, push back politely and specifically: name the boundary in one short
   explanation, refuse only the conflicting part, preserve any safe part of the
   mission, and offer the nearest compliant next step or the exact approval needed.
   Do not scold, shame, lecture, argue repeatedly or use a guardrail to block unrelated
   safe work.
9. Reconcile cursor, register, today, ledger and evidence before ending a session.
10. Acquire the worker's exclusive session lease before changing cursor, register,
    today, ledger, evidence or capability state. Commit those files only with the
    lease's expected-state hash; never bypass a lease conflict.
11. Follow `SESSION-START.md` for version checks. An automatic update may run only on
    the first calendar day at 10:00 AM in the offset-aware worker-local time explicitly
    supplied by the approved scheduler adapter, with no live task or writer, and only
    for a verified released backward-compatible version. Never infer the worker's clock
    from the machine running the lifecycle command.
12. A reusable capability remains a proposal until the user chooses `PROPOSE` and
    the designated supervisor approves its proof and scope. `LATER` and `REJECT` never
    activate it.
