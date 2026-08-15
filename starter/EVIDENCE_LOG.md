# EVIDENCE LOG

| Task ID | Timestamp UTC | Before state | After state | Verification | Result | Artifact or readback | Undo |
|---|---|---|---|---|---|---|---|

This is the detailed proof file. Record the real readback or artifact and a usable undo
path whenever state changed; never use `changed` or `done` as proof by itself. The
validator screens obvious placeholders; it cannot prove a well-written claim is true.
Use concrete evidence that another person can independently read back.
For a routine local reversible artifact, one sentence confirming the requested content
was read back is enough. Do not calculate hashes, byte counts, receipt paths or
transaction details unless the user requested an integrity check.
