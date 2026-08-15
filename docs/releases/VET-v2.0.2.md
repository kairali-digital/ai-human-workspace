# Verification evidence and trust record: v2.0.2

## Candidate identity

- Version: `2.0.2`
- Lane: `LOCAL_BUILD_ONLY` / `LOCAL_BUILD_ONLY`
- Compatibility: backward-compatible from configured v2.0.0 and held v2.0.1 workers
- Automatic update eligible: no
- Publication condition: all deterministic, behavioral, package, security, protected
  GitHub, production and independent Monitor gates must pass

## Why v2.0.1 was held

After v2.0.1 publication, the independent Monitor forced two lifecycle calls to prepare
from the same pre-lease state. Both task starts could report success, the second could
replace the first live task, and the validator could still pass. The same stale-state
pattern existed in completion. The finding failed the code-vetting ship gate.

Containment was immediate: the stable portal was rolled back to v2.0.0, the v2.0.1
GitHub release was marked prerelease and renamed with a do-not-install warning, and
both recipient groups received a correction notice. v2.0.1 remains in history for
auditability and is not the stable install path.

## Correction implemented

- The deterministic task lifecycle acquires its exclusive lease before any state read,
  live-task decision, ID allocation, artifact validation or render.
- The transition callback executes while that lease is held.
- The expected controlled-state hash is rechecked immediately before the atomic commit.
- Any preparation, commit or validation failure releases only the caller's own lease
  and reports failure without claiming task success.

## Candidate evidence

- Python syntax and targeted lifecycle regressions: PASS.
- Forced concurrent task starts: PASS, exactly one winner and one refusal; winner state
  and receipt preserved; no abandoned lease; final validator PASS.
- Forced concurrent task completions: PASS, exactly one winner and one refusal; one
  ledger row, one evidence row and one completion receipt; final validator PASS.
- Existing local reversible success, failed-close truthfulness and false-undo rejection
  regressions: PASS.
- Complete lifecycle suite, release validator, extracted edition checks, Claude
  full-permission behavioral reruns, portal checks and independent Monitor rereview:
  PENDING in the local candidate lane.

## Current decision

`DO NOT PUBLISH YET`. This record describes a local correction candidate. It becomes a
release record only after the remaining gates pass, the independent Monitor returns
SHIP, the manifests are owner-approved/released, and protected publication and live
verification complete.
