# Technical setup

Technical employees may use Git, GitHub Desktop or an IDE. The repository and release
rules are identical regardless of client.

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

Do not run an update during a live task. `--at-checkpoint` is an assertion that the
owner has deliberately reached a safe checkpoint; the tool still checks and preserves
state. Removal moves the installed system to a timestamped recoverable folder and does
not delete company or employee state.

## Contribution flow

Use one task branch, run `python3 scripts/validate_release.py .` and
`python3 -m unittest discover -s tests -v`, then open a pull request. A merge is not a
rollout. Employees receive only tagged releases.
