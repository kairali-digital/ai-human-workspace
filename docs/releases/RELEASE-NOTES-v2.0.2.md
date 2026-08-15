# AI-Human Workspace v2.0.2

v2.0.2 is the concurrency correction for the held v2.0.1 release. It keeps the
proportional achievement model while ensuring that two chats cannot silently replace
each other's task state.

## What changes

- Task start acquires the exclusive worker lease before it checks for live work,
  allocates a task ID or reads and renders controlled state.
- Task completion acquires the lease before it checks the live task, reads the open
  row, verifies local artifacts or prepares completion state.
- Both paths recheck the leased state hash immediately before one atomic commit.
- Forced two-caller regressions require exactly one winner and one clean refusal for
  both start and completion. The winner's task, receipt, ledger and evidence remain
  intact, the lease is cleared and the final validator passes.
- Requested artifact fields missing from the named source stay visibly not provided or
  use a labelled placeholder; the assistant does not infer audience, objective,
  channel, date, claim or owner facts from context.

## What remains proportionate

- Read-only questions answer directly without creating task state.
- Clear reversible local work completes through the lightweight lifecycle path.
- A mixed Gate 0 request withholds only the conflicting part and finishes the safe
  local result.
- One complete uploaded document with 150 entries remains one intact artifact. Creating
  150 separate GitHub issues remains 150 external actions, executed in checkpointed
  batches of no more than 25.
- Gate 0 remains a confirmed private profile for the exact company, legal entity,
  operating unit, jurisdictions, purpose and user relationship.

## Install or recover

- **Configured v2.0.0 worker:** run the normal read-only update check, then approve the
  v2.0.2 update at a safe checkpoint. User-owned work and state remain preserved.
- **Held v2.0.1 worker:** preserve the existing worker and files. Do not reinstall.
  Run the same read-only check and approve v2.0.2 only when no task is live.
- **Pre-v2 worker:** first complete the guided exact-scope Gate 0 setup migration.
- **New setup:** choose exactly one edition. Kairali staff use the Kairali Employee
  Edition; everyone else uses the company-neutral Reusable Edition.

Automatic update eligibility remains off. A portal label or download is not proof that
an individual worker was updated; its own version, preservation receipt and validator
result are the proof.
