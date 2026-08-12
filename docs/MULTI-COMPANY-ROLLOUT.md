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
3. Let the Setup Helper install and validate that worker.
4. Run one harmless read-only task and the session-end ritual.
5. Expand in batches of no more than 25 people.
6. At each checkpoint, record install version, validation result and blocker count.
7. Release shared upgrades centrally; workers check at session start and update only at
   a safe checkpoint.

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
