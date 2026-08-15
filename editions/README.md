# Distribution editions

The v2.0.2 release produces two separate, deterministic public download archives:

- **Reusable Edition** contains only company-neutral core, starter, lifecycle and
  beginner control guides. Its filenames and readable content are checked for Kairali,
  Abhilash, the legacy `Abilash` misspelling and Ambuj contamination.
- **Kairali Employee Edition** contains the same workspace plus the complete Kairali
  company kit and exact Kairali Setup Helper path.

Both carry `APPROVED_BY_OWNER` and `RELEASED` manifests. Future pre-release builds use
separate `LOCAL-CANDIDATE` filenames and remain `LOCAL_BUILD_ONLY`; building an archive
alone is never an approval or rollout.
