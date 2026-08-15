# Technical setup

Technical users may use Git, GitHub Desktop or an IDE. The repository and release
rules are identical regardless of client.

GitHub Desktop `Fetch origin`/`Pull origin` updates only the selected checkout. It does
not install or update `.ai-human` in another worker, the company reference kit, or an
opt-in skill. Use the lifecycle below after the release is tagged and checked.

## Install a new worker from a checked-out release

First copy `company-profiles/template/GATE-PROFILE.example.json` to a private
controlled location. Fill it for one exact company/group, legal entity, operating
unit, jurisdictions, purpose and user relationship. Every gate must reference a
current authoritative source and name its approval owner and evidence requirement.
Historical charts belong only in `unverified_leads`. The named compliance owner must
confirm the profile; `unknowns` must be empty and the review date current. A materially
different company, entity, unit or jurisdiction gets a separate profile and worker.

```bash
python3 scripts/ai_human.py install "/absolute/worker/folder" \
  --company "Company name" \
  --legal-entity "Exact legal entity" \
  --operating-unit "Exact operating unit" \
  --jurisdiction "Country / state / local jurisdiction" \
  --company-owner "Company owner" \
  --owner "Mission owner" \
  --name "Worker name" \
  --role "Role name" \
  --purpose "One bounded purpose" \
  --user-relationship "employee / owner / contractor / external user / other" \
  --compliance-owner "Confirming person or role" \
  --gate-profile "/absolute/private/gate-profile.json" \
  --worker-id "approved-worker-id" \
  --timezone "confirmed-IANA-time-zone" \
  --supervisor "designated supervisor"
```

Use `--adopt` only when adding the system to an existing project. Adoption creates
missing worker files and never overwrites an existing project file.
`GATES.md` and `COMPLIANCE-SOURCES.md` are deterministic views of
`.ai-human/control/gate-profile.json`; the validator rejects identity mismatch,
unresolved compliance, expired review, profile tampering or hand-edited rendered files.
Task-specific operating locks belong in `WORK-GATES.md`; they may narrow work but never
replace the entity profile.

## Migrate an existing pre-profile worker

Version 2.0.0 is deliberately `SETUP_MIGRATION_REQUIRED`, not automatically
backward-compatible with a worker that has no entity profile. At a real checkpoint,
run the new release's lifecycle with the same exact identity/profile arguments before
applying the managed update:

```bash
python3 scripts/ai_human.py configure-gate-profile "/absolute/existing/worker" \
  --source "/absolute/extracted/released/source" \
  --company "Company name" \
  --legal-entity "Exact legal entity" \
  --operating-unit "Exact operating unit" \
  --jurisdiction "Country / state / local jurisdiction" \
  --purpose "The existing worker's exact bounded purpose" \
  --user-relationship "employee / owner / contractor / external user / other" \
  --compliance-owner "Confirming person or role" \
  --gate-profile "/absolute/private/gate-profile.json" \
  --at-checkpoint
```

The command refuses a live task or writer lease. It archives the old `GATES.md`, strips
its obsolete universal Gate 0 section while preserving task locks in `WORK-GATES.md`,
creates the source/file-map records, binds the profile, validates and prints the
recovery archive. Only then run the normal managed update. Migration releases are never
eligible for automatic update selection.

## Lifecycle

```bash
python3 scripts/ai_human.py status "/absolute/worker/folder"
python3 scripts/ai_human.py validate "/absolute/worker/folder"
python3 scripts/ai_human.py verify-state "/absolute/worker/folder" --expect ACTIVE
python3 scripts/ai_human.py suspend "/absolute/worker/folder" --reason "Owner requested local rules off"
python3 scripts/ai_human.py verify-state "/absolute/worker/folder" --expect SUSPENDED
python3 scripts/ai_human.py resume "/absolute/worker/folder"
python3 scripts/ai_human.py check "/absolute/worker/folder"
python3 scripts/ai_human.py update "/absolute/worker/folder" --latest --at-checkpoint
python3 scripts/ai_human.py rollback "/absolute/worker/folder" --version 1.0.0
python3 scripts/ai_human.py uninstall "/absolute/worker/folder" --at-checkpoint
python3 scripts/ai_human.py verify-state "/absolute/worker/folder" --expect UNINSTALLED
```

`check` is read-only. Run `update` only after the user approves `UPDATE NOW` and a
real checkpoint exists. For an installed Kairali reference kit, compare its
`.ai-human-component.json` version with the latest catalog, then upgrade separately:

Completion proof is the installed version, validation `PASS`, update receipt,
preserved-state result and recovery location. A fetched or pulled commit is not this
proof.

```bash
python3 scripts/ai_human.py install-pack kairali-company-rollout \
  "/absolute/reference-kit/folder" --latest --upgrade --at-checkpoint
```

## Optional company components

```bash
python3 scripts/ai_human.py components --source .
python3 scripts/ai_human.py install-skill kairali-akshar-marketing-science \
  --runtime codex --source .
python3 scripts/ai_human.py install-pack kairali-company-rollout \
  "/absolute/reference-kit/folder" --source .
python3 scripts/ai_human.py remove-pack "/absolute/reference-kit/folder" \
  --at-checkpoint
```

Use `--latest` instead of `--source .` when running the managed lifecycle tool from an
installed worker. A skill upgrade or any component removal requires
`--at-checkpoint`. Removal moves the component to a recoverable archive.

Do not run an update during a live task. A suspended worker defers direct and fleet
automatic updates with `SYSTEM_SUSPENDED`; it does not mutate the installed version.
`--at-checkpoint` is an assertion that the
owner has deliberately reached a safe checkpoint; the tool still checks and preserves
state. Removal moves the installed system and active AI-human adapters to a timestamped
recoverable folder, preserves a pre-existing independent adapter, and does not delete
company or user state.

## Controlled writer and capability lifecycle

These commands are integration surfaces for technical maintainers and Setup Helper;
beginners never type them. Acquire one lease, use its returned expected-state hash for
every controlled write and release it after validation:

```bash
python3 scripts/ai_human.py session-acquire "/absolute/worker/folder" \
  --session-id "session-id" --actor "user"
python3 scripts/ai_human.py state-commit "/absolute/worker/folder" \
  --session-id "session-id" --expected-state-hash "returned-hash" \
  --changes "/absolute/state-change.json"
python3 scripts/ai_human.py session-release "/absolute/worker/folder" \
  --session-id "session-id" --expected-state-hash "new-returned-hash"
```

Capability proposals use `capability-propose`, then `capability-choice` with exactly
`PROPOSE`, `LATER` or `REJECT`. `capability-activate` checks the configured supervisor
and complete proof results. The proposal must cite every active local gate ID; it
cannot substitute a universal or another company's Gate 0. Company scope records
approval for a future release; it does not publish or distribute anything.

`automatic-update` enforces the confirmed local schedule and eligibility contract.
`fleet-update` reads a content-free batch manifest, pilots Daily Email Triage first and
processes no more than 25 workers. The public scheduler adapter is a production concern;
the local candidate accepts a verified local source for deterministic testing only.
Deterministic tests pass `--now-local` with an explicit UTC offset. The production
scheduler adapter must supply the same kind of offset-aware worker-local value for the
confirmed time-zone cohort; the lifecycle command refuses to infer it from the host
clock. This avoids a hidden Windows IANA-database dependency and prevents a host in a
different time zone from silently choosing the wrong calendar window.

Existing idle workers use `configure-control` once after the governed update. It
requires the approved worker ID, confirmed IANA time zone, designated supervisor,
ACTIVE/DISABLED automatic-update setting and a durable approval reference. It refuses
to run during a live task or writer lease and preserves all user state.

## Check what the batch cap counts

Use the read-only planner when an artifact contains many task descriptions and the
batch unit could be misread:

```bash
python3 scripts/ai_human.py batch-plan artifact-upload \
  --units 1 --embedded-entries 150
python3 scripts/ai_human.py batch-plan external-record-write --units 150
```

The first plan preserves one complete artifact; its embedded entries are not batch
units. The second treats every separately created remote record as a unit and returns
batches no larger than 25. `assignment-intake` likewise preserves a complete backlog
without authorizing its execution; use `item-execution` when the listed work is being
performed.

## Contribution flow

Use one task branch. A local-only build runs
`python3 scripts/validate_release.py . --candidate`; a ruled release runs
`python3 scripts/validate_release.py .`. GitHub Actions uses `--ci` to select between
those lanes from the two manifest status fields. Then run
`python3 -m unittest discover -s tests -v`, then open a pull request. A merge is not a
rollout. Users receive only tagged releases.
