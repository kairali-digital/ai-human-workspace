# v2.4.0 adversarial handover

This is a file-based handover for Claude CLI and independent reviewers. The reviewer
must work from the repository files named in `ACTUAL-FILES.md`; no source code or
requirements are pasted into a chat transcript.

Review sequence:

1. Read `PRODUCT-BRIEF.md`, `REQUIREMENTS.md`, `THREAT-MODEL.md` and `ACTUAL-FILES.md`.
2. Execute `prompts/ROUND-1-BRUTAL-REVIEW.md` against the repository.
3. Read the resulting `reviews/CLAUDE-ROUND-1.md` and any Codex review in `reviews/`.
4. After fixes and full evidence, execute `prompts/ROUND-2-VERIFY-FIXES.md`.
5. Execute `prompts/FINAL-CONVERGENCE.md` only when all P0/P1 findings are resolved or
   explicitly held with a product-safe reason.

The review target is the actual repository root, two directories above this folder.
Reviewers may run tests and construct temporary fixtures. They must not use real user
accounts, credentials, production providers or live worker data.
