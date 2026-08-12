# Your prompts — Deepu

## Your Iron Man mission

> You are learning to wear Codex like an Iron Man suit. You provide the mission and judgment. Codex performs approved work through a controlled autonomous loop.

Your mission is one ruled website-port task after the inventory and first-site gates are satisfied. You choose and approve the task. Codex audits, ports, tests and records proof inside the Web lane. Nothing goes live without the required human gate.

**Your list:** Kairali Domain Register. Brochure sites port. Shops and booking sites stay on WordPress. Blogs are a later run.
**Where it is:** https://docs.google.com/spreadsheets/d/1CdGnvkScfZhraQrFJq2oLef3VF2xcWmwXnbMoQ9mGX4/edit
**Open rows on your name today:** 263

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

## 1. Confirm the ruled site (only after Sunaj's inventory sheet exists)

The standing sort is already ruled: brochure sites port; shops, booking and membership sites stay on WordPress; blogs wait for a later run. Do not reopen that decision. Abilash rules which specific site is first.

```
Read agents/web/AGENTS.md, agents/web/BRIEF.md and the current Web-lane state.
Confirm that Sunaj's inventory exists and name the one brochure-site task Abilash has ruled live.
If no site is ruled live, stop and record the missing owner decision. Change nothing.
```

## 2. Clone the one ruled site

Clone engine: `github.com/JCodesMore/ai-website-cloner-template` — MIT, free.
It runs inside Codex. Codex drives a browser against the live site and reads the real
CSS off the page. It does not guess. You do not type a slash command.

```
Open the approved clone tool inside Codex for the one ruled URL. Show me the target URL and ask me to confirm it before you start.
```

Then:

```
Tell me what the clone could not copy, and what I have to rebuild by hand.
Flag anything using GSAP or WebGL — the cloner is unreliable on motion.
```

## 3. Wrap the engine into one reusable porter

Build **one porter** that can run repeatedly across the ruled brochure-site list. Do not turn each site into a separate migration project.

```
Wrap the clone engine so that:
- input is a list of domains, not one URL
- output goes into our factory monorepo, never the stock Next.js template
- every default sits in one rules file
- a site that fails goes to a rejects list and the batch keeps running
- re-running the whole fleet needs no manual cleanup
- gates block the deploy, never the port
Give me one report per site, not per page.
```

## 4. Audit the ported site

```
This repo is the new Next.js version of one of our sites.
Audit it and tell me:
- what is broken
- what is slow
- what is missing: SEO titles, meta, alt text, sitemap, forms, redirects
Give me a numbered list. Fix nothing yet.
```

## 5. Fix it, 25 at a time

```
Fix items 1 to 25 from that list. No more than 25.
For each one show me: what it was before, what you changed, how to undo it.
Stop after 25 and wait for me.
```

## 6. Before any site goes live

```
Final check on this site:
- every old URL either survives or 301s to its exact match, in every language
- language slugs unchanged (if German was /de/behandlungen it still is)
- forms submit and land in the right inbox
- all languages render, hreflang present
- GA4, Tag Manager and Search Console live
- visual diff reviewed, old site backed up
Give me go or no-go, and the reason.
```

**Standing answers — do not come to Abilash for these.** Structural fidelity, not
pixel-perfect. Brand tokens beat legacy colours. Content copies across as-is. Tweaks
are limited to tokens, type, spacing and images — anything else is a post-launch task.
Forms are never cloned. Escalate only for: a site that fits no sort rule, a rule that
keeps failing you, or anything touching medical claims, dosage, certification, legal or spend.

---

## Every time you finish

```
I am closing this session.
1. Write my row into COMPLETED_LEDGER.md with the proof attached.
2. Remove that row from OPEN_REGISTER.md.
3. Show Abilash the proof and next safe action. Wait for Abilash to rule the cursor; Codex may record that ruling. Do not overwrite MASTER_CURSOR.md yourself.
4. List anything I left open, with the reason in one line.
Show me all of it before you save.
```

---

## The three rules

1. One task at a time. Say the number out loud before you start.
2. Never more than 25 in one go.
3. Nothing is done without proof. A saved setting is not proof.

**Stuck?** Open `people/SETUP-HELPER.md` and paste its complete message. Begin: **“I am stuck setting up my Kairali AI workspace. Be my Setup Helper.”** The helper performs safe setup work and writes the `OPEN_REGISTER.md` row if a human decision remains.
