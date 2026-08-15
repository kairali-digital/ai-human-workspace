# Install, pause, remove and revoke access

The local workspace and external account access are separate. Use the smallest action
that matches the result you want.

| Result wanted | Action | What remains |
|---|---|---|
| Stop the workspace rules temporarily | Suspend | Project files and account connections remain |
| Turn the workspace rules back on | Resume | The prior automatic-update setting returns |
| Stop using this workspace system in the project | Reversible uninstall | Work files remain; the managed system and its active adapters move to a recoverable archive |
| Stop an external service from being reachable | Remove the plugin and separately disconnect its connector or operating-system permission | Local project files remain |

## Temporarily turn it off

Paste this in the worker chat:

```text
Temporarily suspend the AI-human system in this project because I want to work without its managed rules. Preserve all project files and external account connections. Disable its managed automations and automatic updates. Then run the read-only state verification and show me SUSPENDED with PASS.
```

**DONE WHEN:** the readback says `SUSPENDED`, managed rules and automations `OFF`,
automatic updates `DISABLED`, project files preserved and verification `PASS`.

## Turn it back on

```text
Resume the AI-human system in this project. Restore the automatic-update setting that existed before suspension. Then run the read-only state verification and show me ACTIVE with PASS.
```

**DONE WHEN:** the readback says `ACTIVE`, managed rules `ON` and validator `PASS`.

## Reversibly uninstall it

```text
Reversibly uninstall the AI-human system from this project. If a live task exists, first show me the checkpoint needed and wait. Preserve every project and work-state file. Archive the managed .ai-human folder and every active local AI-human adapter. Then verify UNINSTALLED and show me the archive and receipt locations.
```

**DONE WHEN:** `.ai-human` and active AI-human adapters are absent, the work files are
unchanged, a recoverable archive exists and state verification reports `UNINSTALLED`
with `PASS`. Do not delete the whole project folder.

## Remove external access separately

Removing this workspace does not disconnect Gmail, Drive, GitHub or another service.
Official OpenAI documentation says to open **Plugins**, use the **Installed** row, open
the plugin and select **Uninstall plugin** when available. It also states that bundled
connectors remain connected until they are managed separately in ChatGPT:
https://learn.chatgpt.com/docs/plugins

For Computer Use, open ChatGPT Settings and review Computer Use access. On Mac, also
open System Settings, then Privacy & Security, and turn off ChatGPT under Screen
Recording and Accessibility. Official settings reference:
https://learn.chatgpt.com/docs/reference/settings

If the visible labels differ, do not hunt through unrelated settings. Ask the Setup
Helper to show one visible click at a time and verify the specific plugin, connector or
computer permission is no longer available. Workspace-managed or default plugins may
require the workspace administrator.

## Troubleshooting

- **The ZIP does not open:** on Windows, use **Extract All** instead of opening files
  inside the compressed folder. On Mac, double-click the ZIP once. If extraction still
  fails, keep the downloaded file, download it once more, and ask the Setup Helper to
  compare the visible filename and checksum. Do not install another utility without approval.
- **Codex cannot see the files:** confirm the extracted working folder, not the ZIP or
  untouched source folder, is the active local project. Official project reference:
  https://learn.chatgpt.com/docs/projects
- **It says local candidate:** stop. The package has not been released and must not be
  installed for real work.
- **Suspend says PASS but restrictions continue:** start a new chat in the same local
  project and run the SUSPENDED verification prompt. A stale chat is not proof.
- **Uninstall says PASS but `AGENTS.md` still loads the system:** run UNINSTALLED
  verification. Any active system adapter is a failed uninstall and must be recovered
  from the receipt, not ignored.
- **The plugin is removed but the account still appears connected:** remove the
  connector separately; plugin uninstall alone does not revoke that connection.
- **You want the project deleted:** stop. Folder deletion is separate and destructive;
  uninstall intentionally preserves work.

At the first uncertain step, paste the complete Setup Helper message from
`START-HERE.md` and add the exact visible error.
