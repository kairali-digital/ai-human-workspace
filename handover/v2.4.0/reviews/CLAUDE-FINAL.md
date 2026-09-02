# Claude final — independent release decision for v2.4.0

Reviewer: Claude CLI, repository-local. No subagents, no MCP, no network, no external
accounts, no real user data. Every fixture is temporary and lives under `/tmp/neg`,
`/tmp/final_check` and `/tmp/parity`. No product file was edited in this round; the
working tree is byte-identical to the pre-review snapshot (§7).

Target: working tree at `agent/v240-governed-automation`, uncommitted on top of
`efbe027`. This pass re-derives the decision from repository bytes, the current test
suite, `release-proof.json`, the two published archives, the portal build output and
all five prior review files. Claims in `PRODUCT-BRIEF.md`, `REQUIREMENTS.md`,
`VET-v2.4.0.md`, `CHANGELOG.md` and the release notes were treated as assertions to be
checked against executables, never as evidence.

---

## Verdict

**AGREE: RELEASE v2.4.0**

Every P0 and P1 raised across the two Codex reviews and the two Claude rounds is closed
in code, and I reproduced each closure myself rather than accepting the record. The two
round-2 P0s — a stale published runtime and an unpinned fleet repository — are not just
patched; each now has a gate that fails when the defect is reintroduced, which I proved
by reintroducing it. The residual risks below are P2/P3 and operational, and none of
them makes a user-visible claim false.

---

## 1. Every prior P0/P1, independently re-verified

### Claude round 2

| # | Finding | Status | How I verified it |
|---|---|---|---|
| N1 | Published kits ship a pre-fix runtime | **CLOSED** | Archive/source hash parity + new gate proven to fail on a stale archive |
| N2 | `fleet-update --repository` installs foreign managed code | **CLOSED** | Foreign release refused on both update and fleet paths; no rebinding, no payload |
| N3 | `SCHEDULED` runs never compared to the real clock | **CLOSED** | Live run at a +30-day fictional clock refused; `schedule.json` byte-identical after |
| N4 | Persistent decision becomes unremovable | **CLOSED** | `improvement-forget DECISION` exists; CLI test `test_purged_run_decision_can_be_explicitly_reconsidered` |
| N5 | Guard bypassable by Windows trailing dot/space | **CLOSED** | 10 target variants refused, zero `SKILL.md` written |
| N6 | Validator guard check proves ordering, not protection | **CLOSED** | Wrong-object and removed-guard variants now both return `False` |
| N7 | Editing your own daily files deadlocks the worker | **CLOSED** | `test_supervisor_can_recover_an_abandoned_lease_after_acknowledged_edits` |
| N8 | `remove-skill` leaves a tree inside the host skills root | **CLOSED** | Test asserts `assertNotIn(skills_root, preserved.parents)` and no `SKILL.md` under the root |
| N9 | Brief contradicts itself once value is measured | **CLOSED** | `render_improvement_brief` now selects `value_truth` conditionally on `measured` (`scripts/ai_human.py:4526`) |
| N10 | Release proof covers the wrong set of files | **CLOSED** | Proof is now 281 files including 72 `portal/` entries, both ZIPs and both checksums |
| P2-3 | Suspend accepts a resumable external schedule | **CLOSED** | `suspend` refuses live; shares `external_improvement_schedule_still_exists` with `uninstall` |
| P2-5 | Fleet pilot lane hardcoded | Unchanged, accepted (§5) | `load_fleet` still requires `daily-email-triage` |
| P2-6 | `RELEASED` while VET is `HOLD`/`PENDING` | **CLOSED** | Six `PENDING` gates replaced with results; I reproduced the substantive ones |

### N1 — the sharpest round-2 finding, and the strongest fix

The employee kit's shipped runtime is now the repository's runtime, exactly:

```
$ shasum -a 256 <emp-kit>/KAIRALI-EMPLOYEE-EDITION/workspace/scripts/ai_human.py
ed84d52a11e7522480556300f32f97dbc86eee168cf89e16e8addd5421e5384f
$ shasum -a 256 scripts/ai_human.py
ed84d52a11e7522480556300f32f97dbc86eee168cf89e16e8addd5421e5384f
$ python3 -c "...release-manifest.json managed_files scripts/ai_human.py..."
ed84d52a11e7522480556300f32f97dbc86eee168cf89e16e8addd5421e5384f
```

The reusable kit differs by exactly the two documented neutral substitutions and nothing
else — a four-line diff:

```
28,29c28,29
< DEFAULT_REPOSITORY = "kairali-digital/ai-human-workspace"
< DEFAULT_RELEASE_PUBLISHER = "AbhilashKairali"
---
> DEFAULT_REPOSITORY = "standalone-local/ai-human-workspace"
> DEFAULT_RELEASE_PUBLISHER = "standalone-local"
```

Round-2's complaint was not the stale bytes but that four green gates agreed with each
other about an artifact none of them checked. That is now false:
`validate_public_edition_runtime_parity` (`scripts/validate_release.py:891`) compares the
archived runtime to current source. I proved it has teeth by rebuilding the employee ZIP
in a scratch copy with one appended comment line:

```
$ python3 scripts/validate_release.py .        # /tmp/parity/repo, tampered archive
AI-HUMAN PUBLIC RELEASE VALIDATION: FAIL
- edition runtime differs from the current source: KAIRALI-AI-HUMAN-v240-EMPLOYEE-EDITION-PUBLIC-KIT.zip
```

The exact round-2 P0 is now a release-blocking gate rather than a thing four validators
were blind to.

### N2 — foreign managed code, both paths

`fleet_update` (`scripts/ai_human.py:6013`) pins the CLI flag *and* the release manifest;
`apply_update` (`:5194`) binds the manifest repository to the worker's installed
metadata. Reproduced offline with a local release declaring `attacker/example` and a
marked payload:

```
$ python3 scripts/ai_human.py components --latest --repository attacker/example
AI-HUMAN COMPONENTS: FAIL - component repository must match the pinned release repository
$ ... install-pack ... --latest --repository attacker/example
AI-HUMAN INSTALL-PACK: FAIL - component repository must match the pinned release repository
$ ... fleet-update --repository attacker/example ...
AI-HUMAN FLEET-UPDATE: FAIL - fleet repository must match the pinned release repository

$ ... update /tmp/neg/worker --source /tmp/neg/evil --at-checkpoint
AI-HUMAN UPDATE: FAIL - release repository differs from the worker's pinned installed repository
$ ... fleet-update --fleet ... --source /tmp/neg/evil ...
AI-HUMAN FLEET-UPDATE: FAIL - fleet release repository must match the pinned release repository

$ python3 -c "...install.json..."
kairali-digital/ai-human-workspace 2.4.0      <- origin NOT rebound
$ grep -c OWNED-BY-FOREIGN-REPOSITORY /tmp/neg/worker/.ai-human/bin/ai_human.py
0                                             <- attacker payload absent
```

All three flag refusals happen before any network call. The legitimate pinned path still
functions (`fleet-update --source .` produced a normal batch report). Round-2's charge
that `docs/UPDATES-ROLLBACK-REMOVAL.md:52` was false for `fleet-update` no longer holds.

### N3 — schedule truth is tied to the real clock

`validate_current_improvement_run` (`:892`) is now applied in **every** mode, and
`expired_improvement_paths` / `collect_improvement_evidence` /
`automatic_recommendations` all receive `actual_utc` rather than the caller's moment
(`:4575-4595`). Live, on a `VERIFIED_ACTIVE` schedule 30 days out:

```
$ ... improvement-run W --mode SCHEDULED --now-local 2026-10-03T10:30:00+05:30 ...
AI-HUMAN IMPROVEMENT-RUN: FAIL - improvement run time must be within five minutes of the current clock
--- schedule.json before: e9e040ea378b1dbf69063819865220c124882a7d06ab7ebadbb984e84c8cf8d4
--- schedule.json after : e9e040ea378b1dbf69063819865220c124882a7d06ab7ebadbb984e84c8cf8d4
```

The walk-forward chain is broken at its first step: no purge against a fictional cutoff,
no silent advance of the visible next run.

### N5 / round-1 P1-1 — the reference pack cannot reach a discovery path

Ten target variants, all refused, nothing written:

```
/tmp/neg/p1/.claude              -> FAIL - ... host skill-discovery path: .claude
/tmp/neg/p2/skills/kit           -> FAIL - ... : skills
/tmp/neg/p3/.codex/skills/kit    -> FAIL - ... : .codex, skills
/tmp/neg/p4/.CLAUDE/x            -> FAIL - ... : .claude          (case fold)
/tmp/neg/p5/.claude.             -> FAIL - non-portable trailing dot or space
/tmp/neg/p6/.claude /kit         -> FAIL - non-portable trailing dot or space
/tmp/neg/p7/.agents/skills/k     -> FAIL - ... : .agents, skills
/tmp/neg/p8/skills.              -> FAIL - non-portable trailing dot or space
symlinked parent -> .claude      -> FAIL - ... : .claude
.claude/../.claude/kit           -> FAIL - ... : .claude
$ find /tmp/neg -name SKILL.md | wc -l
0
```

### Round-1 P1-3 — a `REJECT` survives its run file

Reproduced end to end through the CLI on a fresh worker (`retention-days 1`, `MONTHLY`,
`COMPLETED_LEDGER`, two repeated ledger rows), then the run file deleted as retention
would delete it:

```
RUN  run-20260902T223020Z   rec-bea694617ca65521
     improvement-decision ... REJECT   -> persisted to decisions.json
     rm .ai-human/improvement/runs/run-20260902T223020Z.json

runs/ directory contents : []
decisions.json exists    : True
REJECTED signature still suppressed AFTER the run file is gone: True
retention would purge    : []
ledger ever selected     : False
```

`IMPROVEMENT-BRIEF.md` still renders the dated history for the vanished run. The
round-1 resurrection (`RESURRECTED REJECTED ID: True`) cannot be reproduced.

---

## 2. Exact test and gate evidence

```
$ python3 -m unittest tests.test_lifecycle -v            # Python 3.9.6
Ran 96 tests in 52.442s
OK

$ /opt/homebrew/bin/python3.12 -m unittest discover -s tests -v   # Python 3.12.13
Ran 96 tests in 51.224s
OK

$ python3 scripts/validate_release.py .
AI-HUMAN PUBLIC RELEASE VALIDATION: PASS
- version: 2.4.0
- managed files: 12
- component catalog entries: 3
- local company and user state: excluded
- secret and absolute-path scan: PASS

$ python3 scripts/validate_release.py . --ci                 -> PASS
$ python3 scripts/validate_portal_deploy.py .
PORTAL PRODUCTION RELEASE GATE: PASS

$ node portal/scripts/validate-portal.mjs
PORTAL VALIDATION: PASS
- downloads verified: 47

$ npm run typecheck            # tsc --noEmit
(clean, exit 0)

$ npm run build                # Next.js 16.3.0 (Turbopack), Node v24.18.0
✓ Compiled successfully in 2.1s
✓ Generating static pages using 7 workers (6/6)
Route (app): / , /_not-found , /icon.svg , /robots.txt , /sitemap.xml   (all static)

$ shasum -a 256 -c portal/public/downloads/*v240*.zip.sha256
AI-HUMAN-v240-REUSABLE-EDITION-PUBLIC-KIT.zip: OK
KAIRALI-AI-HUMAN-v240-EMPLOYEE-EDITION-PUBLIC-KIT.zip: OK
```

The portal typecheck and production build were the two gates round 2 could not run and
that had no recorded run anywhere. I ran both; both pass. My run used Node v24.18.0
rather than the declared Node 22 — the CI workflow pins `node-version: "22"`, so the
matrix result still belongs to protected CI, but the build is not Node-24-specific.

Release proof coverage, read from `release-proof.json`:

```
total files 281 — portal 72, packages 109, docs 23, starter 21, handover 15,
core 11, scripts 6, .github 5, company-profiles 5, editions 5, tests 1, roles 1, ...
portal/public/downloads/{both ZIPs, both .sha256}  present
```

**Structural invariants, re-proven with negatives rather than read:**

```
fixed-unavailable handlers (AST):
  action_execute             True      autonomy_skill_install     True
  install_skill              True      validate_autonomy_consent  True
  tampered action_execute (one write before the raise)  -> False   (gate has teeth)

install_pack guard binding (AST):
  real source                       True
  guard removed                     False
  guard called on the WRONG object  False

edition runtime parity:
  tampered employee ZIP -> validate_release.py FAIL
```

**Safe-disabled contract, every entry point exercised live:**

```
$ ai action-execute W --batch none.json
FAIL - UNAVAILABLE_NO_NATIVE_BROKER: external email and LinkedIn effects are
safe-disabled before authorization, ticket creation or provider contact
$ ai autonomy-skill-install W kairali-rahul-sales-system --runtime claude
FAIL - UNAVAILABLE_NO_TRUSTED_SKILL_LOADER: ... before a lock, download, staging
directory or runtime change
$ ai install-skill kairali-rahul-sales-system --runtime claude
FAIL - UNAVAILABLE_NO_HUMAN_PRESENCE_AUTHORITY: ...
$ cat core/AUTHORITY-REGISTRY.json
{"authorities": [], "schema": "ai-human.effect-authority-registry/v1"}   # exactly empty
```

**Research provenance and injection, re-run against the real validators:**

```
undated REDDIT finding             REFUSED - community research receipts require a source publication or update date
instruction_content_ignored=False  REFUSED - research must record that source instructions were ignored
personal_data_excluded=False       REFUSED - research receipt must exclude personal data
credentialed URL                   REFUSED - research source URL must be a public HTTP(S) URL without credentials
file:// scheme                     REFUSED - research source URL must be a public HTTP(S) URL without credentials
REDDIT channel on non-Reddit host  REFUSED - Reddit research receipt must use a Reddit URL
result_rank 26                     REFUSED - research result rank must be between 1 and 25
extra injected field               REFUSED - research receipt fields differ from the required schema

valid OFFICIAL / dated REDDIT / dated YOUTUBE receipts   ACCEPTED
```

The positives matter as much as the negatives: the loop is not failing closed on
everything, it is discriminating correctly.

**Schedule lifecycle (Requirement 12):**

```
$ ai uninstall W --at-checkpoint
FAIL - remove and visibly verify the external personal-improvement schedule before uninstalling
$ ai suspend W --reason "operator pause"
FAIL - remove and visibly verify the external personal-improvement schedule before suspension
```

`external_improvement_schedule_still_exists` (`:6146`) covers `VERIFIED_ACTIVE`,
`VERIFIED_PAUSED` and the stale-from-either case, and is shared by `suspend`,
`uninstall` and `prepare_downgrade`. Suspend can no longer print "automations: OFF"
over a resumable card.

---

## 3. Verified client benefit

An ordinary client gets, and I confirmed each of these against running code:

- **A cadence they choose, bound to what they can see.** `MONTHLY` or `QUARTERLY` at an
  exact local time and zone; `improvement-schedule-prompt` prints the exact prompt next
  to its SHA-256, and the Scheduled card is only `VERIFIED_ACTIVE` when the pasted
  fingerprint matches. Configuration drift invalidates the old proof instead of
  silently inheriting it.
- **A schedule that cannot lie about time.** Fictional clocks are refused in every mode,
  so the visible card and the recorded next run stay in agreement.
- **Decisions that persist.** A `REJECT` recorded in one quarter survives the retention
  window that deletes its run file, so the assistant does not re-propose the thing the
  client already declined — the single most trust-relevant fix in this release. A dated
  `LATER` is evaluated against the real clock, not a caller-supplied date. And, new
  since round 2, a purged decision can still be reconsidered via
  `improvement-forget DECISION`, so persistence is not permanence.
- **A readable, honest brief.** `IMPROVEMENT-BRIEF.md` ranks opportunities by
  `priority_score`, cites source links, shows dated decision history, and reports
  `Forecast value: Unknown until the owner supplies a baseline`. Once the owner records
  `--baseline-minutes` / `--observed-minutes`, it prints the observed difference and
  `money saved: NOT CLAIMED` — and the closing value-truth line is now conditional, so a
  measured brief no longer contradicts itself.
- **Recovery that works.** Crash journal with a refusal of all other commands until
  `recover-lifecycle`; rollback from a trusted exact release rather than a mutable local
  backup; a reversible uninstall archive; and a hash-inventoried pre-v2.4 downgrade
  export/restore. This remains the strongest part of the release.

---

## 4. Explicit unavailable boundaries

These are refusals in code, structurally enforced by AST checks in the release
validator, not promises in prose:

- **No email or LinkedIn effect.** `action_execute` is a single fixed `raise`
  (`UNAVAILABLE_NO_NATIVE_BROKER`), refusing before authorization, ticket creation or
  provider contact. No path in the runtime contacts an email or LinkedIn provider; the
  only network egress is `api.github.com` for release identity and download.
- **No skill installation or activation.** `install_skill` and `autonomy_skill_install`
  are fixed `raise` bodies (`UNAVAILABLE_NO_HUMAN_PRESENCE_AUTHORITY`,
  `UNAVAILABLE_NO_TRUSTED_SKILL_LOADER`), refusing before any lock, download, staging
  directory or runtime change. `install_pack` cannot place a tree in `.claude`,
  `.codex`, `.agents` or `skills` at any depth, under case folding, NFC normalisation,
  symlinked parents, `..` traversal or Windows trailing-dot/space aliases.
- **No standing effect authority.** `core/AUTHORITY-REGISTRY.json` is exactly
  `{"authorities": [], "schema": ...}` and the validator requires it stay exactly that.
  `validate_autonomy_consent` fails closed with `UNAVAILABLE_NO_TRUSTED_EFFECT_RUNTIME`.
- **No inferred value.** Time saved is owner-measured or `UNKNOWN`. Money saved is never
  claimed, in any code path.
- **No autonomy over the update origin.** `automatic_update_eligible` is `false`; the
  repository is pinned on the CLI, in the manifest and against the worker's installed
  metadata.

The prose matches. I checked the three specific claims round 2 called false —
`docs/UPDATES-ROLLBACK-REMOVAL.md:52` (configured-repository download),
`editions/kairali/START-HERE.md:5` ("v2.4 never installs or activates a skill") and
`core/QUARTERLY-IMPROVEMENT.md:99` (visible future next-run proof) — and all three are
now true of the executable. **The handover does not overrule the code anywhere I
tested; where the two differed in earlier rounds, the code was changed, not the prose.**

---

## 5. Remaining P2 and operational risks

None of these blocks the tag. All are stated so the owner ships with them knowingly.

1. **P2 — the reference pack's own content supplies a `skills/` directory.** The guard
   inspects the *target* path parts, not the resulting tree, so
   `install-pack kairali-company-rollout /project/kit` legitimately produces
   `/project/kit/skills/<name>/SKILL.md` — the same shape that is refused if typed as a
   target (`/project/kit/skills` → `FAIL ... : skills`). This is **not** reachable under
   `.claude` or `.codex`, which are blocked at any depth, and neither Claude Code nor
   Codex discovers a bare `<dir>/skills/`; the product's own discovery root is
   `~/.claude/skills` (`default_skills_root`). So no supported host activates it, and
   the pack is documented as being for "separately approved manual adoption". Worth
   tightening later by refusing a pack whose *tree* reintroduces a discovery part.
2. **P2 — the claimed compatibility floor is wider than the tested one.**
   `release-manifest.json` declares `minimum_supported_version: 2.0.0`, but no test
   installs a configured v2.0.0, v2.1.0 or v2.2.0 worker and updates it; only v2.3.0 is
   exercised. I confirmed `required_managed_targets` returns an identical 8 targets for
   2.0.0/2.1.0/2.2.0/2.3.0 versus 10 for 2.4.0, so the code path is genuinely shared —
   but the evidence for the bottom three quarters of the range is inference, not a run.
3. **P2 — the fleet pilot lane is still hardcoded `daily-email-triage`** (`load_fleet`,
   `:5786`) in a release where email effects are unavailable. Operators must use a lane
   label that names a capability the release refuses to perform. Cosmetic but confusing.
4. **P2 — component commands take no worker mutex.** They have no `worker` positional,
   so `main()`'s serialization does not cover them. Structural, low impact.
5. **P2 — measured saving still starts at zero.** The loop needs a human to run CLI
   steps through an agent and to supply before/after minutes. This is the honest design,
   not a defect, but it means the client sees value only with disciplined use.
6. **Operational — `release-proof.json` must be regenerated before the tag.** The proof
   covers `handover/` (15 files) and this file is the 16th. Writing
   `CLAUDE-FINAL.md` will make `validate_release.py` report
   `release proof is missing payload file: handover/v2.4.0/reviews/CLAUDE-FINAL.md`.
   That is expected and self-inflicted by the review process; regenerate the proof, then
   confirm `validate_release.py .` returns to `PASS` **before** publishing.
7. **Operational — two things remain unverifiable offline.** The live `--latest` GitHub
   identity path (final tag, non-draft, author login, 40-hex commit,
   `verification.verified is True`) was read but never executed against
   `api.github.com`. And protected CI on Ubuntu, macOS and Windows must run on the exact
   candidate commit — my Windows-alias evidence is a macOS simulation of Win32 path
   semantics, not a Windows run. `VET-v2.4.0.md` already holds publication for both;
   that hold must be honoured.

---

## 6. Why this is materially better than v2.3.0

v2.3.0 gave a worker a quarterly improvement loop whose recommendations came from a
model-authored file, whose identity drifted as evidence accumulated, whose "best
opportunity" was chosen by hash, and which had no way to measure whether anything
improved. v2.4.0 changes the kind of thing it is:

- **Evidence replaces assertion.** v2 recommendations are derived from installed
  governed evidence; `improvement_run` refuses a `--recommendations` file on a v2
  config. An untrusted model file can no longer set the agenda.
- **Identity is stable, so decisions mean something.** Signatures are
  `{category, subject_key_sha256}` only, so a decision recorded in March still matches
  the same workflow in July. In v2.3 the thing you rejected changed name as evidence
  grew, which made the whole `PROPOSE / LATER / REJECT` vocabulary decorative.
- **Time is real.** Every run is clamped to the actual clock, so retention, suppression
  and schedule truth cannot be walked forward by a caller-chosen date. v2.3 had no
  equivalent because it had no scheduled execution to protect.
- **Failure is recoverable rather than mixed.** The lifecycle journal, trusted-release
  rollback and the pre-v2.4 downgrade export replace v2.3's mutable local backup, which
  a round-1 finding showed could become rollback authority.
- **The download is the release.** v2.3 had no source-to-archive parity gate; v2.4 has
  one, and round 2's stale-kit P0 proves why it was needed. A future release cannot
  repeat that failure without turning `validate_release.py` red.
- **The boundaries are enforced, not described.** Four fixed-unavailable handlers, an
  exactly-empty authority registry and a target-bound install guard are all checked by
  AST at release time. v2.3 relied on the handlers simply not being called.

The client-visible difference is smaller than the engineering difference, and I want to
be plain about that: this is still a CLI-driven loop that an agent operates on the
user's behalf, and its measured time saving on day one is zero by construction. What
changed is that the things it tells the user are now true, and the things it promises
not to do are things it structurally cannot do.

---

## 7. Review hygiene

```
$ git status --short
35 modified, 9 untracked      # identical to the pre-review snapshot, before and after
```

No product file was edited in this round. `handover/v2.4.0/reviews/CLAUDE-FINAL.md` is
the sole file added. All fixtures are under `/tmp` and no real account, credential,
production provider or live worker data was used. The portal build wrote only
`portal/.next`, which is excluded from tracking and from the release proof.

**No P0 or P1 remains open. Release v2.4.0 after regenerating `release-proof.json` and
completing the protected hosted checks that `VET-v2.4.0.md` already requires.**
