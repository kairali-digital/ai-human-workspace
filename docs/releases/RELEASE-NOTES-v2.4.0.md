# AI-Human Workspace v2.4.0

v2.4.0 makes the personal AI-human improve on a useful cadence and makes core updates
safer. It does not pretend that a project file can authorize a silent external action.

## Product changes

- Each worker can choose a monthly or quarterly personal improvement run, exact local
  time, time zone, approved local sources, freshness and retention windows.
- The generated Scheduled-task prompt is versioned and hashed. Active schedule proof
  must match the cadence, prompt hash and offset-aware next run; a changed configuration
  becomes stale until the visible schedule is checked again.
- Approved research can actively cover official sources, Reddit and YouTube. The worker
  records a query, channel, rank, URL and concise claims rather than raw pages. Imports
  are capped at 25 receipts, community findings require a publication date, and source
  instructions are treated as untrusted.
- Repeated-work, friction, conflict, stale-fact and research opportunities are derived
  from governed evidence. The model cannot supply its own recommendation file in the
  v2 path.
- A visible brief shows source coverage, current source links, priority-ranked unresolved
  opportunities, persistent decision history and owner-supplied value measurements.
  It calculates observed minutes from baseline, after-time and occurrence count but
  never invents a money-saving claim.
- `PROPOSE`, dated `LATER` and `REJECT` persist in a compact ledger that ordinary run
  retention does not delete. No run mode can move the decision or retention clock
  forward, and an explicit workflow-signature forget lets the owner reconsider a
  decision whose original run has expired.
  `PROPOSE` creates an inactive capability proposal awaiting the existing supervisor
  proof path; it installs or activates nothing.
- Automatic core updates now serialize direct and fleet worker operations, require a
  pilot in the same batch, keep a crash-recovery transaction journal, restore from a
  trusted tagged release, require the pinned GitHub publisher and verified commit
  signature, reject repository rebinding at both fleet and worker boundaries, and
  provide a recoverable v2-state export before a pre-v2.4 downgrade.
- Scheduled runs require the real current clock plus fresh visible proof of the following
  occurrence. Suspend and uninstall both require the external improvement schedule to
  be visibly removed first.
- Cross-platform validation and both public editions include a hash-pinned first-party
  IANA time-zone prerequisite so Windows applies the same schedule checks as macOS and
  Linux; the Setup Helper handles it for beginners.

## Explicitly unavailable

Email sends/replies, unsubscribe/filter changes and LinkedIn effects do not execute in
v2.4. The authority registry is exactly empty, and `action-execute` stops before local
effect state or provider contact. Silent skill activation and the generic managed
`install-skill` entry point also stop before download, staging or runtime change.
Reference packs are restricted to dedicated documentation folders: targets containing
`.agents`, `.claude`, `.codex` or `skills` are rejected before copying, and remote
component lookup is pinned to this lifecycle's release repository. Windows path aliases
and legacy removal archives inside the active skills root are rejected.

Those effects need security boundaries that do not exist in the workspace runtime: a
native broker holding credentials and authoritative consent outside the project, plus
an authenticated result/readback; or a host-controlled skill loader that verifies a
signed project-scoped artifact before discovery and proves a human is present. Local
Markdown or JSON is not accepted as that authority.

This boundary covers the governed v2.4 lifecycle. It cannot stop an unrelated tool
running as the same operating-system user from being invoked directly; host isolation
and connector controls remain necessary.

## Compatibility and release policy

Configured v2.0.0 through v2.3.0 workers can update at a safe checkpoint with their
local task, evidence, gate, capability, improvement and autonomy-choice state preserved.
Automatic update eligibility remains off for this release. Pre-v2 workers still use
the guided exact-scope Gate 0 setup migration.
