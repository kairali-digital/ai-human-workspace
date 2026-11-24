"""Rebuild the two pinned edition fixtures locally on the disposable Actions runner."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

root = Path(sys.argv[1]).resolve()
harness = Path(__file__).resolve().parent
assert sys.platform == "win32" and os.environ.get("GITHUB_ACTIONS") == "true"
assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip() == "17367141f9c03e41d02238ae481c10ee01fcf343"
subprocess.run(["git", "apply", str(harness / "windows_floor.patch")], cwd=root, check=True)
assert hashlib.sha256((root / "scripts/ai_human.py").read_bytes()).hexdigest() == "f82ab83acaf524df7190391685c6b0a8037b61ea7bdd40fdc2e4aa335cf391c3"
for name in ["release-manifest.json", "component-manifest.json"]:
    path = root / name
    value = json.loads(path.read_bytes())
    assert value["release_status"] == value["approval_status"] == "LOCAL_BUILD_ONLY"
    value.update(approval_status="APPROVED_BY_OWNER", release_status="RELEASED")
    if name == "release-manifest.json":
        value.update(schema="ai-human.workspace-release/platform-v2", supported_platforms=["win32"])
        value["compatibility"]["minimum_supported_version"] = "2.4.0"
    path.write_bytes((json.dumps(value, indent=2, sort_keys=True) + "\n").encode())
for script in ["build_release.py", "build_editions.py"]:
    subprocess.run([sys.executable, "-B", str(root / "scripts" / script)], cwd=root, check=True)
env = dict(os.environ, PYTHONPATH=str(root / "tests"))
subprocess.run([sys.executable, "-B", "-m", "unittest", "-v",
                "test_lifecycle.LifecycleTests.test_current_cli_validates_and_updates_a_genuine_pre_v24_worker_shape"],
               cwd=root, env=env, check=True)
