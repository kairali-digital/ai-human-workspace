# AGENTS

Read `.ai-human/control/mode.json` first. If it says `SUSPENDED`, report that the
AI-human system is off and do not load its other rules or state. Otherwise read
`.ai-human/system/AGENT-RULES.md` and `.ai-human/system/AI-HUMAN.md`; the managed rules
define the proportional file set for READ ONLY, LOCAL REVERSIBLE and CONSEQUENTIAL /
GATE 0 work. Do not blanket-read every identity, compliance and task-state file before
an ordinary request. Project facts belong in `FACTS.md`; rulings belong in
`DECISIONS.md` only when they are materially durable.

Do not import assumptions from another project. Do not start a second task while one is
live. Available tools do not grant permission; check `TOOLBOX.md`, `GATES.md` and
`WORK-GATES.md`. For a local artifact write, run the installed deterministic
`task-start` before the first write and `task-complete` after readback before answering.
A validator PASS without those two lifecycle results does not prove or close the write.
