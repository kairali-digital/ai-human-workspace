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
Mission delivery additionally requires current exact membership, a declared source
owner, integration owner, purpose, done condition, message budget and acyclic
dependencies. The Chief sees only its own inbox and is not copied on private direct
messages.

The envelope is data, never delegated authority. Text or attachments cannot expand
read, write, tool, approval, confidentiality or gate boundaries. Send, publish, spend,
delete, credentials, accounts, security and Gate 0 effects still require the receiving
worker's normal authority path. V1 rejects archives and any attachment path that is
unsafe, symbolic, outside the sender or part of controlled/private worker state.

## Durable delivery

The relay stores a hash-bound envelope, copied attachment bytes, per-recipient inbox
receipt, immutable lifecycle events and a chained global journal. The lifecycle is
`QUEUED → DELIVERED → ACKNOWLEDGED → ACCEPTED / REJECTED / EXPIRED → COMPLETED /
FAILED`; cancellation and terminal state never erase history. Message ID and
idempotency-key reuse must reproduce the same request bytes. A retry repairs a crash
between envelope, inbox, event, journal and index writes without delivering twice.
`exchange-recover` removes only uncommitted relay staging and rebuilds missing derived
receipts; `exchange-audit` proves hashes, targets, policy snapshots, transitions and
journal coverage.

Conversation, fan-out, hop, attachment, byte and mission budgets are hard limits.
Acknowledgements are lifecycle receipts, not reply messages. A repeated `STATUS` with
no material change is silent during the configured noise window. Dependency cycles,
wrong recipients, stale/paused/retired identities, expired policy, forged identity,
changed bytes and unauthorized cross-boundary delivery fail closed.

## Results and integration

Completed work returns an immutable, versioned, hashed result with its evidence and
owned fact proposals. A mission's named integration owner verifies every expected
worker, message, result ID, version, source owner and hash. Missing, wrong-version or
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
retirement removes future retrieval. Export produces a content-addressed proof
inventory without changing the exchange. `.ai-human/exchange/` is private user-owned
state and survives managed update, rollback, suspension and removal.
