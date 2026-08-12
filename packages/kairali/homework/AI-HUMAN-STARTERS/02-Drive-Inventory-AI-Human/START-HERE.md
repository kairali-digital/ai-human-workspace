# Start here - Drive Scraper (safe name: Drive Inventory AI Human)

> You are learning to wear Codex like an Iron Man suit. You provide the mission and
> judgment. Codex performs approved work through a controlled autonomous loop.

This project reads the labels around company Drive files and makes a future-searchable
local index. It does not open file contents or change Drive. You do not need Terminal,
PowerShell, Command Prompt, Python, Git, GitHub, or VS Code.

## If anything on the screen does not match

Start a new normal ChatGPT chat. Paste the complete message below. Do not shorten it.

```text
I am stuck setting up my Kairali AI workspace. I do not know Terminal, Python, Git, GitHub, folders, projects or Codex.

Be my Setup Helper.

1. Work out whether I am on Mac or Windows and check what is already installed before changing anything.
2. Do every approved safe setup step you can yourself.
3. If a click, login, account choice or permission must be done by me, show me only that one action in plain Mac or Windows words. Wait for me, then verify it worked.
4. Never ask me to use Terminal, PowerShell, Command Prompt, Python, a CLI or type a command.
5. Never ask for, read or repeat my password or one-time code.
6. Use only my approved company account and company folder.
7. Keep permissions on Ask for approval. Never choose Full access.
8. For the shared Kairali workspace, use GitHub Desktop buttons. For a standalone local project, do not install GitHub unless it is actually needed.
9. Continue until ChatGPT is installed, Codex is open, the correct project is connected, AGENTS.md is visible, approved apps are connected when required, and the startup test passes.
10. If you cannot continue safely, write one OPEN_REGISTER.md row with the failed step, exact error, what you checked, and the one human access or decision needed. Then tell me whether Ambuj or Abilash must help.

Do not teach me how the machinery works unless I ask. Start now by checking what I already have.
```

## The whole job

1. Open this folder as a second, separate local project in the ChatGPT desktop app.
2. Choose Codex and start a new chat inside this Drive project.
3. Paste the first-run prompt below after replacing `[TYPE YOUR NAME]`.
4. Complete only a provider login or account-choice screen yourself. Never paste a
   password or one-time code into chat.
5. Choose `TEST 25` for one practice batch or `FULL DRIVE INDEX` to index everything
   the connected company account can see. Full mode is recommended.
6. Stop when Codex shows the index, coverage report and proof.

Do not add this folder to the Email Triage project. Each AI human keeps separate memory
and state.

## Paste this exact first-run prompt

```text
My name is [TYPE YOUR NAME]. This is task DRIVE-HW-001.

Read AGENTS.md, AI-HUMAN.md, PARAMETERS.md, MASTER_CURSOR.md, OPEN_REGISTER.md,
TODAY.md, TOOLBOX.md, GATES.md and DECISIONS.md.

First, replace “Kairali employee using this copy” with my name in this project's
owner fields only. Do not change the worker's name, purpose, task, limits or gates.

Then check whether the Google Drive plugin is installed and connected to my approved
company account. If it is missing or disconnected, do not troubleshoot with Terminal
and do not ask for my password. Show me only the next click or login I must do, wait
for me, and verify the connection before continuing.

When the approved company Drive is connected, ask me one question: Choose TEST 25 or
FULL DRIVE INDEX (recommended). Wait for my answer. Do not ask another setup question.

For either choice, read metadata only. Never open or download file contents. Use batches
of no more than 25 items and checkpoint after every batch.

Create or update these local files:
- DRIVE-INDEX.csv, with one row per unique Drive item and these columns: item_id, name,
  file_type, owner_or_relationship, modified_time, parent_or_location, sharing_status,
  web_link, source_scope, indexed_at_utc, review_note;
- DRIVE-INDEX.md, with the account label without secrets, chosen mode, coverage by
  source scope, batch count, unique item count, duplicate count, unavailable fields,
  and a plain-language guide for asking Codex to find a file later; and
- DRIVE-INDEX-CURSOR.md, with chosen mode, current source scope, last completed batch,
  the connector's next-page state when safely available, unique item count, and the
  exact next action. Never store a password, one-time code or access token.

Use the connector's stable item ID to prevent duplicates. If a saved page cursor expires,
restart that source scope and skip every item ID already present in DRIVE-INDEX.csv.
Use UNKNOWN for every unavailable value instead of a guess. Use HUMAN REVIEW for titles
or metadata that point to medical, dosage, certification, legal, spend,
credentials, banking, personal HR or other highly sensitive material; do not open them.

If I choose TEST 25, index up to 25 recently modified or recently viewed items, label
the result TEST 25 COMPLETE — FULL DRIVE NOT INDEXED, then stop.

If I choose FULL DRIVE INDEX, enumerate every page the connector exposes for all
visible scopes it supports: owned or created by me, shared with me, shared by me when
that relationship is available, and visible shared drives. Work in batches of no more
than 25. After each batch, save the CSV, summary, cursor, state files and evidence, then
continue automatically inside this approved task. If the session must end, validate the
workspace and leave the cursor ready so a new session resumes without starting over.
Call the result complete only when every supported scope has no next page. Record any
scope the connector cannot expose as UNKNOWN — CONNECTOR COVERAGE GAP; never claim it
was scanned.

Put this exact sentence in DRIVE-INDEX.md: “No Drive file content was opened or
downloaded, and no Drive item was created, edited, renamed, moved, shared, unshared,
deleted or organized.”

Read the finished index summary back to me. If it passes the task's exit evidence,
update the ledger, register, cursor, today file and evidence log. Then validate this
workspace.
```

## Done when

- `DRIVE-INDEX.csv`, `DRIVE-INDEX.md` and `DRIVE-INDEX-CURSOR.md` are visible.
- Every processing batch contains no more than 25 items and has a checkpoint.
- Missing facts say `UNKNOWN`; sensitive titles say `HUMAN REVIEW`.
- `TEST 25` clearly says the full Drive was not indexed; `FULL DRIVE INDEX` ends only
  after every supported connector scope has no next page and lists coverage gaps.
- The index says file contents were not opened and Drive was not changed.
- Codex says the workspace validator passed.

An installation or a connected account by itself is not homework proof. The visible
index files and the evidence rows are the proof. The local index helps Codex find names,
links and metadata later. Opening a file's contents later still requires current Drive
permission and a new approved task.
