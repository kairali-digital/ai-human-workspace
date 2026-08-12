# AGENTS

## Scope

This repository owns the company-neutral AI-human core, starter templates, lifecycle
tooling and release evidence. Company facts and live employee state do not belong here.

## Working rules

1. One task at a time and one task ID.
2. Keep batches at 25 items or fewer, then checkpoint.
3. Do not put company, customer, employee or project facts in `core/`.
4. Do not add secrets, credentials, browser data, private evidence or live state.
5. An update may change only manifest-listed shared files under `.ai-human/`.
6. Installer adoption never overwrites an existing project file.
7. Removal preserves user state and creates a reversible removed-system folder.
8. Changed is not done: lifecycle tests, release validation and secret-history checks
   must pass before a release.
9. Medical, dosage, certification, legal wording and spend remain human gates.

## Release

Update `core/VERSION` and `CHANGELOG.md`, build the manifest hashes, run the validator
and lifecycle tests, then publish a semantic-version release. A branch or merge is not
an employee rollout; only a versioned release is.
