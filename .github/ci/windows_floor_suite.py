"""Exercise the corrected runtime without publishing new installer artifacts."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

harness = Path(__file__).resolve().parent
root = Path(sys.argv[1]).resolve()
shard = int(sys.argv[2])
assert sys.platform == "win32" and os.environ.get("GITHUB_ACTIONS") == "true" and shard in range(4)
assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip() == "17367141f9c03e41d02238ae481c10ee01fcf343"
subprocess.run(["git", "apply", str(harness / "windows_floor.patch")], cwd=root, check=True)
runtime = hashlib.sha256((root / "scripts/ai_human.py").read_bytes()).hexdigest()
assert runtime == "f82ab83acaf524df7190391685c6b0a8037b61ea7bdd40fdc2e4aa335cf391c3"
for script in ("build_release.py", "build_editions.py", "build_release.py"):
    subprocess.run([sys.executable, "-B", str(root / "scripts" / script)], cwd=root, check=True)
subprocess.run([sys.executable, "-B", str(root / "scripts/validate_release.py"), ".", "--candidate"], cwd=root, check=True)
with tempfile.TemporaryDirectory() as tmp:
    receipt = Path(tmp) / "shard.json"
    subprocess.run([sys.executable, "-B", str(harness / "windows_candidate.py"), "--shard", str(shard),
                    "--child-source", str(root), "--child-result", str(receipt)], cwd=root, check=True)
    data = json.loads(receipt.read_bytes())
    assert data["tests_run"] == 62
    print("FLOOR_SHARD", json.dumps({"shard": shard, "runtime": runtime, "results": data}, sort_keys=True), flush=True)
