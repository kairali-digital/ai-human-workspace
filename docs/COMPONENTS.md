# Optional company components

The shared operating core and company components have different jobs.

- The core is installed in every worker and updates only `.ai-human/` managed files.
- A role-prompt or homework reference pack is copied to a separate folder.
- A governed skill is installed only after the role or owner explicitly names it.
- Third-party, platform and system skills on a maintainer's computer are never copied
  into a company bundle by default.

## Kairali bundle

`packages/kairali` is one integrity-checked company kit with two separately installable
skills:

1. `kairali-company-rollout` — the complete `people/`, homework and skill-file
   reference kit;
2. `kairali-akshar-marketing-science` — optional governed marketing skill; and
3. `kairali-rahul-sales-system` — optional governed sales-system skill.

The component catalog verifies every file before installation. An upgrade first moves
the previous copy to `.ai-human-component-archive`. Removal moves the installed copy to
the same recoverable archive and deletes nothing.

## Employee-state boundary

The homework package is a reference kit. Once the Setup Helper copies one of its starter
projects into an employee's own worker folder, that new folder is employee state. A
later component upgrade or removal never manages that worker.
