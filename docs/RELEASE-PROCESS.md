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
   proof.
3. Run release validation, lifecycle/component tests, beginner regression and a Git-history secret
   scan.
4. Review the complete diff and public repository contents.
5. Tag exactly the validated commit and create release notes from the changelog.

Only the repository owner or delegated maintainer publishes a release.
