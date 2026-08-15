# Verification evidence and trust record: v2.1.0

## Candidate identity

- Version: `2.1.0`
- Lane: `APPROVED_BY_OWNER` / `RELEASED`
- Compatibility: backward-compatible from configured v2.0.0 and held v2.0.1 workers
- Automatic update eligible: no
- Scope: the v2.0.2 lease-order correction plus the H-48 Drive dual-register and
  optional weekly-refresh release

## Battle-test evidence

- Forced concurrent task starts: PASS. Exactly one caller wins, the other is refused,
  winner state and receipt are preserved, no lease is abandoned and the final worker
  validator passes.
- Forced concurrent task completions: PASS. Exactly one caller wins, with one ledger
  row, one evidence row, one receipt, no abandoned lease and final validator PASS.
- Synthetic full Drive register: PASS. AI JSONL, formula-safe human CSV, approved Sheet
  readback, stable IDs, generation ID and unique/relationship counts reconcile.
- Synthetic `TEST 25` register: PASS. A valid sample is accepted only with the exact
  `FULL DRIVE NOT INDEXED` status; a shortened completion claim fails closed.
- Negative Drive cases: PASS. Corrupted counts, missing output, duplicate IDs, invalid
  relationship values, generation drift and unsafe cursor secret fields are rejected.
- Release containment: PASS. The validator rejected temporary PDF-inspection PNGs when
  they were accidentally left inside the candidate tree. They were moved outside the
  release, the proof inventory was rebuilt and candidate validation then passed.
- Complete lifecycle suite: PASS in both lanes: 63 candidate tests in 32.192 seconds
  and 64 rebased final public-lane tests in 24.155 seconds. Public-edition extraction, installation
  and worker validation passed.
- Local candidate release validator: PASS, including secret and absolute-path scans.
- Public release and CI validators: PASS, including exact non-portal proof inventory,
  managed hashes, component hashes, secret scan and absolute-path scan.
- Public reusable edition SHA-256:
  `b59af4a285402f832977279469df10544a819b4f0f4898c4d0d912ee4f1f603c`.
- Public Kairali employee edition SHA-256:
  `f7c72f3763396ee152b016781f2a896054e4f3849987e9ec37edc971e5420c6d`.
- Homework pack SHA-256:
  `472ee3660628bc8468cc584ee955555943f749a7dfe88f4a85300f9060ac741b`.
- Beginner rollout gate: PASS across 11 role prompts, the employee guide, facilitator
  path, Setup Helper rescue prompt and Mac/Windows recovery path.
- Guide render: PASS, 12 letter-size pages, visually reviewed with no clipped content
  or blank trailing page.
- Homework video: PASS, 427.47 seconds, 18 ordered caption scenes and visual contact
  sheet reviewed; the Drive scene shows both registers, relationship counts and the
  optional post-full-index weekly refresh.
- Portal production release gate: PASS. Portal validation verified 35 downloadable
  files, canonical metadata, robots, sitemap, scoped download noindex and visible-copy
  rules. TypeScript and the Next.js 16.3.0 optimized build passed under Node 22.23.2;
  the production dependency audit reported zero vulnerabilities.
- Governed-source secret scan: PASS. Gitleaks scanned 12.65 MB and found no leaks;
  generated dependency, `.next` and `dist` output was excluded from source evidence.
- Git-history secret scan: PASS. Gitleaks scanned all 35 commits reachable from the
  rebased release commit and found no leaks.
- A third Claude Fable read-only review was attempted and produced no result before its
  timeout. It made no release edits and is not counted as passing evidence.

## Code-vetting report

`VET AI-Human Workspace v2.1.0 16 August 2026`

- GATE 0 compliance: PASS. No medical claim, dosage, certification, legal text or spend
  was added or changed.
- GATE 1 structure: PASS. No cross-app import or entity structure changed; all Drive
  processing remains capped at 25 with a durable checkpoint.
- GATE 2 facts: PASS. New operational numbers are release/task identifiers, generated
  test evidence, the governed 25-item cap or measured artifact properties. No centre,
  address, phone or certification fact was introduced.
- GATE 3 redirects and languages: PASS, not affected. No route, locale slug, redirect
  or hreflang behavior changed.
- GATE 4 works: PASS in candidate tests and rendered artifact checks. Public package,
  portal build and live checks remain part of the protected publication workflow.
- GATE 5 proof: PASS for the candidate. Before: v2.0.1 was held and Drive output could
  remain incomplete or unverified. After: dual-register and race tests plus release
  validators pass. Undo: revert the v2.1.0 release commit and restore the prior stable
  portal deployment; do not install or announce the held v2.0.1 release.

`VERDICT: SHIP`

`REASON: The exact public packages, lifecycle races, both Drive modes, beginner path,
artifacts and portal build pass; protected GitHub and production readback remain the
publication transaction, not unverified assumptions.`

## Current decision

`SHIP THROUGH THE PROTECTED PUBLICATION WORKFLOW`. Abhilash explicitly authorized one
more battle test and publication. Protected GitHub checks, immutable release assets,
production deploy and live readback must still pass before this task is closed. No
employee announcement or distribution is authorized by this record.
