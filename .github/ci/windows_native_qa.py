"""Exercise the installed updater in one disposable GitHub Windows worker."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import xml.etree.ElementTree as ET


def main():
    if sys.platform != "win32" or os.getenv("GITHUB_ACTIONS") != "true":
        raise RuntimeError("Requires a disposable Windows Actions runner")
    source = Path(sys.argv[1]).resolve()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
    if commit != "17367141f9c03e41d02238ae481c10ee01fcf343":
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
        if runtime_hash != "711e456f32b590d82dbc46fd135eca3d41cff04dd6c694d5e122ed2fee7982f7":
            raise RuntimeError("Installed runtime digest differs")
        def cli(*args):
            return subprocess.run([sys.executable, "-I", str(runner), args[0],
                                   str(worker), *args[1:]], check=True, timeout=60)
        schedule_id = api.expected_update_schedule_id(worker, api.install_metadata(worker))
        task = api.native_update_external_id({"platform": "WINDOWS", "schedule_id": schedule_id})
        def query():
            return subprocess.run(["schtasks", "/Query", "/TN", task, "/XML"],
                                  capture_output=True, text=True, timeout=15)
        def lookup_probe():
            # Read-only controls on the concrete disposable SDK task and its folder.
            script = r"""
$ErrorActionPreference = 'Stop'
$service = New-Object -ComObject 'Schedule.Service'
$service.Connect()
$root = $service.GetFolder('\')
if ($root.Path -ne '\') { throw 'Unexpected root folder' }
try {
    $folder = $service.GetFolder('\AI-Human')
    Write-Output 'folder=present'
    $registered = $folder.GetTask($env:AIH_QA_LEAF)
    Write-Output ('task=present;state=' + $registered.State)
} catch {
    Write-Output ('lookup_hresult=' + $_.Exception.GetBaseException().HResult)
}
"""
            leaf = task.rsplit("\\", 1)[-1]
            probe = subprocess.run(["powershell.exe", "-NoLogo", "-NoProfile", "-NonInteractive",
                                    "-Command", script], env={**os.environ, "AIH_QA_LEAF": leaf},
                                   capture_output=True, text=True, timeout=20, check=True)
            plain = subprocess.run(["schtasks.exe", "/Query", "/TN", task, "/FO", "CSV", "/NH"],
                                   capture_output=True, text=True, timeout=15)
            print("WINDOWS_QA independent lookup", repr(probe.stdout.strip()), "plain query",
                  plain.returncode, repr(plain.stderr.strip()), flush=True)

        lookup_probe()
        if not api.windows_task_missing(query(), task):
            raise RuntimeError("Could not establish task absence before testing")
        if subprocess.check_output(["tzutil", "/g"], text=True).strip() != "UTC":
            raise RuntimeError("Runner time zone is outside this test fixture")
        now = datetime.datetime.now(datetime.timezone.utc)
        due = (now + datetime.timedelta(minutes=2)).replace(second=0, microsecond=0)
        cursor = worker / "MASTER_CURSOR.md"
        original = cursor.read_bytes()
        baseline = fixtures.state_hashes(worker)
        automations = worker / "AUTOMATIONS.md"
        original_register = automations.read_text(encoding="utf-8")
        row_id = "SYSTEM-MONTHLY-UPDATE-001"
        initial_row, = [r for r in api.parse_table_rows(automations) if r and r[0] == row_id]
        created_here = False
        try:
            # Observe the native registration diagnostic on this disposable runner.
            # The wrapper only logs a failing command and returns its original result.
            real_run = subprocess.run
            def observed_run(argv, *args, **kwargs):
                nonlocal created_here
                result = real_run(argv, *args, **kwargs)
                if argv[:2] == ["schtasks.exe", "/Create"] and result.returncode == 0:
                    created_here = True
                    exported = query()
                    if exported.returncode == 0:
                        root = ET.fromstring(exported.stdout)
                        for node in root.iter():
                            tag = node.tag.split("}")[-1]
                            if tag in {"UserId", "Author", "Command", "Arguments", "URI", "Description"}:
                                node.text = "REDACTED"
                        print("WINDOWS_QA exported task:", ET.tostring(root, encoding="unicode"), flush=True)
                if result.returncode and argv[:2] == ["schtasks.exe", "/Create"]:
                    print("WINDOWS_QA schtasks register:", result.returncode, result.stderr, flush=True)
                return result
            from unittest.mock import patch
            with patch.object(subprocess, "run", observed_run):
                api.update_schedule_configure(fixture.schedule_args(
                    worker, platform="WINDOWS", cadence="WEEKLY", weekday=due.strftime("%A").upper(),
                    local_time=due.strftime("%H:%M"), timezone="UTC", native_timezone_id="UTC",
                    rollout_lane="GENERAL", max_retry_attempts=1))
            cli("update-schedule-show", "--verify-native")
            print("WINDOWS_QA registration and native definition verified", flush=True)
            lookup_probe()
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
                lookup_probe()
                final_query = query()
                if final_query.returncode:
                    print("WINDOWS_QA final query diagnostic", final_query.returncode, repr(final_query.stderr),
                          repr(final_query.stdout), flush=True)
                absent = api.windows_task_missing(final_query, task)
                print("WINDOWS_QA final task absence " + str(absent), flush=True)
                if not absent:
                    if created_here:
                        subprocess.run(["schtasks.exe", "/Delete", "/TN", task, "/F"],
                                       capture_output=True, check=True, timeout=15)
                        print("WINDOWS_QA fixture teardown absence", api.windows_task_missing(query(), task), flush=True)
                    raise RuntimeError("Product task cleanup could not be verified")
        cli("validate")
        config = api.update_schedule_config(worker)
        native = api.native_update_schedule(worker, required=True, config=config)
        if config["status"] != "REMOVED" or native["status"] != "VERIFIED_REMOVED":
            raise RuntimeError("Managed schedule did not reach verified removal")
        # The updater owns one status row. Preserve the starting register text,
        # require its exact expected replacement, and hash every other state file.
        row = api.update_automation_row(worker, config, native, last_run=initial_row[6])
        expected_register = api.update_task_table(original_register, row_id, row)
        baseline["AUTOMATIONS.md"] = hashlib.sha256(expected_register.encode("utf-8")).hexdigest()
        if fixtures.state_hashes(worker) != baseline:
            raise RuntimeError("Worker-owned state changed")
        print(json.dumps({"result": "PASS", "candidate": commit, "runtime": runtime_hash,
                          "native_due": "LIVE_TASK", "pause_resume": True, "cleanup": True}))
    finally:
        fixture.tearDown()


if __name__ == "__main__":
    main()
