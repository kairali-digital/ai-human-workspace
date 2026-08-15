# WORKSPACE MAP — WHAT IS STORED WHERE

Each kind of durable information has one file of record. Do not duplicate a ruling in
several files and then guess which copy wins.

| File of record | Store here | Do not store here |
|---|---|---|
| `WORKSPACE-MAP.md` | The authoritative map from each durable information type to its one owning file | Task data, duplicated rulings or credentials |
| `COMPANY.md` | Company or group, exact legal entity, operating unit, jurisdictions, company owner, compliance owner and active gate-profile identity | Task progress, credentials or guessed compliance |
| `PARAMETERS.md` | User relationship, worker purpose, scope, task-selection and execution controls | Company facts or task history |
| `ROLE.md` | This worker's responsibilities, inclusions and exclusions | Another worker's live state |
| `.ai-human/control/gate-profile.json` | Machine-readable confirmed Gate 0 profile, exact scope, sources, gates, owners, review date and unresolved-question status | Secrets, case data or unsupported guesses |
| `GATES.md` | Generated human-readable active gates and escalation path | Hand-edited replacement gates; change and reconfirm the profile instead |
| `WORK-GATES.md` | Task-specific Email, Drive, messaging or other operating locks | Company/entity compliance claims or a substitute Gate 0 |
| `COMPLIANCE-SOURCES.md` | Generated current authoritative sources, historical/unverified leads and review due date | Treating an old chart as current authority |
| `FACTS.md` | Verified operational facts with source and verification date | Decisions, gates or unknowns stated as facts |
| `DECISIONS.md` | Owner or compliance-owner rulings, reasons and supersession | Raw evidence or passwords |
| `TOOLBOX.md` | Allowed tools, accounts, permissions and approval boundaries | Credentials or assumption that availability equals permission |
| `AUTOMATIONS.md` | Explicitly approved unattended jobs, schedule, owner, proof and stop rule | Ad hoc tasks or silently enabled jobs |
| `MASTER_CURSOR.md` | The one live task and exact next position | Backlog or completion claims |
| `OPEN_REGISTER.md` | All queued ideas/tasks and their status | Detailed proof artifacts |
| `TODAY.md` | Today's bounded working set and next action | Long-term archive |
| `COMPLETED_LEDGER.md` | Completion index: task, close time, before, after and undo | Completion without evidence |
| `EVIDENCE_LOG.md` | Detailed checks, results and artifact/readback references | Unsupported “done” statements |

`AGENTS.md`, `CLAUDE.md`, `AI-HUMAN.md`, `START-HERE.md` and `READ-ME-FIRST.txt`
are local adapters and onboarding. `.ai-human/system/` contains managed shared rules.
Neither location stores credentials, passwords, one-time codes, private keys or tokens.

For multiple companies or materially different legal entities/operating units, create
separate worker folders and separate confirmed gate profiles. Never blend their state.
