# Multi-company rollout

## One public core, isolated company work

Use this public repository for shared rules, lifecycle tooling and releases. Do not put
private company profiles or employee state in it.

Each company keeps one approved private profile source containing:

- the company owner and escalation route;
- shared facts and their owning source;
- approved roles and work sources;
- tool and permission boundaries; and
- its Setup Helper wording.

Each employee or specialist receives a separate worker folder. Two workers never write
the same cursor, register, ledger or evidence log.

## Rollout sequence

1. Copy `company-profiles/template` into a private company-controlled location and
   fill only verified facts.
2. Choose one real role and one bounded purpose for a pilot worker.
3. Select only the company components approved for that role. Do not install every
   available skill.
4. Let the Setup Helper install and validate that worker.
5. Give an unmapped employee the universal homework fallback instead of inventing a
   role plan.
6. Run one harmless read-only task and the session-end ritual.
7. Expand in batches of no more than 25 people.
8. At each checkpoint, record core version, component list, validation result and
   blocker count.
9. Release shared upgrades centrally; publish the semantic version and stable portal,
   then announce the exact read-only check prompt to one named batch of at most 25.
10. Workers check at session start, wait for employee approval, and update only at a
    safe checkpoint. The Setup Helper records version, validation, receipt and
    preserved-state proof; Monitor reports missing/deferred/mismatched workers.

## Employee update announcement contract

Every company announcement contains the approved version, a plain-language change
summary, affected layers (core, reference pack, named opt-in skills), the stable portal
and the exact `CHECK FOR [COMPANY] UPDATE` prompt. The announcement is not permission
to overwrite files; the employee still approves `UPDATE NOW` at a safe checkpoint.

GitHub Desktop repository sync is announced separately when an assigned private
repository has new commits. It is never described as installing or updating the public
managed release.

## Access model

- Everyone may read the public core without a paid GitHub seat or individual invitation.
- Only maintainers need write access to the public repository.
- Technical repositories, company profiles, employee state and private evidence stay
  in their existing controlled locations.
- Git knowledge does not grant write authority. Permissions follow the role.

## Supervisors

A supervisor may read worker status and report drift. It does not silently rewrite a
worker's live task. Portfolio automation must operate on read-only summaries unless the
owner explicitly grants a narrower write action.
