# Start here

This folder is one bounded AI human:

- Company: `{{COMPANY_NAME}}`
- Exact legal entity: `{{LEGAL_ENTITY}}`
- Operating unit(s): `{{OPERATING_UNITS}}`
- Jurisdiction(s): `{{JURISDICTIONS}}`
- Worker: `{{WORKER_NAME}}`
- User relationship: `{{USER_RELATIONSHIP}}`
- Mission owner: `{{OWNER_NAME}}`
- Compliance owner: `{{COMPLIANCE_OWNER}}`
- Role: `{{ROLE_NAME}}`
- Purpose: `{{PURPOSE}}`
- Gate 0 profile: `{{GATE_PROFILE_ID}}` (review due `{{GATE_REVIEW_DUE}}`)

Open this folder as the project in Codex or Claude. Then ask:

```text
Read AGENTS.md, AI-HUMAN.md, COMPANY.md, PARAMETERS.md, ROLE.md, GATES.md, WORK-GATES.md,
COMPLIANCE-SOURCES.md, WORKSPACE-MAP.md, MASTER_CURSOR.md, OPEN_REGISTER.md and
TODAY.md. Tell me the exact legal entity, operating unit, jurisdiction, user
relationship, mission owner, purpose, Gate 0 profile ID and review due date, live task,
installed version and latest approved version. This is a read-only update check.
Change nothing and wait for my approval before applying an update.
```

The safe first answer confirms the configured identity, scope and local Gate 0 profile,
says no task is live, and does not invent tools, permissions, compliance or work.
