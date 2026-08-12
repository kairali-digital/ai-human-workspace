#!/usr/bin/env python3
"""End-to-end lifecycle tests for the AI-Human workspace."""

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts/ai_human.py"
SPEC = importlib.util.spec_from_file_location("ai_human_lifecycle", CLI)
AI_HUMAN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AI_HUMAN)
STATE_FILES = (
    "AGENTS.md", "CLAUDE.md", "AI-HUMAN.md", "COMPANY.md", "PARAMETERS.md",
    "ROLE.md", "MASTER_CURSOR.md", "OPEN_REGISTER.md", "TODAY.md",
    "COMPLETED_LEDGER.md", "EVIDENCE_LOG.md", "FACTS.md", "DECISIONS.md",
    "TOOLBOX.md", "GATES.md", "AUTOMATIONS.md", "START-HERE.md",
    "READ-ME-FIRST.txt",
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def state_hashes(worker):
    return {name: sha256(worker / name) for name in STATE_FILES if (worker / name).is_file()}


def refresh_release(release, version):
    (release / "core/VERSION").write_text(version + "\n", encoding="utf-8")
    manifest_path = release / "release-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["version"] = version
    for record in manifest["managed_files"]:
        record["sha256"] = sha256(release / record["source"])
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ai-human-test-")
        self.base = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def run_cli(self, *args, expect=0):
        result = subprocess.run(
            [sys.executable, str(CLI), *map(str, args)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != expect:
            self.fail(
                "unexpected CLI exit " + str(result.returncode) + "\nSTDOUT:\n" +
                result.stdout + "\nSTDERR:\n" + result.stderr
            )
        return result

    def install(self, worker, release=ROOT, adopt=False):
        arguments = [
            "install", worker, "--source", release,
            "--company", "Example Holdings", "--company-owner", "Owner Person",
            "--owner", "Mission Owner", "--name", "Employee One",
            "--role", "Operations", "--purpose", "Run one controlled mission",
        ]
        if adopt:
            arguments.append("--adopt")
        return self.run_cli(*arguments)

    def test_fresh_install_and_validation_support_spaces(self):
        worker = self.base / "Company Folder" / "Employee Workspace"
        result = self.install(worker)
        self.assertIn("AI-HUMAN INSTALL: PASS", result.stdout)
        self.assertEqual((worker / ".ai-human/VERSION").read_text().strip(), "1.2.0")
        self.assertIn("Example Holdings", (worker / "COMPANY.md").read_text())
        self.assertNotIn("{{", (worker / "PARAMETERS.md").read_text())
        self.assertEqual(self.run_cli("validate", worker).returncode, 0)

    def test_windows_manifest_separator_normalizes_for_required_targets(self):
        self.assertEqual(
            AI_HUMAN.portable_key(r".ai-human\system\AI-HUMAN.md"),
            ".ai-human/system/AI-HUMAN.md",
        )

    def test_component_tree_hash_uses_portable_case_sensitive_path_order(self):
        component = self.base / "mixed-case-component"
        (component / "homework").mkdir(parents=True)
        (component / "README.md").write_text("read me\n", encoding="utf-8")
        (component / "homework/data.txt").write_text("data\n", encoding="utf-8")
        expected = hashlib.sha256()
        for relative in ("README.md", "homework/data.txt"):
            expected.update(relative.encode("utf-8") + b"\0")
            expected.update(bytes.fromhex(sha256(component / relative)) + b"\n")
        digest, count = AI_HUMAN.tree_sha256(component)
        self.assertEqual(count, 2)
        self.assertEqual(digest, expected.hexdigest())

    def test_batch_cap_above_25_is_rejected(self):
        worker = self.base / "overlarge-batch"
        result = self.run_cli(
            "install", worker, "--source", ROOT,
            "--company", "Example", "--company-owner", "Owner", "--owner", "Owner",
            "--name", "Employee", "--role", "Role", "--purpose", "Purpose",
            "--batch-cap", "26", expect=1,
        )
        self.assertIn("between 1 and 25", result.stderr)
        self.assertFalse(worker.exists())

    def test_adoption_preserves_existing_project_files(self):
        worker = self.base / "existing-project"
        worker.mkdir()
        sentinel = "# Existing rules\n\nDo not overwrite me.\n"
        (worker / "AGENTS.md").write_text(sentinel, encoding="utf-8")
        self.install(worker, adopt=True)
        self.assertEqual((worker / "AGENTS.md").read_text(), sentinel)
        notice = (worker / ".ai-human/ADOPTION-NOTICE.md").read_text()
        self.assertIn("AGENTS.md", notice)

    def test_update_defers_then_preserves_state_and_rolls_back(self):
        worker = self.base / "worker"
        self.install(worker)

        new_release = self.base / "release-1.3.0"
        shutil.copytree(ROOT, new_release, ignore=shutil.ignore_patterns(".git", "__pycache__", "release-proof.json", "portal"))
        agent_rules = new_release / "core/AGENT-RULES.md"
        agent_rules.write_text(agent_rules.read_text() + "\nRelease-test marker 1.3.0.\n", encoding="utf-8")
        refresh_release(new_release, "1.3.0")

        cursor = worker / "MASTER_CURSOR.md"
        cursor.write_text("# Master Cursor\n\n## LIVE TASK\n`TEST-1` — test checkpoint\n", encoding="utf-8")
        register = worker / "OPEN_REGISTER.md"
        register.write_text(
            "# Open Register\n\n| ID | Priority | Task | Source | Owner | Status | Exit evidence |\n"
            "|---|---:|---|---|---|---|---|\n"
            "| TEST-1 | High | test checkpoint | test | owner | In progress | validator PASS |\n",
            encoding="utf-8",
        )
        today = worker / "TODAY.md"
        today.write_text(
            "# Today\n\n| ID | Task | Status | Next action |\n|---|---|---|---|\n"
            "| TEST-1 | test checkpoint | In progress | checkpoint |\n",
            encoding="utf-8",
        )

        before_defer_version = (worker / ".ai-human/VERSION").read_text()
        deferred = self.run_cli("update", worker, "--source", new_release)
        self.assertIn("AI-HUMAN UPDATE: DEFERRED", deferred.stdout)
        self.assertEqual((worker / ".ai-human/VERSION").read_text(), before_defer_version)
        self.assertIn("CORE-UPDATE-1.3.0", register.read_text())

        before_update_state = state_hashes(worker)
        updated = self.run_cli("update", worker, "--source", new_release, "--at-checkpoint")
        self.assertIn("AI-HUMAN UPDATE: PASS", updated.stdout)
        self.assertEqual((worker / ".ai-human/VERSION").read_text().strip(), "1.3.0")
        self.assertEqual(state_hashes(worker), before_update_state)
        self.assertIn("Release-test marker", (worker / ".ai-human/system/AGENT-RULES.md").read_text())

        before_rollback_state = state_hashes(worker)
        rolled_back = self.run_cli("rollback", worker, "--version", "1.2.0")
        self.assertIn("AI-HUMAN ROLLBACK: PASS", rolled_back.stdout)
        self.assertEqual((worker / ".ai-human/VERSION").read_text().strip(), "1.2.0")
        self.assertEqual(state_hashes(worker), before_rollback_state)
        self.assertNotIn("Release-test marker", (worker / ".ai-human/system/AGENT-RULES.md").read_text())

        repeated = self.run_cli("update", worker, "--source", new_release, "--at-checkpoint")
        self.assertIn("AI-HUMAN UPDATE: PASS", repeated.stdout)
        self.assertEqual((worker / ".ai-human/VERSION").read_text().strip(), "1.3.0")
        matching_backups = list((worker / ".ai-human/backups").glob("1.2.0-before-1.3.0-*"))
        self.assertEqual(len(matching_backups), 2)

    def test_component_catalog_skill_install_upgrade_and_remove(self):
        catalog = self.run_cli("components", "--source", ROOT)
        self.assertIn("kairali-akshar-marketing-science", catalog.stdout)
        self.assertIn("kairali-rahul-sales-system", catalog.stdout)
        skills_root = self.base / "codex-skills"
        component = "kairali-akshar-marketing-science"
        self.run_cli(
            "install-skill", component, "--runtime", "codex",
            "--skills-root", skills_root, "--source", ROOT,
        )
        target = skills_root / component
        self.assertTrue((target / "SKILL.md").is_file())
        self.assertTrue((target / ".ai-human-component.json").is_file())
        self.run_cli(
            "install-skill", component, "--runtime", "codex",
            "--skills-root", skills_root, "--source", ROOT,
            expect=1,
        )
        self.run_cli(
            "install-skill", component, "--runtime", "codex",
            "--skills-root", skills_root, "--source", ROOT, "--upgrade",
            expect=1,
        )
        self.run_cli(
            "install-skill", component, "--runtime", "codex",
            "--skills-root", skills_root, "--source", ROOT, "--upgrade",
            "--at-checkpoint",
        )
        backups = list((skills_root / ".ai-human-component-archive").glob(component + "-before-*"))
        self.assertEqual(len(backups), 1)
        self.run_cli(
            "remove-skill", component, "--runtime", "codex",
            "--skills-root", skills_root, "--at-checkpoint",
        )
        self.assertFalse(target.exists())
        removed = list((skills_root / ".ai-human-component-archive").glob(component + "-removed-*"))
        self.assertEqual(len(removed), 1)

    def test_reference_packs_install_and_remove_reversibly(self):
        kit = self.base / "Kairali Company Kit"
        self.run_cli("install-pack", "kairali-company-rollout", kit, "--source", ROOT)
        self.assertEqual(len(list((kit / "people").glob("*.md"))), 12)
        self.assertTrue((kit / ".ai-human-component.json").is_file())
        self.assertTrue((kit / "homework/EVERYONE-ELSE-AI-HUMAN-HOMEWORK-VIDEO.mp4").is_file())
        self.assertTrue((kit / "skills/kairali-akshar-marketing-science/SKILL.md").is_file())
        starters = kit / "homework/AI-HUMAN-STARTERS"
        self.assertEqual(len([path for path in starters.iterdir() if path.is_dir()]), 3)
        drive_start = (starters / "02-Drive-Inventory-AI-Human/START-HERE.md").read_text(encoding="utf-8")
        self.assertIn("TEST 25", drive_start)
        self.assertIn("FULL DRIVE INDEX", drive_start)
        self.assertIn("DRIVE-INDEX-CURSOR.md", drive_start)
        self.assertIn("Use batches", drive_start)
        self.assertIn("no more than 25 items", drive_start)
        self.run_cli("remove-pack", kit, expect=1)
        self.run_cli("remove-pack", kit, "--at-checkpoint")
        self.assertFalse(kit.exists())
        removed = list(self.base.glob(".ai-human-component-archive/kairali-company-rollout-removed-*"))
        self.assertEqual(len(removed), 1)

    def test_tampered_component_release_is_rejected(self):
        corrupt = self.base / "corrupt-components"
        shutil.copytree(ROOT, corrupt, ignore=shutil.ignore_patterns(".git", "__pycache__", "release-proof.json", "portal"))
        skill = corrupt / "packages/kairali/skills/kairali-rahul-sales-system/SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + "\ntampered\n", encoding="utf-8")
        result = self.run_cli("components", "--source", corrupt, expect=1)
        self.assertIn("component tree hash mismatch", result.stderr)

    def test_component_id_cannot_escape_skills_root(self):
        skills_root = self.base / "skills"
        skills_root.mkdir()
        result = self.run_cli(
            "remove-skill", "../outside", "--runtime", "codex",
            "--skills-root", skills_root, "--at-checkpoint", expect=1,
        )
        self.assertIn("invalid component id", result.stderr)

    def test_uninstall_is_reversible_and_reinstall_adopts_state(self):
        worker = self.base / "worker"
        self.install(worker)
        before = state_hashes(worker)
        self.run_cli("uninstall", worker, "--at-checkpoint")
        self.assertFalse((worker / ".ai-human").exists())
        removed = list(worker.glob(".ai-human-removed-*"))
        self.assertEqual(len(removed), 1)
        self.assertEqual(state_hashes(worker), before)
        self.install(worker, adopt=True)
        self.assertTrue((worker / ".ai-human").is_dir())
        self.assertEqual(state_hashes(worker), before)

    def test_corrupt_release_is_rejected_before_worker_changes(self):
        corrupt = self.base / "corrupt-release"
        shutil.copytree(ROOT, corrupt, ignore=shutil.ignore_patterns(".git", "__pycache__", "release-proof.json", "portal"))
        (corrupt / "core/AI-HUMAN.md").write_text("tampered\n", encoding="utf-8")
        worker = self.base / "should-not-exist"
        result = self.run_cli(
            "install", worker, "--source", corrupt,
            "--company", "Example", "--company-owner", "Owner", "--owner", "Owner",
            "--name", "Employee", "--role", "Role", "--purpose", "Purpose",
            expect=1,
        )
        self.assertIn("hash mismatch", result.stderr)
        self.assertFalse(worker.exists())

    def test_worker_validation_rejects_tampered_managed_file(self):
        worker = self.base / "worker"
        self.install(worker)
        managed = worker / ".ai-human/system/AGENT-RULES.md"
        managed.write_text(managed.read_text() + "\ntampered\n", encoding="utf-8")
        result = self.run_cli("validate", worker, expect=1)
        self.assertIn("managed file integrity mismatch", result.stdout)


if __name__ == "__main__":
    unittest.main()
