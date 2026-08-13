# Complete Kairali component bundle

This directory contains the approved Kairali-specific layer that sits on top of the
company-neutral AI-human core. It contains no employee live state, credentials, email,
Drive content or private evidence.

## What everyone receives

- `people/` — the approved common, named-role, intern and Setup Helper start prompts;
- `homework/` — the complete fallback homework for any attendee without a named plan;
- the Email Triage and Drive Index workers as required, separate read-only projects;
- a `TEST 25` or resumable `FULL DRIVE INDEX` choice; full mode enumerates all
  connector-visible metadata in checkpointed batches of at most 25 and creates a local
  future-searchable CSV, summary and cursor without opening or changing Drive files;
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

## Optional governed skills

- `kairali-akshar-marketing-science` — explicit role opt-in for evidence-led marketing;
- `kairali-rahul-sales-system` — explicit role opt-in for observable sales-system work.

These skills are not installed for everyone and never auto-trigger from generic
marketing or sales wording. A Setup Helper installs only the skill named in an approved
role or owner decision.

## Integrity and removal

The `kairali-company-rollout` component installs this entire directory as one reference
kit, so `people/`, `homework/` and both skill packages stay together. The lifecycle tool
validates the complete tree before copying it. Installing the reference kit does not
activate either skill; skill activation is a separate explicit action. Removal moves
the installed kit to a timestamped recoverable folder and deletes nothing.

Live homework worker folders are employee state. Removing the reference homework pack
does not remove a worker that the employee has already created from it.

For every new release, follow [`UPDATE-WORKFLOW.md`](UPDATE-WORKFLOW.md). The company
notice starts a read-only version check. The employee approves `UPDATE NOW`; the Setup
Helper applies the core, reference pack and any named opt-in skill separately at a safe
checkpoint. GitHub Desktop Fetch/Pull synchronizes an assigned repository only and is
not the install/update mechanism.

Completion requires the installed version, validation receipt, preserved-state result
and recovery location. Employee-owned state and copied workers remain preserved.

This kit is the public setup/reference layer, not the live specialist operations
project. A named Shopify, FMS, Web or Monitor prompt may tell the Setup Helper to attach
that employee's approved private project, where the corresponding `agents/` brief and
live state reside. Those private facts and task states are deliberately not copied here.
