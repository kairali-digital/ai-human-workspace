# Complete Kairali component bundle

This directory contains the approved Kairali-specific layer that sits on top of the
company-neutral AI-human core. It contains no employee live state, credentials, email,
Drive content or private evidence.

## What everyone receives

- `people/` — the approved common, named-role, intern and Setup Helper start prompts;
- `homework/` — the complete fallback homework for any attendee without a named plan;
- the Email Triage and Drive Inventory workers as required, separate read-only projects;
- the optional local LinkedIn Draft worker;
- exact copy-paste prompts, Mac/Windows guide, transcript, captions and narrated video.

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

This kit is the public setup/reference layer, not the live specialist operations
project. A named Shopify, FMS, Web or Monitor prompt may tell the Setup Helper to attach
that employee's approved private project, where the corresponding `agents/` brief and
live state reside. Those private facts and task states are deliberately not copied here.
