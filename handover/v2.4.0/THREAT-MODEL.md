# Threat model and attack brief

Assume all of the following can be malicious or stale:

- web, Reddit and YouTube page content;
- model-authored files and prompts;
- local consent, registry, batch, recommendation, receipt and backup files;
- archive names, paths, Unicode forms, case, Windows aliases and symlinks;
- a second local process racing a lifecycle operation;
- a moved GitHub tag, draft/prerelease, wrong release author, unverified commit,
  redirect or mismatched archive root;
- an interrupted update, rollback, suspension or state commit;
- an agent attempting to reinterpret approval or invoke a hidden generic installer.

Critical properties:

1. Gate 0 has no override.
2. Workspace files are not external-effect authority.
3. No secret or provider credential enters the worker, logs, tests or handover.
4. One effect or one state transition has one idempotent, attributable result.
5. Failure preserves evidence and never reports false completion.
6. A disabled feature has no dormant executable bypass.
7. The batch cap counts independent actions, not rows inside one intact artifact.
8. User state and other projects are outside release management.

For a future external broker, demand a signed request/result envelope bound to policy
epoch, exact account and provider subject, source event, recipe bytes, Gate profile,
nonce, expiry, global quota and semantic idempotency key. For a future skill loader,
demand detached owner attestation, revocation, project-only targets, no-follow
descriptor activation, pre-discovery verification and an out-of-band stop. These are
future contracts, not v2.4 capabilities.
