# Changelog

All notable changes are recorded here in plain language.

## [1.3.0] - 2026-08-13

- Upgrade Email Triage from a one-time read-only sample into a verified daily Email
  Importance Brief at each employee's chosen local time and confirmed time zone.
- Require a manual read-only 25-message pilot before scheduling; every later batch
  remains capped at 25 even when a complete daily period needs more than one batch.
- Let the employee explicitly choose `BRIEF ONLY` or `BRIEF + SAFE FILING`; safe mode
  applies only approved reversible labels, archive and read-state changes to clearly
  low-risk mail.
- Add a monthly false-positive audit, durable triage cursor, concise action/read/waiting
  report and human-reviewed rule queue. Permanent Gmail filters are never changed
  silently.

## [1.2.0] - 2026-08-12

- Replace the Drive homework's one-batch ceiling with an employee choice: `TEST 25`
  or a resumable `FULL DRIVE INDEX`.
- Keep the hard safety cap at 25 items per processing batch and write a durable cursor,
  local index and evidence checkpoint after every batch.
- Cover every connector-visible owned/created, shared-with, shared-by and shared-drive
  scope the approved company account exposes, while recording unsupported scopes as
  explicit coverage gaps.
- Keep the index metadata-only and non-mutating; future file-content access still
  requires current Drive permission and a new approved task.

## [1.1.0] - 2026-08-12

- Add the complete Kairali company component bundle: twelve approved employee/setup
  prompts, two governed optional skills, and the validated universal homework pack.
- Add hashed component manifests plus reversible skill and reference-pack installation.
- Add the Email Triage and Drive Inventory homework workers, optional LinkedIn Draft
  worker, exact prompts, printable guide, captions, transcript and narrated video.
- Preserve the shared core/company boundary: components are explicit opt-ins and never
  overwrite live employee state.

## [1.0.0] - 2026-08-12

- First public, company-neutral AI-human workspace release.
- Adds clean install, safe adoption, status, validation, version check, update,
  checkpoint, rollback and reversible uninstall.
- Separates shared system files from company, role and employee state.
- Adds beginner and technical setup paths plus multi-company rollout controls.
- Adds automated lifecycle, public-safety and release-integrity validation.
