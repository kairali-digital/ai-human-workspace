# Verification evidence and trust record: v2.0.0

## Release identity

- Version: `2.0.0`
- Date: `2026-08-15`
- Approval: `APPROVED_BY_OWNER`
- Release status: `RELEASED`
- Compatibility: `SETUP_MIGRATION_REQUIRED`
- Automatic update eligible: `false`

## Verified behavior

- One complete artifact containing 150 issue descriptions is stored or uploaded as one
  intact assignment unit; it is not truncated at row 25.
- Separately executed tasks and separately created external records are still split into
  batches of no more than 25 with checkpoints.
- Gate 0 is exact-scope, source-backed, compliance-owner confirmed, tamper-evident and
  isolated by worker. Unresolved or overdue profiles block ACTIVE.
- Completion requires the correct ledger and detailed passing evidence; `done`, `ok`
  and similar placeholders fail validation.
- Suspend, resume, uninstall and access revocation are separate, reversible controls
  with explicit state verification.
- Managed release sources and worker targets reject symbolic-link redirection.
- Duplicate JSON keys, protected control-state descendants, duplicate/symbolic-link ZIP
  members and stale or incomplete release proofs fail closed.
- Remote GitHub Actions are pinned to immutable commit SHAs, and production application
  dependencies are audited before portal build and deployment.

## Verification commands and expected evidence

- `python3 scripts/build_release.py .`: release proof and managed/component hashes pass.
- `python3 scripts/validate_release.py .`: public release validation passes.
- `python3 -m unittest discover -s tests -v`: all lifecycle and adversarial tests pass.
- `python3 scripts/build_editions.py`: two released public edition ZIPs and sidecars pass.
- `python3 scripts/validate_portal_deploy.py .`: production status/asset gate passes.
- `npm audit --omit=dev`: zero production dependency vulnerabilities.
- `npm run validate`, `npm run typecheck`, `npm run build`: portal integrity and
  production build pass.
- Local and production browser checks cover desktop/mobile layout, links, downloads,
  console/network errors, indexing endpoints and security headers.

Five completed independent Claude Opus adversarial reviews were used during candidate
hardening. Every reported product defect was remediated and re-tested. A sixth broader
run timed out without a report and is explicitly not counted as a pass or failure.

## Trust boundaries and residual risk

- Repository-local workflow hashes detect accidental or one-sided workflow changes;
  they cannot defeat a malicious co-edit of a workflow and its validator. Protected
  main, required hosted checks, immutable Action pins, exact-diff review and the owner
  release decision are the external trust root.
- The Vercel CLI is deployment tooling, not a portal application dependency. The
  shipped production dependency graph is audited separately and must remain clean.
- This release contains no live user state, private evidence, credentials or real
  company compliance profile. Setup must obtain and confirm those locally.
- Release does not install anything on employee devices and does not broaden connector,
  plugin, browser or operating-system permissions.

## Rollback

- GitHub: retain v1.5.1 and its checksums; do not overwrite immutable v2.0.0 assets.
- Portal: use Vercel's prior production deployment if a post-release verification fails.
- Worker: v2.0.0 setup migration makes a checked backup before managed changes; restore
  that backup and re-run validation if application fails.
