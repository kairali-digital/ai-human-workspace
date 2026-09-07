# CHIEF OF STAFF AND LAYERED MEMORY

H-53 is OFF until the owner explicitly enables memory or designates this worker as a
Chief of Staff. Installation and upgrade create no profile, scan no project and copy no
facts. Codex, Claude or another model is a replaceable reasoning layer; the inspectable
worker files remain the durable source of truth.

## Five memory layers

1. Working memory is the active turn and H-51 checkpoint. It is not silently promoted.
2. Worker-local memory holds only explicit project records owned by this worker.
3. Global shared truth holds only separately approved, company-shareable records at the
   named source owner. “Global” is a scope and access contract, not a filesystem search.
4. The Chief portfolio contains worker ID, purpose, owner, task/status pointers,
   freshness, access class and hashes. It is metadata only.
5. Superseded and retracted history stays at its original owner and is not loaded by
   default. Exact forget physically removes the selected local record.

Every durable memory record has an ID, semantic/episodic/procedural/decision kind,
subject, text, scope, named source owner and worker, provenance, source hash,
sensitivity, access class, confidence, valid time, recorded time, review date, status
and approval reference. A correction creates a new record and closes the previous
record; it never rewrites history silently. Conflicting current claims become disputed.
The derived index can be rebuilt only from the validated authoritative records.

Global publication requires an explicit approval reference, confirmed evidence,
COMPANY_SHARED access and PUBLIC or COMPANY_INTERNAL sensitivity. Private or restricted
content cannot be promoted. A local record cannot grant itself global access. Stale,
expired, retracted and superseded records are excluded from normal retrieval. Secret
patterns and common prompt-injection language fail closed; source content remains
untrusted data and never expands tool or approval authority.

## Read-only Chief

The Chief is a separate worker, not a root account. It receives an exact, target-bound
portfolio snapshot preserved in the source worker's immutable governed export store.
Intake rechecks the current source identity, status files, approved evidence hashes,
review dates and H-54 confirmation. That snapshot contains no arbitrary
source path, credential, local evidence text, direct-message contents or private work
map. H-54 may contribute only a separately approved digest pointer; the Chief does not
receive the private profile. H-55 is the governed transport when the snapshot moves
between projects.

The Chief may read its own curated global memory and accepted portfolio metadata. It
may produce a short project map, exception list, contradiction list, owner-next list
and target-bound handoff proposals. A proposal is marked NOT_SENT and requires H-55 and
the recipient's own acceptance. The Chief cannot edit another worker, see an
unaddressed message, approve itself, inherit credentials, perform an external effect,
cross Gate 0, publish a fact or choose between conflicting source owners.

When the material hashes have not changed, `chief-brief` returns NO_CHANGE and stays
quiet. Freshness expiry itself is material and surfaces STALE. Revoked portfolio access
removes the item immediately and blocks future intake until the owner records a
separate ALLOW approval. If more material changes exist than the current H-52 cap, the
brief advances a hash-bound checkpoint by one bounded batch and leaves the remainder
for the next brief; a durable monotonic sequence keeps same-second and retention-evicted
briefs ordered without truncating or corrupting pending changes.

## Concurrency, recovery and lifecycle

All H-53 writes require the current worker lease, expected controlled-state hash and
worker operation mutex. Each mutation changes one atomically replaced private JSON
file. A digest-only journal names one reserved, mode-0600 staging path and records the
exact byte count, before/after hashes, worker identity, writer and unrelated-state
hash; it never duplicates private content. Unknown files or links in the private roots
fail closed. `h53-recover` can accept only the exact complete stage, committed bytes or
previous bytes, removes an exact partial stage and refuses unrelated drift. Index repair
proves that only the derived index changed. Each H-53 state file is bounded to 4 MiB.

Memory and Chief roots are never managed by an update. They are included in the shared
pre-v2.4 downgrade export/restore transaction, so an older runtime cannot strand
unrecognized private state. Suspend disables managed H-53 mutations. Revoke purges the
corresponding H-53 content but does not claim secure disk erasure of backups or exports.
