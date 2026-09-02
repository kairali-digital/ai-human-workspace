# Claude round 2 — verification of the v2.4.0 fixes

Reviewer: Claude CLI, repository-local. No subagents, no MCP, no network, no external
accounts, no real user data. All fixtures are temporary and live under `/tmp/r2`. No
product file was edited in this round (`git status` at the end of the pass is identical
to the start; see §9).

Target: working tree at `agent/v240-governed-automation`, uncommitted on top of
`efbe027`. Round 1 was written at `02:59:20`; `scripts/ai_human.py` (`03:05:20`),
`scripts/validate_release.py` (`03:07:14`) and `tests/test_lifecycle.py` (`03:07:08`)
changed after it. `docs/releases/VET-v2.4.0.md` (`01:08:08`) and
`portal/public/downloads/*v240*` (`02:26:58`) did **not**.

---

## Verdict

**HOLD.**

The three round-1 P1s are genuinely fixed *in source* and I reproduced each fix. That
work is real and well done.

The release is not shippable for two reasons that are both artifacts of the release
process rather than of the design:

1. **The published v2.4.0 kits do not contain the fixes.** Both archives in
   `portal/public/downloads/` were built at `02:26:58`, before round 1 was even written.
   The employee kit's shipped `ai_human.py` has no `refuse_skill_discovery_target`, no
   `validate_current_manual_run` and no decision ledger. I reproduced round-1 P1-1
   end-to-end **using the shipped kit's own runtime**. Every gate — 89 unit tests,
   `validate_release.py`, `validate-portal.mjs`, `validate_portal_deploy.py` — passes
   over this stale artifact, because none of them compares the archive's workspace to
   the repository release.
2. **`fleet-update --repository` is still unpinned, and nothing binds a release
   manifest's repository to the worker's installed repository.** I installed a release
   declaring `repository: attacker/example` onto a worker through the ordinary update
   path *and* through the fleet path; the worker's managed runtime was replaced and its
   update origin was permanently rebound to the foreign repository. Round-1 P2-1 was
   closed for component commands only.

Both are correctable in minutes (rebuild the editions; pin the fleet repository and add
a repository-binding check). Neither is a design failure. But shipping today would
publish a download whose behaviour contradicts its own release notes.

---

## 1. Status of every former P0/P1

### Claude round 1

| # | Finding | Status |
|---|---|---|
| P1-1 | `install_pack` installs and activates skills | **NOT RESOLVED** — source fix is correct, but the defect is live in the published kits, and the guard is bypassable on Windows |
| P1-2 | Unbounded `--now-local` lifts `LATER` suppression | **RESOLVED** (residual filed as N3) |
| P1-3 | Retention purge destroys `REJECT` / `LATER` | **RESOLVED** (residual filed as N4) |
| P2-1 | `--repository` defeats publisher pinning | **NOT RESOLVED** — components pinned, `fleet-update` not; escalated to **P0** (N2) |
| P2-2 | `improvement-forget` discards suppression silently | **RESOLVED** |
| P2-3 | Suspend accepts a resumable external schedule | **NOT RESOLVED** |
| P2-4 | Component commands take no worker mutex | **NOT RESOLVED** (structural, low) |
| P2-5 | Fleet pilot lane hardcoded `daily-email-triage` | **NOT RESOLVED** |
| P2-6 | `RELEASED` / `APPROVED_BY_OWNER` while VET is HOLD | **NOT RESOLVED** |

### Codex round 1

All five reliability P0s and the product P0 remain closed; I re-verified them by code
and by the full suite. One correction to the round-1 record:

- Reliability P0-1 (canonical publisher on `--latest`) is **RESOLVED, but its fix is the
  origin of N2.** `release_publisher` (`scripts/ai_human.py:5272`) returns
  `DEFAULT_RELEASE_PUBLISHER` for the pinned repository and `repository.split("/")[0]`
  for anything else, so for a non-default repository the "pinned owner" check compares
  the attacker to themselves.
- Product P0 (uninstall with a live external schedule) is **RESOLVED** — I reproduced
  the refusal (§5, Journey 4). Its sibling P2-3 for `suspend` is still open.

---

## 2. Round-1 P1 reproductions against the current source

### P1-1 — `install_pack` (RESOLVED in source)

`HOST_SKILL_DISCOVERY_PARTS` (`:167`), `refuse_skill_discovery_target` (`:6408`) and its
call in `install_pack` (`:6580`) are new, plus an AST assertion in
`validate_release.py:846`.

```
$ python3 scripts/ai_human.py install-pack kairali-company-rollout /tmp/r2/packtest/project/.claude
AI-HUMAN INSTALL-PACK: FAIL - reference-pack target enters a host skill-discovery path: .claude

$ ... /tmp/r2/packtest/project/skills/kit
AI-HUMAN INSTALL-PACK: FAIL - ... : skills
$ ... /tmp/r2/packtest/project/.codex/skills/kit
AI-HUMAN INSTALL-PACK: FAIL - ... : .codex, skills
$ ... /tmp/r2/packtest/project2/.CLAUDE/x            # case fold
AI-HUMAN INSTALL-PACK: FAIL - ... : .claude
$ ... "/tmp/r2/packtest/project3/.claude/skílls"     # NFD normalisation
AI-HUMAN INSTALL-PACK: FAIL - ... : .claude
$ ... /tmp/r2/sym/entry/plain/kit                    # parent symlink -> .claude
AI-HUMAN INSTALL-PACK: FAIL - ... : .claude
$ ... "/tmp/r2/sym/host/.claude/../.claude/kit"      # traversal
AI-HUMAN INSTALL-PACK: FAIL - ... : .claude
$ find /tmp/r2/packtest /tmp/r2/sym -name SKILL.md   # nothing written
```

Case folding, NFC normalisation, symlinked parents and `..` traversal are all covered.
See N5 for the one alias class that is not.

### P1-2 — caller-chosen `--now-local` (RESOLVED)

`MAX_MANUAL_RUN_CLOCK_SKEW` (`:166`) + `validate_current_manual_run` (`:892`), called
from `improvement_run` (`:4543`). `prior_recommendation_decisions` (`:4222`) now derives
`today` from `datetime.now(timezone.utc)` instead of the caller's moment.

```
$ ai improvement-run W --mode MANUAL ... --now-local 2027-07-01T10:30:00+05:30
AI-HUMAN IMPROVEMENT-RUN: FAIL - manual improvement run time must be within five
minutes of the current clock
```

And the dated `LATER` holds even when the run *is* legitimately dated in the future:

```
# LATER recorded with revisit_on = 2026-09-10
$ ai improvement-run W --mode SCHEDULED ... --now-local 2026-12-05T10:30:00+05:30 ...
AI-HUMAN PERSONAL IMPROVEMENT RUN: PASS
- recommendations awaiting review: 0        <- suppression held past the revisit date
```

The real-clock comparison is the right fix: it holds in `SCHEDULED` mode too, where the
five-minute clamp is deliberately not applied.

### P1-3 — retention purge resurrecting decisions (RESOLVED)

New: `IMPROVEMENT_DECISIONS_PATH` (`:49`), `validate_persistent_decision` (`:1325`),
`improvement_decision_ledger` (`:1350`), `upsert_improvement_decision` (`:1379`). The
ledger lives at `.ai-human/improvement/decisions.json`, outside `runs/` and `research/`,
so `expired_improvement_paths` (`:4510`) cannot reach it.

Full CLI reproduction of the exact round-1 scenario (`retention-days 1`, `MONTHLY`,
source `COMPLETED_LEDGER`, two repeated ledger rows):

```
RUN1 run-20260902T214907Z   rec-bea694617ca65521  "Turn repeated work into a reusable
                                                   governed workflow: Prepare weekly brief"
     improvement-decision <RUN1> <REC> REJECT  -> persisted to decisions.json
RUN2 (MANUAL, now)          recommendations awaiting review: 0
RUN3 (SCHEDULED at +31d)    recommendations awaiting review: 0
     $ ls .ai-human/improvement/runs/
       run-20260902T214948Z          <- RUN1 and RUN2 purged by retention
     $ cat .ai-human/improvement/decisions.json | jq '.records|length'
       1                             <- REJECT survived
```

`IMPROVEMENT-BRIEF.md` after the purge still shows the history for a run file that no
longer exists:

```
## Decision history

- `run-20260902T214907Z/rec-bea694617ca65521` — **REJECT** at 20260902T214917Z
```

Round-1 P1-3 is closed. The regression test
(`tests/test_lifecycle.py:3514 test_persistent_decisions_survive_run_retention_and_ignore_caller_clock`)
is in-process only; the end-to-end CLI resurrection path above is still untested.

---

## 3. New findings

### N1 — P0: the published v2.4.0 kits ship a pre-fix runtime, and every gate passes

`portal/public/downloads/*v240*` were built at `02:26:58`. `scripts/ai_human.py` was
last changed at `03:05:20`. `build_editions.py:93` reads `ROOT/"scripts/ai_human.py"` at
build time, so the archives are simply stale — they were never rebuilt after the fixes.

```
$ unzip -q KAIRALI-AI-HUMAN-v240-EMPLOYEE-EDITION-PUBLIC-KIT.zip \
      'KAIRALI-EMPLOYEE-EDITION/workspace/scripts/ai_human.py'
$ cat .../workspace/core/VERSION
2.4.0
$ shasum -a 256 .../workspace/scripts/ai_human.py
bd7363d1f331695daf1a0696e37a679be85227ed303340f823275a3005586a50
$ shasum -a 256 scripts/ai_human.py
8d7c1b662017171ff0df0ef855773ddeae90977d219cbc364607d8e554934ef0   <- release-manifest value
$ grep -c refuse_skill_discovery_target      .../workspace/scripts/ai_human.py   -> 0
$ grep -c "def validate_current_manual_run"  .../workspace/scripts/ai_human.py   -> 0
$ grep -c "improvement-decisions/v1"         .../workspace/scripts/ai_human.py   -> 0
$ grep -m1 ^DEFAULT_REPOSITORY               .../workspace/scripts/ai_human.py
DEFAULT_REPOSITORY = "kairali-digital/ai-human-workspace"
```

Round-1 P1-1 reproduced with the shipped kit's own runtime:

```
$ python3 <shipped-kit>/workspace/scripts/ai_human.py \
      install-pack kairali-company-rollout /tmp/r2/shipped/project/.claude --source .
AI-HUMAN COMPONENT INSTALL: PASS
- component: kairali-company-rollout
- target: /private/tmp/r2/shipped/project/.claude
$ find /tmp/r2/shipped -name SKILL.md
/tmp/r2/shipped/project/.claude/skills/kairali-rahul-sales-system/SKILL.md
/tmp/r2/shipped/project/.claude/skills/kairali-akshar-marketing-science/SKILL.md
```

The reusable kit is equally stale (`5cf29cf1…`, no guard; its
`DEFAULT_REPOSITORY = "standalone-local/…"` rewrite is intentional per
`build_editions.py:98`, the missing fixes are not).

Why nothing caught it:

- `tests/test_lifecycle.py:1751` and `:1796` assert the archives exist, contain the
  expected names, install and validate. Neither compares the archive's
  `workspace/scripts/ai_human.py` to the repository's.
- `portal/content/download-manifest.json` was regenerated at `02:28:31` against the
  stale zips, so `validate-portal.mjs` confirms the bytes are the bytes it was told to
  expect. `PORTAL VALIDATION: PASS — downloads verified: 47`.
- `validate_release.py:139` `PROOF_IGNORED_PARTS` includes `portal`, so
  `release-proof.json` contains **zero** `portal/` entries. The published downloads are
  outside all release integrity proof.

This is the sharpest instance of security theatre in the release: four green gates, all
of them agreeing with each other about an artifact none of them checks against the code.

**Fix:** rerun `build_editions.py` and `refresh-download-manifest.mjs`, then add a test
asserting the Kairali kit's `workspace/scripts/ai_human.py` sha256 equals
`release-manifest.json`'s entry, and the reusable kit's equals it after the two
documented byte substitutions.

### N2 — P0: `fleet-update --repository` installs foreign managed code and rebinds the worker's update origin

Round-1 P2-1 was closed at `component_release` (`:6373`):

```
$ ai components --latest --repository attacker/example
AI-HUMAN COMPONENTS: FAIL - component repository must match the pinned release repository
$ ai install-pack ... --latest --repository attacker/example
AI-HUMAN INSTALL-PACK: FAIL - component repository must match the pinned release repository
```

`fleet_update` (`:5954`) has the same flag (`parser`, `:6941`) and no such check:

```python
5960:        temporary, release, manifest = download_release(args.repository)
```

`download_release` → `github_release` (`:5280`) computes
`expected_owner = release_publisher(repository)`, which for `attacker/example` is
`"attacker"`. Both identity checks (`:5301` release author login, `:5315` commit author
login + `verification.verified`) then compare the attacker's repository to the
attacker's own account. A GPG-verified commit on one's own repository satisfies them.

Downstream there is no repository binding either: `apply_update` (`:5130`) never
compares `manifest["repository"]` to `install_metadata(worker)["repository"]`, and
`write_install_metadata` (`:1861`) overwrites the stored repository from the incoming
manifest. Demonstrated offline with a local release declaring `attacker/example`:

```
$ ai update /tmp/r2/worker --source /tmp/r2/evil --at-checkpoint
AI-HUMAN UPDATE: PASS
- previous version: 2.4.0
- new version: 2.4.1
- company, role and user state hashes: preserved
$ python3 -c "...install.json..."
attacker/example 2.4.1                          <- update origin permanently rebound
$ grep -c OWNED-BY-FOREIGN-REPOSITORY .ai-human/bin/ai_human.py
1                                               <- attacker payload is the managed runtime
$ ai validate /tmp/r2/worker
AI-HUMAN WORKER VALIDATION: PASS
```

Through the fleet path, with the worker's automatic-update setting `ACTIVE`:

```
$ ai fleet-update --fleet fleet.json --fleet-state fleet-state.json \
      --source /tmp/r2/evil --now-local "2026-10-01T10:00:00+05:30"
AI-HUMAN FLEET BATCH
- Daily Email Triage pilot: PASS
- worker-001: UPDATED — CHECK_COMPLETE
$ ...install.json -> attacker/example 2.4.1 ; attacker marker present: 1
```

After this, the worker's own `update --latest`, `automatic-update --latest` and
`check` all read `install_metadata(worker)["repository"]` and go to the attacker's
repository forever.

Mitigations that exist: the worker must have automatic updates `ACTIVE` for the fleet
path (a plain `update --latest` has no `--repository` flag), and `rollback --version
2.4.0 --source <trusted>` cleanly restores both the bytes and the repository (verified,
§5 Journey 5a). Neither removes the finding.

`docs/UPDATES-ROLLBACK-REMOVAL.md:52` — "The lifecycle tool downloads only the
configured repository's final canonical GitHub release. It verifies the configured
owner…" — is false for `fleet-update`, where the repository is an operator CLI flag.

**Fix:** reject `--repository != DEFAULT_REPOSITORY` in `fleet_update` exactly as
`component_release` does; and in `apply_update`, refuse a manifest whose `repository`
differs from the worker's installed metadata.

### N3 — P1: `SCHEDULED` runs are never compared to the real clock

`improvement_run` (`:4528`) applies `validate_current_manual_run` only in `MANUAL` mode.
In `SCHEDULED` mode the only constraint is `moment == schedule["next_run_local"]`, and
`improvement_schedule_record` bounds that value to ≤32 (monthly) / ≤94 (quarterly) days
*ahead of the moment the schedule was recorded*. `expired_improvement_paths` then uses
that claimed moment as the retention cutoff, and the run's own `--next-run-local` is
validated against the claimed moment rather than the real clock — so the chain walks
forward one cadence per call.

Executed within roughly ten seconds of real time, by a lease-holding agent:

```
$ ai improvement-schedule W --status ACTIVE ... --next-run-local 2026-10-04T10:30:00+05:30
AI-HUMAN PERSONAL IMPROVEMENT SCHEDULE: VERIFIED_ACTIVE
$ ai improvement-run W --mode SCHEDULED ... --now-local 2026-10-04T10:30:00+05:30 \
                                          --next-run-local 2026-11-04T10:30:00+05:30
AI-HUMAN PERSONAL IMPROVEMENT RUN: PASS      # purged 2 run files
$ ai improvement-run W --mode SCHEDULED ... --now-local 2026-11-04T10:30:00+05:30 \
                                          --next-run-local 2026-12-05T10:30:00+05:30
AI-HUMAN PERSONAL IMPROVEMENT RUN: PASS      # purged 1 more
$ ai improvement-show W
- cadence: monthly at 10:30 in Asia/Kolkata
- next run: 2026-12-05T10:30:00+05:30        <- 93 days out, for a MONTHLY cadence
$ ai validate W
AI-HUMAN WORKER VALIDATION: PASS
```

Two consequences. First, silent private-state destruction: research receipts and run
reports are deleted against a fictional cutoff (decisions survive, thanks to P1-3's
fix). Second, `improvement-run` rewrites the *verified* schedule's `next_run_local` from
caller text with no fresh visible-card proof, and `validate_improvement_state` (`:1516`)
checks frequency, local time, zone and prompt hash but never that `next_run_local` is
within one cadence of now. `core/QUARTERLY-IMPROVEMENT.md` claims "A scheduled run must
refresh the visible future next-run proof before it can report success" — the value is
refreshed, the *visible* part is not enforced.

**Fix:** require the real clock to be within a bounded window of
`schedule["next_run_local"]` for a `SCHEDULED` run; compute the retention cutoff from
real UTC; and validate `next_run_local` against real UTC in `validate_improvement_state`.

### N4 — P2: a persistent decision becomes unremovable once its run is purged

`improvement_forget` (`:4842`) requires the run file to exist before it will drop that
run's ledger records. Ordinary retention deletes run files but not ledger records. The
combination leaves entries that cannot be reached by any command:

```
$ ai improvement-forget W RUN run-20260902T214907Z --session-id s4 ...
AI-HUMAN IMPROVEMENT-FORGET: FAIL - quarterly improvement item is missing: run-20260902T214907Z
$ ai improvement-show W
- persistent improvement decisions: 1        <- still suppressing, permanently
```

`improvement-decision` also refuses a recommendation that is not `REVIEW_REQUIRED`, so
there is no un-`REJECT` path at all. A client who rejects a suggestion in March and
changes their mind in July must hand-edit `.ai-human/improvement/decisions.json` — which
then breaks the lease state hash (N7). Round-1 P1-3 correctly demanded persistence; it
did not ask for permanence.

**Fix:** let `improvement-forget DECISION <workflow_signature>` (or
`improvement-decision --reconsider`) drop a ledger record with a receipt.

### N5 — P1: the skill-discovery guard is bypassable by Windows path aliases

`refuse_skill_discovery_target` (`:6408`) normalises NFC and case-folds, but does not
strip trailing dots or spaces. Win32 does strip them, so `.claude.` and `.claude ` both
resolve to `.claude` on Windows — an alias class the threat model names explicitly, and
which `safe_relative` in the same file already rejects at `:319`
(`part.endswith((" ", "."))`).

```
$ python3 scripts/ai_human.py install-pack kairali-company-rollout "/tmp/r2/sym/v3/.claude."
AI-HUMAN COMPONENT INSTALL: PASS
- target: /private/tmp/r2/sym/v3/.claude.
$ find /tmp/r2/sym/v3 -name SKILL.md
/tmp/r2/sym/v3/.claude./skills/kairali-rahul-sales-system/SKILL.md
/tmp/r2/sym/v3/.claude./skills/kairali-akshar-marketing-science/SKILL.md

$ ... "/tmp/r2/sym/v2/.claude /kit"     # trailing space
AI-HUMAN COMPONENT INSTALL: PASS
```

On macOS these are literal directory names and harmless. On Windows the first command
writes `…\.claude\skills\<name>\SKILL.md` — byte-for-byte the round-1 P1-1 outcome. CI
runs `windows-latest`, and `tests/test_lifecycle.py:1312` covers only `.claude`,
`.codex/skills`, `.agents/skills` and `skills`.

**Fix:** apply the `safe_relative` portability rules to each target part before the
`HOST_SKILL_DISCOVERY_PARTS` intersection.

### N6 — P2: the validator's guard check proves ordering, not protection

`handler_guard_precedes_effect` (`validate_release.py:204`) matches call *names* by line
number. It does not check that the guard receives the value the effect consumes, or that
the call is reachable:

```
real source passes guard check: True
guard called on the WRONG object still passes: True     # refuse_skill_discovery_target(release)
guard in a dead branch still passes: True               # if False: refuse_...(target)
```

The failure message it emits — "reference-pack install is not guarded before a host
skill-discovery write" (`:850`) — claims more than the check establishes. The runtime
guard is real; the gate asserting it is decorative. Compare `fixed_unavailable_handler`
(`:175`), which genuinely constrains the whole function body and is sound.

**Fix:** require the guard's single argument to be the same `ast.Name` passed as the
target argument of `install_component_tree`, and require both calls at the function's
top statement level.

### N7 — P2: editing your own daily files during a session deadlocks the worker

`COORDINATION_STATE_FILES` (`:87`) puts `MASTER_CURSOR.md`, `OPEN_REGISTER.md`,
`TODAY.md`, `COMPLETED_LEDGER.md`, `EVIDENCE_LOG.md` and `AUTOMATIONS.md` inside
`controlled_state_hash`. If any changes while a lease is held:

```
$ echo "| T-3 | ... |" >> COMPLETED_LEDGER.md      # the user, in their editor
$ ai improvement-run W --mode MANUAL ...
AI-HUMAN IMPROVEMENT-RUN: FAIL - controlled state changed outside the lease transaction
$ ai session-release W --session-id s1 --expected-state-hash <old>
AI-HUMAN SESSION-RELEASE: FAIL - controlled state changed outside the lease transaction
$ ai session-recover W --actor "Supervisor One" --expected-state-hash <current>
AI-HUMAN SESSION-RECOVER: FAIL - expected-state hash mismatch; do not recover over changed state
$ ai session-recover W --actor "User One" ...
AI-HUMAN SESSION-RECOVER: FAIL - only the designated supervisor may recover an abandoned lease
```

`session_recover` (`:2713`) demands `current == lease["state_hash"]`, so the one command
meant for this situation is unusable in it. The only escape I found is deleting
`.ai-human/control/session-lease.json` by hand — undocumented, and indistinguishable
from tampering.

This behaviour is inherited unchanged from v2.3 (`git show HEAD:scripts/ai_human.py`,
same function, same `COORDINATION_STATE_FILES`), so it is not a v2.4 regression. v2.4
enlarges its blast radius: the improvement loop expects a scheduled agent to hold the
lease across a long research-and-run session, and `AUTOMATIONS.md` +
`.ai-human/improvement/**.json` are now controlled state too.
`docs/GOVERNED-CAPABILITIES-AND-FLEET.md:24` states the constraint ("using the unchanged
expected-state hash") but no beginner document says what to do when it bites.

**Fix:** allow supervisor recovery over changed state when the reason is recorded and
the divergence is written into the recovery receipt; document the escape in
`docs/BEGINNER-SETUP.md`.

### N8 — P3: `remove-skill` leaves a `SKILL.md` tree inside the host skills root

`remove_component_target` archives through `unique_component_archive` (`:6440`), which
creates its archive in `target.parent` — i.e. inside `~/.claude/skills`:

```
$ ai remove-skill kairali-rahul-sales-system --runtime claude \
      --skills-root /tmp/r2/hostskills --at-checkpoint
AI-HUMAN COMPONENT REMOVE: PASS
- preserved at: …/hostskills/.ai-human-component-archive/…-removed-…/component
- deleted files: 0
$ find /tmp/r2/hostskills
…/.ai-human-component-archive/kairali-rahul-sales-system-removed-…/component/SKILL.md
```

Two levels deeper than the `<root>/<name>/SKILL.md` pattern and inside a dot-directory,
so ordinary discovery is very unlikely to reach it — but it is the one managed write
that lands in a path `core/AUTONOMY-CONTROL.md` says is rejected outright. Archive
outside the skills root instead.

### N9 — P3: the brief contradicts itself once value is measured

`render_improvement_brief` (`:4404`) always appends "Time or money saved stays unknown
until the owner provides a baseline and a later run measures it", even in a document
that already reports `Observed value: **36 Minutes.**` and a measurement block. Make the
closing line conditional. (The `## Decision history` list also runs directly into
`## Source links` with no blank line.)

### N10 — process: `release-proof.json` covers the wrong set of files

It excludes `portal/` entirely (N1) while **including** all 14 `handover/v2.4.0/` files.
Writing this review therefore invalidates `validate_release.py` until the proof is
regenerated:

```
release proof is missing payload file: handover/v2.4.0/reviews/CLAUDE-ROUND-2.md
```

That is expected and is not a defect I introduced — but adversarial review artifacts
being release payload while the published downloads are not is backwards.

---

## 4. Full suite and gate evidence

```
$ python3 -m unittest discover -s tests -v          # Python 3.9.6 (local default)
Ran 89 tests in 45.823s
OK

$ /opt/homebrew/bin/python3.12 -m unittest discover -s tests -v   # nearest to CI's 3.11
Ran 89 tests in 43.727s
OK

$ python3 scripts/validate_release.py .
AI-HUMAN PUBLIC RELEASE VALIDATION: PASS
- version: 2.4.0
- managed files: 12
- component catalog entries: 3
- local company and user state: excluded
- secret and absolute-path scan: PASS

$ python3 scripts/validate_release.py . --ci      -> PASS
$ node portal/scripts/validate-portal.mjs
PORTAL VALIDATION: PASS
- downloads verified: 47
$ python3 scripts/validate_portal_deploy.py .
PORTAL PRODUCTION RELEASE GATE: PASS
$ shasum -a 256 -c *v240*.zip.sha256              -> both OK
```

Not obtainable in this environment, and still outstanding for the VET record:
`npm ci`, `npm run typecheck`, `npm run build` (no `node_modules`, no network, and the
volume has ~600 MB free); and the live `--latest` GitHub identity path.

**Safe-disabled contract — every entry point exercised:**

```
$ ai action-execute W --batch none.json
FAIL - UNAVAILABLE_NO_NATIVE_BROKER: external email and LinkedIn effects are
safe-disabled before authorization, ticket creation or provider contact
$ ai autonomy-skill-install W kairali-rahul-sales-system --runtime claude
FAIL - UNAVAILABLE_NO_TRUSTED_SKILL_LOADER: ... before a lock, download, staging
directory or runtime change
$ ai install-skill kairali-rahul-sales-system --runtime claude
FAIL - UNAVAILABLE_NO_HUMAN_PRESENCE_AUTHORITY: ...
$ ai autonomy-choice W ENABLE --approval-reference REF-1 ...
FAIL - UNAVAILABLE_NO_TRUSTED_EFFECT_RUNTIME: v2.4 cannot enable any standing effect
$ cat core/AUTHORITY-REGISTRY.json
{"authorities": [], "schema": "ai-human.effect-authority-registry/v1"}
```

No path in the current source contacts an email or LinkedIn provider. The only network
egress remains `api.github.com` — which is precisely why N2 matters.

**Research provenance and injection — no regression:**

```
unapproved domain      -> FAIL - official research source is outside the approved domain allowlist
undated REDDIT finding -> FAIL - community research receipts require a source publication or update date
26-receipt batch       -> FAIL - research batch must contain 1 to 25 receipts
instruction_content_ignored=false
                       -> FAIL - research must record that source instructions were ignored
```

---

## 5. The five client journeys

**Journey 1 — a beginner installs from the public download.** Extract
`AI-HUMAN-v240-REUSABLE-EDITION-PUBLIC-KIT.zip`, run the Setup Helper prompt.
`AI-HUMAN INSTALL: PASS — version 2.4.0, created local files: 21, local gate profile:
profile-example-reg-001 (CONFIRMED)`. Works. **But the runtime they just installed is
the pre-fix build (N1).** The `START-HERE.md` in that same zip tells them "v2.4 never
installs or activates a skill", which is untrue of the binary beside it.

**Journey 2 — turn on the monthly review and let it run.** `SET UP MY PERSONAL
IMPROVEMENT REVIEW` → `improvement-choice ENABLE --cadence MONTHLY --local-time 10:30
--timezone Asia/Kolkata` → `improvement-schedule-prompt` prints the exact prompt and its
SHA-256 → the human creates the Scheduled card → `improvement-schedule --status ACTIVE
--visible-card --task-prompt-sha256 … --next-run-local …` → `VERIFIED_ACTIVE`. The
paste-prompt hides the CLI well and the prompt/card binding is genuinely operable by a
beginner: the fingerprint they must match is printed next to the text they must paste.
Two frictions: the whole flow dies if the user edits `TODAY.md` mid-session (N7), and
the "verified" next run can drift from the card afterwards (N3).

**Journey 3 — decide and measure.** Run produced
`rec-138acbd38de8b015 "Turn repeated work into a reusable governed workflow: Draft board
update"` from two `COMPLETED_LEDGER` rows.

```
$ ai improvement-decision W <run> <rec> PROPOSE ...
- capability activation: NONE
- governed proposal: improvement-138acbd38de8b015 — AWAITING SUPERVISOR
$ ai improvement-value W <run> <rec> --baseline-minutes 20 --observed-minutes 8 \
      --occurrences 3 --evidence "Owner timed three fixture runs."
- observed total difference: 36 minutes
- money saved: NOT CLAIMED
```

The brief shows `Evidence priority score: 82`, `Forecast value: Unknown until the owner
supplies a baseline`, the measurement block and dated decision history. This is the
honest core of the release and it holds up — no invented value anywhere. Its stated
limit is real: measured saving starts at zero and only grows if a human keeps timing
things. `REJECT` is also now irreversible (N4).

**Journey 4 — pause, then remove.** `improvement-schedule --status REMOVED` →
`improvement-control REMOVE` → `session-release` → `uninstall --at-checkpoint`:
`removed system moved to .ai-human-removed-20260902T215813Z`, `active local adapters
archived: 5`, `project, company and user work state: preserved`, and all 18 user files
plus `IMPROVEMENT-BRIEF.md` remain. `verify-state --expect UNINSTALLED` → PASS. Skipping
the schedule removal is correctly refused:
`FAIL - remove and visibly verify the external personal-improvement schedule before
uninstalling`. **But the equivalent `suspend` does not refuse** (old P2-3): with a
`VERIFIED_PAUSED` card still live, `AI-HUMAN SUSPEND: PASS — managed rules and
automations: OFF` and `verify-state --expect SUSPENDED` repeats it.

**Journey 5 — something goes wrong.** (a) After the foreign-repository install of N2,
`rollback --version 2.4.0 --source <trusted>` restored the correct bytes *and* reset
`install.json` to `kairali-digital/ai-human-workspace`; validator PASS. (b)
`prepare-downgrade --target-version 2.3.0` moved v2 private state to
`.ai-human/downgrade-exports/v2.4.0-before-v2.3.0-…` (`.ai-human/improvement` gone), and
`restore-downgrade` brought back `config.json` with `improvement-show` reporting the
original quarterly configuration; validator PASS. Recovery remains the strongest part of
this release.

---

## 6. Client benefit

Unchanged from round 1 and slightly better. A client gets an optional cadence they
choose, a Scheduled card hash-bound to the exact prompt, a readable ranked brief with
source links, and — new since round 1 — decisions that genuinely persist. The
`REJECT`-survives-retention fix is the single most valuable change in this round: it
removes the "the assistant keeps asking me the same thing" failure that would have
eroded trust within one retention window. Recovery (journal, trusted-release rollback,
uninstall archive, downgrade export/restore) is verified working end to end.

The honest limits are unchanged: the loop still needs a human to run CLI steps through
an agent and to supply before/after minutes, so measured saving starts at zero; and the
thing a client would actually download today does not contain any of the above.

---

## 7. Scores (0-10) — round 1 → round 2

| Dimension | R1 | R2 | Basis |
|---|---:|---:|---|
| Usefulness | 7 | 7 | Ranked, evidence-derived, source-linked, decisions now durable; `REJECT` is irreversible (N4) |
| Time saving | 5 | 5 | Measurement path verified honest and owner-driven; still nothing demonstrated in-repo |
| Beginner ease | 6 | 5 | Paste-prompt journeys and the printed prompt fingerprint work well; lease deadlock has no documented escape (N7), and the published kit is the wrong build (N1) |
| Truthfulness | 7 | 5 | Release notes and CHANGELOG assert fixes the shipped artifact lacks; "pinned GitHub publisher" is false for `fleet-update`; suspend still prints automations OFF; VET still HOLD/PENDING while manifests say RELEASED |
| Recovery | 8 | 7 | Rollback, `recover-lifecycle`, uninstall archive and downgrade export/restore all verified; offset by the un-forgettable decision and the lease deadlock |
| Security | 6 | 4 | Effects genuinely safe-disabled in source; two P0s (stale shipped runtime carrying the known skill defect; unpinned fleet repository installing foreign managed code), plus a Windows alias bypass and a decorative AST gate |

---

## 8. Missing tests

1. Archive-to-repository runtime parity for both editions — would have caught N1 alone.
2. Windows-alias targets (`.claude.`, `.claude `, `skills.`) in
   `test_reference_pack_cannot_enter_host_skill_discovery_paths`.
3. `fleet-update --repository attacker/example` rejected before any network call, mirroring
   `test_component_commands_reject_an_unpinned_repository_before_network`.
4. `apply_update` refusing a manifest whose `repository` differs from the worker's
   installed metadata.
5. A `SCHEDULED` run rejected when the real clock is far from `next_run_local`, and a
   retention cutoff computed from real UTC.
6. The round-1 P1-3 resurrection scenario at CLI level (the current regression test is
   in-process only).
7. `handler_guard_precedes_effect` rejecting a guard called on the wrong object or in an
   unreachable branch.
8. Supervisor lease recovery after legitimate user edits to `TODAY.md` /
   `COMPLETED_LEDGER.md`.

---

## 9. Conditions for SHIP

1. **Rebuild and republish both editions** from the current source, refresh
   `download-manifest.json`, and add the parity test (N1). Confirm the employee kit's
   `workspace/scripts/ai_human.py` sha256 equals the `release-manifest.json` entry
   `8d7c1b66…`.
2. **Pin `fleet-update --repository`** to `DEFAULT_REPOSITORY`, and make `apply_update`
   refuse a manifest whose repository differs from the worker's installed metadata (N2).
3. **Bound `SCHEDULED --now-local` to the real clock**, compute retention from real UTC,
   and validate `next_run_local` against real UTC (N3).
4. **Normalise trailing dots and spaces** in `refuse_skill_discovery_target` (N5).
5. **Replace the six `PENDING` gates in `docs/releases/VET-v2.4.0.md`** with real
   results, or set the manifests back to `LOCAL_BUILD_ONLY` until they exist. Requirement
   13 is currently unmet by the repository's own record, and `release-manifest.json` /
   `component-manifest.json` already say `RELEASED` / `APPROVED_BY_OWNER`. The portal
   *typecheck* and *production build* still have no recorded run anywhere.
6. Add the regression tests in §8 (1–5 at minimum).

Optional but recommended before the tag: give `suspend` the same schedule refusal as
`uninstall` (P2-3); add a way to reconsider a persisted decision (N4); tighten
`handler_guard_precedes_effect` (N6); document the lease-deadlock escape (N7).

**Product files touched this round: none.**

```
$ git status --short        # identical to the pre-review snapshot, 30 modified + 9 untracked
```

`handover/v2.4.0/reviews/CLAUDE-ROUND-2.md` is the sole file added, and
`release-proof.json` must be regenerated for `validate_release.py` to pass again (N10).
