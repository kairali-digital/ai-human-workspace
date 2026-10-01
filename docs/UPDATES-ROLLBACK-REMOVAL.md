# Updates, suspension, rollback and removal

## Choose the result you actually want

| Result wanted | Action | What remains |
|---|---|---|
| Stop the workspace rules temporarily | Suspend | Work files and external account connections |
| Turn the workspace rules back on | Resume | Work files; the prior automatic-update setting returns |
| Stop using this system in one project | Reversible uninstall | Work files and a recoverable archive |
| Stop Gmail, Drive, GitHub or computer access | Remove the plugin and separately revoke its connector or operating-system permission | Local project files |

Suspension and uninstall act only on the local project. They do not silently revoke an
external account. Plugin uninstall may also leave a bundled connector connected, so
account access has its own verification.

If you are a Kairali employee and the first step does not work, paste this complete
rescue message into your approved ChatGPT chat. The helper checks what is present;
it does not need you to reinstall or use a terminal.

```text
I am stuck setting up my Kairali AI workspace. I do not know Terminal, Python, Git, GitHub, folders, projects or Codex.

Be my Setup Helper.

Before installing, ask me one question at a time for the exact company or group, legal entity, operating unit, jurisdictions, purpose, my relationship to the company, and compliance owner. Check current authoritative sources, treat historical charts only as leads, create a separate confirmed Gate 0 profile for each materially different entity or unit, and do not report ACTIVE while compliance questions remain.

1. Work out whether I am on Mac or Windows and check what is already installed before changing anything.
2. Do every approved safe setup step you can yourself.
3. If a click, login, account choice or permission must be done by me, show me only that one action in plain Mac or Windows words. Wait for me, then verify it worked.
4. Never ask me to use Terminal, PowerShell, Command Prompt, Python, a CLI or type a command.
5. Never ask for, read or repeat my password or one-time code.
6. Use only my approved company account and company folder.
7. Keep permissions on Ask for approval. Never choose Full access.
8. For the shared Kairali workspace, use GitHub Desktop buttons. For a standalone local project, do not install GitHub unless it is actually needed.
9. Continue until ChatGPT is installed, Codex is open, the correct project is connected, AGENTS.md is visible, approved apps are connected when required, and the startup test passes.
10. If you cannot continue safely, write one OPEN_REGISTER.md row with the failed step, exact error, what you checked, and the one human access or decision needed. Then tell me whether Ambuj or Abhilash must help.

Do not teach me how the machinery works unless I ask. Start now by checking what I already have.
```

## Temporarily suspend and prove it is off

Paste this into the worker chat:

```text
Temporarily suspend the AI-human system in this project because I want to work without its managed rules. Preserve all project files and external account connections. Disable its managed automations and automatic updates. Then run the read-only state verification and show me SUSPENDED with PASS.
```

If a visible personal-improvement Scheduled task exists, pause it and verify the card
first. Suspension stops rather than claiming all automation is off while an external
schedule may still run.

**DONE WHEN:** mode is `SUSPENDED`, managed rules and automations are `OFF`, automatic
updates are `DISABLED`, project files are preserved and verification is `PASS`.
Automatic and fleet update checks return `DEFERRED — SYSTEM_SUSPENDED`; they do not
change the worker.

## Resume and prove it is active

```text
Resume the AI-human system in this project. Restore the automatic-update setting that existed before suspension. Then run the read-only state verification and show me ACTIVE with PASS.
```

**DONE WHEN:** mode is `ACTIVE`, managed rules are `ON`, the prior automatic-update
setting is restored and the validator reports `PASS`.

## Governed update flows

Manual:

`RELEASE → ANNOUNCE → READ-ONLY CHECK → EMPLOYEE APPROVAL → DECLARED SAFE CHECKPOINT + NO ACTIVE WRITER → BACKUP → APPLY MANIFEST → VALIDATE → RECEIPT → MONITOR PROOF`

Optional native automatic updates (off until separately configured):

`OWNER-CHOSEN WEEKLY/MONTHLY TIME → VERIFY SCHEDULE + IDLE WORKER → READ-ONLY CHECK → APPROVED IMMUTABLE RELEASE + COMPATIBILITY → BACKUP → APPLY MANIFEST → VALIDATE → RECEIPT → MONITOR PROOF`

The lifecycle tool downloads only the configured repository's final canonical GitHub
release. It verifies the configured owner, semantic version, immutable commit, GitHub
signature status, archive root and every managed-file hash, and applies only
manifest-listed targets under `.ai-human/`.

Company, owner, role, purpose, facts, decisions, tools, gates, cursor, register, today,
ledger, evidence, automation records, credentials, browser sessions and personal files
are never managed by a release. Private improvement, governor, continuity, exchange,
personal-context, Chief/memory and native update-schedule state are also preserved.

Every new installation offers a schedule but leaves it off. The user chooses weekly
or monthly, the day, exact local time, confirmed IANA time zone and retry limit. The
Setup Helper verifies the actual native task before calling it enabled; no default
time or cadence is inferred. It performs the technical steps itself and gives the
user only an unavoidable choice or click. **DONE WHEN:** the selected rule and live
native readback agree, or the schedule is visibly not enabled with the reason given.
If setup cannot verify, use the complete Setup Helper rescue message in
`packages/kairali/people/SETUP-HELPER.md`; never ask an employee to run shell commands.

An opted-in, idle worker may update only from an explicitly immutable, owner-approved,
`RELEASED`, hash-verified, `BACKWARD_COMPATIBLE` release with verified recovery and
state preservation. General workers also require exact-release pilot evidence. Native
ticks stay quiet when not due or already checked; status and receipts remain available
for review. Other cases defer or fail without applying an update. Manual `UPDATE NOW`
approval remains separate. Company components are checked and applied separately, so
an optional role skill is never installed or upgraded merely because a core release exists.

Older externally configured schedules used the first calendar day at 10:00 AM. They
are not silently converted or duplicated. The helper must verify removal of that exact
old schedule before configuring the new native one. Pause, edit, remove and bounded
retry controls remain available. If the operating-system build or time zone changes,
activation fails closed; exact-owned-task safety cleanup remains available where it
can prove removal. See `core/UPDATE-SCHEDULER.md` for platform/runtime requirements.
This local candidate is not approved for installation; real Windows release proof and
final same-byte audits remain pending.

## GitHub Desktop is not the installer

`Fetch origin` checks the selected repository for commits. `Pull origin` copies those
commits into that repository checkout. These buttons are the beginner-safe sync path
for an assigned shared Kairali repository, but they do not update `.ai-human` inside a
separate user worker, a separately installed company reference kit, or an opt-in
skill. The Setup Helper performs those lifecycle actions from the tagged release.

Technical employees may keep a public source checkout current with Git or GitHub
Desktop, but installed workers still change only through the manifest lifecycle.

## Live-task protection

When a live task or writer lease exists, the automatic update reports `DEFERRED`. It
does not write behind the active session. A native occurrence may be explicitly retried
when idle within the owner's retry bound, or left for the next occurrence. The manual
path still waits for a declared checkpoint.

## Rollout proof

The release owner publishes one semantic-version release and the stable portal must
show the same version. The company announcement names the version, change summary,
affected managed layers, stable portal and exact check prompt. Each updated worker
provides `.ai-human/VERSION`, validation `PASS`, an update/component receipt and an
evidence-log reference. A Monitor reads those proofs for the announced employee batch
and reports any missing, deferred or mismatched worker; it never rewrites worker state.

## Rollback

Before every manual or automatic update, the current managed files are copied to a unique
`.ai-human/backups/<old>-before-<new>-<UTC timestamp>/` folder with a closed inventory
and per-file hashes. A failed validation restores that backup while the worker mutex is
held. If the process stops, a persistent transaction journal blocks ordinary work until
`recover-lifecycle` verifies the applied release or restores the exact trusted tagged
pre-transaction release. A deliberate rollback also reads the named trusted release;
mutable backup bytes cannot redefine an old version.

Before crossing a v2.4 or v2.5 private-state boundary, `prepare-downgrade` provides
the governed export required by rollback. It requires an idle task/writer checkpoint,
resolved governor/context/handoff work, and verified removal of schedules and routes
belonging to the exported features. Only incompatible roots move to a hash-inventoried
`.ai-human/downgrade-exports/` archive; compatible v2.4 improvement/autonomy state stays
in place when targeting v2.4. Direct rollback always refuses an active writer. Like a
manual update, rollback with a live task requires the owner's explicit safe-checkpoint
approval (`--at-checkpoint`); it preserves the task and its state. This does not relax
unattended idle-only updates or the fully idle requirement for private-state export.

`restore-downgrade` requires an installed runtime supporting every archived root:
v2.5 for the new memory, Chief, exchange, map, governor, continuity, resource and
native-update state; v2.4 for legacy archives. Upgrade first, then restore. Historical
receipts are not rewritten. Conflicting automation edits or unexpected archive files
are preserved and must be reconciled, never overwritten. Interrupted export/restore
uses `recover-downgrade` to resume or restore the previous state.

## Fleet isolation

The automatic fleet path starts with a Daily Email Triage pilot. General workers wait
until that pilot passes in the same invocation for the same exact release. Prior editable
fleet state is evidence only and never grants authority. Each fleet batch contains no more than 25
workers. A release-level identity or hash failure stops before any worker changes; a
worker-local failure is isolated and reported while other safe workers continue.

The fleet and worker reports contain worker identity, installed/latest versions, last
check, validator result and controlled status only. They never contain user work.

## Removal

Paste:

```text
Reversibly uninstall the AI-human system from this project. If a live task exists, first show me the checkpoint needed and wait. Preserve every project and work-state file. Archive the managed .ai-human folder and every active local AI-human adapter. Then verify UNINSTALLED and show me the archive and receipt locations.
```

If a personal-improvement Scheduled task exists—even if paused—remove it and verify the
visible card first. Uninstall refuses to leave a resumable external schedule behind.
An AI-Human native update task also requires verified removal before uninstall or
downgrade; suspension requires verified pause or removal. Interrupted schedule changes
must be recovered before ordinary work resumes.

Uninstall does not delete the worker. It moves the installed `.ai-human` system and
the local adapters created by the system to
`.ai-human-removed-<UTC timestamp>`, preserves a pre-existing project adapter, and
writes a removal receipt. Company and user files remain where they were. Reinstall
can restore the managed system later.

**DONE WHEN:** `.ai-human` is absent, no active AI-human adapter remains, preserved-work
hashes agree, the recoverable archive and receipt exist, and verification reports
`UNINSTALLED` with `PASS`.

Deleting an entire worker folder is a separate destructive owner action and is not part
of the lifecycle tool.

## Revoke external access separately

In ChatGPT, open **Plugins**, use the **Installed** row, open the named plugin and choose
**Uninstall plugin** when available. Then manage its connector separately and verify a
new chat cannot use that service. Workspace or default plugins may require the
administrator. Official instructions:
`https://learn.chatgpt.com/docs/plugins`

For Computer Use, open ChatGPT Settings and review Computer Use access. On Mac, also
open System Settings → Privacy & Security and turn off ChatGPT under Screen Recording
and Accessibility. Official settings reference:
`https://learn.chatgpt.com/docs/reference/settings`

**DONE WHEN:** a new chat cannot use the named plugin, connector or computer permission.
A missing plugin button alone is not proof that its connector was revoked.

## Troubleshooting

- `SUSPENDED` passes but an old chat remains restrictive: start a new chat in the same
  local project and verify again.
- Uninstall leaves a generated `AGENTS.md`, `CLAUDE.md` or another active adapter: the
  uninstall failed; use the receipt and do not ignore it.
- A custom project `AGENTS.md` remains after uninstall: this is correct when it was
  present before adoption and does not load the AI-human system.
- Plugin removed but the service remains reachable: disconnect the connector
  separately.
- You want all work deleted: stop. That is a separate destructive owner action.

## Optional components

Company role packs, homework reference kits and governed skills are listed in
`component-manifest.json`. They are never silently installed with a core update.

- fresh component install verifies the complete source tree;
- component upgrade requires a declared checkpoint and preserves the previous copy;
- component removal requires a checkpoint and moves the full copy to
  `.ai-human-component-archive`;
- user workers created from a homework template are outside component management.
