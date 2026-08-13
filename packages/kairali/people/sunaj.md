# Your prompts — Sunaj

## Your Iron Man mission

> You are learning to wear Codex like an Iron Man suit. You provide the mission and judgment. Codex performs approved work through a controlled autonomous loop.

Before this role mission, use `people/ALL-EMPLOYEES.md` to verify the common three-worker setup: Daily Email and Full Drive are required; Saturday LinkedIn is optional. Available in the kit is not live for you until the named proof passes.

Your first mission is the fleet inventory that unlocks Deepu; the FMS audit follows under feature freeze. You judge infrastructure risk and approve access. Codex inventories or audits in bounded batches, records evidence and never changes DNS or releases the freeze on its own.

**Your list:** Fleet inventory first. Then FMS sheets, Google Sheets and Apps Scripts — 200 in all
**Where it is:** https://docs.google.com/spreadsheets/d/19MP_sEVE8JrC2hOMXbhhGDWTGCOcfoVTwLj0M422Di0/edit
**Open rows on your name today:** 357 — the biggest list in the company

Copy these one at a time. Do not run two at once.

---

## Every time you start

Open the ChatGPT desktop app. Choose Codex, choose **Open folder**, and select the Kairali company project. Start a new chat and paste this:

If you cannot reach that screen, do not troubleshoot it yourself. Open `people/SETUP-HELPER.md` and paste its complete message into ChatGPT on the desktop or at `chatgpt.com`.

```
Read MASTER_CURSOR.md, OPEN_REGISTER.md and TODAY.md.
Tell me the one task that is live, and the first three open rows on my name.
Change nothing yet.
```


---

## 0. First job — the fleet inventory. This blocks Deepu.

Nothing in the website port starts until this sheet exists. One row per site:

```
domain | host | SSH y/n | git on server y/n | PHP version | active theme |
shop or booking y/n | languages | approx page count
```

Do this before anything below.

You also own servers and DNS for the port.

---

> **Then: audit only.** Do not fix anything yet. The feature freeze stays until the audit is done.

## 1. Audit one sheet

```
Open this sheet and its Apps Script. Tell me:
- formulas that are broken, or will break
- data that does not match across tabs
- scripts that fail or time out
- anything hard-coded that should not be
Write it as a list. Change nothing.
```

## 2. Log the bugs

```
Turn that list into register rows. One row per bug.
Each row: ID, what is wrong, where, how bad it is, what proves it.
```

## 3. Time it

```
How long did that sheet take, start to finish?
Give me the number. We use it to plan all 200.
```

Ten sheets first. Then we count.
---

## Every time you finish

```
I am closing this session.
1. Write my row into COMPLETED_LEDGER.md with the proof attached.
2. Remove that row from OPEN_REGISTER.md.
3. Update MASTER_CURSOR.md with what is next, or leave it clear for Abilash.
4. List anything I left open, with the reason in one line.
Show me all of it before you save.
```

---

## The three rules

1. One task at a time. Say the number out loud before you start.
2. Never more than 25 in one go.
3. Nothing is done without proof. A saved setting is not proof.

**Stuck?** Open `people/SETUP-HELPER.md` and paste its complete message. Begin: **“I am stuck setting up my Kairali AI workspace. Be my Setup Helper.”** The helper performs safe setup work and writes the `OPEN_REGISTER.md` row if a human decision remains.
