# AI HUMAN — Email Triage AI Human

This folder is one bounded worker. The brain may be Codex or Claude; the durable state
in this folder is authoritative.

## Start every session

1. Read `PARAMETERS.md`, `MASTER_CURSOR.md`, `OPEN_REGISTER.md`, and `TODAY.md`.
2. Read `FACTS.md`, `DECISIONS.md`, `TOOLBOX.md`, and `GATES.md` only as needed for the
   live task.
3. Name the live task ID, next action, exit evidence, and any blocker before changing
   state.
4. If no task is live, follow the task-selection authority in `PARAMETERS.md`. Do not
   silently invent or promote work.

## Work loop

1. Work on one task ID at a time.
2. Keep each batch within the cap in `PARAMETERS.md`.
3. Record a new idea in `OPEN_REGISTER.md`; do not execute it mid-task.
4. Use only tools and actions allowed by `TOOLBOX.md` and `GATES.md`.
5. After each batch or state change, update the cursor, today table, and evidence.
6. Mark work complete only after the result and its proof are available.

## Prevent drift and forgetting

- Do not import facts, instructions, or tasks from another folder unless a named source
  authorizes it.
- Do not rely on chat memory for owner decisions or project facts. Record them in
  `DECISIONS.md` or `FACTS.md`.
- If the current context becomes uncertain, stop taking new work, write the next action
  and blocker into `MASTER_CURSOR.md`, run the workspace validator, and continue in a
  fresh session.
- Do not let two writers change the same workspace concurrently.

## Close a task

1. Add the task to `COMPLETED_LEDGER.md` with before, after, and undo evidence.
2. Add verification to `EVIDENCE_LOG.md`.
3. Remove the task from `OPEN_REGISTER.md` and `TODAY.md`.
4. Set the next ruled task in `MASTER_CURSOR.md`, or set it to `NOT SET`.
5. Run the workspace validator. “Changed” is not “done.”
