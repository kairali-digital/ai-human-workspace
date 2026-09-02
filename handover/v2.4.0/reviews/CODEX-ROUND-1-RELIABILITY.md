# Codex round 1 — reliability and compatibility

Reviewer: independent reliability/compatibility critique agent
Initial verdict: **HOLD**

The first review found five P0 release blockers:

1. Real `--latest` requests rejected the canonical GitHub publisher identity.
2. A mutable, self-consistent local backup could become executable rollback authority.
3. A process crash could leave an unrecoverable mixed-version worker.
4. A legitimate v2.3 rollback was rejected by unconditional v2.4-only validation.
5. Mutable prior fleet JSON could forge pilot authority.

Major findings also covered worker mutex bypass in fleet runs, an unusable general-only
pilot progression, no verified fleet `--latest` path, false timezone offsets, runs not
bound to the visible scheduled time, unstable decision suppression, stale/future
research, forged minimal run files, a legacy v1 `PROPOSE` crash, false suspend state,
non-transactional uninstall receipts, Windows/device-name aliases, misleading prompt
text, arbitrary ranking, no measurement path, and no governed downgrade migration.

Required before re-review: pin canonical release identity; use trusted exact releases
for rollback and recovery; add a durable lifecycle journal; make validation
version-aware; require pilot proof from the same batch; acquire every worker mutex;
validate exact zone/time/scope; close schemas and stable signatures; compensate
suspend/uninstall; reject filesystem aliases; and rerun every release gate.

This is a historical finding record. Round 2 must independently reproduce the fixes.
