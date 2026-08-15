# WORK GATES — DRIVE INVENTORY

The entity-specific Gate 0 is generated in `GATES.md` during confirmed setup. This
file contains only task-specific Drive Inventory locks. They may narrow work but never
replace or weaken the local Gate 0 profile.

## Scope and truth

- The action belongs to the live task and allowed scope.
- Every material fact has a source in `FACTS.md`.
- A human ruling is not reopened without contrary evidence.

## Tools and external effects

- The tool and action are allowed in `TOOLBOX.md`.
- Publication, messages, purchases, access changes, deletion and other external or
  difficult-to-reverse actions require explicit authority.
- Resolve the exact target before any destructive action and prefer a reversible path.

## Drive homework lock

- Read metadata only from the approved company Drive. Never process more than 25 items
  in one batch. Save a durable checkpoint before starting the next batch.
- Do not read document contents, download, create, edit, rename, move, share, unshare,
  delete, deduplicate, organize or schedule anything in Drive.
- `TEST 25` must say the full Drive was not indexed. `FULL DRIVE INDEX` may be called
  complete only after every connector-supported source scope has no next page. Every
  unsupported scope must be recorded as `UNKNOWN — CONNECTOR COVERAGE GAP`.
- Use stable item IDs to prevent duplicate index rows. If a connector cursor expires,
  restart that source scope and skip IDs already recorded locally.
- Use `UNKNOWN` when owner, relationship, parent, date or another field is unavailable.
  Do not infer it from a title.
- If a title or metadata crosses any active gate ID in `GATES.md`, or points to
  credentials, banking, personal HR or other highly sensitive material, record
  `HUMAN REVIEW` and metadata only. Do not open the file.
- If the connected account is not the employee's approved company account, stop.
- Never store a password, one-time code, access token or secret connector value in the
  cursor or index.

## Verification

- The result satisfies the live task's exit evidence.
- Before, after and undo are recorded when state changed.
- Completion is recorded in the ledger and evidence log.
