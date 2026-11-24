"""Exercise the installed updater in one disposable GitHub Windows worker."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def main():
    if sys.platform != "win32" or os.getenv("GITHUB_ACTIONS") != "true":
        raise RuntimeError("Requires a disposable Windows Actions runner")
    source = Path(sys.argv[1]).resolve()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
    if commit != "699b7c16deb1768d2a07a2e9392e1b955d8be8ed":
        raise RuntimeError("Candidate differs from the approved Windows source")
    sys.path.insert(0, str(source / "tests"))
    import test_lifecycle as fixtures

    api = fixtures.AI_HUMAN
    fixture = fixtures.LifecycleTests()
    fixture.setUp()
    worker = (fixture.base / "native-ci-worker").resolve()
    try:
        # Only this disposable source gets the synthetic approval state.
        manifest = api.read_json(fixture.release / "release-manifest.json")
        actual = api.read_json(source / "release-manifest.json")
        manifest.update(schema=actual["schema"], supported_platforms=actual["supported_platforms"])
        api.atomic_json(fixture.release / "release-manifest.json", manifest)
        fixture.run_cli("install", worker, "--source", fixture.release,
                        *fixture.required_install_arguments(), "--worker-id", "native-ci-worker",
                        "--timezone", "UTC")
        runner = worker / ".ai-human/bin/ai_human.py"
        runtime_hash = hashlib.sha256(runner.read_bytes()).hexdigest()
        if runtime_hash != "0b270069b660728ac45a1194e7ceb4b4b05e301c966c65a1cc355b85ef60933b":
            raise RuntimeError("Installed runtime digest differs")
        def cli(*args):
            return subprocess.run([sys.executable, "-I", str(runner), args[0],
                                   str(worker), *args[1:]], check=True, timeout=60)
        schedule_id = api.expected_update_schedule_id(worker, api.install_metadata(worker))
        task = api.native_update_external_id({"platform": "WINDOWS", "schedule_id": schedule_id})
        def query():
            return subprocess.run(["schtasks", "/Query", "/TN", task, "/XML"],
                                  capture_output=True, text=True, timeout=15)
        if not api.windows_task_missing(query()):
            raise RuntimeError("Could not establish task absence before testing")
        if subprocess.check_output(["tzutil", "/g"], text=True).strip() != "UTC":
            raise RuntimeError("Runner time zone is outside this test fixture")
        now = datetime.datetime.now(datetime.timezone.utc)
        due = (now + datetime.timedelta(minutes=2)).replace(second=0, microsecond=0)
        cursor = worker / "MASTER_CURSOR.md"
        original = cursor.read_bytes()
        baseline = fixtures.state_hashes(worker)
        try:
            cli("update-schedule-configure", "--platform", "WINDOWS", "--cadence", "WEEKLY",
                "--weekday", due.strftime("%A").upper(), "--local-time", due.strftime("%H:%M"),
                "--timezone", "UTC", "--native-timezone-id", "UTC",
                "--confirm-native-timezone-matches-iana", "--rollout-lane", "GENERAL",
                "--approval-reference", "Disposable Windows QA", "--max-retry-attempts", "1")
            cli("update-schedule-show", "--verify-native")
            print("WINDOWS_QA registration and native definition verified", flush=True)
            api.atomic_text(cursor, "# QA\n\n## LIVE TASK\nTask ID: `NATIVE-QA`\nSynthetic busy worker.\n")
            if not api.live_task(worker):
                raise RuntimeError("Synthetic live task missing")
            report = worker / ".ai-human/version-report.json"
            deadline = time.monotonic() + 205
            while time.monotonic() < deadline:
                if report.is_file() and api.read_json(report).get("reason") == "LIVE_TASK":
                    break
                time.sleep(1)
            else:
                raise RuntimeError("No due-time live-task deferral from the native scheduler")
            cursor.write_bytes(original)
            for action in ("PAUSE", "RESUME"):
                cli("update-schedule-control", action, "--approval-reference", "Disposable QA")
                cli("update-schedule-show", "--verify-native")
        finally:
            cursor.write_bytes(original)
            try:
                if (worker / api.UPDATE_SCHEDULE_TRANSACTION_PATH).exists():
                    cli("recover-update-schedule")
                if api.update_schedule_config(worker).get("status") in ("ENABLED", "PAUSED"):
                    cli("update-schedule-control", "REMOVE", "--approval-reference", "Disposable QA")
            finally:
                absent = api.windows_task_missing(query())
                print("WINDOWS_QA final task absence " + str(absent), flush=True)
                if not absent:
                    raise RuntimeError("Task cleanup could not be verified")
        cli("validate")
        if fixtures.state_hashes(worker) != baseline:
            raise RuntimeError("Worker-owned state changed")
        print(json.dumps({"result": "PASS", "candidate": commit, "runtime": runtime_hash,
                          "native_due": "LIVE_TASK", "pause_resume": True, "cleanup": True}))
    finally:
        fixture.tearDown()


if __name__ == "__main__":
    main()
