#!/usr/bin/env python3
"""Bounded CI on a pinned export; no release, deployment, secrets or fleet writes."""

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import zipfile


CANDIDATE = "bb559d7a764d50e5c53ea6171e3af3849cab4c20"
TREE = "fff977a11d42e041585dd659be9eac2a2ca37d89"
RUNTIME = "827bad01c2a2c6ffce3e85b3bbb705a6ada3c45ee1566981060b432baf504ade"
REPO = Path(__file__).resolve().parents[2]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root):
    result = {}
    for path in sorted(root.rglob("*")):
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        if path.is_symlink():
            raise RuntimeError("unexpected payload symlink")
        if path.is_file():
            result[path.relative_to(root).as_posix()] = sha256(path)
    return result


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    if not args.prepare_only and (sys.platform != "win32" or os.environ.get("GITHUB_ACTIONS") != "true"):
        parser.error("execution requires a real GitHub Actions Windows runner")
    tree = subprocess.check_output(["git", "rev-parse", CANDIDATE + "^{tree}"], cwd=REPO, text=True).strip()
    if tree != TREE:
        raise RuntimeError("candidate tree mismatch")
    base = Path(tempfile.mkdtemp(prefix="ai-human-windows-ci-", dir=os.environ.get("RUNNER_TEMP")))
    source = base / "source"
    archive = base / "candidate.zip"
    subprocess.run(["git", "archive", "--format=zip", "--output=" + str(archive), CANDIDATE], cwd=REPO, check=True)
    with zipfile.ZipFile(archive) as bundle:
        bundle.extractall(source)
    if sha256(source / "scripts/ai_human.py") != RUNTIME:
        raise RuntimeError("candidate runtime mismatch")
    for name in ("release-manifest.json", "component-manifest.json"):
        value = json.loads((source / name).read_text(encoding="utf-8"))
        if (value.get("approval_status"), value.get("release_status")) != ("LOCAL_BUILD_ONLY", "LOCAL_BUILD_ONLY"):
            raise RuntimeError("candidate must remain unreleased")
    if json.loads((source / "release-manifest.json").read_text(encoding="utf-8")).get("automatic_update_eligible") is not False:
        raise RuntimeError("candidate cannot enable automatic updates")
    receipt = {
        "schema": "ai-human.windows-ci/v1", "candidate_commit": CANDIDATE,
        "candidate_tree": TREE, "runtime_sha256": RUNTIME,
        "ci_commit": os.environ.get("GITHUB_SHA"),
        "run_id": os.environ.get("GITHUB_RUN_ID"),
        "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "platform": platform.platform(), "python": sys.version,
        "image_os": os.environ.get("ImageOS"), "image_version": os.environ.get("ImageVersion"),
        "started_utc": now(), "steps": [], "status": "RUNNING",
        "release_approval": False, "desktop_onboarding_proof": False,
        "native_scheduler_integration_proof": False,
        "limitations": ["Hosted administrator account with UAC disabled", "Native scheduler fixtures remain simulated"],
    }
    print("CI evidence directory: " + str(base), flush=True)

    def run(label, argv, timeout=180):
        step = {"label": label, "argv": argv, "started_utc": now()}
        receipt["steps"].append(step)
        print("STEP " + label, flush=True)
        result = subprocess.run(argv, cwd=source, timeout=timeout, check=False)
        step.update(exit_code=result.returncode, ended_utc=now())
        if result.returncode:
            raise RuntimeError(label + " failed with exit " + str(result.returncode))

    try:
        original = inventory(source)
        if not args.prepare_only:
            run("pinned-prerequisites", [sys.executable, "-m", "pip", "install", "--require-hashes", "-r", "requirements.txt"])
        run("build-test-editions", [sys.executable, "scripts/build_editions.py", "."])
        run("build-test-proof", [sys.executable, "scripts/build_release.py", "."])
        built = inventory(source)
        changes = sorted(name for name in set(original) | set(built) if original.get(name) != built.get(name))
        receipt["packaging_changed_paths"] = changes
        for name in changes:
            if name != "release-proof.json" and not (
                name.startswith("portal/public/downloads/") and name.endswith((".zip", ".zip.sha256"))
            ):
                raise RuntimeError("packaging unexpectedly changed " + name)
        run("validate-before", [sys.executable, "scripts/validate_release.py", ".", "--candidate"])
        if not args.prepare_only:
            try:
                run("lifecycle-suite", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], timeout=1500)
            finally:
                receipt["payload_unchanged"] = inventory(source) == built
                run("validate-after", [sys.executable, "scripts/validate_release.py", ".", "--candidate"])
        run("compile", [sys.executable, "-m", "compileall", "-q", "scripts", "tests"])
        receipt["payload_unchanged"] = inventory(source) == built
        if not receipt["payload_unchanged"]:
            raise RuntimeError("test changed candidate payload")
        receipt["built_inventory_sha256"] = hashlib.sha256(json.dumps(built, sort_keys=True).encode()).hexdigest()
        receipt["built_file_count"] = len(built)
        receipt["status"] = "PREPARATION_ONLY_PASS" if args.prepare_only else "WINDOWS_AUTOMATED_PASS_NOT_RELEASE_APPROVAL"
    except Exception as error:
        receipt["status"] = "FAIL"
        receipt["error"] = str(error)
        raise
    finally:
        receipt["ended_utc"] = now()
        encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
        (base / "RECEIPT.json").write_text(encoded, encoding="utf-8")
        print("BEGIN_AI_HUMAN_CI_RECEIPT\n" + encoded + "END_AI_HUMAN_CI_RECEIPT", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
