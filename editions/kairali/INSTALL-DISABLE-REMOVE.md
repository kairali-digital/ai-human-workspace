# Kairali install, pause, remove and access-revocation guide

An employee can pause or reversibly remove the AI-human system from one local project
without deleting their work. Removing external account access is a separate action.

## Temporarily disable the Abhilash system in this project

Paste:

```text
Temporarily suspend the Kairali AI-human system in this project because I want to work without its managed rules. Preserve all project, company and employee files and all external account connections. Disable its managed automations and automatic updates. Then run the read-only state verification and show me SUSPENDED with PASS. Record the receipt for Monitor; do not ask me to justify the decision further.
```

**DONE WHEN:** the readback says `SUSPENDED`, managed rules and automations `OFF`,
automatic updates `DISABLED`, work files preserved and verification `PASS`.

## Resume later

```text
Resume the Kairali AI-human system in this project. Restore the automatic-update setting that existed before suspension. Then run the read-only state verification and show me ACTIVE with PASS.
```

**DONE WHEN:** the readback says `ACTIVE`, managed rules `ON` and validator `PASS`.

## Reversibly uninstall from this project

```text
Reversibly uninstall the Kairali AI-human system from this project. If a live task exists, first show me the checkpoint needed and wait. Preserve every company, employee and work-state file. Archive the managed .ai-human folder and every active local AI-human adapter. Then verify UNINSTALLED and show me the archive and receipt locations. Do not delete the project folder.
```

**DONE WHEN:** `.ai-human` and active Kairali AI-human adapters are absent, work files
are unchanged, a recoverable archive exists and verification reports `UNINSTALLED`
with `PASS`.

Suspension and uninstall do not disconnect Gmail, Drive, GitHub, LinkedIn, Computer Use
or another account. That separation prevents a local folder operation from silently
changing a company account.

## Revoke plugin, connector or computer access separately

1. Open **Plugins** in ChatGPT and use the **Installed** row.
2. Open the named plugin and select **Uninstall plugin** when available.
3. Ask the Setup Helper to manage the plugin's connector separately and verify that the
   named service is no longer available. Official OpenAI documentation warns that a
   bundled connector can remain connected after plugin uninstall:
   https://learn.chatgpt.com/docs/plugins
4. For Computer Use, open ChatGPT Settings and review Computer Use access. On Mac,
   also open System Settings, then Privacy & Security, and turn off ChatGPT under
   Screen Recording and Accessibility:
   https://learn.chatgpt.com/docs/reference/settings
5. Start a new chat and ask the helper to verify the removed plugin, connector or
   permission cannot be used. A missing button alone is not proof.

Workspace-installed or default plugins may be controlled by the company administrator.
The helper escalates only that access decision; it does not ask for a password or choose
Full access.

## Troubleshooting

- **Wrong edition:** this folder must be named `KAIRALI-EMPLOYEE-EDITION` and contain
  `workspace/packages/kairali/`. Stop if it does not.
- **ZIP will not open:** on Windows, use **Extract All** instead of opening files inside
  the compressed folder. On Mac, double-click the ZIP once. If extraction still fails,
  preserve it, download once more, and let the Setup Helper compare the visible filename
  and checksum.
- **Codex cannot see AGENTS.md:** confirm the extracted employee working folder, not the
  ZIP or source copy, is the active local project. Official project reference:
  https://learn.chatgpt.com/docs/projects
- **It says local candidate:** stop. Nothing is approved for employee installation yet.
- **Suspend passes but the old chat stays restrictive:** start a new chat in the same
  project and run the SUSPENDED test. The new readback must say the system is off.
- **Uninstall leaves an active adapter:** treat this as a failed uninstall. Use the
  receipt and Setup Helper; do not delete employee files.
- **Plugin removed but service still reachable:** disconnect the connector separately.
- **Need everything deleted:** stop and ask Abhilash. Deleting a worker folder is a
  separate destructive action, not uninstall.

## Exact rescue prompt

At the first failure point, paste the complete Setup Helper message from `START-HERE.md`
and add the exact visible result. The helper gives one action at a time and shows
**DONE WHEN** after each one.
