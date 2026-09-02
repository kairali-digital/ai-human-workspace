# Verification evidence and trust record: v2.3.0

## Release identity

- Version: `2.3.0`
- Lane: `APPROVED_BY_OWNER` / `RELEASED`
- Compatibility: backward-compatible from configured v2.0.0, held v2.0.1, v2.0.2,
  v2.1.0 and v2.2.0 workers
- Automatic update eligible: no
- Publication authority: explicit owner instruction on 2 September 2026

## Behavioral proof

- Quarterly configuration refuses a write without the exclusive lease and expected
  state hash; `DECLINE` remains a complete valid result.
- Scheduler activation requires a visible Scheduled card, exact configured local time,
  offset-aware future next run and recorded adapter identity. Unavailable scheduling is
  reported as not active. Pause, edit, resume and removal reject stale external state.
- Approved-source scans detect repetition, stale facts and conflicting active facts.
  An unapproved evidence reference or a recommendation missing a local Gate 0 ID fails
  before a report is committed.
- Hostile research receipts fail unless source instructions were ignored. Raw web pages,
  credentials and personal data are excluded; correction-by-supersession and exact-ID
  forget are verified.
- Reports remain read-only and do not create or activate capability records. Managed
  updates preserve the private improvement configuration byte-for-byte.

## Verification evidence

- Focused quarterly-improvement adversarial suite: PASS.
- Complete lifecycle suite: PASS, 69 tests.
- Public release validator and exact payload proof: PASS.
- Reusable and Kairali edition archive install/readback: PASS.
- Secret and personal absolute-path scan: PASS.
- Cross-platform hosted validation remains a required protected check before the tag.

## Code-vetting report

GATE 0 compliance    PASS — recommendations preserve every confirmed local gate and no regulated ruling was changed
GATE 1 structure     PASS — company-neutral managed core, isolated private state and batch cap preserved
GATE 2 facts         PASS — derived counts cite source rows; missing freshness stays explicit
GATE 3 redirects     PASS — no redirect, route or locale behavior changed
GATE 4 works         PASS — enable/decline, scheduling truth, scan, correction, forget and update-preservation paths verified
GATE 5 proof         PASS — before, after, failure, recovery and update-preservation evidence covered

VERDICT: SHIP
REASON: v2.3.0 adds a private evidence-bound quarterly improvement loop without automatic activation, permission expansion or loss of user state.
