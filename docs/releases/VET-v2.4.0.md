# Verification evidence and trust record: v2.4.0

## Release identity

- Version: `2.4.0`
- Lane: `APPROVED_BY_OWNER` / `RELEASED`
- Compatibility: backward-compatible from configured v2.0.0 through v2.3.0
- Automatic update eligible: no
- Publication authority: explicit owner instruction on 3 September 2026

## Required behavioral proof

- Monthly and quarterly configurations bind an exact prompt hash, visible cadence and
  bounded next run. Changed configuration cannot inherit stale schedule proof.
- Research batches reject more than 25 receipts, unapproved channels, missing community
  dates, unsafe URLs, copied raw pages, personal data and followed source instructions.
- v2 recommendations are derived from installed evidence; identical decided workflow
  signatures are suppressed on later runs. A compact decision ledger survives run
  retention, and explicit decision-forget provides a recorded reconsideration path.
  `PROPOSE` creates only an inactive proposal.
- Update, rollback, suspension, uninstall and fleet paths serialize through a
  crash-released operation lock. Suspension latches STOP before waiting.
- Release download trusts only the final canonical GitHub tag owned by the configured
  repository owner, a matching immutable commit and a GitHub-verified commit signature.
- Fleet and per-worker updates refuse a release repository different from the pinned
  installed repository before managed bytes can change.
- Every improvement run is tied to the real clock. Scheduled and missed-run-recovery
  paths require fresh visible-card, cadence and prompt-hash proof for the next occurrence;
  fictional future dates cannot purge retained artifacts or advance schedule truth.
- The authority registry is exactly empty. AST validation requires `action_execute`,
  `autonomy_skill_install`, `install_skill` and `validate_autonomy_consent` to contain
  only their fixed unavailable exception. Runtime tests prove no ticket, result, lock,
  staging directory, provider contact or skill root is produced.
- Reference packs reject `.agents`, `.claude`, `.codex`, `skills` and their Windows
  trailing-dot/space aliases. The structural validator binds that guard to the exact
  target passed to the copy effect, and edition runtimes must byte-match current source.

## Verification evidence

- Full lifecycle suite after convergence fixes:
  - Python 3.9.6: `python3 -m unittest discover -s tests -v` — 96 tests, `OK`, 53.356s.
  - Python 3.12: `python3.12 -m unittest discover -s tests -v` — 96 tests, `OK`, 51.050s.
- Public release validator: `python3 scripts/validate_release.py .` — `PASS`, 12 managed
  files, three component entries, secret/absolute-path scan `PASS`. The 282-file release
  proof includes portal source, both current ZIPs, their checksums and review evidence;
  only generated/build/cache directories are excluded.
- Editions and readback:
  - deterministic edition rebuild completed after the final source fixes;
  - reusable checksum `aa207752c1ca0422de598fc11c55af789d54f2e3fa70a3f85009086a51225afb`;
  - Kairali checksum `91eff73ea0552c3f8b92847c58e6f2a6ea7d372487058f8906205eba1abbb617`;
  - both checksum files report `OK`;
  - Kairali archived runtime SHA-256 equals the managed runtime SHA-256
    `ed84d52a11e7522480556300f32f97dbc86eee168cf89e16e8addd5421e5384f`;
  - reusable archived runtime byte-matches the two documented neutral substitutions;
  - archive extraction, installation, repository identity and worker validation pass in
    `test_public_edition_archives_install_and_validate_after_extraction`.
- Beginner rollout: company `gates/validate_beginner_rollout.py` — `PASS`, 11 role
  prompts plus deck, setup guide, homework, facilitator runbook and helper card; no
  employee command-line action found.
- Portal on the declared Node 22 runtime (`22.23.2`): clean dependency install, production
  audit `0 vulnerabilities`, 47-download validation `PASS`, TypeScript `PASS`, and
  Next.js 16.3.0 production build `PASS` with static `/`, 404, icon, robots and sitemap.
- `scripts/validate_portal_deploy.py .` — `PASS`; released/owner-approved manifests and
  no candidate-only portal assets or labels.
- Secret checks:
  - current tracked tree after removing generated `.next`: no leaks;
  - both v2.4 archives, including nested archive depth 2: no leaks;
  - Git history: 44 commits scanned, no leaks.
- Adversarial review records:
  - both Codex round-one reviews found and drove closure of update/recovery, publisher,
    fleet-proof, schedule, research, value and safe-disabled defects;
  - Claude round one `HOLD` identified three remaining decision/pack defects;
  - Claude round two `HOLD` confirmed those source fixes and found stale ZIP,
    repository-rebinding, real-clock, Windows-alias and proof-coverage gaps;
  - every round-two P0/P1 and recommended concrete recovery/truthfulness item now has a
    code fix plus regression test;
  - Claude final convergence independently reintroduced the former P0 failures, proved
    the new gates turn red, reran the high-risk negative paths and returned the exact
    verdict `AGREE: RELEASE v2.4.0`. It found no open P0/P1 and records the remaining
    P2/operational risks in `handover/v2.4.0/reviews/CLAUDE-FINAL.md`.
- Protected GitHub validation on Ubuntu, macOS and Windows remains mandatory after the
  exact candidate commit is pushed and before `v2.4.0` is tagged.

## Production hardening review

| Area | Result | Evidence |
|---|---|---|
| Configuration and secrets | PASS | No embedded credential; current tree, nested v2.4 archives and 44-commit history scans clean |
| Dependencies | PASS | Node 22 clean install and production audit with zero vulnerabilities |
| Reliability and recovery | PASS | Mutex, preemptive stop, transaction journal, trusted-release rollback, downgrade export, explicit lease-divergence recovery |
| Data/state safety | PASS | Managed-only update, state hash checks, retained decisions, bounded cleanup, recoverable component removal |
| External effects | PASS / unavailable | Empty authority registry; email, LinkedIn and managed skill installation fail before effect state or provider/runtime change |
| Observability | PASS | Receipts, validator readback, visible schedule proof, deployment inspection and hosted checks required |
| Rollout/rollback | PASS | Automatic eligibility off; checkpoint update; exact prior-release rollback; deployment promotion only after preview verification |

## Code-vetting report

GATE 0 compliance    PASS — no medical, dosage, certification, legal-text or spend decision changed; exact local profiles remain authoritative and non-overridable
GATE 1 structure     PASS — manifests, portable paths, protected state, batch cap, repository binding and source-to-edition parity verified
GATE 2 facts         PASS — values remain owner-measured or UNKNOWN; source receipts are scoped, dated and injection-resistant; no number is inferred
GATE 3 redirects     PASS — canonical metadata, robots, sitemap, download paths and candidate-asset refusal verified
GATE 4 works         PASS — install, update, deferral, refusal, scheduled proof, suspend, recovery, rollback, removal and archive readback paths exercised
GATE 5 proof         PASS LOCALLY — dual-runtime 96-test suites, exact payload proof, archive parity/checksums, beginner gate, portal build/audit and secret scans passed

VERDICT: LOCAL RELEASE GATES PASS; PROTECTED HOSTED CHECKS REQUIRED BEFORE TAG
REASON: the candidate has independent release agreement and explicit unavailable
boundaries. This record does not pre-claim protected cross-platform checks, GitHub
publication or production deployment; those remain required against the exact commit.
