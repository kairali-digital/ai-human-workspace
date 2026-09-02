# Kairali managed update workflow

This is the company workflow for keeping managed `.md` and system files current after
go-live. It does not silently overwrite employee work.

## What the release manages

- Core managed files listed in `release-manifest.json` under `.ai-human/`.
- The separately installed Kairali reference kit, when its component receipt shows an
  older version.
- No governed skill: v2.4 keeps catalog skill records inactive and cannot install or
  activate them.

The release never manages `COMPANY.md`, `PARAMETERS.md`, `ROLE.md`, `FACTS.md`,
`DECISIONS.md`, `MASTER_CURSOR.md`, `OPEN_REGISTER.md`, `TODAY.md`,
`COMPLETED_LEDGER.md`, `EVIDENCE_LOG.md`, `GATES.md`, `WORK-GATES.md`,
`COMPLIANCE-SOURCES.md`, `WORKSPACE-MAP.md`, the private gate profile,
`AUTOMATIONS.md`, credentials, browser sessions or personal files. A copied homework
worker is employee-owned state and is not rewritten when the reference kit changes.

## What happens when a release is ready

1. The release owner approves one semantic-version GitHub release. The stable portal
   and GitHub release must show the same version and checked downloads.
2. The company announces that version to one named employee batch of no more than 25.
   The notice includes the stable portal, change summary, affected managed layers and
   the exact check prompt below.
3. Each employee opens each affected existing worker in Codex and starts a new chat.
4. The employee pastes the check prompt. This is read-only and may also run
   automatically at session start when the release is reachable.
5. If a live task exists, the Setup Helper records the available update and defers it.
6. At a safe checkpoint, the employee says `UPDATE NOW`.
7. The Setup Helper verifies the tagged release and hashes, backs up the current
   managed copy, updates only the affected managed layer, validates it and shows the
   receipt. Core and reference kit are handled separately; skill records stay inactive.
8. The employee's evidence log points to the receipt. Monitor reads version, receipt
   and validation proof for the announced batch and reports any missing, deferred or
   mismatched worker. Monitor never rewrites a worker's state.

## Mandatory v2 Gate 0 migration

The first v2 update is not automatic. At a safe checkpoint, the Setup Helper identifies
the exact legal entity, operating unit, jurisdictions, purpose, employee relationship
and compliance owner; checks current authoritative sources; obtains confirmation; then
runs the checkpoint-only Gate 0 configuration. It archives the old generic gate file,
preserves task locks separately in `WORK-GATES.md` and validates the exact profile.
Different entities or materially different units use different worker/profile pairs.
Only after that proof may the managed v2 update run.

## Post-migration automatic path

This local candidate adds a second path without removing the manual one. It is not
active on any employee worker yet.

1. Each configured worker checks once on the first calendar day at 10:00 AM in its
   confirmed local time zone.
2. The worker reports its ID, installed/latest version, last check, validator result
   and controlled status without exposing email or other employee content.
3. If a live task or writer lease exists, report `DEFERRED` and change nothing.
4. If the worker is idle and its automatic setting is ACTIVE, apply only a later released,
   owner-approved, hash-verified, explicitly backward-compatible core update.
5. Back up first, preserve every employee file and setting, validate afterward, issue
   the employee/supervisor receipt and roll back automatically on failure.
6. Start with the Daily Email Triage pilot. Continue only after that pilot passes, in
   verified batches no larger than 25. Isolate a worker-local failure and continue safe
   workers; stop before all workers for a release-level identity or hash failure.

Only a separately approved release and rollout may change this candidate path from
local proof to employee use.

## Exact employee check prompt

```text
CHECK FOR KAIRALI UPDATE

Read .ai-human/VERSION, .ai-human/system/SESSION-START.md and the installed component receipts for this project.
Check only the latest approved semantic-version release from kairali-digital/ai-human-workspace.
Do not change any file yet.

Tell me:
1. my installed core version and the latest approved version;
2. whether my Kairali reference kit or any already approved role skill is older;
3. the plain-language changes;
4. whether a live task means the update must wait; and
5. exactly which managed files may change and which employee-owned files stay preserved.

If everything is current, show the version check proof and stop.
If an update is available, wait for me to say UPDATE NOW. Never ask me to use Terminal, PowerShell, Command Prompt, Python, a CLI or type a command.
```

## Exact approval at a safe checkpoint

```text
UPDATE NOW

Use the Setup Helper. Confirm there is no uncheckpointed live task. Back up the current managed copy, verify the tagged release and hashes, update only the affected managed core/reference-kit/already-approved-skill layer, validate it, and show me the old version, new version, receipt, preserved-state result and undo. If any check fails, restore the prior managed copy and stop.
```

**DONE WHEN:** the worker shows the approved version, validation `PASS`, the receipt,
the preserved-state result and the recovery location. A deferred update is done for the
current session only when its register row and safe checkpoint are visible.

## GitHub Desktop boundary

- `Fetch origin` checks only the repository selected in GitHub Desktop.
- `Pull origin` copies that repository's approved commits to the local checkout.
- For an assigned private Kairali operations repository, beginners use those buttons
  before starting shared repository work and verify the expected branch/commit.
- Fetch/Pull does not install or update `.ai-human` in a separate worker, a separately
  installed Kairali reference kit or a governed skill.
- A standalone local worker does not need GitHub Desktop.
- Technical employees may use Git instead of GitHub Desktop, but the tagged-release,
  checkpoint, backup, manifest, validation and receipt rules remain the same.

## Rollback and removal

If an update fails, the lifecycle restores the previous managed copy automatically.
At a later safe checkpoint, the employee may ask the Setup Helper to roll back to the
named backup version. Removal moves the managed system or component into a timestamped
recoverable archive and deletes no employee work. Deleting an entire worker remains a
separate destructive owner action.
