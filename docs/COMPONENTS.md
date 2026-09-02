# Optional company components

The shared operating core and company components have different jobs.

- The core is installed in every worker and updates only `.ai-human/` managed files.
- A role-prompt or homework reference pack is copied to a dedicated reference folder.
  Every path component named `.agents`, `.claude`, `.codex` or `skills` is rejected so
  reference material cannot enter a host's automatic skill-discovery tree. Windows
  trailing-dot and trailing-space aliases are also rejected.
- The skill catalog is inspectable, but v2.4 does not activate a managed skill. Both
  silent activation and the generic `install-skill` path fail before runtime change
  until the host provides a trusted pre-discovery loader and human-presence authority.
- Third-party, platform and system skills on a maintainer's computer are never copied
  into a company bundle by default.

## Kairali bundle

`packages/kairali` is one integrity-checked company kit with two separately installable
skills:

1. `kairali-company-rollout` — the complete `people/`, homework and skill-file
   reference kit;
2. `kairali-akshar-marketing-science` — optional governed marketing skill; and
3. `kairali-rahul-sales-system` — optional governed sales-system skill.

The component catalog verifies every listed source tree. Remote component lookup is
pinned to the release repository named by the lifecycle; a caller-supplied repository
is rejected before network access. Reference-pack installation, upgrade and reversible
removal remain available. Governed skill entries are catalog records only in v2.4 and
are not installed by this lifecycle. Removing a legacy governed skill moves it to a
recoverable archive outside the host's `skills` directory.

## Employee-state boundary

The homework package is a reference kit. Once the Setup Helper copies one of its starter
projects into a user's own worker folder, that new folder is user state. A
later component upgrade or removal never manages that worker.
