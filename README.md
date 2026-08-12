# AI-Human Workspace

One public, versioned operating system for durable Codex or Claude workers across many
companies. The human provides the mission, judgment and approvals. The AI performs
approved work through a controlled loop and records durable state in the worker folder.

## What this repository provides

- a complete starter workspace for one employee or specialist;
- company, owner, role and purpose parameters without company facts in the shared core;
- separate adapters for Codex (`AGENTS.md`) and Claude (`CLAUDE.md`);
- durable cursor, register, today, ledger, evidence, facts and decision files;
- an installer that can also adopt an existing project without overwriting files;
- versioned update, checkpoint, rollback, validation, status and reversible removal;
- a zero-command beginner path and an optional Git/CLI path for technical teams;
- release validation, secret checks and lifecycle tests on every pull request.

## The architecture

```text
Public repository and approved releases
  └── shared system, templates and lifecycle tool
         ↓ install or update
Company A / employee worker       Company B / employee worker
  ├── .ai-human/system/           ├── .ai-human/system/   updated
  ├── COMPANY.md                  ├── COMPANY.md          preserved
  ├── PARAMETERS.md               ├── PARAMETERS.md       preserved
  ├── ROLE.md                     ├── ROLE.md             preserved
  └── cursor/register/evidence    └── cursor/register/evidence preserved
```

Updates are allowed to manage only the files named in `release-manifest.json`. They do
not manage company facts, role instructions, task state, credentials, evidence or
personal files.

## Start here

- New or nontechnical employee: [`docs/BEGINNER-SETUP.md`](docs/BEGINNER-SETUP.md)
- Technical employee: [`docs/TECHNICAL-SETUP.md`](docs/TECHNICAL-SETUP.md)
- Rollout owner: [`docs/MULTI-COMPANY-ROLLOUT.md`](docs/MULTI-COMPANY-ROLLOUT.md)
- Updates and removal: [`docs/UPDATES-ROLLBACK-REMOVAL.md`](docs/UPDATES-ROLLBACK-REMOVAL.md)

The public repository is a distribution channel, not a company work repository. Never
commit live employee state, customer data, credentials or private evidence here.
