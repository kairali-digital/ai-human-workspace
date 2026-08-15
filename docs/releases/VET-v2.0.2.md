# Verification evidence and trust record: v2.0.2

## Release identity

- Version: `2.0.2`
- Lane: `APPROVED_BY_OWNER` / `RELEASED`
- Compatibility: backward-compatible from configured v2.0.0 and held v2.0.1 workers
- Automatic update eligible: no
- Publication condition: owner authorization and independent Monitor SHIP are complete;
  protected GitHub, production and distribution verification still gate each channel

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

## Verification evidence

- Python syntax and targeted lifecycle regressions: PASS.
- Forced concurrent task starts: PASS, exactly one winner and one refusal; winner state
  and receipt preserved; no abandoned lease; final validator PASS.
- Forced concurrent task completions: PASS, exactly one winner and one refusal; one
  ledger row, one evidence row and one completion receipt; final validator PASS.
- Existing local reversible success, failed-close truthfulness and false-undo rejection
  regressions: PASS.
- First v2.0.2 Claude mixed-draft run correctly withheld Gate 0 content but inferred
  three missing brief fields. The candidate was not promoted; explicit missing-source
  guidance and a regression were added.
- Complete local-candidate lifecycle suite: PASS, 63 tests in one continuous run.
- Local candidate release validator: PASS, including secret and absolute-path scans.
- Separate reusable and Kairali candidate archives: PASS, including extraction,
  candidate-lane install refusal and company-content isolation.
- Reusable candidate SHA-256:
  `1177afb021317620d1e488d8b1e756c5cf20f8b9ff43af9e35f1456195aac212`.
- Kairali candidate SHA-256:
  `f9307ba86eb93cdc4cf97df598e612197a87524315ed1f208ea4804881531bd6`.
- Reusable public-edition SHA-256:
  `946e8db54f03fc32b270f7a276b3bd3bdf14ed00806b8b1eb580a10a6f76f0f6`.
- Kairali public-edition SHA-256:
  `1eff6396ff9ef19907653e3156c1eae97bbaf77a318bdd55c5b974e71fad3e29`.
- Claude full-permission read-only run: PASS in 13.4 seconds and 4 turns; exact source
  answer, no file diff, validator PASS and zero web-search/fetch requests.
- Corrected Claude full-permission local artifact run: PASS in 51.5 seconds and 17
  turns; missing due dates stayed `Not provided in source`, task start preceded the
  write, task completion followed readback, exactly two receipts and validator PASS.
- Corrected Claude full-permission mixed Gate 0 run: PASS in 70.6 seconds and 22 turns;
  all missing brief fields stayed `Not provided in source`, only the unsupported claim
  was withheld, its exact wording was absent from the artifact, the approval path was
  correct, exactly two receipts and validator PASS.
- All Claude behavioral runs had zero permission denials and zero web-search/fetch
  requests. No browser, account, message, publication or external action was allowed.
- Portal TypeScript, direct Next.js 16.3.0 optimized build and production dependency
  audit: PASS; zero vulnerabilities. The local host was Node 24, while the repository
  remains pinned to Node 22 for protected CI and production verification.
- Before promotion, the candidate production portal gate failed closed as expected
  because its manifests were `LOCAL_BUILD_ONLY` and no v2.0.2 public-edition assets
  existed.
- Independent Monitor rereview: PASS across Gates 0–5; verdict `SHIP`. Ten real-process
  task-start races and ten task-completion races each produced exactly one winner and
  one clean refusal with no state loss, abandoned lease or validator failure.
- Promoted public-lane lifecycle suite: PASS, 63 tests in one continuous run.
- Public release validator and production portal gate: PASS.
- Portal manifest, TypeScript and Next.js production build: PASS across 31 verified
  downloads; production dependency audit reports zero vulnerabilities.
- Both public-edition checksum files and ZIP extraction tests: PASS.
- Zero-knowledge beginner rollout gate: PASS across all 11 role prompts and the full
  Mac/Windows setup and recovery material.
- Full-history secret scan: PASS across 32 commits. Offline recipient addresses have
  zero exact matches in tracked public repository text.

## Current decision

`APPROVED FOR THE PROTECTED PUBLICATION WORKFLOW`. Owner authorization, independent
Monitor SHIP and owner-approved/released manifests are complete. This decision is not
proof that GitHub, the stable portal or recipient distribution has already completed;
each requires its own protected checks and post-publication verification.
