# TOOLBOX

An available tool is not automatically allowed. The read permission below stands while
serving the user's current declared task. The reversible-write permission becomes active
only after deterministic `task-start` returns the current task ID. Add a row for every
other tool or permission.

| Tool | Purpose | Allowed actions | Approval needed | Required proof |
|---|---|---|---|---|
| Worker-local read | Understand the task and inspect files already inside this worker | List, search and read worker files needed for the current task; no account, connector or external access | Standing within the current declared task | Name the source used; no state ritual for a read-only answer |
| Worker-local reversible artifact write | Create or edit the bounded local result the user explicitly requested | After `task-start` returns the current task ID, write and read back ordinary task files inside this worker; preserve unrelated files; exclude `.ai-human/`, controlled state, secrets, security settings, destructive actions and external effects | The user's current explicit request plus successful deterministic task start; a new approval is required for deletion, unrecoverable overwrite or expanded scope | Artifact path, concrete readback and usable undo recorded through deterministic task close before answering |

No task ID means no local write permission. A standalone validator PASS is not task
closure. Use the lifecycle task start/close path for controlled state. Never add routine task
wording to `FACTS.md` or `DECISIONS.md`, and never edit cursor, register, today, ledger
or evidence manually when that path is available.
