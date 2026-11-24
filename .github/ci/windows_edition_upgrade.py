"""Exercise the two 2.4.0 distribution ZIPs against a pinned 2.5.1 preview."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile


CANDIDATE = "17367141f9c03e41d02238ae481c10ee01fcf343"
STABLE_PACKAGES = {
    "AI-HUMAN-v240-REUSABLE-EDITION-PUBLIC-KIT.zip": "6bb4facccb68c70f1c99f20e6f5fd4eba80bb82f5e396983e69f8a12953a0f91",
    "KAIRALI-AI-HUMAN-v240-EMPLOYEE-EDITION-PUBLIC-KIT.zip": "44bf2035d2702d547f5895075d44d9abe4fb286cb489178cecc39ecfaf6b210c",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unpack(archive, expected_hash, directory):
    assert digest(archive) == expected_hash
    with zipfile.ZipFile(archive) as payload:
        directories = {name.split("/")[0] for name in payload.namelist()}
        assert len(directories) == 1
        payload.extractall(directory)
    return directory / directories.pop() / "workspace"


def exercise(helper, old, new, directory, preview_hash):
    worker = (directory / "worker").resolve()
    def run(source, command, *args, refuse=None):
        result = subprocess.run(
            [sys.executable, "-I", "-B", str(source / "scripts/ai_human.py"),
             command, str(worker), *map(str, args)],
            cwd=directory, capture_output=True, text=True, timeout=120,
        )
        if refuse:
            assert result.returncode and refuse in result.stdout + result.stderr, result
        else:
            assert result.returncode == 0, result.stdout + result.stderr

    helper.base = directory
    helper.profile_counter = 0
    run(old, "install", "--source", old, *helper.required_install_arguments(),
        "--worker-id", "edition-qa", "--timezone", "UTC", "--supervisor", "QA supervisor")
    run(old, "validate")
    (worker / "fixture-note.txt").write_text("Synthetic employee-owned file\n", encoding="utf-8")

    def inventory(owned_only=False):
        files = (path for path in worker.rglob("*") if path.is_file())
        return {str(path.relative_to(worker)): digest(path) for path in files
                if not owned_only or path.relative_to(worker).parts[0] != ".ai-human"}

    baseline = inventory()
    run(old, "update", "--source", new, refuse="unsupported release manifest schema")
    assert inventory() == baseline
    manifest = new / "release-manifest.json"
    assert digest(manifest) == preview_hash
    run(new, "update", "--source", new, "--source-manifest-sha256", preview_hash,
        refuse="local candidate")
    assert inventory() == baseline

    # Change only a disposable extracted fixture. The committed ZIP remains a preview.
    raw = manifest.read_bytes()
    metadata = json.loads(raw)
    assert metadata["version"] == "2.5.1" and metadata["automatic_update_eligible"] is False
    assert metadata["repository"] == json.loads((old / "release-manifest.json").read_bytes())["repository"]
    metadata.update(approval_status="APPROVED_BY_OWNER", release_status="RELEASED")
    manifest.write_bytes((json.dumps(metadata, indent=2, sort_keys=True) + "\n").encode())
    try:
        run(new, "update", "--source", new, "--source-manifest-sha256", preview_hash, refuse="approved SHA-256")
        assert inventory() == baseline
        owned = inventory(owned_only=True)
        run(new, "update", "--source", new, "--source-manifest-sha256", digest(manifest))
        assert (worker / ".ai-human/VERSION").read_text(encoding="utf-8").strip() == "2.5.1"
        run(new, "validate")
        backup = json.loads((worker / ".ai-human/update-receipt.json").read_bytes())["backup"]
        assert Path(backup).is_dir() and inventory(owned_only=True) == owned
        run(new, "rollback", "--source", old, "--version", "2.4.0", "--at-checkpoint")
        run(old, "validate")
        assert (worker / ".ai-human/VERSION").read_text(encoding="utf-8").strip() == "2.4.0"
        assert inventory(owned_only=True) == owned
        return len(owned)
    finally:
        manifest.write_bytes(raw)


def main():
    source = Path(sys.argv[1]).resolve()
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip() == CANDIDATE
    assert not sys.flags.optimize
    sys.path.insert(0, str(source / "tests"))
    import test_lifecycle as fixtures
    records = json.loads((source / "portal/content/v251-edition-integrity.json").read_bytes())
    downloads = source / "portal/public/downloads"
    for stable, checksum in STABLE_PACKAGES.items():
        preview = stable.replace("v240", "v251").replace("PUBLIC-KIT", "LOCAL-CANDIDATE")
        record = records[preview]
        with tempfile.TemporaryDirectory(prefix="edition-qa-") as temp:
            directory = Path(temp).resolve()
            old = unpack(downloads / stable, checksum, directory / "old")
            new = unpack(downloads / preview, record["archive_sha256"], directory / "new")
            count = exercise(fixtures.LifecycleTests(), old, new, directory, record["manifest_sha256"])
            print("EDITION_QA", json.dumps(dict(candidate=CANDIDATE, archive=preview, sha256=record["archive_sha256"],
                                                source_version="2.4.0", restored_version="2.4.0", preserved=count,
                                                platform=sys.platform)), flush=True)


if __name__ == "__main__":
    main()
