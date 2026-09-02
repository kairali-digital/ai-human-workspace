# Claude round 1 — bounded file-based review of v2.4.0

Reviewer: Claude CLI, repository-local, no subagents, no MCP, no network, no external
accounts. Full test suite deliberately not run (Codex supplies that evidence). No
product file was edited. Findings below were reproduced against the working tree at
`agent/v240-governed-automation` using temporary fixtures only.

## Verdict

**HOLD.**

Three requirement-level defects survive, all reproduced. Separately,
`docs/releases/VET-v2.4.0.md` still reads `VERDICT: HOLD UNTIL FINAL EVIDENCE IS
INSERTED` with all six code-vetting gates `PENDING`, while `release-manifest.json` and
`component-manifest.json` already carry `RELEASED` / `APPROVED_BY_OWNER`. Requirement 13
is therefore unmet by the repository's own record, and I must not infer the gates passed.

The engineering quality of this release is genuinely high — every original P0 from both
Codex reviews is closed in code, not in prose. The hold is narrow, not a rejection.

---

## Remaining P0/P1

### P1-1 — `install_pack` installs and activates skills (`scripts/ai_human.py:6400`)

`REQUIREMENTS.md` §10 and "Deliberately not claimed" state: *no v2.4 managed mechanism
installs or activates a skill*. `install_skill` (`:6375`) and `autonomy_skill_install`
(`:6382`) are hard-disabled and AST-verified by `validate_release.py`. `install_pack` is
not, and the `kairali-company-rollout` reference pack (`component-manifest.json`,
`source: packages/kairali`, 109 files) **contains two complete skill trees**, each with a
valid `SKILL.md` frontmatter — `tests/test_lifecycle.py:1240` asserts exactly this.

`install_pack` resolves its target with `safe_worker(args.target, must_exist=False)`
(`:6404`), which rejects only the filesystem root and `$HOME`. There is no
skills-directory check, no `--at-checkpoint`, no lease, no consent, no human-presence
gate — the precise controls the two disabled entry points exist to enforce.

Minimal reproduction (executed):

```bash
mkdir -p /tmp/packtest/project
python3 scripts/ai_human.py install-pack kairali-company-rollout \
  /tmp/packtest/project/.claude
# AI-HUMAN COMPONENT INSTALL: PASS
find /tmp/packtest -name SKILL.md
# /tmp/packtest/project/.claude/skills/kairali-rahul-sales-system/SKILL.md
# /tmp/packtest/project/.claude/skills/kairali-akshar-marketing-science/SKILL.md
```

Both files now sit where Claude auto-discovers project skills; `.codex` behaves the same
for Codex. A managed command printed `PASS` while doing the thing the release notes,
`core/AUTONOMY-CONTROL.md`, `editions/kairali/START-HERE.md` ("v2.4 never installs or
activates a skill") and `portal/content/site-data.ts` all say cannot happen.

Minimal fix: in `install_pack`, reject any target whose resolved path has a `.claude`,
`.codex`, `.agents` or `skills` component, or refuse packs whose tree contains a
`SKILL.md`; then add the constraint to `validate_release.py` alongside the existing AST
checks.

### P1-2 — Unbounded `--now-local` lifts `LATER` suppression (`improvement_run`, `:4391`)

`improvement_run` derives `moment_utc` from `args.now_local` and passes it to
`automatic_recommendations` → `prior_recommendation_decisions` (`:4105`), where a dated
`LATER` blocks only while `revisit > moment_utc.date()`. In `MANUAL` mode nothing
compares `--now-local` to the real clock (the `SCHEDULED` binding at `:4409-4416` is not
applied). A lease-holding agent picks the date at which a deferral has "expired".

Reproduction (executed, in-process):

```python
# prior run: {"decision": "LATER", "revisit_on": "2027-06-01", "workflow_signature": sig}
automatic_recommendations(w, findings, {"G1"}, datetime(2026,9,3,tz=utc))  # -> 0
automatic_recommendations(w, findings, {"G1"}, datetime(2027,7,1,tz=utc))  # -> 1
```

Fix: clamp `--now-local` in `MANUAL` mode to a small window around
`datetime.now(timezone.utc)`, and evaluate `revisit_on` against real UTC rather than the
caller-supplied moment.

### P1-3 — Retention purge silently destroys `REJECT` / `LATER` decisions (`expired_improvement_paths`, `:4374`)

`expired_improvement_paths` selects run files by `created_utc < now - retention_days`
with no check for a recorded human decision, and `improvement_run` deletes them in the
same commit. Because decisions live only inside run JSON, purging a run erases the
suppression that `REQUIREMENTS.md` §5 and §7 require to persist. `--retention-days 1` is
a legal value and is settable through `improvement-choice` with nothing but a lease.

Reproduction (executed end-to-end via the CLI on a fresh installed worker;
`retention-days 1`, `MONTHLY`, source `COMPLETED_LEDGER`, two repeated ledger rows):

```
RUN1  rec-c02bd60bc02cbdab "Turn repeated work into a reusable governed workflow: Weekly brief"
      improvement-decision <run1> rec-c02bd60bc02cbdab REJECT     -> persisted
RUN2  (--now-local +3 days)  recommendations awaiting review: 0
      run1 file still present: False        <- purged by retention
RUN3  (--now-local +6 days)  rec-c02bd60bc02cbdab  decision=REVIEW_REQUIRED
      RESURRECTED REJECTED ID: True
```

The rejected item returns under its **identical id**, and its history disappears from
`IMPROVEMENT-BRIEF.md`. This is not limited to the minimum value: any `REJECT` older
than `retention_days` is resurrected, which for a quarterly loop is the normal case.

Fix: keep a compact append-only decision ledger (signature, choice, dated
`revisit_on`, `decision_utc`) outside the retention window, and have
`prior_recommendation_decisions` read it; or exclude any run holding a non
-`REVIEW_REQUIRED` decision from `expired_improvement_paths`.

---

## Original P0/P1 I independently confirmed resolved

Reliability P0s:

1. **Canonical publisher rejected on `--latest`** — `release_publisher` (`:5107`) +
   `DEFAULT_RELEASE_PUBLISHER = "AbhilashKairali"`; `github_release` (`:5115`) checks the
   final `v`-prefixed tag, non-draft/non-prerelease, author login, a 40-hex commit,
   `verification.verified is True` and `reason == "valid"`, then binds the archive root
   to `commit_sha[:7]`. Code path verified by reading; no network call made.
2. **Mutable backup as rollback authority** — `rollback` (`:5466`) and
   `recover_lifecycle` (`:5204`) both load a trusted release (`--source` or the exact
   tagged download). `restore_backup` (`:4822`) survives only as an in-process
   compensator with a closed schema, per-file digests and `from_version`/`to_version`
   binding to the live transaction.
3. **Crash → mixed-version worker** — `write_lifecycle_transaction` (`:4941`) journals
   `PREPARED`/`APPLIED`; `main()` (`:6835`) refuses every command except
   `recover-lifecycle` while the journal exists; `recover_lifecycle` finalizes a verified
   `APPLIED` state or restores the exact pre-transaction release.
4. **v2.4-only validation blocking a legitimate v2.3 rollback** —
   `required_managed_targets(installed_version)` (`:532`) and
   `validate_autonomy_state(worker, installed_version)` (`:1977`) are version-aware.
5. **Forged prior fleet proof** — `fleet_update_loaded` (`:5807`) computes
   `pilot_cohort_sha256` / `pilot_proof_sha256` from the current invocation only and
   reads no prior fleet state; `pilot_pass` is `False` when the batch has no pilot.

Product P0 and majors:

- **Uninstall with a live external schedule** — `uninstall` (`:6103`) refuses on
  `external_improvement_schedule_still_exists` (blocks `VERIFIED_ACTIVE` **and**
  `VERIFIED_PAUSED` and the stale-from-either case). `prepare_downgrade` applies the same
  test.
- **Prompt consistency** — `improvement_task_prompt` (`:1039`) is a single operational
  script that states "External effects and all managed skill installation are unavailable
  in v2.4", and is bound by hash into schedule proof and `validate_improvement_state`.
- **Research scope/freshness** — `validate_research_payload` (`:1135`) plus
  `validate_research_scope_and_freshness` (`:1200`) enforce channel/host agreement,
  dated community sources, approved questions, the official domain allowlist, both
  freshness edges and a future-access rejection. `collect_improvement_evidence` re-checks
  at read time and reports `excluded_receipts`; `validate_improvement_state` (`:1481`)
  rejects an active receipt whose channel is not approved, so the record path fails
  closed at commit.
- **Model-supplied recommendations** — `improvement_run` (`:4427`) rejects
  `--recommendations` on a v2 config; `automatic_recommendations` (`:4130`) derives them.
- **Signature stability** — `{category, subject_key_sha256}` only, so growing evidence
  ids no longer change identity.
- **Arbitrary "best opportunity"** — ranked by `priority_score` then signature (`:4218`).
- **Time measurement** — `improvement_value` (`:4637`) + `validate_v2_measurement`
  (`:1279`) recompute the total from owner-supplied baseline/observed/occurrences and
  print "money saved: NOT CLAIMED".
- **Downgrade exit** — `prepare_downgrade` / `restore_downgrade` (`:5308`, `:5399`) move
  v2-only state to a hash-inventoried archive with automation backup and full rollback.
- **Mutex** — `main()` wraps every worker-scoped command; fleet takes each worker's mutex
  in `run_fleet_worker_update`; suspend latches STOP before waiting 30s.
- **Fixed-unavailable effects** — `action_execute`, `autonomy_skill_install`,
  `install_skill`, `validate_autonomy_consent` are single-`raise` bodies, structurally
  enforced by `fixed_unavailable_handler` in `validate_release.py:175`;
  `AUTHORITY-REGISTRY.json` must be exactly `{"authorities": [], "schema": …}`. I found
  no path that contacts an email/LinkedIn provider. The only network egress is
  `api.github.com` for release identity and download.
- **Beginner / edition / portal copy** — `docs/BEGINNER-SETUP.md`, both `START-HERE.md`
  files, `site-data.ts` and `validate-portal.mjs` all move to v2.4.0, add the natural
  -language activation journey, and state the unavailable boundary. Apart from P1-1 the
  user-facing copy is accurate, including "the worker truthfully records `UNAVAILABLE`
  without claiming that a schedule exists".

---

## New P2 risks

1. **`--repository` defeats publisher pinning for component commands**
   (`add_component_source_options`, `:6422`). `release_publisher` returns
   `repository.split("/")[0]` for any non-default repo, so an attacker-owned repo
   satisfies its own owner check. Combined with P1-1 this is an arbitrary-source
   skill-tree install. Pin component commands to the installed worker's repository.
2. **`improvement-forget RUN`** (`:4695`) deletes a run and its decisions with no warning
   that suppression is being discarded.
3. **Suspend accepts a resumable external schedule.** `suspend` blocks only
   `external_improvement_schedule_may_run` (`VERIFIED_ACTIVE`), so a `VERIFIED_PAUSED`
   card survives while suspend prints "managed rules and automations: OFF" and
   `verify-state` repeats it. Effect is contained (`improvement-run` is in
   `MODE_GUARDED_COMMANDS`), but the wording overstates and disagrees with uninstall.
4. **Component commands take no worker mutex** — they have no `worker` positional, so
   `main()`'s serialization does not apply.
5. **Fleet pilot lane is hardcoded `daily-email-triage`** (`load_fleet`, `:5762`) in a
   release where email effects are unavailable. Operators must invent a lane label to
   ship any fleet batch.
6. **Repository already marked `RELEASED` / `APPROVED_BY_OWNER`** while
   `VET-v2.4.0.md` records HOLD and six `PENDING` gates. Publishing from this state would
   be the "false completion" the threat model forbids.

---

## Client benefit

Real and better than v2.3. An ordinary client gets an optional cadence they choose, a
schedule whose visible card is hash-bound to the exact prompt (drift invalidates the
proof instead of silently lying), and a readable `IMPROVEMENT-BRIEF.md` that ranks
opportunities, cites source links, shows dated decision history and refuses to invent
value. Recovery is the strongest part: crash journal, trusted-release recovery, a
reversible uninstall archive and a governed pre-v2.4 downgrade export. The honest
limit is that the loop still needs a human to run the CLI steps and supply
before/after minutes, so measured time saved starts at zero and grows only with
disciplined use — and P1-3 means a client who rejects a suggestion will be asked about
it again after the retention window.

## Scores (0-10)

| Dimension | Score | Basis |
|---|---:|---|
| Usefulness | 7 | Evidence-derived, ranked, source-linked; still CLI-heavy |
| Time saving | 5 | Owner-measured only; no saving demonstrated in-repo |
| Beginner ease | 6 | Good paste-prompt journeys; the underlying commands are expert-level |
| Truthfulness | 7 | Strong throughout, defeated by the P1-1 skill claim and a PENDING VET record |
| Recovery | 8 | Journal, trusted-release recovery, reversible uninstall, downgrade export |
| Security | 6 | Effects genuinely safe-disabled; P1-1 and unpinned `--repository` are real holes |

## Conditions for SHIP

1. Close P1-1: `install_pack` cannot place a `SKILL.md` tree in a host-discovered
   directory, enforced by both runtime and `validate_release.py`.
2. Close P1-2 and P1-3 so a `REJECT` and a dated `LATER` survive retention and cannot be
   expired by a caller-chosen `--now-local`.
3. Pin component-command `--repository` to the installed worker's repository.
4. Replace the `PENDING` gates in `VET-v2.4.0.md` with real results: full lifecycle
   suite, release validator, both archive extraction/install/readback runs, beginner
   rollout validator and portal build.
5. Add regression tests for each of the three reproductions above.
