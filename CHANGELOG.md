# Changelog

All notable changes are recorded here in plain language.

## [2.2.0] - 2026-08-16

- Upgrade the required Email worker into a fixed-time Personal Work Memory + Daily
  Email EA. Its neat brief shows priorities, follow-ups, useful reading, newsletter and
  filter proposals, and concise local replies visibly marked `NOT SENT`.
- Add employee-owned, source-backed work memory for role, priorities, people,
  communication preferences, recurring work and commitments. Memory distinguishes
  `CONFIRMED` from `OBSERVED — VERIFY` and supports visible show, correct, exclude,
  forget and refresh controls without copying a mailbox or inferring sensitive traits.
- Make `DRIVE-INDEX.jsonl` the Drive worker's normalized AI-readable file of record.
  Generate exactly one human register from it: an explicitly approved Google Sheet or
  otherwise `DRIVE-REGISTER.csv`.
- Fail Drive completion closed unless JSONL, the human register, summary and cursor
  reopen under one generation ID and agree on object/data-row, unique, relationship,
  overlap, unknown and refresh counts. A failed reconciliation never advances the
  last-success cursor.
- Offer, but never silently activate, a weekly Drive refresh only after full-index
  proof. The employee confirms day, exact local time and time zone or records `NOT
  ENABLED BY CHOICE`; missed-run, pause, edit and removal paths stay visible.
- Let optional manually supplied LinkedIn work contribute only concise reusable tone
  or work-context learning that the employee explicitly confirms, can correct and can
  forget. LinkedIn remains entirely human-accessed and human-sent.
- Carry forward the v2.0.2 lifecycle correction: task start and completion acquire the
  exclusive lease before reading or preparing state, and forced two-caller races prove
  one winner, one clean refusal and no state loss.
- Refresh the beginner guide, DOCX, PDF, video, captions, prompts, component bundle,
  edition downloads, validators and portal under one governed v2.2.0 release.

## [2.0.2] - 2026-08-16

- Hold v2.0.1 after an independent post-publication Monitor test found that two task
  lifecycle calls prepared from the same pre-lease state could both report success
  while the later write silently replaced the earlier live task.
- Move every task-start and task-complete state read, live-task check, ID allocation,
  artifact check and multi-file render inside the exclusive worker lease. Recheck the
  leased state hash immediately before the atomic commit.
- Add forced concurrent start and completion regressions. Each race must produce one
  winner and one clean refusal, preserve the winner's exact state and receipt, leave no
  duplicate ledger/evidence rows or abandoned lease, and finish with validator PASS.
- Make source truth explicit for generated artifacts: a field absent from the named
  source stays `Not provided in source` or a labelled placeholder instead of being
  inferred from context.
- Preserve the proportional v2.0.1 work model: direct read-only answers, reversible
  local achievement, narrow Gate 0 withholding, and the distinction between one intact
  assignment artifact and separately executed actions capped at 25.
- Support checkpointed recovery from configured v2.0.0 workers and held v2.0.1 workers
  while keeping automatic update eligibility off. Pre-v2 workers still require the
  guided exact-scope Gate 0 setup migration.

## [2.0.1] - 2026-08-15

- Add three proportional execution paths. Read-only requests answer directly without
  task-state changes; ordinary reversible local work uses standing task-scoped local
  read/write permissions; consequential, external and Gate 0 work retains the full
  approval, source, lease, evidence and rollback controls.
- Add deterministic `task-start` and `task-complete` lifecycle commands. They
  auto-generate a task ID when the user supplied none, own cursor/register/today/
  ledger/evidence formatting, acquire and release the writer lease internally, commit
  state atomically and refuse to report completion until final validation passes.
- Give fresh workers standing permission to read worker-local sources and create or
  edit the bounded reversible artifact explicitly requested by the user. The permission
  excludes controlled state, `.ai-human/`, secrets, external effects, deletion,
  unrecoverable overwrites, accounts and security changes, so routine work no longer
  creates one-off tool, fact or decision rows.
- Parse live task IDs only from an explicit `Task ID:` field or the leading legacy ID,
  never from a later backticked filename in the task description. Parse escaped table
  separators without corrupting a title or proof row.
- Normalize a leading explanatory `PASS` result while keeping the explanation in the
  verification field. Deterministic close removes the completed ID from both open and
  today state in the same validated transaction, preventing the v2.0.0 false-completion
  case.
- Keep the artifact/assignment distinction unchanged: a complete file with 150 embedded
  entries remains one intact unit, while 150 separately executed items or remote writes
  remain checkpointed in batches of no more than 25.
- Keep a mixed request on the fast local path when its gated part is withheld. The
  worker reads the exact company profile, completes the safe artifact and does not add
  a redundant manual writer lease.
- Require a complete non-claim note or no reference when content is withheld. Created
  artifacts paraphrase the blocked category instead of reproducing unsupported wording
  or leaving a dangling section reference.
- Reject literally false undo evidence such as “no other files changed”; task closure
  stays open until the proof distinguishes the requested artifact from lifecycle state
  and internal receipts.
- Classify the patch as backward-compatible for an already configured v2.0.0 worker.
  A pre-v2 worker still needs the existing guided exact-scope Gate 0 migration before
  entering the v2 line; automatic update eligibility remains off.

## [2.0.0] - 2026-08-15

- Replace the incorrect universal company Gate 0 with a confirmed local profile bound
  to one exact company/group, legal entity, operating unit, jurisdictions, purpose and
  user relationship. Setup requires current authoritative sources and compliance-owner
  confirmation; historical charts remain unverified leads. Different scopes use
  isolated workers/profiles.
- Add tamper-evident `.ai-human/control/gate-profile.json`, generated `GATES.md` and
  `COMPLIANCE-SOURCES.md`, separate task-specific `WORK-GATES.md`, and
  `WORKSPACE-MAP.md`, which makes the file of record for
  identity, gates, facts, decisions, tools, task state, completion and evidence explicit.
- Classify this release as `SETUP_MIGRATION_REQUIRED`. A checkpoint-only migration
  archives the old universal gate file, preserves task locks, binds and validates the
  exact profile, and remains ineligible for automatic updates.
- Make reusable core and starter language user-neutral. Kairali-specific materials use
  employee only where that relationship has been confirmed.
- Add an ACTIVE-mode pushback contract: name the exact boundary politely, refuse only
  the conflicting part, preserve safe work and guide the owner to the nearest compliant
  path or approval. The pattern is deliberately off when the system is SUSPENDED.
- Add two non-overlapping public downloads: a complete Kairali Employee Edition and
  a company-neutral Reusable Edition tested to contain no Kairali, Abhilash or Ambuj
  content. Add one five-step beginner install path with visible `DONE WHEN` proof.
- Add owner-controlled `ACTIVE`, `SUSPENDED` and `UNINSTALLED` modes. Suspension turns
  managed rules, automations and automatic updates off; automatic checks defer without
  mutation. Reversible uninstall archives the managed system and active generated
  adapters while preserving independent project instructions and work files.
- Add install, troubleshooting, resume, uninstall and separate plugin/connector/
  Computer Use revocation guidance to the website and both edition guides.
- Use the canonical owner name `Abhilash` throughout Kairali-facing material while
  rejecting both canonical and legacy spellings from the reusable edition.
- Give Mac and Windows separate ZIP extraction steps, reject weak completion evidence
  such as `done` or `ok`, and map `WORKSPACE-MAP.md` to itself as the map's file of record.
- Report a setup-migration release as a safe automatic-update deferral instead of a
  failed rollback, and let CI select the candidate or public validation lane from the
  manifest without weakening either lane.
- Make the portal indexable with canonical metadata, robots.txt and a sitemap; keep
  download binaries under a scoped `noindex` response header and gate production on
  exact released manifests and public-edition assets.
- Put a fail-closed public-release and candidate-asset gate before every production
  portal deployment command; an indexable local candidate still cannot deploy.
- Normalize and minimum-size completion proof so punctuation cannot turn `done` or `ok`
  into detailed evidence, and require the approved scheduler adapter to supply an
  offset-aware worker-local timestamp instead of falling back to the host clock.
- Treat commented workflow commands as inactive and require both production gates
  before Vercel pull, build or deploy. Reject combinations of weak proof words and count
  Unicode combining marks so Malayalam and other Indic evidence is not undercounted.
- Detect alternate or second-job Vercel production commands, reject shell overrides,
  and structurally verify active PR/lifecycle/secret CI jobs. Parse only true Markdown
  delimiter rows, expand weak-phrase screening, and state that lexical checks do not
  prove a completion claim is true.
- Pin all three allowed GitHub Actions workflows to governed SHA-256 values and reject
  every additional workflow file, closing folded-scalar, command-continuation,
  shallow-history, command-neutralizer and trigger-narrowing fail-open paths.
- Add exclusive session leases and expected-state compare-and-swap commits for the
  cursor, register, today, ledger and evidence files. A second writer is rejected,
  out-of-band changes are detected, and failed multi-file state commits restore their
  before copy.
- Add governed capability proposals with required ownership, source, tool, gate,
  deterministic/model-judgment, proof, version, secret and retirement fields.
  Users choose `PROPOSE`, `LATER` or `REJECT`; only the configured supervisor can
  activate a proven proposal or approve it for a later company release.
- Add first-calendar-day, 10:00 AM user-local version checks and idle-only
  automatic updates. Automatic application requires a released, owner-approved,
  hash-verified, backward-compatible manifest and an explicitly active worker setting.
- Add a Daily Email Triage pilot gate and isolated fleet batches capped at 25. A local
  worker failure is reported without stopping other safe workers; general workers wait
  until the pilot is verified.
- Define the batch unit before applying the cap: one intact artifact or assignment
  intake may contain any number of entries and must not be truncated, while separately
  executed items and separately created external records remain capped at 25. Add a
  read-only batch planner and regression tests for a 150-entry artifact versus 150
  GitHub issue writes.
- Enforce the generated release proof as an exact non-portal payload inventory, reject
  duplicate JSON keys, protected-state subtree targets, source/worker symlinks and
  duplicate or symbolic-link ZIP members before installation or update writes.
- Release v2.0.0 as owner-approved and installable while keeping automatic updates off:
  its exact-scope Gate 0 migration must be completed at a safe checkpoint.

## [1.5.1] - 2026-08-13

- Add one explicit employee update workflow from company announcement through
  read-only version check, employee approval, checkpointed apply, validation receipt
  and Monitor coverage proof.
- Make the automatic/manual boundary exact: session start may check for a newer
  approved release, but no managed file is overwritten until the employee approves
  `UPDATE NOW` at a safe checkpoint.
- Separate GitHub Desktop repository sync from lifecycle install/update. Fetch/Pull
  updates the selected repository checkout; it does not update an installed worker,
  reference kit or governed skill.
- Preserve employee-owned company, role, facts, decisions, cursor, register, today,
  ledger, evidence, automation, credential and personal files; keep checked backups,
  rollback receipts and recoverable removal archives.
- Refresh the beginner guide, Setup Helper, facilitator/technical guidance, decks,
  release artifacts and stable portal with the same workflow and proof contract.

## [1.5.0] - 2026-08-13

- Add one zero-knowledge, task-scoped Computer Use setup for the optional LinkedIn
  worker, using ChatGPT's real permission prompt rather than a fake portal control.
- Allow `@Computer` only inside the approved local worker and `@Chrome` only on a named
  non-LinkedIn public page; keep Ask for approval and prohibit Full access/Always allow.
- Require the exact `YOUR TURN ON LINKEDIN` stop/handoff before LinkedIn appears. While
  LinkedIn is visible, the AI cannot inspect, move, click, type, read, copy, paste or
  send; the employee performs and confirms every LinkedIn action.
- Refresh the starter, prompts, guides, homework video/captions, decks, release proofs
  and noindex portal to the same right-level-access behavior.
- Add one three-worker go-live readback across the common/named prompts, Setup Helper,
  homework, presentations, repository and portal. The public kit being available is
  distinct from an employee worker being activated and proven.
- Make `FULL DRIVE INDEX` the required company-homework completion state; `TEST 25`
  remains a safe setup proof. Saturday LinkedIn remains optional and may be recorded
  as `NOT ENABLED BY CHOICE`.

## [1.4.0] - 2026-08-13

- Replace the optional one-time LinkedIn profile draft with a weekly Saturday message
  assistant configured at each employee's chosen local time and confirmed time zone.
- Learn tone and routing only from employee-supplied prior message/reply pairs and
  employee-confirmed outcomes, in checkpointed batches of no more than 25.
- Separate routine `READY TO SEND` drafts from a persistent numbered
  `NEEDS YOUR DECISION` queue and keep unresolved items across sessions.
- Preserve a strict human gate: the employee manually copies messages, reviews every
  draft and manually sends. The AI never accesses, controls or sends through LinkedIn.
- Update all employee prompts, homework, guides, decks, release artifacts and portal
  downloads to the same v1.4.0 behavior.

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
