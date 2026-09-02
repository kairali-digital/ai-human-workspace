# AI-Human Workspace v2.3.0

v2.3.0 adds one focused product capability: a governed quarterly improvement loop for
each AI-human worker. It reviews only user-approved local evidence, optionally adds
dated linked research, and returns personalized recommendations for human judgment.

## What changed

- The user can enable or decline the loop and explicitly set its local time, time zone,
  approved source categories, optional research lane, fact-freshness window and private
  retention window.
- A configured loop is not described as scheduled until the approved scheduler shows
  a visible Scheduled card and a matching offset-aware next run. Unavailable, stale,
  paused and removed schedules remain visibly inactive.
- Read-only scans surface repeated completed work, blocked or deferred work, stale or
  unknown-freshness facts, conflicting facts and existing capability status through
  narrow evidence references rather than copied source content.
- Optional web research stores only concise receipts with an HTTP(S) source, access
  time, publication/update date or an explicit missing-date label, trust class and
  claim summary. It excludes raw pages, credentials and personal data and records that
  source instructions were ignored.
- Every recommendation cites approved evidence, includes every active local gate ID
  and remains `REVIEW_REQUIRED`, `NOT_ACTIVATED` and `external_effect: NONE`.
- The existing `PROPOSE / LATER / REJECT` and designated-supervisor proof gate remains
  the only route from a recommendation to a governed capability.
- The user can inspect status, correct research by superseding a receipt, forget an
  exact receipt or report, pause, resume, edit, remove and recover a missed run.
- Private `.ai-human/improvement/` state is excluded from release management and is
  preserved through update and rollback paths.

## What did not change

The v2.2 Email EA, Personal Work Memory, Drive index and optional LinkedIn learning
controls are not rebuilt. Website design, company presentation materials and specialist
Shopify, FMS and Web lanes are outside this release.

Automatic update eligibility remains off. A configured v2.0.0, held v2.0.1, v2.0.2,
v2.1.0 or v2.2.0 worker can take v2.3.0 at a safe checkpoint with user-owned state
preserved. A pre-v2 worker still needs the existing exact-scope Gate 0 setup migration.
