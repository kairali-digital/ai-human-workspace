# Release process

`CHANGE → REVIEW → VALIDATE → OWNER APPROVES → TAGGED RELEASE → WORKER CHECK → UPDATE`

Use semantic versioning:

- `v1.0.0`: first stable public core;
- `v1.1.0`: backward-compatible capability;
- `v1.1.1`: backward-compatible correction; and
- `v2.0.0`: migration requiring local role or workspace changes.

Before release:

1. Update `core/VERSION`, `CHANGELOG.md`, `release-manifest.json` and
   `component-manifest.json` together.
2. Run the release builder to refresh managed-file hashes, component-tree hashes and
   the exact source-and-portal payload proof. Public validation rejects a missing, stale,
   incomplete or extra proof entry and every symbolic link in the governed payload.
3. Run release validation, lifecycle/component tests, beginner regression and a Git-history secret
   scan.
4. Review the complete diff and public repository contents.
5. Tag exactly the validated commit and create release notes from the changelog.

A local candidate uses `approval_status` and `release_status` equal to
`LOCAL_BUILD_ONLY`, keeps `automatic_update_eligible` false and runs
`python3 scripts/validate_release.py . --candidate`. Normal public-release validation
must reject that tree. Only a new owner ruling may change it to an installable
`APPROVED_BY_OWNER` / `RELEASED` manifest and enable automatic selection after all
production gates pass.

CI runs `python3 scripts/validate_release.py . --ci`. That flag reads the manifest and
selects the local-candidate lane only when both status fields are `LOCAL_BUILD_ONLY`;
otherwise it uses the stricter public-release lane. It never changes either status.

The production portal workflow separately runs the public release validator and
`scripts/validate_portal_deploy.py` before any Vercel command. A local candidate, an
unapproved component manifest or a candidate-only portal label/download stops the job.
Page indexability never counts as release or deployment approval.

Every remote GitHub Action is pinned to an immutable commit SHA. Repository-local
workflow hashes catch accidental or one-sided changes, but a same-commit edit to both a
workflow and its validator is outside that trust boundary. Protected `main`, required
hosted checks, exact-diff review and the owner's tag/release decision are therefore the
external trust root.

The portal application dependency graph excludes the Vercel deployment CLI and runs
`npm audit --omit=dev` before build and deployment. Deployment tooling remains isolated
from the shipped application graph.

Only the repository owner or delegated maintainer publishes a release.
