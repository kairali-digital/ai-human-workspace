# Reusable AI-Human Edition — start here

This edition is for a person or company that is not using a company-specific rollout.
It contains only the reusable workspace, lifecycle controls and generic starter files.

## Install in five visible steps

1. On the website, select **Download the reusable edition**.
   **DONE WHEN:** the ZIP appears in Downloads.
2. Open Downloads. On Mac, double-click the ZIP. On Windows, right-click the ZIP,
   select **Extract All**, then select **Extract**.
   **DONE WHEN:** a folder named `AI-HUMAN-REUSABLE-EDITION` appears.
3. Open the ChatGPT desktop app, sign in and start a new chat.
   **DONE WHEN:** the new chat box is visible.
4. Paste the Setup Helper message below. The helper checks the computer, creates one
   working copy in Documents, identifies the exact company/entity scope and its
   confirmed Gate 0 profile, installs the local workspace and opens that working folder
   in Codex. You do not type a command.
   **DONE WHEN:** Codex is open with the new working folder as its local project.
5. Paste the startup test below.
   **DONE WHEN:** the answer reports `ACTIVE`, names the exact entity, unit,
   jurisdiction, user relationship, owner, purpose and confirmed Gate 0 profile, says
   no task is live, reports the installed version and shows validator `PASS`.

## Setup Helper message

```text
I am setting up the reusable AI-human workspace. I do not know Terminal, Python, Git, GitHub, folders, projects or Codex.

Be my Setup Helper.

1. Work out whether I am on Mac or Windows and check what is already installed before changing anything.
2. Find the extracted AI-HUMAN-REUSABLE-EDITION folder in Downloads and preserve it as the untouched source copy.
3. Ask me one question at a time for the company or group, exact legal entity, operating unit, jurisdictions, one bounded purpose, my relationship to the company, mission owner and compliance owner. If this is personal work with no company, record that explicitly instead of inventing an entity.
4. For that exact scope, research current authoritative sources and draft the local Gate 0 profile. Treat historical charts, old profiles and remembered requirements only as unverified leads. Show each gate, its current source, approval owner and evidence requirement to the compliance owner. Do not report ACTIVE until the profile is CONFIRMED, its unknowns are empty and validation passes. If I need materially different companies, entities or operating units, create separate working folders and profiles; never blend them.
5. Do every safe local setup step you can yourself. Create one working folder in Documents/AI Humans for this one confirmed scope.
6. If a click, login, account choice or permission must be done by me, show me only that one action in plain Mac or Windows words. Wait for me, then verify it worked.
7. Never ask me to use Terminal, PowerShell, Command Prompt, Python, a CLI or type a command.
8. Never ask for, read or repeat my password or one-time code. Start without plugins or external account connections. Keep permissions on Ask for approval; never choose Full access or Always allow.
9. Continue until Codex is open in the working folder and the ACTIVE startup test passes.
10. If you cannot continue safely, tell me the failed step, exact visible error, what you checked and the one action or decision needed.

Do not teach me the machinery unless I ask. Start by checking what I already have.
```

## Startup test

```text
Read the AI-human mode, AGENTS.md, COMPANY.md, PARAMETERS.md, GATES.md, WORK-GATES.md, COMPLIANCE-SOURCES.md, WORKSPACE-MAP.md, MASTER_CURSOR.md and the installed version. Change nothing. Tell me the company or personal scope, exact legal entity, operating unit, jurisdictions, user relationship, mission owner, purpose, Gate 0 profile ID, Gate 0 review date, live task, installed version and whether the system is ACTIVE. Run the read-only state verification and show me PASS or the exact failed check.
```

## What ACTIVE should feel like

If a request crosses a declared boundary, the assistant politely names the exact
boundary, refuses only the conflicting part, preserves any safe part of the mission and
offers the nearest compliant next step or approval path. It must not scold, lecture or
turn a narrow rule into a broad ban. This pattern is off when the system is verified
`SUSPENDED`.

## Already using an older version?

Open the existing working folder in Codex, start a new chat and paste this exact prompt:

```text
CHECK FOR AI-HUMAN UPDATE

Read .ai-human/VERSION and .ai-human/system/SESSION-START.md in this project.
Check only the latest approved semantic-version release from this worker's configured repository.
Do not change any file yet.

Tell me my installed version, the latest approved version, the plain-language changes, whether a live task means the update must wait, exactly which managed files may change and which company/user files stay preserved.
If everything is current, show the version-check proof and stop.
If an update is available, wait for me to say UPDATE NOW. Never ask me to use Terminal, PowerShell, Command Prompt, Python, a CLI or type a command.
```

If the check says the worker is compatible and idle, paste `UPDATE NOW`. The helper
backs up, verifies the release, updates only managed files and validates. A configured
v2.0.0 or held v2.0.1 worker can take v2.1.0 directly. A pre-v2 worker first needs the
guided exact-scope Gate 0 migration.

**DONE WHEN:** the installed version is `2.1.0`, validation is `PASS`, preserved state
is confirmed and a recovery location is shown.

## If anything fails

Do not guess, reinstall repeatedly or delete the working folder. Paste the complete
Setup Helper message again and add the exact visible error. See
`INSTALL-DISABLE-REMOVE.md` for troubleshooting, temporary suspension, resuming,
reversible uninstall and separate account-access removal.

This package is a local candidate until its manifest says `RELEASED` and
`APPROVED_BY_OWNER`. A local candidate must refuse installation outside synthetic
testing.
