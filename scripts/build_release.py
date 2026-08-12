#!/usr/bin/env python3
"""Refresh release hashes and create a deterministic release proof."""

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path, value):
    temp = path.with_name(path.name + ".build-temp")
    temp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(path)


def main():
    parser = argparse.ArgumentParser(description="Build AI-Human release integrity data")
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    manifest_path = root / "release-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for record in manifest["managed_files"]:
        record["sha256"] = sha256(root / record["source"])
    atomic_json(manifest_path, manifest)

    included = {}
    ignored_parts = {".git", ".pytest_cache", "__pycache__", "dist"}
    for path in sorted(root.rglob("*")):
        if (
            not path.is_file()
            or any(part in ignored_parts for part in path.parts)
            or path.name == "release-proof.json"
            or path.suffix == ".pyc"
            or path.name.endswith((".write-temp", ".update-temp", ".build-temp"))
        ):
            continue
        included[str(path.relative_to(root))] = sha256(path)
    proof = {
        "approval_status": manifest["approval_status"],
        "files": included,
        "repository": manifest["repository"],
        "schema": "ai-human.workspace-release-proof/v1",
        "version": manifest["version"],
    }
    atomic_json(root / "release-proof.json", proof)
    print("AI-HUMAN RELEASE BUILD: PASS")
    print("- version: " + manifest["version"])
    print("- managed hashes: " + str(len(manifest["managed_files"])))
    print("- proof files: " + str(len(included)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
