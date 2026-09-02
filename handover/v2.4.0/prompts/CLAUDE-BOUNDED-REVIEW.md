Review AI-Human Workspace v2.4.0 from the actual files in this repository. Do not use
subagents, MCP, network access, browser access or external accounts. Do not run the
full test suite in this pass; Codex supplies that evidence separately. Do not edit any
product file.

Read these handover files first: README.md, PRODUCT-BRIEF.md, REQUIREMENTS.md,
THREAT-MODEL.md, ACTUAL-FILES.md and both CODEX-ROUND-1 review files under
handover/v2.4.0. Then inspect the v2.3.0 diff and the exact implementations of:

- personal-improvement configuration, prompt, research validation,
  recommendations, decisions and time measurement;
- update/download/rollback/recovery, fleet pilot/mutex, suspend/uninstall and
  downgrade export/restore;
- fixed-unavailable external actions and skill installation;
- beginner, public-edition and portal instructions.

Determine independently whether every original P0/P1 is resolved. Check especially
for false completion, mutable files granting authority, compensation failures,
research outside owner scope, decision suppression bypass, misleading user copy and
a path that contacts providers or activates a skill.

Write the review directly to
`handover/v2.4.0/reviews/CLAUDE-ROUND-1.md`. Use `SHIP`, `HOLD`, or
`SHIP WITH EXPLICIT SAFE-DISABLED LIMITS`. For each remaining P0/P1 give the exact
file/function and a minimal reproduction. List resolved original blockers, new P2
risks, client benefit, and honest 0-10 scores for usefulness, time saving, beginner
ease, truthfulness, recovery and security. Maximum 2,500 words. If evidence is
insufficient, say HOLD; never infer success from this prompt.
