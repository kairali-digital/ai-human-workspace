#!/usr/bin/env python3
"""Build and verify the six public GitHub release assets for the current version."""

import argparse
import hashlib
import json
import shutil
import stat
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IGNORED_PARTS = {".git", ".pytest_cache", "__pycache__", "dist", "portal"}
ZIP_TIME = (2026, 8, 15, 0, 0, 0)


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


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_files(source, relative_to, ignored_parts=()):
    files = []
    for path in sorted(source.rglob("*"), key=lambda item: item.relative_to(source).as_posix()):
        relative = path.relative_to(relative_to)
        if any(part in ignored_parts for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError("public release source contains a symbolic link: " + relative.as_posix())
        if (
            not path.is_file()
            or path.suffix == ".pyc"
            or path.name.endswith((".write-temp", ".update-temp", ".build-temp"))
        ):
            continue
        files.append((path, relative.as_posix()))
    return files


def write_archive(output, prefix, files):
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path, relative in sorted(files, key=lambda item: item[1]):
            info = zipfile.ZipInfo(prefix + "/" + relative, date_time=ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())


def verify_archive(path, expected_prefix, expected_count):
    with zipfile.ZipFile(path) as archive:
        records = archive.infolist()
        names = [record.filename for record in records]
        if len(names) != expected_count or len(set(names)) != len(names):
            raise ValueError("public release ZIP inventory differs or contains duplicates: " + path.name)
        if any(not name.startswith(expected_prefix + "/") for name in names):
            raise ValueError("public release ZIP has an unexpected root: " + path.name)
        for record in records:
            if stat.S_IFMT(record.external_attr >> 16) == stat.S_IFLNK:
                raise ValueError("public release ZIP contains a symbolic link: " + record.filename)
            with archive.open(record) as stream:
                while stream.read(1024 * 1024):
                    pass
        if archive.testzip() is not None:
            raise ValueError("public release ZIP CRC verification failed: " + path.name)


def build(root, output):
    manifest = read_json(root / "release-manifest.json")
    components = read_json(root / "component-manifest.json")
    if (manifest.get("approval_status"), manifest.get("release_status")) != (
        "APPROVED_BY_OWNER", "RELEASED",
    ):
        raise ValueError("public release assets require an owner-approved RELEASED manifest")
    if (components.get("approval_status"), components.get("release_status")) != (
        "APPROVED_BY_OWNER", "RELEASED",
    ):
        raise ValueError("public release assets require released components")
    version = str(manifest.get("version", ""))
    if version != (root / "core/VERSION").read_text(encoding="utf-8").strip():
        raise ValueError("public release version differs from core/VERSION")

    proof = read_json(root / "release-proof.json")
    if proof.get("version") != version or proof.get("release_status") != "RELEASED":
        raise ValueError("release proof is stale or is not public")

    notes_source = root / "docs/releases" / ("RELEASE-NOTES-v" + version + ".md")
    vet_source = root / "docs/releases" / ("VET-v" + version + ".md")
    for source in (notes_source, vet_source):
        if source.is_symlink() or not source.is_file():
            raise ValueError("public release evidence is missing: " + str(source.relative_to(root)))

    output.mkdir(parents=True, exist_ok=True)
    workspace_name = "ai-human-workspace-" + version + ".zip"
    company_name = "kairali-company-rollout-" + version + ".zip"
    notes_name = notes_source.name
    vet_name = vet_source.name
    workspace_files = collect_files(root, root, IGNORED_PARTS)
    company_root = root / "packages/kairali"
    company_files = collect_files(company_root, company_root, {"__pycache__"})

    workspace_path = output / workspace_name
    company_path = output / company_name
    write_archive(workspace_path, "ai-human-workspace-" + version, workspace_files)
    write_archive(company_path, "kairali-company-rollout-" + version, company_files)
    verify_archive(workspace_path, "ai-human-workspace-" + version, len(workspace_files))
    verify_archive(company_path, "kairali-company-rollout-" + version, len(company_files))

    shutil.copyfile(root / "release-proof.json", output / "release-proof.json")
    shutil.copyfile(notes_source, output / notes_name)
    shutil.copyfile(vet_source, output / vet_name)
    names = [workspace_name, company_name, "release-proof.json", notes_name, vet_name]
    (output / "SHA256SUMS").write_text(
        "".join(sha256(output / name) + "  " + name + "\n" for name in names),
        encoding="utf-8",
    )

    expected = set(names) | {"SHA256SUMS"}
    actual = {path.name for path in output.iterdir() if path.is_file()}
    if actual != expected:
        raise ValueError("public release output inventory differs from the six governed assets")
    print("AI-HUMAN PUBLIC RELEASE ASSET BUILD: PASS")
    print("- version: " + version)
    print("- workspace files: " + str(len(workspace_files)))
    print("- Kairali company files: " + str(len(company_files)))
    for name in sorted(expected):
        print("- " + sha256(output / name) + "  " + name)


def main():
    parser = argparse.ArgumentParser(description="Build deterministic public release assets")
    parser.add_argument("root", nargs="?", default=str(ROOT))
    parser.add_argument("--output")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    version = (root / "core/VERSION").read_text(encoding="utf-8").strip()
    output = Path(args.output).resolve() if args.output else root / "dist" / ("v" + version + "-public-release")
    build(root, output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
