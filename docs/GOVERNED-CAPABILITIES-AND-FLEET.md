# Governed capabilities and fleet updates

This document describes the v2 control plane, introduced in v2.0.0 and retained in the
current owner-approved v2.3.0 release. v2.0.1 is held after a post-publication
concurrency finding. v2.3.0 is backward-compatible from configured v2.0.0, held v2.0.1,
v2.0.2, v2.1.0 and v2.2.0 workers; a pre-v2 worker still needs the exact-scope setup migration.
Automatic update selection remains disabled. The v2.3.0 manifests are
`APPROVED_BY_OWNER` / `RELEASED`; unapproved pre-release builds use `LOCAL_BUILD_ONLY`,
and the lifecycle refuses to install them.

## One live task, one writer

Before controlled state changes, the Setup Helper or agent acquires one exclusive
session lease. A second session is rejected. The lease records the expected hash of
the cursor, register, today, ledger, evidence and local capability records.

Controlled state changes are staged as one transaction. The lifecycle checks the
lease owner and expected-state hash, applies no more than 25 file changes, validates
the worker and records a receipt. A stale hash stops without overwriting newer state.
An incoherent live task rolls the files back to their before copy. The session releases
the lease only after validation passes.

There is no guessed expiry threshold. If a session is genuinely abandoned, only the
designated supervisor may recover its lease, using the unchanged expected-state hash
and a recorded reason. A changed hash blocks recovery.

## Assignment is not execution

The batch cap follows the independently authorized action, not every row of data the
action happens to contain.

| Authorized action | Batch unit | Example with one file containing 150 issue descriptions |
|---|---|---|
| Artifact upload | Each complete artifact uploaded or committed | Upload the complete file as one unit; verify its hash and entry count |
| Assignment intake | Each supplied backlog/intake artifact stored atomically | Preserve all 150 descriptions, but do not execute them |
| Item execution | Each task actually performed | Work through the descriptions in batches of no more than 25 |
| External record write | Each remote record separately created or changed | Creating separate GitHub Issues is repeated external work capped at 25 per batch |

The system must never truncate, split or partially upload one artifact merely because
its embedded entry count exceeds 25. Conversely, wrapping many external actions in one
instruction or source file does not bypass the cap. Assignment/intake records the whole
backlog; it does not silently authorize execution.

## Gate 0 is an exact local profile

The core contains the Gate 0 process, not a universal list of company rules. Setup binds
each worker to `.ai-human/control/gate-profile.json`, which names one company/group,
exact legal entity, operating unit(s), jurisdiction(s), purpose, user relationship and
compliance owner. Each gate has a unique ID, current authoritative source references,
trigger, stop/escalation action, approval owner and evidence requirement.

`GATES.md` and `COMPLIANCE-SOURCES.md` are generated views of that profile. Validation
fails closed on identity mismatch, unresolved questions, overdue review, profile
tampering or edits to either view. Historical charts and prior profiles may be retained
as unverified leads but cannot support an active gate. Materially different companies,
entities, units, jurisdictions or purposes use isolated profiles and workers.

## From proven process to capability proposal

The system does not count completions and invent a suggestion threshold. The agent
must explain why the process is genuinely repeated and useful, and cite local evidence.
Every proposal includes:

- owner, purpose and source;
- allowed tools and every active gate ID from the worker's confirmed local Gate 0 profile;
- deterministic steps and model-judgment steps;
- proof tests and evidence references;
- semantic version, `NO_SECRETS_OR_CREDENTIALS` policy and retirement rule.

The user sees exactly `PROPOSE`, `LATER` or `REJECT`. `PROPOSE` means “send this
governed candidate to the supervisor”; it does not activate anything. The designated
supervisor must match the worker configuration and every declared proof test must pass
before worker activation or company-reuse approval. Company-reuse approval still does
not publish or distribute the capability; that needs a separately approved release.

## Monthly update control plane

Each configured worker is due for one read-only check on the first calendar day at
10:00 AM in its confirmed IANA time zone. The approved scheduler adapter supplies that
worker-local offset-aware timestamp; the lifecycle command does not infer it from its
host machine. The report contains only worker ID, installed version, latest version,
last check, validator result and one of `CURRENT`,
`UPDATE AVAILABLE`, `UPDATED`, `DEFERRED`, `MISSING`, `MISMATCH` or `FAILED`.

An existing v1.5.1 worker first receives a confirmed exact-scope Gate 0 profile at a
safe checkpoint. `configure-gate-profile` archives the legacy gate file, separates
task locks into `WORK-GATES.md`, creates the file map/source record and validates. It
then receives its approved worker ID, confirmed time zone, designated supervisor and
ACTIVE/DISABLED automatic-update setting only while idle. The migration preserves user
state and records the local decision reference and validator receipts; it never guesses
these settings. Because entering the v2 line requires this setup migration, it is not
an automatic path. The v2.3.0 release remains profile-preserving and explicitly
`BACKWARD_COMPATIBLE` from configured v2.0.0, held v2.0.1, v2.0.2, v2.1.0 and v2.2.0 workers, while its automatic-
update eligibility remains off.

For Mac/Windows portability, scheduling does not assume Python can supply a bundled
IANA time-zone database. The approved scheduler adapter must invoke a confirmed
time-zone cohort with an explicit offset-aware worker-local timestamp. The lifecycle
refuses a missing timestamp, verifies the worker belongs to that cohort and checks the
supplied local calendar day and hour. This keeps daylight-saving calculation with the
approved scheduler adapter instead of guessing from the lifecycle host or a fixed
offset.

Automatic application requires all of the following:

- the worker's automatic-update setting is `ACTIVE`;
- no live task and no writer lease;
- immutable owner-approved `RELEASED` identity and matching file hashes;
- explicit `BACKWARD_COMPATIBLE` classification and a compatible installed version;
- a backup before managed-only changes;
- unchanged user state and settings;
- worker validation after the change.

Failure restores the backup and records the failed update. A live task or writer
returns `DEFERRED`. A deferred worker may retry after it becomes idle in the same
month; a successful monthly check is not duplicated.

## Daily Email Triage pilot and batches

The first fleet phase must contain only workers labelled `daily-email-triage`. General
workers remain deferred until that pilot is due, completes and validates. Every fleet
file contains no more than 25 workers. Later general-only batches require durable proof
that the same release passed the pilot.

A malformed or unverified release is systemic and stops before any worker changes. A
worker-local missing file, identity mismatch, validator failure or update failure is
isolated to that worker; the control plane continues other safe workers and records a
content-free fleet report for Monitor reconciliation.

## Candidate proof journey

The automated tests use synthetic workers only. They prove artifact-versus-execution
batch classification, lease exclusion,
expected-state rejection, transaction rollback, user/supervisor capability gates,
exact entity/jurisdiction Gate 0 binding, profile isolation and tamper evidence,
first-day 10:00 AM local scheduling, idle-only automatic update, state preservation,
Daily Email Triage pilot gating and isolation of a broken general worker.

No test connects email, changes a user worker, publishes a release, deploys a
portal, sends a message or pushes Git history.
