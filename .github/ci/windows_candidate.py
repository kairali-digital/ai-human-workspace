#!/usr/bin/env python3
"""Four exhaustive CI shards on one pinned export; never release or deploy."""

import argparse
import base64
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import traceback
import unittest
import zipfile


# Update all five candidate pins together after freezing a new product commit.
CANDIDATE = "5fa38f65d0bc9b4650968159e102f823866c740c"
TREE = "726a091e8cf1f282133a55cfef9565f8d698914d"
RUNTIME = "7ac940131ad6ac684c6772558fe448cf4258879be15dd2236a1c9a2053c1147d"
EXPECTED_TEST_COUNT = 237
EXPECTED_SUITE_SHA256 = "a1a12bf5b12e34839f84dfa9ee35e27e1470b9689d295ea9e5f0b2dd597fe944"
SHARD_COUNT = 4
# These POSIX-only tests are inapplicable on this Windows runner. Discovery uses
# start_dir=tests, so canonical IDs start with test_private_files, not tests.
# Existing lifecycle checks and all NativeWindowsPrivateFileTests must execute.
ALLOWED_WINDOWS_SKIP_IDS = frozenset({
    "test_private_files.PrivateFileTests.test_posix_mode_and_tampering_without_windows_calls",
    "test_private_files.PrivateFileTests.test_posix_preexisting_symlink_and_hardlink_refused",
})
REPO = Path(__file__).resolve().parents[2]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


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


def ids_sha256(ids):
    """Hash ordered UTF-8 IDs, each followed by exactly one LF."""
    return hashlib.sha256(("\n".join(ids) + "\n").encode("utf-8")).hexdigest()


def test_plan(ids, shard):
    ids = sorted(ids)
    if not ids or len(ids) != len(set(ids)) or any("\n" in name or "\r" in name for name in ids):
        raise RuntimeError("empty, duplicate or invalid discovered test IDs")
    digest = ids_sha256(ids)
    if len(ids) != EXPECTED_TEST_COUNT or digest != EXPECTED_SUITE_SHA256:
        raise RuntimeError("discovered suite pin mismatch: count=" + str(len(ids)) + " sha256=" + digest)
    shards = [ids[index::SHARD_COUNT] for index in range(SHARD_COUNT)]
    flattened = [name for group in shards for name in group]
    if any(not group for group in shards) or sorted(flattened) != ids or len(set(flattened)) != len(ids):
        raise RuntimeError("shards must be nonempty, exhaustive and disjoint")
    return {
        "assignment": "sort test.id() lexicographically; zero-based position modulo 4",
        "id_digest_encoding": "UTF-8; one LF after every ID; ordered as logged",
        "suite_test_ids": ids, "suite_count": len(ids), "suite_sha256": digest,
        "shard_index": shard, "shard_count": SHARD_COUNT,
        "shard_test_ids": shards[shard], "shard_test_count": len(shards[shard]),
        "shard_sha256": ids_sha256(shards[shard]),
        "all_shard_counts": [len(group) for group in shards],
        "all_shard_sha256": [ids_sha256(group) for group in shards],
        "exhaustive_disjoint_assignment": True,
    }


def flatten_suite(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from flatten_suite(test)
        else:
            yield test


class TrackedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.started_ids = []
        self.finished_ids = []
        self.success_ids = []

    def startTest(self, test):
        self.started_ids.append(test.id())
        super().startTest(test)

    def stopTest(self, test):
        self.finished_ids.append(test.id())
        super().stopTest(test)

    def addSuccess(self, test):
        self.success_ids.append(test.id())
        super().addSuccess(test)


def child(source, shard, result_path, discover_only):
    evidence = {"status": "FAIL", "started_utc": now()}
    exit_code = 1
    try:
        os.chdir(source)
        sys.path.insert(0, str(source))
        loader = unittest.TestLoader()
        tests = list(flatten_suite(loader.discover(str(source / "tests"), pattern="test*.py")))
        if loader.errors:
            raise RuntimeError("unittest discovery failed: " + "\n".join(loader.errors))
        plan = test_plan([test.id() for test in tests], shard)
        evidence["plan"] = plan
        print("SUITE_SHA256 " + plan["suite_sha256"], flush=True)
        for name in plan["suite_test_ids"]:
            print("SUITE_TEST_ID " + name, flush=True)
        print("SHARD " + str(shard) + " SHA256 " + plan["shard_sha256"], flush=True)
        for name in plan["shard_test_ids"]:
            print("SHARD_TEST_ID " + name, flush=True)
        if discover_only:
            evidence["status"] = "DISCOVERY_ONLY"
            exit_code = 0
        else:
            by_id = {test.id(): test for test in tests}
            selected = unittest.TestSuite(by_id[name] for name in plan["shard_test_ids"])
            result = unittest.TextTestRunner(
                stream=sys.stdout, verbosity=2, failfast=False, resultclass=TrackedResult,
            ).run(selected)
            unexpected_skips = [test.id() for test, _ in result.skipped if test.id() not in ALLOWED_WINDOWS_SKIP_IDS]
            evidence.update(
                tests_run=result.testsRun, started_test_ids=result.started_ids,
                finished_test_ids=result.finished_ids,
                passed_test_ids=result.success_ids, passed_test_count=len(result.success_ids),
                executed_test_count=result.testsRun - len(result.skipped),
                skipped_test_count=len(result.skipped),
                allowed_platform_skip_ids=sorted(ALLOWED_WINDOWS_SKIP_IDS),
                unexpected_skip_ids=unexpected_skips,
                failure_record_count=len(result.failures), error_record_count=len(result.errors),
                failures=[test.id() for test, _ in result.failures],
                errors=[test.id() for test, _ in result.errors],
                skipped=[{"test_id": test.id(), "reason": reason} for test, reason in result.skipped],
                expected_failures=[test.id() for test, _ in result.expectedFailures],
                unexpected_successes=[test.id() for test in result.unexpectedSuccesses],
            )
            complete = (
                result.testsRun == plan["shard_test_count"]
                and result.started_ids == plan["shard_test_ids"]
                and result.finished_ids == plan["shard_test_ids"]
            )
            evidence["all_assigned_tests_finished"] = complete
            if not complete or not result.wasSuccessful() or unexpected_skips or result.expectedFailures:
                raise RuntimeError("shard failed, skipped an undeclared check, or did not finish every assigned test")
            evidence["status"] = "SHARD_PASS_NOT_FULL_SUITE_OR_RELEASE_APPROVAL"
            exit_code = 0
    except Exception as error:
        evidence["error"] = str(error)
        print(traceback.format_exc(), end="", flush=True)
    finally:
        evidence["ended_utc"] = now()
        result_path.write_bytes((json.dumps(evidence, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    return exit_code


def emit_receipt(receipt, base):
    receipt["ended_utc"] = now()
    encoded = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if base is not None:
        try:
            (base / "RECEIPT.json").write_bytes(encoded)
        except OSError as error:
            receipt["status"] = "FAIL"
            receipt["errors"].append("receipt write failed: " + str(error))
            encoded = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8")
    digest = hashlib.sha256(encoded).hexdigest()
    body = base64.b64encode(encoded).decode("ascii")
    chunks = [body[index:index + 1536] for index in range(0, len(body), 1536)]
    # All child output has finished. Bounded numbered lines avoid log-line truncation;
    # decode joined chunks and verify the byte digest before trusting the JSON.
    print("BEGIN_AI_HUMAN_CI_RECEIPT_V2 " + json.dumps({
        "encoding": "base64", "chunks": len(chunks), "sha256": digest,
        "shard_index": receipt["shard_index"], "candidate_commit": CANDIDATE,
    }, sort_keys=True), flush=True)
    for index, chunk in enumerate(chunks):
        print("AI_HUMAN_CI_RECEIPT_V2_CHUNK " + str(index) + " " + chunk, flush=True)
    print("END_AI_HUMAN_CI_RECEIPT_V2 " + digest, flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard", type=int, choices=range(SHARD_COUNT), required=True)
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--repository", type=Path, default=REPO, help="local preparation only")
    parser.add_argument("--child-source", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--child-result", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--discover-only", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.child_source is not None:
        if args.child_result is None:
            parser.error("child result path is required")
        if not args.discover_only and (sys.platform != "win32" or os.environ.get("GITHUB_ACTIONS") != "true"):
            parser.error("test execution requires a real GitHub Actions Windows runner")
        return child(args.child_source.resolve(), args.shard, args.child_result.resolve(), args.discover_only)
    if args.discover_only or args.child_result is not None:
        parser.error("child-only arguments need --child-source")
    receipt = {
        "schema": "ai-human.windows-ci/v2", "candidate_commit": CANDIDATE,
        "candidate_tree": TREE, "runtime_sha256": RUNTIME,
        "expected_test_count": EXPECTED_TEST_COUNT, "expected_suite_sha256": EXPECTED_SUITE_SHA256,
        "allowed_windows_skip_ids": sorted(ALLOWED_WINDOWS_SKIP_IDS),
        "shard_index": args.shard, "shard_count": SHARD_COUNT,
        "ci_commit": os.environ.get("GITHUB_SHA"), "run_id": os.environ.get("GITHUB_RUN_ID"),
        "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "platform": platform.platform(), "python": sys.version,
        "image_os": os.environ.get("ImageOS"), "image_version": os.environ.get("ImageVersion"),
        "started_utc": now(), "steps": [], "errors": [], "status": "RUNNING",
        "release_approval": False, "desktop_onboarding_proof": False,
        "native_scheduler_integration_proof": False, "full_suite_proof": False,
        "limitations": [
            "Hosted administrator account with UAC disabled",
            "Native scheduler fixtures remain simulated",
            "Full automated suite requires four passing receipts from this run attempt with matching candidate and suite pins",
        ],
    }
    base = None

    def run(label, argv, cwd, timeout=180):
        step = {"label": label, "argv": argv, "started_utc": now()}
        receipt["steps"].append(step)
        print("STEP " + label, flush=True)
        log = base / (label + ".log")
        try:
            # Redirect both child streams to the same private file, then replay them
            # before the receipt. No asynchronous stderr can split receipt chunks.
            with log.open("wb") as output:
                result = subprocess.run(argv, cwd=cwd, stdout=output, stderr=subprocess.STDOUT,
                                        timeout=timeout, check=False)
            step["exit_code"] = result.returncode
            if result.returncode:
                raise RuntimeError(label + " failed with exit " + str(result.returncode))
        except subprocess.TimeoutExpired:
            step["timed_out"] = True
            raise RuntimeError(label + " exceeded " + str(timeout) + " seconds") from None
        finally:
            step["ended_utc"] = now()
            if log.exists():
                step["log_sha256"] = sha256(log)
                print(log.read_bytes().decode("utf-8", errors="replace"), end="", flush=True)

    def checked(label, operation):
        try:
            operation()
        except Exception as error:
            receipt["errors"].append(label + ": " + str(error))

    try:
        if not args.prepare_only and (sys.platform != "win32" or os.environ.get("GITHUB_ACTIONS") != "true"):
            raise RuntimeError("execution requires a real GitHub Actions Windows runner")
        if not args.prepare_only and args.repository.resolve() != REPO:
            raise RuntimeError("repository override is permitted only for local preparation")
        base = Path(tempfile.mkdtemp(prefix="ai-human-windows-ci-", dir=os.environ.get("RUNNER_TEMP")))
        source, archive = base / "source", base / "candidate.zip"
        print("CI evidence directory: " + str(base), flush=True)
        run("candidate-tree", ["git", "rev-parse", CANDIDATE + "^{tree}"], args.repository)
        if (base / "candidate-tree.log").read_text(encoding="utf-8").strip() != TREE:
            raise RuntimeError("candidate tree mismatch")
        run("candidate-export", ["git", "archive", "--format=zip", "--output=" + str(archive), CANDIDATE], args.repository)
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
        original = inventory(source)
        if not args.prepare_only:
            run("pinned-prerequisites", [sys.executable, "-m", "pip", "install", "--require-hashes", "-r", "requirements.txt"], source)
        run("build-test-editions", [sys.executable, "scripts/build_editions.py", "."], source)
        run("build-test-proof", [sys.executable, "scripts/build_release.py", "."], source)
        built = inventory(source)
        changes = sorted(name for name in set(original) | set(built) if original.get(name) != built.get(name))
        receipt["packaging_changed_paths"] = changes
        for name in changes:
            if name != "release-proof.json" and not (
                name.startswith("portal/public/downloads/") and name.endswith((".zip", ".zip.sha256"))
            ):
                raise RuntimeError("packaging unexpectedly changed " + name)
        receipt["built_inventory_sha256"] = hashlib.sha256(json.dumps(built, sort_keys=True).encode()).hexdigest()
        receipt["built_file_count"] = len(built)
        run("validate-before", [sys.executable, "scripts/validate_release.py", ".", "--candidate"], source)
        discovery_path = base / "DISCOVERY.json"
        command = [sys.executable, str(Path(__file__).resolve()), "--shard", str(args.shard), "--child-source", str(source)]
        run("discover-suite", command + ["--child-result", str(discovery_path), "--discover-only"], source)
        discovery = json.loads(discovery_path.read_text(encoding="utf-8"))
        receipt["test_plan"] = discovery["plan"]
        if discovery["status"] != "DISCOVERY_ONLY" or discovery["plan"] != test_plan(discovery["plan"]["suite_test_ids"], args.shard):
            raise RuntimeError("invalid discovery receipt")
        if not args.prepare_only:
            shard_path = base / "SHARD.json"
            checked("lifecycle-shard", lambda: run("lifecycle-shard", command + ["--child-result", str(shard_path)], source, timeout=1500))

            def check_shard():
                result = json.loads(shard_path.read_text(encoding="utf-8"))
                receipt["test_result"] = result
                if result.get("plan") != receipt["test_plan"]:
                    raise RuntimeError("execution discovered a different test plan")
                if result.get("status") != "SHARD_PASS_NOT_FULL_SUITE_OR_RELEASE_APPROVAL" or result.get("all_assigned_tests_finished") is not True:
                    raise RuntimeError("shard did not prove completion with only declared platform skips")

            checked("shard-result", check_shard)
        receipt["payload_unchanged_before_validation"] = inventory(source) == built
        if not receipt["payload_unchanged_before_validation"]:
            receipt["errors"].append("discovery or tests changed candidate payload")
        checked("validate-after", lambda: run("validate-after", [sys.executable, "scripts/validate_release.py", ".", "--candidate"], source))
        checked("compile", lambda: run("compile", [sys.executable, "-m", "compileall", "-q", "scripts", "tests"], source))
        receipt["payload_unchanged"] = inventory(source) == built
        if not receipt["payload_unchanged"]:
            receipt["errors"].append("candidate payload changed")
        receipt["status"] = "FAIL" if receipt["errors"] else (
            "PREPARATION_ONLY_PASS" if args.prepare_only else "WINDOWS_SHARD_PASS_NOT_FULL_SUITE_OR_RELEASE_APPROVAL"
        )
    except Exception as error:
        receipt["status"] = "FAIL"
        receipt["errors"].append(str(error))
        print(traceback.format_exc(), end="", flush=True)
    finally:
        emit_receipt(receipt, base)
    # Do not re-raise after receipt output: traceback stderr corrupted the first run.
    return 1 if receipt["status"] == "FAIL" else 0


if __name__ == "__main__":
    sys.stderr = sys.stdout
    raise SystemExit(main())
