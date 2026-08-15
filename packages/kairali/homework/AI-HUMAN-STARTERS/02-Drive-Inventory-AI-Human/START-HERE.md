# Start here - Drive Master Index AI Human

> You are learning to wear Codex like an Iron Man suit. You provide the mission and
> judgment. Codex performs approved work through a controlled autonomous loop.

This project reads the labels around company Drive files and makes a future-searchable
master index. `DRIVE-INDEX.jsonl` is the AI-readable file of record. One human register
is generated from that exact data: an approved Google Sheet when its connector and
write permission are explicitly confirmed, otherwise `DRIVE-REGISTER.csv`. It does
not open file contents or change Drive. You do not need Terminal, PowerShell, Command
Prompt, Python, Git, GitHub, or VS Code.

## If anything on the screen does not match

Start a new normal ChatGPT chat. Paste the complete message below. Do not shorten it.

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

## The whole job

1. Open this folder as a second, separate local project in the ChatGPT desktop app.
2. Choose Codex and start a new chat inside this Drive project.
3. Paste the first-run prompt below after replacing `[TYPE YOUR NAME]`.
4. Complete only a provider login or account-choice screen yourself. Never paste a
   password or one-time code into chat.
5. Choose `TEST 25` for one practice batch or `FULL DRIVE INDEX` to index everything
   the connected company account can see. Full mode is required for completed company
   homework; test mode proves setup only.
6. Verify the JSONL master, the one human register, summary and cursor all show the
   same generation ID and reconciled counts.
7. After the first successful full index, choose whether to set a weekly refresh. It
   is offered, never silently activated.
8. Stop when Codex shows the index, coverage, schedule decision and proof.

Do not add this folder to the Email Triage project. Each AI human keeps separate memory
and state.

## Paste this exact first-run prompt

```text
My name is [TYPE YOUR NAME]. This is task DRIVE-HW-001.

Read AGENTS.md, AI-HUMAN.md, PARAMETERS.md, MASTER_CURSOR.md, OPEN_REGISTER.md,
TODAY.md, TOOLBOX.md, GATES.md, WORK-GATES.md, DECISIONS.md, AUTOMATIONS.md,
DRIVE-REGISTER-SCHEMA.md and WEEKLY-DRIVE-REFRESH-PROMPT.md.

First, replace “Kairali employee using this copy” with my name in this project's
owner fields only. Do not change the worker's name, purpose, task, limits or gates.

Then check whether the Google Drive app is available under Apps and connected to my
approved company account. If it is missing or disconnected, do not troubleshoot with Terminal
and do not ask for my password. Show me only the next click or login I must do, wait
for me, and verify the connection before continuing.

When the approved company Drive is connected, show both choices in plain language and
ask me one question: “Choose TEST 25 for a 25-item learning sample, or FULL DRIVE INDEX
for the completed company master index.” Wait for my answer. Do not choose for me.

For either choice, read metadata only. Never open or download file contents. Use batches
of no more than 25 items and checkpoint after every batch.

Immediately create or update these local files after I choose a mode. Start one new
generation ID for the selected run and put it in every output. Do not report a
successful run until the outputs are created, reopened and reconciled:
- `DRIVE-INDEX.jsonl`, the normalized AI-readable file of record, with one JSON object
  per stable item ID and these fields: generation_id, item_id, name, file_type,
  owner_or_relationship, owned_or_created_by_me, shared_with_me, shared_by_me,
  modified_time, parent_or_location, sharing_status, web_link, source_scope,
  visibility_status, first_indexed_at_utc, last_seen_at_utc, indexed_at_utc,
  generation_id and review_note;
- one human register generated from that exact JSONL data. If a Google Sheets app is
  already connected and I explicitly approve its write permission and exact target,
  ask whether I want `GOOGLE SHEET` or `LOCAL CSV`. Otherwise create
  `DRIVE-REGISTER.csv` without asking for broader access. A Sheet or CSV uses the same
  fields and generation ID as the JSONL. Never maintain two human registers for the
  same generation;
- `DRIVE-INDEX.md`, with the generation ID, human-register type and locator, approved
  account label without secrets, chosen mode, coverage by source scope, batch count,
  unique item count, owned-or-created count, shared-with-me count, shared-by-me count,
  overlap count, unknown-relationship count, duplicate count, unavailable fields,
  added/updated/unchanged/unknown counts, last successful refresh time and a
  plain-language guide for asking Codex or Claude to find a file later; and
- `DRIVE-INDEX-RECEIPT.json`, with the same generation ID, mode, selected human-register
  type and locator, its readback generation/row count/time, source-scope coverage and
  all relationship and refresh counts; and
- `DRIVE-INDEX-CURSOR.json`, with the same generation ID, chosen mode and counts,
  current source scope, last reconciled batch, connector next-page state when safely
  available, last successful refresh and exact next action. Never store a password,
  one-time code or access token.

Use the connector's stable item ID to upsert the JSONL file of record and prevent
duplicates. If a saved page cursor expires or a supported change feed is unavailable,
restart a bounded source-scope scan and skip or update item IDs already present in
`DRIVE-INDEX.jsonl`. Do not delete a record merely because it is temporarily invisible;
retain it and mark visibility `NOT SEEN THIS RUN — VERIFY`.
Use UNKNOWN for every unavailable value instead of a guess. Use HUMAN REVIEW for titles
or metadata that point to medical, dosage, certification, legal, spend,
credentials, banking, personal HR or other highly sensitive material; do not open them.

If I choose TEST 25, index up to 25 recently modified or recently viewed items, label
the result TEST 25 COMPLETE — FULL DRIVE NOT INDEXED, then stop.

If I choose FULL DRIVE INDEX, enumerate every page the connector exposes for all
visible scopes it supports: owned or created by me, shared with me, shared by me when
that relationship is available, and visible shared drives. Work in batches of no more
than 25. After each batch, save the JSONL file, regenerate or update the one human
register, reopen both registers, reconcile them, then advance the cursor and save the
summary, state files and evidence. Continue automatically inside this approved task.
If the session must end, validate the workspace and leave the cursor ready so a new
session resumes without starting over.
Call the result complete only when every supported scope has no next page. Record any
scope the connector cannot expose as UNKNOWN — CONNECTOR COVERAGE GAP; never claim it
was scanned.

After the selected mode finishes, reopen `DRIVE-INDEX.jsonl`, parse every non-empty
line, count its objects and unique item IDs, and reject malformed JSON or duplicate
IDs. Reopen the selected human register and count its non-header data rows. For a
Google Sheet, read back the exact approved sheet range; for CSV, reopen
`DRIVE-REGISTER.csv`. Compare both readbacks with `DRIVE-INDEX.md` and
`DRIVE-INDEX-RECEIPT.json` and `DRIVE-INDEX-CURSOR.json`. The generation ID, unique total and relationship,
overlap/unknown and added/updated/unchanged totals must agree everywhere. Missing,
empty, malformed or disagreeing output fails closed and the cursor does not advance.
Relationship flags use TRUE, FALSE or UNKNOWN only; one item may be true in more than
one relationship, so never add relationship counts as if they were unique items.
Run `validate_drive_register.py`. If it fails, report `FAILED — REGISTER NOT READY`,
preserve the prior successful cursor and keep the task open.

Put this exact sentence in DRIVE-INDEX.md: “No Drive file content was opened or
downloaded, and no Drive item was created, edited, renamed, moved, shared, unshared,
deleted or organized.”

After the first successful `FULL DRIVE INDEX`, offer a weekly refresh; do not activate
one silently. Ask whether I choose `SET WEEKLY REFRESH` or `NOT NOW`. If I choose it,
ask one schedule question for my day, exact local time within my preferred window and
time zone. Suggest Sunday night as a cadence, but invent no time. Create one recurring
automation named “Weekly Drive Index Refresh — [MY NAME]” against this exact project,
using `WEEKLY-DRIVE-REFRESH-PROMPT.md`. Verify its card, day, time, time zone, project
and prompt, then record the matching `ACTIVE` row in `AUTOMATIONS.md`. Explain that it
runs only while the computer is awake, ChatGPT is running, this folder is available
and connector approvals still work. Show me how to pause, edit or remove its visible
automation card. If I choose `NOT NOW`, record `NOT ENABLED BY CHOICE`.

Read the finished index summary back to me. If it passes the task's exit evidence,
update the ledger, register, cursor, today file and evidence log. Then validate this
workspace.
```

## Done when

- `DRIVE-INDEX.jsonl`, one selected human register, `DRIVE-INDEX.md`,
  `DRIVE-INDEX-RECEIPT.json` and `DRIVE-INDEX-CURSOR.json` are visible and non-empty.
- Both registers were reopened; JSONL object/unique-ID count and Sheet or CSV data-row
  count equal the recorded unique totals.
- Generation ID, relationship flags, unique, overlap, unknown and refresh counts are
  explicit and agree everywhere.
- Every processing batch contains no more than 25 items and has a checkpoint.
- Missing facts say `UNKNOWN`; sensitive titles say `HUMAN REVIEW`.
- `TEST 25` clearly says the full Drive was not indexed; `FULL DRIVE INDEX` ends only
  after every supported connector scope has no next page and lists coverage gaps.
- The index says file contents were not opened and Drive was not changed.
- `validate_drive_register.py` and the workspace validator pass.
- After full mode, the employee either verified the weekly automation card or recorded
  `NOT ENABLED BY CHOICE`; an unconfirmed schedule is never called active.

Mark this worker **LIVE FOR ME** only after `FULL DRIVE INDEX` and the final validator
pass. `TEST 25` remains a valid bounded setup proof, but it does not complete the
company homework.

An installation or a connected account by itself is not homework proof. The visible,
reconciled outputs and evidence rows are the proof. The JSONL file may become an
employee-approved metadata source for later Codex or Claude tasks, but every later use
must disclose its coverage and freshness, respect current Drive permissions and ask
separately before opening any file content. It is never a whole-life profile.
