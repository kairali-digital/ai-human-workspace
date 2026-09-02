#!/usr/bin/env python3
"""Refresh release hashes and create a deterministic release proof."""

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path

from validate_release import (
    path_uses_symlink,
    portable_path,
    read_json,
    release_inventory,
    safe_relative,
)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_sha256(root):
    digest = hashlib.sha256()
    count = 0
    paths = sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix())
    for path in paths:
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8") + b"\0")
        digest.update(bytes.fromhex(sha256(path)) + b"\n")
        count += 1
    return digest.hexdigest(), count


def atomic_json(path, value):
    data = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    descriptor, temp_name = tempfile.mkstemp(prefix="." + path.name + ".", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def main():
    parser = argparse.ArgumentParser(description="Build AI-Human release integrity data")
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    manifest_path = root / "release-manifest.json"
    manifest = read_json(manifest_path)
    for record in manifest["managed_files"]:
        source = str(record.get("source", ""))
        if not safe_relative(source):
            raise ValueError("unsafe managed source: " + repr(source))
        if path_uses_symlink(root, source):
            raise ValueError("managed source may not use symbolic links: " + source)
        source_path = root / Path(portable_path(source))
        if not source_path.is_file():
            raise ValueError("managed source missing: " + source)
        record["sha256"] = sha256(source_path)
    atomic_json(manifest_path, manifest)

    component_path = root / "component-manifest.json"
    components = read_json(component_path)
    if components.get("version") != manifest.get("version"):
        raise ValueError("component and release manifest versions differ")
    if components.get("repository") != manifest.get("repository"):
        raise ValueError("component and release manifest repositories differ")
    for component in components["components"]:
        source = str(component.get("source", ""))
        if not safe_relative(source):
            raise ValueError("unsafe component source: " + repr(source))
        if path_uses_symlink(root, source):
            raise ValueError("component source may not use symbolic links: " + source)
        component_root = root / Path(portable_path(source))
        if not component_root.is_dir():
            raise ValueError("component source missing: " + source)
        digest, count = tree_sha256(component_root)
        component["tree_sha256"] = digest
        component["file_count"] = count
    atomic_json(component_path, components)

    included, inventory_failures = release_inventory(root)
    if inventory_failures:
        raise ValueError("; ".join(inventory_failures))
    proof = {
        "approval_status": manifest["approval_status"],
        "automatic_update_eligible": manifest.get("automatic_update_eligible", False),
        "files": included,
        "release_status": manifest.get("release_status", "RELEASED"),
        "repository": manifest["repository"],
        "schema": "ai-human.workspace-release-proof/v1",
        "version": manifest["version"],
    }
    atomic_json(root / "release-proof.json", proof)
    print("AI-HUMAN RELEASE BUILD: PASS")
    print("- version: " + manifest["version"])
    print("- managed hashes: " + str(len(manifest["managed_files"])))
    print("- component hashes: " + str(len(components["components"])))
    print("- proof files: " + str(len(included)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
