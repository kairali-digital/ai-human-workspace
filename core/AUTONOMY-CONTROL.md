# GOVERNED STANDING PERMISSION

> **v2.4 availability:** EMAIL AND LINKEDIN EXTERNAL EFFECTS ARE NOT AVAILABLE.
> This release ships no native credential broker, and the managed authority registry
> is intentionally empty. External schemas are documented future-contract scaffolding
> only; no v2.4 managed workspace file, consent, adapter or command can activate
> sending, replying, unsubscribing, filtering or LinkedIn effects.
> Silent project-skill installation is also unavailable because the hosts do not expose
> a trusted loader hook that can verify bytes before discovery.
> No standing-permission channel executes an effect in v2.4.

Standing permission removes repeated approval prompts only for an exact, owner-reviewed
recipe. It is not blanket autonomy. Gate 0—medical, dosage, certification, legal text
and spend—always stops and has no override.

## Authority boundary

Workspace files are evidence and cache, not the authority for an external effect. A
silent email, unsubscribe or LinkedIn API effect requires an external authority broker
that:

- keeps provider credentials and the authoritative consent outside the project;
- binds the exact provider account, tenant, approved API, recipe version, targets,
  source types, variables, limits, expiry and Gate 0 clearance;
- resolves the immutable provider source event itself instead of trusting a caller ID;
- atomically rejects a duplicate semantic effect in an account-global ledger;
- applies the provider action with the semantic key as its idempotency key; and
- returns provider readback and the matching authority receipt.

The local runtime must stop if the broker receipt, provider-resolved source, exact
content hash, connector subject, policy hash or Gate 0 profile differs. A browser,
Computer Use session or unofficial third-party tool may never automate LinkedIn.
LinkedIn is eligible only through an explicitly approved first-party or partner API
and the same external authority boundary.

## Exact recipe

Consent is one-time but expiring. Each recipe binds one account and channel; exact
actions, targets and source references; a versioned immutable template; an enumerated
set of variable values; exact provider scopes; the external authority receipt or exact
released skill artifact; per-action daily limits; and the current Gate 0, `TOOLBOX.md`
and `WORK-GATES.md` hashes. At most 25 fully rendered effects may exist in a recipe.

Every rendered variant is reviewed before activation. The active compliance or gate
owner records the decision in local evidence, and the external broker holds the
authoritative effect authorization. New content, target, account, scope, source event,
recipe version, provider or connector requires new consent.

## Supervised pilot and future external execution

External channel pilots and execution remain unavailable until a separately shipped
native broker passes OS peer
attestation, remote policy-epoch revocation, provider-owned quota and global-dedup
tests. The runtime refuses `action-execute` before a ticket, lock, journal, socket or
network request exists. It also refuses `autonomy-skill-install` before a lock,
download, staging directory or runtime change exists.

## Project-scoped skills

Silent skill installation never targets a global runtime directory. Codex uses
`.agents/skills/<component>` and Claude uses `.claude/skills/<component>` inside the
worker. The recipe binds repository, released version, component tree SHA-256, runtime,
fixed target and `SKILL_INSTALL` or `SKILL_UPGRADE`. Candidate releases, reference
packs, arbitrary roots, unpinned versions, changed existing trees and downgrades stop.
These constraints define the future contract only. The v2.4 managed `install-skill`
entry point is also disabled because the runtime cannot distinguish human presence
from an agent invocation. The catalog remains inspectable, but activation requires a
future host-controlled human-presence and pre-discovery loader boundary.

Reference-pack copying remains a separate documentation operation. It rejects every
target with a `.agents`, `.claude`, `.codex` or `skills` path component, so a pack's
included `SKILL.md` files cannot cross into current host discovery. Windows
trailing-dot and trailing-space aliases are rejected too. Remote component
retrieval is pinned to the lifecycle release repository and rejects alternate
repositories before network access.

Removing a legacy governed skill does not delete its bytes. It moves the component to
a restricted recoverable archive outside the host's active `skills` directory.

## Stop, inspect and recover

Suspend immediately latches the emergency stop and disables automatic updates. Resume
does not create or activate standing permission. `autonomy-show` reports both unavailable
runtime boundaries without exposing credentials. Any legacy action ticket, result,
lock, attempt or staging file makes v2.4 validation fail; update, rollback and uninstall
also refuse unresolved legacy effect state. Deleting such evidence is never recovery.
