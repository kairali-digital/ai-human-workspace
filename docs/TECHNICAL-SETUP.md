# Technical setup

Technical employees may use Git, GitHub Desktop or an IDE. The repository and release
rules are identical regardless of client.

GitHub Desktop `Fetch origin`/`Pull origin` updates only the selected checkout. It does
not install or update `.ai-human` in another worker, the company reference kit, or an
opt-in skill. Use the lifecycle below after the release is tagged and checked.

## Install a new worker from a checked-out release

```bash
python3 scripts/ai_human.py install "/absolute/worker/folder" \
  --company "Company name" \
  --company-owner "Company owner" \
  --owner "Employee name" \
  --name "Worker name" \
  --role "Role name" \
  --purpose "One bounded purpose"
```

Use `--adopt` only when adding the system to an existing project. Adoption creates
missing worker files and never overwrites an existing project file.

## Lifecycle

```bash
python3 scripts/ai_human.py status "/absolute/worker/folder"
python3 scripts/ai_human.py validate "/absolute/worker/folder"
python3 scripts/ai_human.py check "/absolute/worker/folder"
python3 scripts/ai_human.py update "/absolute/worker/folder" --latest --at-checkpoint
python3 scripts/ai_human.py rollback "/absolute/worker/folder" --version 1.0.0
python3 scripts/ai_human.py uninstall "/absolute/worker/folder" --at-checkpoint
```

`check` is read-only. Run `update` only after the employee approves `UPDATE NOW` and a
real checkpoint exists. For an installed Kairali reference kit, compare its
`.ai-human-component.json` version with the latest catalog, then upgrade separately:

Completion proof is the installed version, validation `PASS`, update receipt,
preserved-state result and recovery location. A fetched or pulled commit is not this
proof.

```bash
python3 scripts/ai_human.py install-pack kairali-company-rollout \
  "/absolute/reference-kit/folder" --latest --upgrade --at-checkpoint
```

## Optional company components

```bash
python3 scripts/ai_human.py components --source .
python3 scripts/ai_human.py install-skill kairali-akshar-marketing-science \
  --runtime codex --source .
python3 scripts/ai_human.py install-pack kairali-company-rollout \
  "/absolute/reference-kit/folder" --source .
python3 scripts/ai_human.py remove-pack "/absolute/reference-kit/folder" \
  --at-checkpoint
```

Use `--latest` instead of `--source .` when running the managed lifecycle tool from an
installed worker. A skill upgrade or any component removal requires
`--at-checkpoint`. Removal moves the component to a recoverable archive.

Do not run an update during a live task. `--at-checkpoint` is an assertion that the
owner has deliberately reached a safe checkpoint; the tool still checks and preserves
state. Removal moves the installed system to a timestamped recoverable folder and does
not delete company or employee state.

## Contribution flow

Use one task branch, run `python3 scripts/validate_release.py .` and
`python3 -m unittest discover -s tests -v`, then open a pull request. A merge is not a
rollout. Employees receive only tagged releases.
