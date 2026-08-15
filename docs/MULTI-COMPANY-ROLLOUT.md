# Multi-company rollout

## One public core, isolated company work

Use this public repository for shared rules, lifecycle tooling and releases. Do not put
private company profiles or user state in it. The core defines the confirmation and
enforcement process; it does not define one universal company Gate 0.

Each exact compliance scope keeps one approved private company source and Gate 0
profile containing:

- company/group, exact legal entity, operating unit and jurisdictions;
- the user's relationship, worker purpose, company owner and compliance owner;
- shared facts and their owning source;
- approved roles, work sources, tools and permission boundaries;
- current authoritative compliance sources;
- active gate IDs, triggers, required actions, approval owners, evidence requirements
  and review date; and
- historical materials labelled only as unverified leads.

One company can need several profiles. If two legal entities, operating units,
jurisdictions or purposes have materially different gates, they use separate profiles
and separate workers. No worker borrows another scope's certifications, registrations,
tax status, clinical requirements or other compliance conclusions.

Each user or specialist receives a separate worker folder. Two workers never write the
same cursor, register, ledger or evidence log.

## Rollout sequence

1. Ask the user one question at a time for the company/group, exact legal entity,
   operating unit, jurisdictions, purpose, relationship and compliance owner.
2. Copy `company-profiles/template` into a private company-controlled location. Check
   current authoritative sources for the exact scope. Historical charts and prior
   profiles are leads only.
3. Draft Gate 0 with source IDs, triggers, stop/escalation action, approval owner and
   evidence requirement. The compliance owner confirms it; unknowns must be empty.
4. Choose one real role and one bounded purpose for a pilot worker.
5. Select only the company components approved for that role. Do not install every
   available skill.
6. Let the Setup Helper install and validate that worker. The proof must name the local
   profile ID and review date and show that `GATES.md` and `COMPLIANCE-SOURCES.md`
   match it. Role/task operating locks remain separately in `WORK-GATES.md`.
7. Give an unmapped Kairali employee the universal homework fallback instead of
   inventing a role plan.
8. Run one harmless read-only task and the session-end ritual.
9. Expand in batches of no more than 25 users.
10. At each checkpoint, record core version, component list, profile ID/review date,
    validation result and blocker count.
11. Release shared upgrades centrally; publish the semantic version and stable portal,
    then announce the exact read-only check prompt to one named batch of at most 25.
12. Workers check at session start, wait for user approval, and update only at a safe
    checkpoint. The Setup Helper records version, validation, receipt and preserved-
    state proof; Monitor reports missing/deferred/mismatched workers.

## User update announcement contract

Every company announcement contains the approved version, a plain-language change
summary, affected layers (core, reference pack, named opt-in skills), the stable portal
and the exact `CHECK FOR [COMPANY] UPDATE` prompt. The announcement is not permission
to overwrite files; the user still approves `UPDATE NOW` at a safe checkpoint.

GitHub Desktop repository sync is announced separately when an assigned private
repository has new commits. It is never described as installing or updating the public
managed release.

## Access model

- Everyone may read the public core without a paid GitHub seat or individual invitation.
- Only maintainers need write access to the public repository.
- Technical repositories, company profiles, user state and private evidence stay in
  their existing controlled locations.
- Git knowledge does not grant write authority. Permissions follow the role.

## Supervisors

A supervisor may read worker status and report drift. It does not silently rewrite a
worker's live task. Portfolio automation must operate on read-only summaries unless the
owner explicitly grants a narrower write action.
