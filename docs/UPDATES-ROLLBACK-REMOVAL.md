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

## Temporarily suspend and prove it is off

Paste this into the worker chat:

```text
Temporarily suspend the AI-human system in this project because I want to work without its managed rules. Preserve all project files and external account connections. Disable its managed automations and automatic updates. Then run the read-only state verification and show me SUSPENDED with PASS.
```

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

`RELEASE → ANNOUNCE → READ-ONLY CHECK → EMPLOYEE APPROVAL → NO LIVE TASK OR WRITER → BACKUP → APPLY MANIFEST → VALIDATE → RECEIPT → MONITOR PROOF`

Automatic:

`FIRST DAY 10:00 AM LOCAL → READ-ONLY CHECK → ACTIVE SETTING → RELEASED + BACKWARD-COMPATIBLE → NO LIVE TASK OR WRITER → BACKUP → APPLY MANIFEST → VALIDATE → RECEIPT → MONITOR PROOF`

The lifecycle tool downloads only the configured repository's latest GitHub release,
verifies semantic version and every managed-file hash, and applies only manifest-listed
targets under `.ai-human/`.

Company, owner, role, purpose, facts, decisions, tools, gates, cursor, register, today,
ledger, evidence, automation records, credentials, browser sessions and personal files
are never managed by a release. Private quarterly configuration, schedule proof,
research receipts and read-only reports under `.ai-human/improvement/` are also
preserved.

The scheduled read-only check runs once on the first calendar day at 10:00 AM in the
worker's confirmed local time zone. When that worker's automatic-update setting is
`ACTIVE`, the core may apply without a new employee click only if the release is
immutable, owner-approved, `RELEASED`, hash-verified, explicitly
`BACKWARD_COMPATIBLE`, compatible with the installed version and the worker is idle.
The employee and supervisor still receive the version report and receipt. Any other
case uses the existing `UPDATE NOW` approval path. Company components are checked and
applied separately, so an optional role skill is never installed or upgraded merely
because a core release exists.

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
does not write behind the active session. The deferred worker may retry after it is idle
in the same month. The manual path still waits for a declared checkpoint.

## Rollout proof

The release owner publishes one semantic-version release and the stable portal must
show the same version. The company announcement names the version, change summary,
affected managed layers, stable portal and exact check prompt. Each updated worker
provides `.ai-human/VERSION`, validation `PASS`, an update/component receipt and an
evidence-log reference. A Monitor reads those proofs for the announced employee batch
and reports any missing, deferred or mismatched worker; it never rewrites worker state.

## Rollback

Before every manual or automatic update, the current managed files are copied to a unique
`.ai-human/backups/<old>-before-<new>-<UTC timestamp>/` folder. A failed local validation restores that backup
automatically. A deliberate rollback restores the named old version and verifies that
employee-state hashes did not change.

## Fleet isolation

The automatic fleet path starts with a Daily Email Triage pilot. General workers wait
until the same release passes the pilot. Each fleet batch contains no more than 25
workers. A release-level identity or hash failure stops before any worker changes; a
worker-local failure is isolated and reported while other safe workers continue.

The fleet and worker reports contain worker identity, installed/latest versions, last
check, validator result and controlled status only. They never contain user work.

## Removal

Paste:

```text
Reversibly uninstall the AI-human system from this project. If a live task exists, first show me the checkpoint needed and wait. Preserve every project and work-state file. Archive the managed .ai-human folder and every active local AI-human adapter. Then verify UNINSTALLED and show me the archive and receipt locations.
```

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
