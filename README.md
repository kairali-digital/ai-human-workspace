# AI-Human Workspace

One public, versioned operating system for durable Codex or Claude workers across many
companies. The human provides the mission, judgment and approvals. The AI performs
approved work through a controlled loop and records durable state in the worker folder.

## What this repository provides

- a complete starter workspace for one user or specialist;
- company, exact legal entity, operating unit, jurisdiction, user relationship, owner,
  role and purpose parameters without company facts in the shared core;
- separate adapters for Codex (`AGENTS.md`) and Claude (`CLAUDE.md`);
- a confirmed, exact-scope local Gate 0 profile with generated gate/source views;
- durable cursor, register, today, ledger, evidence, facts and decision files plus an
  explicit [`WORKSPACE-MAP.md`](starter/WORKSPACE-MAP.md) defining what belongs where;
- an installer that can also adopt an existing project without overwriting files;
- versioned update, checkpoint, rollback, validation, status, temporary suspension and
  reversible removal with `ACTIVE`, `SUSPENDED` and `UNINSTALLED` proof;
- a zero-command beginner path and an optional Git/CLI path for technical teams;
- release validation, secret checks and lifecycle tests on every pull request.
- an optional, hashed Kairali company bundle with approved role prompts, two governed
  skills and the complete universal homework pack.

## The architecture

```text
Public repository and approved releases
  └── shared system, templates and lifecycle tool
         ↓ install or update
Company A / user worker           Company B / user worker
  ├── .ai-human/system/           ├── .ai-human/system/   updated
  ├── .ai-human/control/          ├── .ai-human/control/  isolated Gate 0 profile
  ├── COMPANY.md                  ├── COMPANY.md          preserved
  ├── GATES.md                    ├── GATES.md            generated and verified
  ├── PARAMETERS.md               ├── PARAMETERS.md       preserved
  ├── ROLE.md                     ├── ROLE.md             preserved
  └── cursor/register/evidence    └── cursor/register/evidence preserved
```

Updates are allowed to manage only the files named in `release-manifest.json`. They do
not manage company facts, role instructions, task state, credentials, evidence or
personal files.

## Start here

- Download exactly one edition: Kairali employees use the Kairali Employee Edition;
  everyone else uses the company-neutral Reusable Edition. Source guides live in
  [`editions/`](editions/).
- New or nontechnical user: [`docs/BEGINNER-SETUP.md`](docs/BEGINNER-SETUP.md)
- Technical user: [`docs/TECHNICAL-SETUP.md`](docs/TECHNICAL-SETUP.md)
- Rollout owner: [`docs/MULTI-COMPANY-ROLLOUT.md`](docs/MULTI-COMPANY-ROLLOUT.md)
- Updates and removal: [`docs/UPDATES-ROLLBACK-REMOVAL.md`](docs/UPDATES-ROLLBACK-REMOVAL.md)
- Kairali complete bundle: [`packages/kairali/README.md`](packages/kairali/README.md)
- Kairali employee update workflow: [`packages/kairali/UPDATE-WORKFLOW.md`](packages/kairali/UPDATE-WORKFLOW.md)
- Three-worker go-live: [`docs/THREE-WORKER-GO-LIVE.md`](docs/THREE-WORKER-GO-LIVE.md)
- Governed capability and fleet-update control plane:
  [`docs/GOVERNED-CAPABILITIES-AND-FLEET.md`](docs/GOVERNED-CAPABILITIES-AND-FLEET.md)

v2.0.2 is the current correction candidate for the held v2.0.1 release. It is
backward-compatible for configured v2.0.0 and v2.0.1 workers and keeps automatic update
eligibility off. A pre-v2 worker still needs the guided exact-scope Gate 0 setup
migration before entering the v2 line. Until every release gate passes, v2.0.2 remains
`LOCAL_BUILD_ONLY`; candidate validation proves that lane while normal public-release
validation rejects it.

Skills are not installed indiscriminately. The Kairali Akshar marketing skill and Rahul
sales-system skill are explicit, role-based options. Platform/system and third-party
skills from a maintainer's computer are not part of this repository.

The public repository is a distribution channel, not a company work repository. Never
commit live user state, customer data, credentials or private evidence here.

GitHub Desktop `Fetch origin` or `Pull origin` synchronizes only the selected repository
checkout. It does not install or update the managed system inside a user worker.
Beginners ask the Setup Helper to run the checked lifecycle at a safe checkpoint;
technical users may run the same lifecycle directly.

The local system and external access are separate. Suspension turns managed rules,
automations and automatic updates off without deleting work. Reversible uninstall
archives the managed system and its active adapters while preserving work. Plugins,
connectors and operating-system permissions must be revoked separately and verified in
a new chat.
