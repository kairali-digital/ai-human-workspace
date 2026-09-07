# WORK GOVERNOR

The configured hard ceiling is a safety boundary, never a throughput target. For each
bounded action, the runtime calculates the effective batch from the minimum of the
owner policy, action risk, provider/API allowance, rollback and evidence capacity,
context budget, computer resources and proven healthy throughput. A missing signal is
stored as `UNKNOWN`; it is never guessed.

States are mechanical:

- `PILOT` uses at most the owner-configured pilot size while evidence accumulates.
- `STEADY` requires the configured number of consecutive, immutable success receipts.
- `BACKOFF` immediately returns to the pilot bound after throttling, partial failure,
  context or resource pressure, ambiguous output, slow evidence or an evidence backlog.
- `HALT` authorizes zero work for Gate 0, uncertain permission, state divergence,
  missing rollback, a wrong target or a non-idempotent retry.

An intact authorized artifact stays one unit even when it contains many entries.
Separately executed items and external writes are separate units. Only an explicit
owner-approved policy version may change the hard ceiling; planning never changes it.
Every executable plan must receive one terminal outcome before another plan is issued.
Fatal rollback and state-divergence outcomes remain halted until a new owner-approved
policy version is active.
