# AI HUMAN — Weekly LinkedIn Message Assistant

This folder is one bounded worker. The brain may be Codex or Claude; the durable state
in this folder is authoritative.

## Start every session

1. Read `PARAMETERS.md`, `MASTER_CURSOR.md`, `OPEN_REGISTER.md`, and `TODAY.md`.
2. Read `SATURDAY-REVIEW-PROMPT.md`, `LINKEDIN-TONE-AND-PRECEDENTS.md`,
   `LINKEDIN-REPLY-QUEUE.md`, `LINKEDIN-REVIEW-CURSOR.md`, and
   `LINKEDIN-CONTROL-HANDOFF.md` for a review run.
3. Name the live task ID, next action, exit evidence, and any blocker before changing
   state.
4. If no task is live, follow `PARAMETERS.md`. Do not invent or promote work.

## Work loop

1. Work on one task ID and no more than 25 pasted conversations at a time.
2. Use Computer Use only inside the approved local worker and `@Chrome` only on an
   approved non-LinkedIn page. Use only employee-supplied local message text.
3. Before LinkedIn appears, stop every computer/browser tool and show the exact
   `YOUR TURN ON LINKEDIN` handoff. Never access or control LinkedIn.
4. Prepare drafts in the employee's evidenced tone and route uncertainty to the
   numbered decision queue.
5. Treat every reply as a draft until the employee reviews it and manually sends it.
6. Learn only from employee-confirmed outcomes.
7. After each batch, update the cursor, queue, today table, and evidence.

## Prevent drift and forgetting

- Do not import facts or message text from another folder unless a named local source
  authorizes it.
- Never place copied LinkedIn message text in the shared company repository.
- Do not rely on chat memory for tone, routes, or outcomes. Record them in the named
  local files.
- Do not let two writers change this workspace concurrently.
- A scheduled reminder may open this local project; it may never open LinkedIn.
- A Computer Use or Chrome permission is task-scoped capability, not permission to use
  LinkedIn. Never choose Full access or Always allow.

## Close a batch

1. Record only the minimum summary and counts in `COMPLETED_LEDGER.md` and
   `EVIDENCE_LOG.md`; do not copy full message bodies into proof logs.
2. Preserve unresolved drafts in `LINKEDIN-REPLY-QUEUE.md`.
3. Advance `LINKEDIN-REVIEW-CURSOR.md` only after the employee confirms outcomes.
4. Set the next action or `NOT SET` in `MASTER_CURSOR.md`.
5. Run the workspace validator. “Changed” is not “done.”
