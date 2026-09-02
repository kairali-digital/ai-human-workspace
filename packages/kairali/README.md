# Complete Kairali component bundle

This directory contains the approved Kairali-specific layer that sits on top of the
company-neutral AI-human core. It contains no employee live state, credentials, email,
Drive content or private evidence.

## What everyone receives

- `people/` — the approved common, named-role, intern and Setup Helper start prompts;
- `homework/` — the complete fallback homework for any attendee without a named plan;
- the Personal Work Memory + Daily Email EA and Drive Index workers as required,
  separate governed projects;
- sourced, dated, employee-controlled work memory with visible show, correct, exclude
  and forget controls, plus a fixed-time daily notification and proposed replies that
  remain unsent;
- a `TEST 25` or resumable `FULL DRIVE INDEX` choice; full mode enumerates all
  connector-visible metadata in checkpointed batches of at most 25 and maintains
  `DRIVE-INDEX.jsonl` as the AI-readable file of record plus one approved Google Sheet
  or otherwise `DRIVE-REGISTER.csv` human register; completion requires reopening both
  registers and reconciling their generation, unique/data-row, relationship, overlap,
  unknown and refresh totals, then verifying or declining the offered weekly refresh;
- the optional Weekly LinkedIn Message Assistant: employee-chosen Saturday time,
  task-scoped Computer control in its local worker, Chrome only on approved
  non-LinkedIn pages, a forced `YOUR TURN ON LINKEDIN` control handoff, manually
  supplied message batches, evidenced tone, numbered drafts and human-only LinkedIn
  access and sending;
- exact copy-paste prompts, Mac/Windows guide, transcript, captions and narrated video.

## What “live” means

The bundle makes all three starters available. It does not activate employee accounts
or schedules. Use `homework/THREE-WORKER-GO-LIVE-CHECKLIST.md` for the final readback.
Email and Full Drive are required; `TEST 25` is Drive setup proof only. Saturday
LinkedIn is optional and may be recorded as `NOT ENABLED BY CHOICE`.

## Governed skill references

- `kairali-akshar-marketing-science` — explicit role opt-in for evidence-led marketing;
- `kairali-rahul-sales-system` — explicit role opt-in for observable sales-system work.

These skill packages remain inactive reference material in v2.4. The lifecycle neither
installs nor activates them because the current hosts do not provide a trusted
pre-discovery loader plus human-presence authority. Generic marketing or sales wording
never activates a skill.

## Integrity and removal

The `kairali-company-rollout` component installs this entire directory as one reference
kit, so `people/`, `homework/` and both inactive skill-reference packages stay together.
The lifecycle tool validates the complete tree before copying it and refuses any target
inside `.agents`, `.claude`, `.codex` or `skills`, including Windows path aliases.
Installing the reference kit cannot place either skill in host discovery. Removal moves
the installed kit to a timestamped recoverable folder and deletes nothing.

Live homework worker folders are employee state. Removing the reference homework pack
does not remove a worker that the employee has already created from it.

For every new release, follow [`UPDATE-WORKFLOW.md`](UPDATE-WORKFLOW.md). The company
notice starts a read-only version check. The employee approves `UPDATE NOW`; the Setup
Helper applies the core and reference pack separately at a safe checkpoint. Governed
skill entries remain inactive in v2.4. GitHub Desktop Fetch/Pull synchronizes an assigned repository only and is
not the install/update mechanism.

Completion requires the installed version, validation receipt, preserved-state result
and recovery location. Employee-owned state and copied workers remain preserved.

This kit is the public setup/reference layer, not the live specialist operations
project. A named Shopify, FMS, Web or Monitor prompt may tell the Setup Helper to attach
that employee's approved private project, where the corresponding `agents/` brief and
live state reside. Those private facts and task states are deliberately not copied here.
