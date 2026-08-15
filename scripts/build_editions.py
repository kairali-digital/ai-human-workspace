#!/usr/bin/env python3
"""Build deterministic reusable and Kairali edition archives for the active lane."""

import hashlib
import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = ROOT / "portal/public/downloads"
VERSION = (ROOT / "core/VERSION").read_text(encoding="utf-8").strip()
ZIP_TIME = (2026, 8, 15, 0, 0, 0)
REUSABLE_ROOT = "AI-HUMAN-REUSABLE-EDITION"
KAIRALI_ROOT = "KAIRALI-EMPLOYEE-EDITION"


def reject_duplicate_json_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON key: " + repr(key))
        value[key] = item
    return value


def read_json(path):
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicate_json_keys,
    )


def release_lane():
    manifest = read_json(ROOT / "release-manifest.json")
    components = read_json(ROOT / "component-manifest.json")
    if manifest.get("version") != VERSION or components.get("version") != VERSION:
        raise ValueError("edition version differs from a release manifest")
    status = (manifest.get("approval_status"), manifest.get("release_status"))
    component_status = (components.get("approval_status"), components.get("release_status"))
    if component_status != status:
        raise ValueError("release and component publication states differ")
    if status == ("LOCAL_BUILD_ONLY", "LOCAL_BUILD_ONLY"):
        return status[0], status[1], "LOCAL-CANDIDATE"
    if status == ("APPROVED_BY_OWNER", "RELEASED"):
        return status[0], status[1], "PUBLIC-KIT"
    raise ValueError("release manifests do not describe a supported distribution lane")


APPROVAL_STATUS, RELEASE_STATUS, ARCHIVE_LANE = release_lane()
VERSION_TOKEN = "v" + "".join(VERSION.split("."))
REUSABLE_NAME = "AI-HUMAN-" + VERSION_TOKEN + "-REUSABLE-EDITION-" + ARCHIVE_LANE + ".zip"
KAIRALI_NAME = "KAIRALI-AI-HUMAN-" + VERSION_TOKEN + "-EMPLOYEE-EDITION-" + ARCHIVE_LANE + ".zip"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_bytes(path):
    return path.read_bytes()


def add_tree(files, source, target):
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise ValueError("edition source may not contain symbolic links: " + str(path))
        if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        files[(target / path.relative_to(source)).as_posix()] = file_bytes(path)


def edition_record(identifier, label):
    return json.dumps(
        {
            "approval_status": APPROVAL_STATUS,
            "edition": identifier,
            "label": label,
            "release_status": RELEASE_STATUS,
            "schema": "ai-human.distribution-edition/v1",
            "version": VERSION,
        },
        indent=2,
        sort_keys=True,
    ).encode("utf-8") + b"\n"


def workspace_files(reusable=False):
    files = {}
    add_tree(files, ROOT / "core", Path("core"))
    add_tree(files, ROOT / "starter", Path("starter"))
    add_tree(files, ROOT / "company-profiles/template", Path("company-profiles/template"))
    script = file_bytes(ROOT / "scripts/ai_human.py")
    manifest = read_json(ROOT / "release-manifest.json")
    components = read_json(ROOT / "component-manifest.json")
    if reusable:
        old_repository = b'kairali-digital/ai-human-workspace'
        new_repository = b'standalone-local/ai-human-workspace'
        if old_repository not in script:
            raise ValueError("reusable repository substitution source is missing")
        script = script.replace(old_repository, new_repository)
        manifest["repository"] = new_repository.decode("utf-8")
        components = {
            "approval_status": APPROVAL_STATUS,
            "components": [],
            "release_status": RELEASE_STATUS,
            "repository": new_repository.decode("utf-8"),
            "schema": "ai-human.component-release/v1",
            "version": VERSION,
        }
    files["scripts/ai_human.py"] = script
    for record in manifest["managed_files"]:
        source = str(record["source"])
        if source == "scripts/ai_human.py":
            record["sha256"] = digest(script)
        else:
            record["sha256"] = digest(files[source])
    files["release-manifest.json"] = (
        json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    )
    files["component-manifest.json"] = (
        json.dumps(components, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    )
    return files


def write_archive(path, root_name, files):
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for relative in sorted(files):
            info = zipfile.ZipInfo(root_name + "/" + relative, date_time=ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, files[relative])
    checksum = digest(path.read_bytes())
    path.with_suffix(path.suffix + ".sha256").write_text(
        checksum + "  " + path.name + "\n", encoding="utf-8"
    )
    return checksum


def build_reusable():
    files = {
        "START-HERE.md": file_bytes(ROOT / "editions/reusable/START-HERE.md"),
        "INSTALL-DISABLE-REMOVE.md": file_bytes(
            ROOT / "editions/reusable/INSTALL-DISABLE-REMOVE.md"
        ),
        "EDITION.json": edition_record("reusable", "Reusable AI-Human Edition"),
    }
    for relative, data in workspace_files(reusable=True).items():
        files["workspace/" + relative] = data
    forbidden = (b"kairali", b"abhilash", b"abilash", b"ambuj")
    for relative, data in files.items():
        lowered = data.lower()
        if any(word in lowered for word in forbidden):
            raise ValueError("reusable edition contains company-specific text: " + relative)
    return write_archive(DOWNLOADS / REUSABLE_NAME, REUSABLE_ROOT, files)


def build_kairali():
    files = {
        "START-HERE.md": file_bytes(ROOT / "editions/kairali/START-HERE.md"),
        "INSTALL-DISABLE-REMOVE.md": file_bytes(
            ROOT / "editions/kairali/INSTALL-DISABLE-REMOVE.md"
        ),
        "EDITION.json": edition_record("kairali-employee", "Kairali Employee Edition"),
    }
    for relative, data in workspace_files().items():
        files["workspace/" + relative] = data
    add_tree(files, ROOT / "packages/kairali", Path("workspace/packages/kairali"))
    add_tree(
        files,
        ROOT / "company-profiles/kairali",
        Path("workspace/company-profiles/kairali"),
    )
    return write_archive(DOWNLOADS / KAIRALI_NAME, KAIRALI_ROOT, files)


def main():
    reusable = build_reusable()
    kairali = build_kairali()
    all_names = {
        "AI-HUMAN-" + VERSION_TOKEN + "-REUSABLE-EDITION-LOCAL-CANDIDATE.zip",
        "AI-HUMAN-" + VERSION_TOKEN + "-REUSABLE-EDITION-PUBLIC-KIT.zip",
        "KAIRALI-AI-HUMAN-" + VERSION_TOKEN + "-EMPLOYEE-EDITION-LOCAL-CANDIDATE.zip",
        "KAIRALI-AI-HUMAN-" + VERSION_TOKEN + "-EMPLOYEE-EDITION-PUBLIC-KIT.zip",
    }
    for obsolete_name in sorted(all_names - {REUSABLE_NAME, KAIRALI_NAME}):
        for obsolete in (
            DOWNLOADS / obsolete_name,
            DOWNLOADS / (obsolete_name + ".sha256"),
        ):
            if obsolete.is_file():
                obsolete.unlink()
    print("AI-HUMAN EDITION BUILD: PASS")
    print("- reusable edition: " + REUSABLE_NAME)
    print("- reusable edition SHA-256: " + reusable)
    print("- Kairali employee edition: " + KAIRALI_NAME)
    print("- Kairali employee edition SHA-256: " + kairali)
    print("- release status: " + RELEASE_STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
