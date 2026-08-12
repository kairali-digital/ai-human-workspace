#!/usr/bin/env python3
"""Install and manage a durable, company-neutral AI-human workspace."""

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path


SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
COMPONENT_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DEFAULT_REPOSITORY = "kairali-digital/ai-human-workspace"
COMPONENT_RECEIPT = ".ai-human-component.json"
STATE_FILES = (
    "AGENTS.md", "CLAUDE.md", "AI-HUMAN.md", "COMPANY.md", "PARAMETERS.md",
    "ROLE.md", "MASTER_CURSOR.md", "OPEN_REGISTER.md", "TODAY.md",
    "COMPLETED_LEDGER.md", "EVIDENCE_LOG.md", "FACTS.md", "DECISIONS.md",
    "TOOLBOX.md", "GATES.md", "AUTOMATIONS.md", "START-HERE.md",
    "READ-ME-FIRST.txt",
)
REQUIRED_MANAGED = {
    ".ai-human/system/AI-HUMAN.md",
    ".ai-human/system/AGENT-RULES.md",
    ".ai-human/system/OPERATING-LOOP.md",
    ".ai-human/system/GATES-SHARED.md",
    ".ai-human/system/SESSION-START.md",
    ".ai-human/system/SESSION-END.md",
    ".ai-human/VERSION",
    ".ai-human/bin/ai_human.py",
}


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def clean(value, label):
    value = " ".join(value.split()).replace("|", "\\|").strip()
    if not value:
        raise ValueError(label + " cannot be empty")
    return value


def safe_worker(raw, must_exist=True):
    path = Path(raw).expanduser().resolve()
    if path == Path(path.anchor).resolve() or path == Path.home().resolve():
        raise ValueError("refusing a filesystem or home root")
    if must_exist and not path.is_dir():
        raise ValueError("worker is not a directory: " + str(path))
    if path.exists() and not path.is_dir():
        raise ValueError("target exists and is not a directory: " + str(path))
    return path


def safe_relative(value, label):
    path = Path(value)
    if not value or path.is_absolute() or ".." in path.parts:
        raise ValueError("unsafe " + label + ": " + repr(value))
    return path


def portable_key(value):
    """Use one comparison form even when Windows Path renders backslashes."""
    return str(value).replace("\\", "/")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_sha256(root, ignore_receipt=False):
    root = Path(root)
    digest = hashlib.sha256()
    count = 0
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("component trees may not contain symbolic links: " + str(path))
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if ignore_receipt and relative == COMPONENT_RECEIPT:
            continue
        digest.update(relative.encode("utf-8") + b"\0")
        digest.update(bytes.fromhex(sha256(path)) + b"\n")
        count += 1
    return digest.hexdigest(), count


def atomic_text(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".write-temp")
    temp.write_text(content, encoding="utf-8")
    os.replace(temp, path)


def atomic_json(path, value):
    atomic_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def version_tuple(value):
    if not SEMVER.fullmatch(str(value)):
        raise ValueError("invalid semantic version: " + repr(value))
    return tuple(int(part) for part in str(value).split("."))


def state_hashes(worker):
    return {name: sha256(worker / name) for name in STATE_FILES if (worker / name).is_file()}


def release_root_from_script():
    candidate = Path(__file__).resolve().parents[1]
    if (candidate / "release-manifest.json").is_file() and (candidate / "starter").is_dir():
        return candidate
    raise ValueError("install must run from a checked-out or extracted release")


def load_release(root):
    root = Path(root).expanduser().resolve()
    manifest_path = root / "release-manifest.json"
    if not manifest_path.is_file():
        raise ValueError("release manifest missing: " + str(manifest_path))
    manifest = read_json(manifest_path)
    if manifest.get("schema") != "ai-human.workspace-release/v1":
        raise ValueError("unsupported release manifest schema")
    version_tuple(manifest.get("version", ""))
    if manifest.get("approval_status") != "APPROVED_BY_OWNER":
        raise ValueError("release is not owner-approved")
    records = manifest.get("managed_files") or []
    targets = set()
    for record in records:
        source_rel = safe_relative(str(record.get("source", "")), "managed source")
        target_rel = safe_relative(str(record.get("target", "")), "managed target")
        target_key = portable_key(target_rel)
        if not target_key.startswith(".ai-human/"):
            raise ValueError("managed target is outside .ai-human: " + str(target_rel))
        if target_key in targets:
            raise ValueError("duplicate managed target: " + str(target_rel))
        targets.add(target_key)
        source = root / source_rel
        if not source.is_file():
            raise ValueError("managed source missing: " + str(source_rel))
        if sha256(source) != record.get("sha256"):
            raise ValueError("managed source hash mismatch: " + str(source_rel))
    if not REQUIRED_MANAGED.issubset(targets):
        raise ValueError("release is missing required managed targets")
    if targets.intersection(set(manifest.get("never_managed") or [])):
        raise ValueError("release tries to manage protected local state")
    return root, manifest


def load_components(root, release_manifest):
    path = root / "component-manifest.json"
    if not path.is_file():
        raise ValueError("component manifest missing: " + str(path))
    manifest = read_json(path)
    if manifest.get("schema") != "ai-human.component-release/v1":
        raise ValueError("unsupported component manifest schema")
    if manifest.get("approval_status") != "APPROVED_BY_OWNER":
        raise ValueError("component release is not owner-approved")
    if manifest.get("version") != release_manifest.get("version"):
        raise ValueError("component and release versions differ")
    if manifest.get("repository") != release_manifest.get("repository"):
        raise ValueError("component and release repositories differ")
    records = manifest.get("components") or []
    identifiers = set()
    for record in records:
        identifier = str(record.get("id", ""))
        if not COMPONENT_ID.fullmatch(identifier):
            raise ValueError("invalid component id: " + repr(identifier))
        if identifier in identifiers:
            raise ValueError("duplicate component id: " + identifier)
        identifiers.add(identifier)
        if record.get("type") not in {"skill", "reference-pack"}:
            raise ValueError("unsupported component type: " + repr(record.get("type")))
        source_rel = safe_relative(str(record.get("source", "")), "component source")
        source_key = portable_key(source_rel)
        if not source_key.startswith("packages/"):
            raise ValueError("component source is outside packages/: " + source_key)
        source = root / source_rel
        if source.is_symlink():
            raise ValueError("component source may not be a symbolic link: " + source_key)
        if not source.is_dir():
            raise ValueError("component source missing: " + source_key)
        digest, count = tree_sha256(source)
        if digest != record.get("tree_sha256"):
            raise ValueError("component tree hash mismatch: " + identifier)
        if count != record.get("file_count"):
            raise ValueError("component file count mismatch: " + identifier)
        if record.get("type") == "skill":
            validate_skill_source(source, identifier)
    return manifest


def validate_skill_source(source, identifier):
    skill = source / "SKILL.md"
    if not skill.is_file():
        raise ValueError("skill component lacks SKILL.md: " + identifier)
    text = skill.read_text(encoding="utf-8")
    frontmatter = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, flags=re.S)
    if not frontmatter:
        raise ValueError("skill frontmatter missing: " + identifier)
    match = re.search(r"^name:\s*['\"]?([^'\"\n]+)", frontmatter.group(1), flags=re.M)
    if not match or match.group(1).strip() != identifier:
        raise ValueError("skill frontmatter name differs from component id: " + identifier)


def live_task(worker):
    path = worker / "MASTER_CURSOR.md"
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"^## LIVE TASK\s*$\n(.*?)(?=^## |\Z)", text, flags=re.M | re.S)
    value = match.group(1).strip() if match else ""
    if not value or "NOT SET" in value.upper() or value.upper() in {"NONE", "NO LIVE TASK"}:
        return ""
    return value


def render(content, replacements):
    for token, value in replacements.items():
        content = content.replace(token, value)
    return content


def managed_targets(manifest):
    return [str(record["target"]) for record in manifest.get("managed_files", [])]


def install_metadata(worker):
    path = worker / ".ai-human/install.json"
    if not path.is_file():
        raise ValueError("install metadata missing")
    return read_json(path)


def write_install_metadata(worker, manifest):
    atomic_json(
        worker / ".ai-human/install.json",
        {
            "installed_version": manifest["version"],
            "managed_targets": managed_targets(manifest),
            "repository": manifest["repository"],
            "schema": "ai-human.workspace-install/v1",
        },
    )
    atomic_json(worker / ".ai-human/release-manifest.json", manifest)


def copy_release_files(worker, release, manifest):
    for record in manifest["managed_files"]:
        source = release / record["source"]
        target = worker / record["target"]
        target.parent.mkdir(parents=True, exist_ok=True)
        temp = target.with_name(target.name + ".update-temp")
        shutil.copy2(source, temp)
        os.replace(temp, target)


def parse_table_ids(path):
    values = []
    if not path.is_file():
        return values
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip().startswith("|") or "---" in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and cells[0] not in {"ID", "Task ID", "—", ""}:
            values.append(cells[0])
    return values


def validate_worker(worker, quiet=False):
    failures = []
    for name in STATE_FILES:
        path = worker / name
        if not path.is_file() or path.stat().st_size == 0:
            failures.append("missing or empty local file: " + name)

    version_path = worker / ".ai-human/VERSION"
    version = version_path.read_text(encoding="utf-8").strip() if version_path.is_file() else ""
    try:
        version_tuple(version)
    except ValueError as exc:
        failures.append(str(exc))

    metadata = {}
    metadata_path = worker / ".ai-human/install.json"
    try:
        metadata = read_json(metadata_path)
    except Exception as exc:
        failures.append("invalid install metadata: " + str(exc))
    manifest = {}
    manifest_path = worker / ".ai-human/release-manifest.json"
    try:
        manifest = read_json(manifest_path)
    except Exception as exc:
        failures.append("invalid installed release manifest: " + str(exc))

    if metadata:
        if metadata.get("schema") != "ai-human.workspace-install/v1":
            failures.append("unsupported install metadata schema")
        try:
            version_tuple(str(metadata.get("installed_version", "")))
        except ValueError as exc:
            failures.append("install metadata " + str(exc))
    if manifest:
        if manifest.get("schema") != "ai-human.workspace-release/v1":
            failures.append("unsupported installed release manifest schema")
        if manifest.get("approval_status") != "APPROVED_BY_OWNER":
            failures.append("installed release is not owner-approved")
        try:
            version_tuple(str(manifest.get("version", "")))
        except ValueError as exc:
            failures.append("installed manifest " + str(exc))

    if metadata and manifest:
        installed_version = str(metadata.get("installed_version", ""))
        manifest_version = str(manifest.get("version", ""))
        if version != installed_version or version != manifest_version:
            failures.append("VERSION, install metadata and manifest versions differ")
        if not metadata.get("repository") or metadata.get("repository") != manifest.get("repository"):
            failures.append("install metadata and manifest repositories differ")

        targets = set()
        for record in manifest.get("managed_files") or []:
            target_value = str(record.get("target", ""))
            try:
                target_rel = safe_relative(target_value, "installed managed target")
            except ValueError as exc:
                failures.append(str(exc))
                continue
            target_key = portable_key(target_rel)
            if not target_key.startswith(".ai-human/"):
                failures.append("installed managed target is outside .ai-human: " + target_key)
                continue
            if target_key in targets:
                failures.append("duplicate installed managed target: " + target_key)
                continue
            targets.add(target_key)
            target = worker / target_rel
            if not target.is_file() or target.stat().st_size == 0:
                failures.append("missing or empty managed file: " + target_key)
            elif sha256(target) != record.get("sha256"):
                failures.append("managed file integrity mismatch: " + target_key)
        for target in sorted(REQUIRED_MANAGED - targets):
            failures.append("required installed managed target missing: " + target)
        if targets.intersection(set(manifest.get("never_managed") or [])):
            failures.append("installed release tries to manage protected local state")
        metadata_targets = {portable_key(value) for value in metadata.get("managed_targets") or []}
        if metadata_targets != targets:
            failures.append("install metadata managed targets differ from the manifest")

    for name in ("AI-HUMAN.md", "COMPANY.md", "PARAMETERS.md", "ROLE.md"):
        path = worker / name
        if path.is_file() and re.search(r"\{\{[A-Z0-9_]+\}\}", path.read_text(encoding="utf-8")):
            failures.append("unresolved parameter in " + name)
    live = live_task(worker)
    if live:
        match = re.search(r"`([^`]+)`", live)
        task_id = match.group(1) if match else live.split()[0].strip("*`-")
        if task_id and task_id not in parse_table_ids(worker / "OPEN_REGISTER.md"):
            failures.append("live task is missing from OPEN_REGISTER.md: " + task_id)
        if task_id and task_id not in parse_table_ids(worker / "TODAY.md"):
            failures.append("live task is missing from TODAY.md: " + task_id)
    if failures:
        if not quiet:
            print("AI-HUMAN WORKER VALIDATION: FAIL")
            for failure in failures:
                print("- " + failure)
        return False, failures
    if not quiet:
        print("AI-HUMAN WORKER VALIDATION: PASS")
        print("- worker: " + str(worker))
        print("- shared system version: " + version)
        print("- company, role and employee state are separate from managed files")
    return True, []


def install(args):
    worker = safe_worker(args.worker, must_exist=False)
    release, manifest = load_release(args.source or release_root_from_script())
    existed = worker.exists()
    if existed and any(worker.iterdir()) and not args.adopt:
        raise ValueError("target is not empty; use --adopt to preserve existing files")
    if (worker / ".ai-human").exists():
        raise ValueError("the system is already installed; use update instead")
    worker.mkdir(parents=True, exist_ok=True)
    replacements = {
        "{{COMPANY_NAME}}": clean(args.company, "company"),
        "{{COMPANY_OWNER}}": clean(args.company_owner, "company owner"),
        "{{OWNER_NAME}}": clean(args.owner, "owner"),
        "{{WORKER_NAME}}": clean(args.name, "worker name"),
        "{{ROLE_NAME}}": clean(args.role, "role"),
        "{{PURPOSE}}": clean(args.purpose, "purpose"),
        "{{BRAIN}}": args.brain,
        "{{TASK_SELECTION}}": "Owner promotes the live task" if args.task_selection == "owner" else "AI may select the highest-priority unblocked row",
        "{{BATCH_CAP}}": str(args.batch_cap),
    }
    created = []
    skipped = []
    try:
        for source in sorted((release / "starter").iterdir()):
            if not source.is_file():
                continue
            target = worker / source.name
            if target.exists():
                skipped.append(source.name)
                continue
            content = render(source.read_text(encoding="utf-8"), replacements)
            atomic_text(target, content)
            created.append(source.name)
        copy_release_files(worker, release, manifest)
        write_install_metadata(worker, manifest)
        if skipped:
            atomic_text(
                worker / ".ai-human/ADOPTION-NOTICE.md",
                "# Adoption notice\n\nPreserved existing project files: " + ", ".join(skipped) +
                ". Ask the project owner to reconcile any existing adapter instructions with `.ai-human/system/AGENT-RULES.md`.\n",
            )
        ok, failures = validate_worker(worker, quiet=True)
        if not ok:
            raise ValueError("installed worker validation failed: " + "; ".join(failures))
    except Exception:
        if (worker / ".ai-human").exists():
            shutil.rmtree(worker / ".ai-human")
        for name in created:
            path = worker / name
            if path.is_file():
                path.unlink()
        if not existed and worker.exists() and not any(worker.iterdir()):
            worker.rmdir()
        raise
    print("AI-HUMAN INSTALL: PASS")
    print("- worker: " + str(worker))
    print("- version: " + manifest["version"])
    print("- created local files: " + str(len(created)))
    print("- preserved existing files: " + str(len(skipped)))
    print("- unattended work: disabled")


def record_deferred(worker, version):
    register = worker / "OPEN_REGISTER.md"
    task_id = "CORE-UPDATE-" + version
    text = register.read_text(encoding="utf-8")
    if task_id not in text:
        newline = "" if text.endswith("\n") else "\n"
        row = "| " + task_id + " | High | Validated shared-system update available; wait for checkpoint | release check | owner | Deferred | local validator PASS |\n"
        atomic_text(register, text + newline + row)


def backup_for_update(worker, old_manifest, new_manifest):
    old_version = install_metadata(worker)["installed_version"]
    new_version = new_manifest["version"]
    backup_parent = worker / ".ai-human/backups"
    stem = old_version + "-before-" + new_version + "-" + now_utc()
    backup = backup_parent / stem
    counter = 2
    while backup.exists():
        backup = backup_parent / (stem + "-" + str(counter))
        counter += 1
    records = []
    targets = set(managed_targets(old_manifest)) | set(managed_targets(new_manifest))
    targets.update({".ai-human/install.json", ".ai-human/release-manifest.json"})
    for relative in sorted(targets):
        target = worker / relative
        existed = target.is_file()
        records.append({"target": relative, "existed": existed})
        if existed:
            destination = backup / "files" / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, destination)
    atomic_json(
        backup / "backup-manifest.json",
        {
            "created_utc": now_utc(), "from_version": old_version,
            "to_version": new_version, "files": records,
        },
    )
    return backup


def restore_backup(worker, backup):
    data = read_json(backup / "backup-manifest.json")
    for record in data["files"]:
        target = worker / safe_relative(record["target"], "backup target")
        if record["existed"]:
            source = backup / "files" / record["target"]
            target.parent.mkdir(parents=True, exist_ok=True)
            temp = target.with_name(target.name + ".rollback-temp")
            shutil.copy2(source, temp)
            os.replace(temp, target)
        elif target.is_file() or target.is_symlink():
            target.unlink()


def apply_update(worker, release, manifest, at_checkpoint=False):
    metadata = install_metadata(worker)
    old_version = metadata["installed_version"]
    new_version = manifest["version"]
    if version_tuple(new_version) <= version_tuple(old_version):
        print("AI-HUMAN UPDATE: NO UPDATE")
        print("- local version: " + old_version)
        print("- release version: " + new_version)
        return
    if live_task(worker) and not at_checkpoint:
        record_deferred(worker, new_version)
        print("AI-HUMAN UPDATE: DEFERRED")
        print("- version: " + new_version)
        print("- reason: live task exists; update recorded for a checkpoint")
        return
    before_state = state_hashes(worker)
    old_manifest = read_json(worker / ".ai-human/release-manifest.json")
    backup = backup_for_update(worker, old_manifest, manifest)
    try:
        copy_release_files(worker, release, manifest)
        obsolete = set(managed_targets(old_manifest)) - set(managed_targets(manifest))
        for relative in obsolete:
            target = worker / safe_relative(relative, "obsolete target")
            if target.is_file() or target.is_symlink():
                target.unlink()
        write_install_metadata(worker, manifest)
        if before_state != state_hashes(worker):
            raise ValueError("update changed company, role or employee state")
        ok, failures = validate_worker(worker, quiet=True)
        if not ok:
            raise ValueError("updated worker validation failed: " + "; ".join(failures))
    except Exception:
        restore_backup(worker, backup)
        raise
    atomic_json(
        worker / ".ai-human/update-receipt.json",
        {
            "backup": str(backup), "from_version": old_version,
            "state_preserved": True, "to_version": new_version, "validator": "PASS",
        },
    )
    print("AI-HUMAN UPDATE: PASS")
    print("- previous version: " + old_version)
    print("- new version: " + new_version)
    print("- company, role and employee state hashes: preserved")
    print("- rollback backup: " + str(backup))


def safe_extract(archive, destination):
    with zipfile.ZipFile(archive) as bundle:
        for item in bundle.infolist():
            relative = safe_relative(item.filename, "archive member")
            target = (destination / relative).resolve()
            if destination.resolve() not in target.parents and target != destination.resolve():
                raise ValueError("archive member escapes extraction root")
        bundle.extractall(destination)


def latest_release(repository):
    request = urllib.request.Request(
        "https://api.github.com/repos/" + repository + "/releases/latest",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "ai-human-workspace"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)
    version = str(data.get("tag_name", "")).lstrip("v")
    version_tuple(version)
    return version, data["zipball_url"]


def download_release(repository):
    version, url = latest_release(repository)
    temp = tempfile.TemporaryDirectory(prefix="ai-human-release-")
    root = Path(temp.name)
    archive = root / "release.zip"
    request = urllib.request.Request(url, headers={"User-Agent": "ai-human-workspace"})
    with urllib.request.urlopen(request, timeout=60) as response, archive.open("wb") as stream:
        shutil.copyfileobj(response, stream)
    extracted = root / "extracted"
    extracted.mkdir()
    safe_extract(archive, extracted)
    manifests = list(extracted.glob("*/release-manifest.json"))
    if len(manifests) != 1:
        temp.cleanup()
        raise ValueError("downloaded release has no unique manifest")
    release, manifest = load_release(manifests[0].parent)
    if manifest["repository"] != repository or manifest["version"] != version:
        temp.cleanup()
        raise ValueError("release repository or tag does not match its manifest")
    return temp, release, manifest


def update(args):
    worker = safe_worker(args.worker)
    if args.latest:
        repository = install_metadata(worker)["repository"]
        temp, release, manifest = download_release(repository)
        try:
            apply_update(worker, release, manifest, args.at_checkpoint)
        finally:
            temp.cleanup()
    else:
        if not args.source:
            raise ValueError("provide --source or --latest")
        release, manifest = load_release(args.source)
        apply_update(worker, release, manifest, args.at_checkpoint)


def rollback(args):
    worker = safe_worker(args.worker)
    current = install_metadata(worker)["installed_version"]
    version_tuple(args.version)
    candidates = []
    backup_parent = worker / ".ai-human/backups"
    for manifest_path in backup_parent.glob("*/backup-manifest.json"):
        try:
            data = read_json(manifest_path)
        except Exception:
            continue
        if data.get("from_version") == args.version and data.get("to_version") == current:
            candidates.append(manifest_path.parent)
    if not candidates:
        raise ValueError("rollback backup missing for " + args.version + " before " + current)
    backup = max(candidates, key=lambda path: (path.stat().st_mtime_ns, path.name))
    before = state_hashes(worker)
    restore_backup(worker, backup)
    if before != state_hashes(worker):
        raise ValueError("rollback changed company, role or employee state")
    ok, failures = validate_worker(worker, quiet=True)
    if not ok:
        raise ValueError("rollback validation failed: " + "; ".join(failures))
    atomic_json(
        worker / ".ai-human/rollback-receipt.json",
        {"from_version": current, "state_preserved": True, "to_version": args.version, "validator": "PASS"},
    )
    print("AI-HUMAN ROLLBACK: PASS")
    print("- restored version: " + args.version)
    print("- company, role and employee state hashes: preserved")


def check(args):
    worker = safe_worker(args.worker)
    metadata = install_metadata(worker)
    local = metadata["installed_version"]
    latest, _ = latest_release(metadata["repository"])
    print("AI-HUMAN UPDATE CHECK: PASS")
    print("- local version: " + local)
    print("- latest release: " + latest)
    print("- update available: " + ("yes" if version_tuple(latest) > version_tuple(local) else "no"))


def checkpoint(args):
    worker = safe_worker(args.worker)
    ok, failures = validate_worker(worker, quiet=True)
    if not ok:
        raise ValueError("checkpoint validation failed: " + "; ".join(failures))
    atomic_json(
        worker / ".ai-human/checkpoint-receipt.json",
        {"created_utc": now_utc(), "live_task": live_task(worker), "state_hashes": state_hashes(worker), "validator": "PASS"},
    )
    print("AI-HUMAN CHECKPOINT: PASS")
    print("- durable state validated and hashed")


def uninstall(args):
    worker = safe_worker(args.worker)
    system = worker / ".ai-human"
    if not system.is_dir():
        raise ValueError("AI-human system is not installed")
    if live_task(worker) and not args.at_checkpoint:
        raise ValueError("live task exists; reach a checkpoint before uninstalling")
    before = state_hashes(worker)
    destination = worker / (".ai-human-removed-" + now_utc())
    if destination.exists():
        raise ValueError("removal destination already exists")
    shutil.move(str(system), str(destination))
    if before != state_hashes(worker):
        raise ValueError("uninstall changed company, role or employee state")
    atomic_text(
        worker / "AI-HUMAN-UNINSTALLED.txt",
        "The managed AI-human system was removed reversibly.\nPreserved system: " + destination.name + "\nCompany and employee state were not deleted.\n",
    )
    print("AI-HUMAN UNINSTALL: PASS")
    print("- removed system moved to: " + str(destination))
    print("- company, role and employee state: preserved")


def status(args):
    worker = safe_worker(args.worker)
    metadata = install_metadata(worker)
    ok, failures = validate_worker(worker, quiet=True)
    print("AI-HUMAN STATUS")
    print("- worker: " + str(worker))
    print("- version: " + metadata["installed_version"])
    print("- repository: " + metadata["repository"])
    print("- live task: " + (live_task(worker) or "NOT SET"))
    print("- validation: " + ("PASS" if ok else "FAIL"))
    if failures:
        for failure in failures:
            print("  - " + failure)


def component_release(args):
    if getattr(args, "latest", False):
        temp, release, release_manifest = download_release(args.repository)
        try:
            component_manifest = load_components(release, release_manifest)
        except Exception:
            temp.cleanup()
            raise
        return temp, release, release_manifest, component_manifest
    source = getattr(args, "source", None)
    release, release_manifest = load_release(source or release_root_from_script())
    component_manifest = load_components(release, release_manifest)
    return None, release, release_manifest, component_manifest


def component_by_id(component_manifest, identifier):
    if not COMPONENT_ID.fullmatch(identifier):
        raise ValueError("invalid component id: " + repr(identifier))
    for record in component_manifest["components"]:
        if record["id"] == identifier:
            return record
    raise ValueError("unknown component: " + identifier)


def safe_component_parent(raw):
    path = Path(raw).expanduser().resolve()
    if path == Path(path.anchor).resolve() or path == Path.home().resolve():
        raise ValueError("refusing a filesystem or home root for components")
    if path.exists() and not path.is_dir():
        raise ValueError("component parent exists and is not a directory: " + str(path))
    return path


def default_skills_root(runtime):
    folder = ".codex" if runtime == "codex" else ".claude"
    return Path.home() / folder / "skills"


def component_receipt(target):
    path = target / COMPONENT_RECEIPT
    if not path.is_file():
        raise ValueError("component install receipt missing: " + str(path))
    receipt = read_json(path)
    if receipt.get("schema") != "ai-human.component-install/v1":
        raise ValueError("unsupported component install receipt")
    if not COMPONENT_ID.fullmatch(str(receipt.get("component_id", ""))):
        raise ValueError("invalid component id in install receipt")
    if receipt.get("component_type") not in {"skill", "reference-pack"}:
        raise ValueError("invalid component type in install receipt")
    return receipt


def unique_component_archive(parent, prefix):
    archive_root = parent / ".ai-human-component-archive"
    archive_root.mkdir(parents=True, exist_ok=True)
    stem = prefix + "-" + now_utc()
    target = archive_root / stem
    counter = 2
    while target.exists():
        target = archive_root / (stem + "-" + str(counter))
        counter += 1
    return target


def install_component_tree(release, release_manifest, record, target, upgrade=False, at_checkpoint=False):
    source = release / safe_relative(record["source"], "component source")
    expected_digest = record["tree_sha256"]
    expected_count = record["file_count"]
    digest, count = tree_sha256(source)
    if digest != expected_digest or count != expected_count:
        raise ValueError("component source changed after validation: " + record["id"])
    if target.exists() and not upgrade:
        raise ValueError("component target already exists; use --upgrade at a checkpoint")
    if target.exists() and not at_checkpoint:
        raise ValueError("component upgrade requires --at-checkpoint")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.parent / ("." + target.name + ".install-" + now_utc())
    if temporary.exists():
        raise ValueError("component temporary target already exists: " + str(temporary))
    backup = None
    try:
        shutil.copytree(source, temporary)
        copied_digest, copied_count = tree_sha256(temporary)
        if copied_digest != expected_digest or copied_count != expected_count:
            raise ValueError("copied component integrity mismatch: " + record["id"])
        if record["type"] == "skill":
            validate_skill_source(temporary, record["id"])
        atomic_json(
            temporary / COMPONENT_RECEIPT,
            {
                "component_id": record["id"],
                "component_type": record["type"],
                "installed_version": release_manifest["version"],
                "repository": release_manifest["repository"],
                "schema": "ai-human.component-install/v1",
                "source_tree_sha256": expected_digest,
            },
        )
        if target.exists():
            backup = unique_component_archive(
                target.parent, record["id"] + "-before-" + release_manifest["version"]
            )
            shutil.move(str(target), str(backup))
        os.replace(temporary, target)
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary)
        if backup and backup.exists() and not target.exists():
            shutil.move(str(backup), str(target))
        raise
    print("AI-HUMAN COMPONENT INSTALL: PASS")
    print("- component: " + record["id"])
    print("- type: " + record["type"])
    print("- release version: " + release_manifest["version"])
    print("- target: " + str(target))
    print("- previous copy: " + (str(backup) if backup else "none"))


def remove_component_target(target, expected_id, expected_type, at_checkpoint=False):
    if not COMPONENT_ID.fullmatch(expected_id):
        raise ValueError("invalid component id: " + repr(expected_id))
    if not at_checkpoint:
        raise ValueError("component removal requires --at-checkpoint")
    if not target.is_dir():
        raise ValueError("installed component missing: " + str(target))
    receipt = component_receipt(target)
    if receipt.get("component_id") != expected_id or receipt.get("component_type") != expected_type:
        raise ValueError("component receipt does not match the requested removal")
    destination = unique_component_archive(target.parent, expected_id + "-removed")
    shutil.move(str(target), str(destination))
    print("AI-HUMAN COMPONENT REMOVE: PASS")
    print("- component: " + expected_id)
    print("- preserved at: " + str(destination))
    print("- deleted files: 0")


def list_components(args):
    temp, _release, release_manifest, component_manifest = component_release(args)
    try:
        print("AI-HUMAN COMPONENT CATALOG: PASS")
        print("- release version: " + release_manifest["version"])
        for record in component_manifest["components"]:
            print(
                "- " + record["id"] + " | " + record["type"] + " | " +
                record["install_policy"] + " | " + str(record["file_count"]) + " files"
            )
    finally:
        if temp:
            temp.cleanup()


def install_skill(args):
    temp, release, release_manifest, component_manifest = component_release(args)
    try:
        record = component_by_id(component_manifest, args.component)
        if record["type"] != "skill":
            raise ValueError("component is not a skill: " + args.component)
        skills_root = safe_component_parent(args.skills_root or default_skills_root(args.runtime))
        target = skills_root / record["id"]
        install_component_tree(
            release, release_manifest, record, target, args.upgrade, args.at_checkpoint
        )
    finally:
        if temp:
            temp.cleanup()


def remove_skill(args):
    if not COMPONENT_ID.fullmatch(args.component):
        raise ValueError("invalid component id: " + repr(args.component))
    skills_root = safe_component_parent(args.skills_root or default_skills_root(args.runtime))
    target = skills_root / args.component
    remove_component_target(target, args.component, "skill", args.at_checkpoint)


def install_pack(args):
    temp, release, release_manifest, component_manifest = component_release(args)
    try:
        record = component_by_id(component_manifest, args.component)
        if record["type"] != "reference-pack":
            raise ValueError("component is not a reference pack: " + args.component)
        target = safe_worker(args.target, must_exist=False)
        install_component_tree(
            release, release_manifest, record, target, args.upgrade, args.at_checkpoint
        )
    finally:
        if temp:
            temp.cleanup()


def remove_pack(args):
    target = safe_worker(args.target)
    receipt = component_receipt(target)
    identifier = str(receipt.get("component_id", ""))
    remove_component_target(target, identifier, "reference-pack", args.at_checkpoint)


def add_component_source_options(command):
    source = command.add_mutually_exclusive_group()
    source.add_argument("--source")
    source.add_argument("--latest", action="store_true")
    command.add_argument("--repository", default=DEFAULT_REPOSITORY)


def parser():
    root = argparse.ArgumentParser(description="AI-Human workspace lifecycle")
    sub = root.add_subparsers(dest="command", required=True)
    install_p = sub.add_parser("install")
    install_p.add_argument("worker")
    install_p.add_argument("--source")
    install_p.add_argument("--company", required=True)
    install_p.add_argument("--company-owner", required=True)
    install_p.add_argument("--owner", required=True)
    install_p.add_argument("--name", required=True)
    install_p.add_argument("--role", required=True)
    install_p.add_argument("--purpose", required=True)
    install_p.add_argument("--brain", choices=("Codex", "Claude", "Codex or Claude"), default="Codex or Claude")
    install_p.add_argument("--task-selection", choices=("owner", "agent"), default="owner")
    install_p.add_argument("--batch-cap", type=int, default=25)
    install_p.add_argument("--adopt", action="store_true")
    install_p.set_defaults(handler=install)

    for name, handler in (("status", status), ("validate", None), ("check", check), ("checkpoint", checkpoint)):
        item = sub.add_parser(name)
        item.add_argument("worker")
        item.set_defaults(handler=handler)
    update_p = sub.add_parser("update")
    update_p.add_argument("worker")
    update_p.add_argument("--source")
    update_p.add_argument("--latest", action="store_true")
    update_p.add_argument("--at-checkpoint", action="store_true")
    update_p.set_defaults(handler=update)
    rollback_p = sub.add_parser("rollback")
    rollback_p.add_argument("worker")
    rollback_p.add_argument("--version", required=True)
    rollback_p.set_defaults(handler=rollback)
    uninstall_p = sub.add_parser("uninstall")
    uninstall_p.add_argument("worker")
    uninstall_p.add_argument("--at-checkpoint", action="store_true")
    uninstall_p.set_defaults(handler=uninstall)

    components_p = sub.add_parser("components")
    add_component_source_options(components_p)
    components_p.set_defaults(handler=list_components)

    install_skill_p = sub.add_parser("install-skill")
    install_skill_p.add_argument("component")
    install_skill_p.add_argument("--runtime", choices=("codex", "claude"), required=True)
    install_skill_p.add_argument("--skills-root")
    install_skill_p.add_argument("--upgrade", action="store_true")
    install_skill_p.add_argument("--at-checkpoint", action="store_true")
    add_component_source_options(install_skill_p)
    install_skill_p.set_defaults(handler=install_skill)

    remove_skill_p = sub.add_parser("remove-skill")
    remove_skill_p.add_argument("component")
    remove_skill_p.add_argument("--runtime", choices=("codex", "claude"), required=True)
    remove_skill_p.add_argument("--skills-root")
    remove_skill_p.add_argument("--at-checkpoint", action="store_true")
    remove_skill_p.set_defaults(handler=remove_skill)

    install_pack_p = sub.add_parser("install-pack")
    install_pack_p.add_argument("component")
    install_pack_p.add_argument("target")
    install_pack_p.add_argument("--upgrade", action="store_true")
    install_pack_p.add_argument("--at-checkpoint", action="store_true")
    add_component_source_options(install_pack_p)
    install_pack_p.set_defaults(handler=install_pack)

    remove_pack_p = sub.add_parser("remove-pack")
    remove_pack_p.add_argument("target")
    remove_pack_p.add_argument("--at-checkpoint", action="store_true")
    remove_pack_p.set_defaults(handler=remove_pack)
    return root


def main():
    args = parser().parse_args()
    try:
        if args.command == "validate":
            ok, _ = validate_worker(safe_worker(args.worker))
            return 0 if ok else 1
        if args.command == "install" and not 1 <= args.batch_cap <= 25:
            raise ValueError("batch cap must be between 1 and 25")
        args.handler(args)
        return 0
    except Exception as exc:
        print("AI-HUMAN " + args.command.upper() + ": FAIL - " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
