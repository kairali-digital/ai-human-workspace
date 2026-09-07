# WORKER EXCHANGE

Worker Exchange is an optional, explicitly configured local post room for separate
AI-human projects. It is off when no exchange and worker join proof have been created.
Codex, Claude or another brain may use the same file protocol; the transport, envelope
and receipts—not a shared chat—are the durable source of truth.

Each worker keeps its own identity, Gate 0 profile, private memory, live task and writer
lease. A sender submits immutable data to the transport-owned spool. It never writes a
recipient's worker files. A recipient verifies an addressed envelope while holding its
own lease, then acknowledges and explicitly accepts or rejects it. Acceptance creates
a queued local receipt and never interrupts the live task.

## Routes and authority

Use only `DIRECT`, `CHIEF_MEDIATED` or an exact, expiring `MISSION_ROOM`. Every sender
and recipient is resolved by stable worker ID through the current directory. Delivery
requires one unexpired exact route policy, accepted message type and access class.
Every route policy carries its exact approval reference. A route crossing company,
legal-entity, operating-unit or human-owner boundaries also requires a separate
explicit cross-boundary authorization reference. Immutable revocation records remove
future delivery and retrieval without deleting the historical envelope or audit trail.
Mission delivery additionally requires current exact membership, a declared source
owner, integration owner, purpose, done condition, message budget and acyclic
dependencies. The Chief sees only its own inbox and is not copied on private direct
messages.

The envelope is data, never delegated authority. Text or attachments cannot expand
read, write, tool, approval, confidentiality or gate boundaries. Send, publish, spend,
delete, credentials, accounts, security and Gate 0 effects still require the receiving
worker's normal authority path. V1 rejects archives and any attachment path that is
unsafe, hidden, secret-bearing, symbolic, outside the sender or part of
controlled/private worker state. Secret-bearing request and result fields also fail
before immutable copy.

## Durable delivery

The relay stores a hash-bound envelope, copied attachment bytes, per-recipient inbox
receipt, immutable lifecycle events and a chained global journal. The lifecycle is
`QUEUED → DELIVERED → ACKNOWLEDGED → ACCEPTED / REJECTED / EXPIRED → COMPLETED /
FAILED`; cancellation and terminal state never erase history. Message ID and
idempotency-key reuse must reproduce the same request bytes. A retry repairs a crash
between envelope, inbox, event, journal and index writes without delivering twice.
`exchange-recover` removes only uncommitted relay staging and rebuilds missing derived
receipts. It expires or fails an undelivered envelope before considering delivery and
never recreates an inbox receipt after expiry, route revocation or member retirement.
`exchange-audit` proves hashes, exact nested descriptors, targets, policy snapshots,
actor roles, chronological transitions, idempotency-index integrity and journal
coverage while preserving immutable historical evidence.

Join commits the directory entry, current relay receipt, immutable join history and
worker-local proof as one recoverable identity. Exact retry repairs a matching partial
join and rejects conflicting bytes. `exchange-directory-refresh` renews only the
verification timestamp; old proofs stay in immutable history so already-sent envelopes
remain auditable. `exchange-policy-revoke` is the owner-controlled current-access
off-switch.

ACK, accept/reject, result, integration and leave also use a digest-bound local mutation
record. ACK and decision write the exact prepared intent before exposing the transport
event. Result publication is bound to prepared relay staging and does not expose
`COMPLETED` until the worker-local result proof and lease are durable. If a process
stops at any boundary, the exact command retry or `exchange-local-recover` verifies the
operation, message, event, result, mission and local bytes, refuses unrelated state
changes or a competing next lifecycle command, rolls forward idempotently and refreshes
the writer lease. Rejections have their own local receipt and never overwrite
acknowledgement evidence.

Conversation, fan-out, hop, attachment, byte and mission budgets are hard limits;
fan-out, independent attachments, result items and integration inputs also obey the
H-52 current effective batch cap. Mission messages are counted across the whole mission,
not merely one conversation ID. `ACK`, `REJECT` and `CANCEL` are not sendable payload
types: acknowledgement and rejection are lifecycle receipts, and cancellation remains
reserved until a governed lifecycle implementation exists. A reply may involve only a
sender or recipient from its exact parent envelope. A repeated `STATUS` with no material
change across every substantive field is silent during the configured noise window.
Dependency cycles, wrong recipients, stale/paused/retired identities, expired policy,
forged identity, changed bytes and unauthorized cross-boundary delivery fail closed.

## Results and integration

Completed work returns an immutable, versioned, hashed result with its evidence and
owned fact proposals. Aggregate result artifact bytes share the configured message
limit and duplicate source paths fail closed. A mission declares the exact worker IDs
whose results are required. Its named integration owner rejects missing or extra
workers and verifies every required lifecycle is `COMPLETED`, then checks the exact
message, result ID, version, source owner and hash. Missing, wrong-version or
conflicting facts stop the join and remain visible. Integration proof does not approve
an external effect or overwrite another worker's source of truth.

## Local prototype trust limit

V1 authenticates a submission with a transport receipt bound to the registered join
proof, current worker identity, exact sender state and active writer lease. This proves
what the local relay process validated. It assumes the exchange directory and worker
folders are protected by the operating system from other users. It is not a
cryptographic identity boundary against another process running as the same OS user.
Cross-user, cross-host or remote production transport therefore needs an authenticated
adapter and stronger key custody before enablement.

Pause stops new delivery; resume restores it; archive is read-only. Directory pause or
retirement removes future retrieval. Before downgrade to a pre-v2.4 runtime, the worker
must have inactive directory membership, no unrevoked active route and a transport-read
`exchange-leave` receipt. The leave proof stores a digest and count over the complete
route inventory, so more than 25 historical routes do not become 25 independent
effects. `prepare-downgrade` archives worker-local exchange state while leaving the
external relay untouched; `restore-downgrade` restores and verifies it. Direct rollback
fails while unreadable H-55 local state remains. Export produces a content-addressed
proof inventory without changing the exchange. `.ai-human/exchange/` is private
user-owned state and survives managed update, same-generation rollback, suspension and
removal.
