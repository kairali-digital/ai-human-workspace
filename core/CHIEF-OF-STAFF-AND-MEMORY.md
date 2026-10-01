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

The source explicitly selects one governed snapshot by digest with
`portfolio-export-artifact`. It writes a complete JSON artifact inside that source
worker without overwriting an existing file; an identical retry is harmless. Hidden,
private and sensitive paths remain excluded by the ordinary H-55 rules. Snapshots
containing H-54 personal-context pointers are refused by both this exporter and the
exchange intake. The owner must create a separately approved pointer-free snapshot to
use this route; no pointer is silently stripped or promoted.

`chief-portfolio-import-exchange` consumes exactly one JSON attachment in an addressed
CHIEF_MEDIATED STATUS message after explicit H-55 acknowledgement and acceptance.
Delivery alone is insufficient. Intake reuses the current H-55 membership, sender,
route, bundle and receipt validators, requires the relay to remain ACCEPTED, and checks
the governed source export and current source status before the local H-53 transaction.
Expired messages or snapshots, revoked routes or portfolio access, changed identities,
source ownership, unresolved source transactions and capacity violations stop intake.
Cross-company, entity, unit or owner intake additionally requires the exact current
H-55 policy with its separate cross-boundary authorization. The direct local upsert
cannot bypass that requirement. Neither command acknowledges, accepts, dispatches or
completes a transport message on anyone's behalf.

This is the existing same-host local relay trust model: the explicitly selected source
worker must be accessible for current-source verification. H-55's controlled-state
fingerprint at send and H-53's status-source digest are separate domains, not equal
hashes. The retained portfolio item supplies source identity, source recording time,
status and evidence digests; the immutable addressed envelope and local receipts retain
delivery and acceptance provenance. A brief uses these recorded snapshots. It reports
live source status and current route authorization as UNKNOWN because it does not
rescan workers or the relay; freshness expiry surfaces STALE. A new intake must recheck
both current source state and route authority.

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

The owner configures a positive fleet capacity independently of the execution batch
cap. Each intake or memory mutation remains a separate authorized operation. Memory
retains its existing 250-record bound, and each H-53 state file remains bounded to
4 MiB; a size refusal preserves the previous state. Revoked-ID history is bounded by
that storage limit, not by the number of actions allowed in one batch.

New briefs are explicit `CHANGED_ITEMS_PAGE` views, not full portfolio listings. Their
selected changes and explicitly requested handoff sources together respect the current
adaptive cap, never above 25. Worker metadata, fact-change metadata, exceptions and
owner-next effects describe only that selection. Removed keys are explicit; obsolete
keys drain before new additions. Each page reports its remaining change count. A
selected subject's complete current contradiction group stays intact, with at most the
existing 250 memory-record references; those references are evidence, not 250 actions.
Old v1 brief history remains readable. The checkpoint index is bounded by the configured
fleet plus memory capacity across prior/current generations and by the same 4 MiB file
limit. Nothing here raises the batch ceiling or grants a new approval or write authority.

H-55 route revocation prevents future retrieval and intake. Previously accepted local
metadata is retained until the Chief owner uses REVOKE or FORGET; transport revocation
does not claim retroactive erasure of a recipient's records.

## Concurrency, recovery and lifecycle

All H-53 writes require the current worker lease, expected controlled-state hash and
worker operation mutex. Each mutation changes one atomically replaced private JSON
file. A digest-only journal names one reserved, mode-0600 staging path and records the
exact byte count, before/after hashes, worker identity, writer and unrelated-state
hash; it never duplicates private content. Unknown files or links in the private roots
fail closed. `h53-recover` can accept only the exact complete stage, committed bytes or
previous bytes, removes an exact partial stage and refuses unrelated drift. Index repair
proves that only the derived index changed. Each H-53 state file is bounded to 4 MiB.

Exchange intake also holds the source and relay operation mutexes through validation
and commit. A conflicting operation fails for a later retry, with no cross-worker task
write. Once the H-53 journal durably records the validated candidate, ordinary H-53
recovery finishes only its exact bytes and bindings; it does not perform a new import.
A later route revocation does not undo that existing local commit point. Every fresh
intake or retry revalidates the current route, even if its snapshot was already stored.

Artifact export uses an atomic hard-link publication and therefore requires filesystem
hard-link support. An unsupported filesystem fails without publishing partial output.
After a process crash, an identical complete output can be retried; a leftover hidden
temporary file is not a transport artifact and remains subject to the private-path
exclusion. Exported artifacts are owner-controlled copies, not a new private memory
store or an automatically transmitted message.

Memory and Chief roots are never managed by an update. They are included in the shared
pre-v2.4 downgrade export/restore transaction, so an older runtime cannot strand
unrecognized private state. Suspend disables managed H-53 mutations. Revoke purges the
corresponding H-53 content but does not claim secure disk erasure of backups or exports.
