Re-open the current repository and all v2.4.0 handover files. Read
handover/v2.4.0/reviews/CLAUDE-ROUND-1.md and every other review in that folder. Inspect
the actual changes made since round 1; do not trust a summary.

Reproduce every former P0/P1, attack the fixes for bypasses and regressions, run the
full relevant suite, and test the five client journeys as executable or precise
file-state walkthroughs. Look especially for security theater, unmeasured-value claims,
schedule configuration that cannot be operated by a beginner, and any path that can
send, install or mutate externally despite the safe-disabled contract.

Write the complete result to handover/v2.4.0/reviews/CLAUDE-ROUND-2.md. Mark each old
finding `RESOLVED`, `NOT RESOLVED` or `REGRESSED`; add new findings; show commands and
results; update the six scores; and state `SHIP`, `HOLD` or `SHIP WITH EXPLICIT SAFE-
DISABLED LIMITS`. Product files must not be edited in this round.
