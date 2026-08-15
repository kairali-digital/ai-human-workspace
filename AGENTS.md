# AGENTS

## Scope

This repository owns the company-neutral AI-human core, starter templates, lifecycle
tooling and release evidence. Company facts and live user state do not belong here.

## Working rules

1. One task at a time and one task ID.
2. Keep batches at 25 items or fewer, then checkpoint.
3. Do not put company, customer, user or project facts in `core/`.
4. Do not add secrets, credentials, browser data, private evidence or live state.
5. An update may change only manifest-listed shared files under `.ai-human/`.
6. Installer adoption never overwrites an existing project file.
7. Removal preserves user state and creates a reversible removed-system folder.
8. Changed is not done: lifecycle tests, release validation and secret-history checks
   must pass before a release.
9. The core defines the Gate 0 setup, source, confirmation and enforcement process; it
   never hardcodes one company's gates. Each worker uses a confirmed exact-scope local
   profile. Higher-priority platform, security and law boundaries remain outside it.
10. Company components are explicit opt-ins. Never copy every installed local skill or
    let a component update rewrite a user worker created from a template.

## Release

Update `core/VERSION` and `CHANGELOG.md`, build the manifest hashes, run the validator
and lifecycle tests, then publish a semantic-version release. A branch or merge is not
a user rollout; only a versioned release is.
