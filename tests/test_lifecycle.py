#!/usr/bin/env python3
"""End-to-end lifecycle tests for the AI-Human workspace."""

import ast
import hashlib
import importlib.util
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import unittest
import warnings
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts/ai_human.py"
CURRENT_VERSION = (ROOT / "core/VERSION").read_text(encoding="utf-8").strip()
SPEC = importlib.util.spec_from_file_location("ai_human_lifecycle", CLI)
AI_HUMAN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AI_HUMAN)
VALIDATOR_PATH = ROOT / "scripts/validate_release.py"
VALIDATOR_SPEC = importlib.util.spec_from_file_location("ai_human_release_validator", VALIDATOR_PATH)
VALIDATOR = importlib.util.module_from_spec(VALIDATOR_SPEC)
VALIDATOR_SPEC.loader.exec_module(VALIDATOR)
STATE_FILES = (
    "AGENTS.md", "CLAUDE.md", "AI-HUMAN.md", "COMPANY.md", "PARAMETERS.md",
    "ROLE.md", "MASTER_CURSOR.md", "OPEN_REGISTER.md", "TODAY.md",
    "COMPLETED_LEDGER.md", "EVIDENCE_LOG.md", "FACTS.md", "DECISIONS.md",
    "TOOLBOX.md", "GATES.md", "WORK-GATES.md", "COMPLIANCE-SOURCES.md", "WORKSPACE-MAP.md",
    "AUTOMATIONS.md", "START-HERE.md", "READ-ME-FIRST.txt",
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def state_hashes(worker):
    return {name: sha256(worker / name) for name in STATE_FILES if (worker / name).is_file()}


def preserved_work_hashes(worker):
    adapters = {"AGENTS.md", "CLAUDE.md", "AI-HUMAN.md", "READ-ME-FIRST.txt", "START-HERE.md"}
    return {
        name: sha256(worker / name)
        for name in STATE_FILES
        if name not in adapters and (worker / name).is_file()
    }


def refresh_release(release, version):
    (release / "core/VERSION").write_text(version + "\n", encoding="utf-8")
    manifest_path = release / "release-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["version"] = version
    manifest["approval_status"] = "APPROVED_BY_OWNER"
    manifest["release_status"] = "RELEASED"
    manifest["compatibility"]["classification"] = "BACKWARD_COMPATIBLE"
    manifest["compatibility"]["minimum_supported_version"] = CURRENT_VERSION
    manifest["compatibility"].pop("migration", None)
    manifest["compatibility"]["preserves_user_state"] = True
    for record in manifest["managed_files"]:
        record["sha256"] = sha256(release / record["source"])
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def approve_test_release(release, automatic=False):
    manifest_path = release / "release-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["approval_status"] = "APPROVED_BY_OWNER"
    manifest["release_status"] = "RELEASED"
    manifest["automatic_update_eligible"] = automatic
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    component_path = release / "component-manifest.json"
    components = json.loads(component_path.read_text(encoding="utf-8"))
    components["approval_status"] = "APPROVED_BY_OWNER"
    components["release_status"] = "RELEASED"
    component_path.write_text(json.dumps(components, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ai-human-test-")
        self.base = Path(self.temp.name)
        self.release = self.base / "approved-release"
        shutil.copytree(
            ROOT,
            self.release,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "release-proof.json", "portal", "dist"),
        )
        approve_test_release(self.release)
        self.profile_counter = 0

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

    def run_serialized_acquire_race(self, operation):
        """Let both callers reach acquisition, then admit them one after the other."""
        original_acquire = AI_HUMAN.acquire_worker_lease
        second_at_acquire = threading.Event()
        first_finished = threading.Event()
        order_lock = threading.Lock()
        result_lock = threading.Lock()
        call_count = 0
        first_thread_id = None
        results = []

        def staged_acquire(worker, session_id, actor):
            nonlocal call_count, first_thread_id
            with order_lock:
                index = call_count
                call_count += 1
                if index == 0:
                    first_thread_id = threading.get_ident()
            if index == 0:
                if not second_at_acquire.wait(5):
                    raise RuntimeError("second concurrent caller did not reach lease acquisition")
                return original_acquire(worker, session_id, actor)
            second_at_acquire.set()
            if not first_finished.wait(10):
                raise RuntimeError("first concurrent caller did not finish")
            return original_acquire(worker, session_id, actor)

        def invoke(label):
            try:
                operation(label)
                outcome = (label, "PASS", "")
            except Exception as exc:  # The losing caller must fail cleanly.
                outcome = (label, "FAIL", str(exc))
            finally:
                if threading.get_ident() == first_thread_id:
                    first_finished.set()
            with result_lock:
                results.append(outcome)

        with (
            mock.patch.object(AI_HUMAN, "acquire_worker_lease", side_effect=staged_acquire),
            mock.patch("builtins.print"),
        ):
            threads = [
                threading.Thread(target=invoke, args=("A",)),
                threading.Thread(target=invoke, args=("B",)),
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(15)
            self.assertFalse(any(thread.is_alive() for thread in threads), "concurrency test hung")
        return results

    def write_gate_profile(
        self,
        *,
        company="Example Holdings",
        legal_entity="Example Holdings Private Limited",
        operating_units=None,
        jurisdictions=None,
        purpose="Run one controlled mission",
        user_relationship="employee",
        compliance_owner="Compliance Owner",
        gate_id="EXAMPLE-REG-001",
        unknowns=None,
        unverified_leads=None,
    ):
        self.profile_counter += 1
        operating_units = operating_units or ["Example Operations Unit"]
        jurisdictions = jurisdictions or ["India / Karnataka"]
        profile = {
            "company": company,
            "compliance_owner": compliance_owner,
            "confirmed_by": compliance_owner,
            "confirmed_utc": "2026-08-15T00:00:00Z",
            "gates": [
                {
                    "action": "STOP_AND_ESCALATE",
                    "approval_owner": compliance_owner,
                    "evidence_required": ["Written compliance-owner ruling"],
                    "gate_id": gate_id,
                    "name": "Synthetic regulated communication boundary",
                    "requirement": "Do not publish the regulated statement without approval.",
                    "source_ids": ["SYNTHETIC-AUTHORITY-001"],
                    "trigger": "A task proposes a regulated public statement.",
                }
            ],
            "jurisdictions": jurisdictions,
            "legal_entity": legal_entity,
            "operating_units": operating_units,
            "profile_id": "profile-" + gate_id.casefold(),
            "purpose_scope": purpose,
            "review_due": "2099-12-31",
            "schema": "ai-human.gate-profile/v1",
            "sources": [
                {
                    "authority": "Synthetic regulator fixture",
                    "checked_utc": "2026-08-15T00:00:00Z",
                    "kind": "LAW_OR_REGULATION",
                    "locator": "https://regulator.example.test/current-rule",
                    "source_id": "SYNTHETIC-AUTHORITY-001",
                    "status": "VERIFIED_CURRENT",
                    "title": "Synthetic current rule for lifecycle tests",
                }
            ],
            "status": "CONFIRMED",
            "unknowns": unknowns or [],
            "unverified_leads": unverified_leads or [],
            "user_relationship": user_relationship,
        }
        path = self.base / ("gate-profile-" + str(self.profile_counter) + ".json")
        path.write_text(json.dumps(profile, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def required_install_arguments(
        self,
        *,
        company="Example Holdings",
        legal_entity="Example Holdings Private Limited",
        operating_units=None,
        jurisdictions=None,
        purpose="Run one controlled mission",
        user_relationship="employee",
        compliance_owner="Compliance Owner",
        gate_profile=None,
    ):
        operating_units = operating_units or ["Example Operations Unit"]
        jurisdictions = jurisdictions or ["India / Karnataka"]
        gate_profile = gate_profile or self.write_gate_profile(
            company=company,
            legal_entity=legal_entity,
            operating_units=operating_units,
            jurisdictions=jurisdictions,
            purpose=purpose,
            user_relationship=user_relationship,
            compliance_owner=compliance_owner,
        )
        arguments = [
            "--company", company,
            "--legal-entity", legal_entity,
            "--company-owner", "Owner Person",
            "--owner", "Mission Owner",
            "--name", "User One",
            "--role", "Operations",
            "--purpose", purpose,
            "--user-relationship", user_relationship,
            "--compliance-owner", compliance_owner,
            "--gate-profile", gate_profile,
        ]
        for operating_unit in operating_units:
            arguments.extend(("--operating-unit", operating_unit))
        for jurisdiction in jurisdictions:
            arguments.extend(("--jurisdiction", jurisdiction))
        return arguments

    def install(
        self,
        worker,
        release=None,
        adopt=False,
        automatic=False,
        worker_id="worker-001",
        **identity,
    ):
        release = release or self.release
        arguments = [
            "install", worker, "--source", release,
            *self.required_install_arguments(**identity),
            "--worker-id", worker_id, "--timezone", "Asia/Kolkata",
            "--supervisor", "Supervisor One",
        ]
        if automatic:
            arguments.append("--automatic-updates")
        if adopt:
            arguments.append("--adopt")
        return self.run_cli(*arguments)

    def output_value(self, output, label):
        match = re.search(r"^- " + re.escape(label) + r": (.+)$", output, flags=re.M)
        self.assertIsNotNone(match, output)
        return match.group(1).strip()

    def build_release_proof(self, release=None):
        release = release or self.release
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/build_release.py"), str(release)],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def test_python_text_reads_declare_utf8_for_windows(self):
        missing = []
        paths = sorted((ROOT / "scripts").glob("*.py")) + sorted(
            (ROOT / "tests").glob("*.py")
        )
        for path in paths:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if not (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "read_text"
                ):
                    continue
                encoding = next(
                    (keyword.value for keyword in node.keywords if keyword.arg == "encoding"),
                    None,
                )
                if not (
                    isinstance(encoding, ast.Constant) and encoding.value == "utf-8"
                ):
                    missing.append(f"{path.relative_to(ROOT)}:{node.lineno}")
        self.assertEqual(
            missing, [], "read_text calls without explicit UTF-8: " + ", ".join(missing)
        )

    def test_fresh_install_and_validation_support_spaces(self):
        worker = self.base / "Company Folder" / "User Workspace"
        result = self.install(worker)
        self.assertIn("AI-HUMAN INSTALL: PASS", result.stdout)
        self.assertEqual(
            (worker / ".ai-human/VERSION").read_text(encoding="utf-8").strip(),
            CURRENT_VERSION,
        )
        self.assertIn("Example Holdings", (worker / "COMPANY.md").read_text(encoding="utf-8"))
        self.assertIn(
            "Example Holdings Private Limited",
            (worker / "COMPANY.md").read_text(encoding="utf-8"),
        )
        self.assertIn("EXAMPLE-REG-001", (worker / "GATES.md").read_text(encoding="utf-8"))
        self.assertIn(
            "SYNTHETIC-AUTHORITY-001",
            (worker / "COMPLIANCE-SOURCES.md").read_text(encoding="utf-8"),
        )
        self.assertIn(
            "gate-profile.json",
            (worker / "WORKSPACE-MAP.md").read_text(encoding="utf-8"),
        )
        profile = json.loads(
            (worker / ".ai-human/control/gate-profile.json").read_text(encoding="utf-8")
        )
        self.assertEqual(profile["legal_entity"], "Example Holdings Private Limited")
        metadata = json.loads(
            (worker / ".ai-human/install.json").read_text(encoding="utf-8")
        )
        self.assertEqual(metadata["user_relationship"], "employee")
        self.assertIn("gate_profile_sha256", metadata)
        self.assertEqual(set(metadata["gate_rendered_hashes"]), {"GATES.md", "COMPLIANCE-SOURCES.md"})
        self.assertNotIn("{{", (worker / "PARAMETERS.md").read_text(encoding="utf-8"))
        self.assertEqual(self.run_cli("validate", worker).returncode, 0)

    def test_gate_profile_must_match_exact_entity_and_have_no_unknowns(self):
        mismatch_worker = self.base / "mismatched-entity"
        profile = self.write_gate_profile(legal_entity="Entity A Limited")
        mismatch = self.run_cli(
            "install", mismatch_worker, "--source", self.release,
            *self.required_install_arguments(
                legal_entity="Entity B Limited", gate_profile=profile,
            ),
            expect=1,
        )
        self.assertIn("legal entity", mismatch.stderr)
        self.assertFalse(mismatch_worker.exists())

        unknown_worker = self.base / "unresolved-compliance"
        unresolved = self.write_gate_profile(unknowns=["Confirm the applicable licence condition"])
        failed = self.run_cli(
            "install", unknown_worker, "--source", self.release,
            *self.required_install_arguments(gate_profile=unresolved),
            expect=1,
        )
        self.assertIn("unknowns must be empty", failed.stderr)
        self.assertFalse(unknown_worker.exists())

    def test_company_gate_profiles_are_isolated_and_tamper_evident(self):
        worker_a = self.base / "entity-a"
        worker_b = self.base / "entity-b"
        profile_a = self.write_gate_profile(
            company="Company A", legal_entity="Company A Limited",
            operating_units=["Company A Unit"], jurisdictions=["Country A / Region A"],
            gate_id="COMPANY-A-GATE-001",
        )
        profile_b = self.write_gate_profile(
            company="Company B", legal_entity="Company B Limited",
            operating_units=["Company B Unit"], jurisdictions=["Country B / Region B"],
            gate_id="COMPANY-B-GATE-001",
        )
        self.install(
            worker_a, company="Company A", legal_entity="Company A Limited",
            operating_units=["Company A Unit"], jurisdictions=["Country A / Region A"],
            gate_profile=profile_a,
        )
        self.install(
            worker_b, company="Company B", legal_entity="Company B Limited",
            operating_units=["Company B Unit"], jurisdictions=["Country B / Region B"],
            gate_profile=profile_b,
        )
        gates_a = (worker_a / "GATES.md").read_text(encoding="utf-8")
        gates_b = (worker_b / "GATES.md").read_text(encoding="utf-8")
        self.assertIn("COMPANY-A-GATE-001", gates_a)
        self.assertNotIn("COMPANY-B-GATE-001", gates_a)
        self.assertIn("COMPANY-B-GATE-001", gates_b)
        self.assertNotIn("COMPANY-A-GATE-001", gates_b)

        (worker_a / "GATES.md").write_text(gates_a + "\nunsafe edit\n", encoding="utf-8")
        failed = self.run_cli("validate", worker_a, expect=1)
        self.assertIn("gate-rendered file integrity mismatch", failed.stdout)

        profile_path = worker_b / ".ai-human/control/gate-profile.json"
        profile_data = json.loads(profile_path.read_text(encoding="utf-8"))
        profile_data["legal_entity"] = "Another Entity Limited"
        profile_path.write_text(json.dumps(profile_data) + "\n", encoding="utf-8")
        failed = self.run_cli("validate", worker_b, expect=1)
        self.assertIn("gate-profile integrity mismatch", failed.stdout)

    def test_completion_requires_the_ledger_and_detailed_passing_evidence(self):
        worker = self.base / "completion-proof"
        self.install(worker)
        (worker / "COMPLETED_LEDGER.md").write_text(
            "# COMPLETED LEDGER\n\n"
            "| ID | Task | Closed UTC | Before | After | Evidence refs | Undo |\n"
            "|---|---|---|---|---|---|---|\n"
            "| DONE-1 | Synthetic completion | 2026-08-15T00:00:00Z | Open | Closed | EVIDENCE_LOG.md DONE-1 | Reopen row |\n",
            encoding="utf-8",
        )
        failed = self.run_cli("validate", worker, expect=1)
        self.assertIn("completed task lacks a passing detailed evidence row", failed.stdout)

        (worker / "EVIDENCE_LOG.md").write_text(
            "# EVIDENCE LOG\n\n"
            "| Task ID | Timestamp UTC | Before state | After state | Verification | Result | Artifact or readback | Undo |\n"
            "|---|---|---|---|---|---|---|---|\n"
            "| DONE-1 | 2026-08-15T00:00:00Z | Open | Closed | Read back the stored result | PASS | artifact://synthetic-proof | Reopen the ledger row |\n",
            encoding="utf-8",
        )
        self.assertEqual(self.run_cli("validate", worker).returncode, 0)

    def test_explanatory_pass_result_is_normalized_without_hiding_other_failures(self):
        worker = self.base / "normalized-pass"
        self.install(worker)
        (worker / "COMPLETED_LEDGER.md").write_text(
            "# COMPLETED LEDGER\n\n"
            "| ID | Task | Closed UTC | Before | After | Evidence refs | Undo |\n"
            "|---|---|---|---|---|---|---|\n"
            "| DONE-1 | Safe local draft | 2026-08-15T00:00:00Z | Draft absent | Draft stored | EVIDENCE_LOG.md DONE-1 | Delete the synthetic draft file |\n",
            encoding="utf-8",
        )
        (worker / "EVIDENCE_LOG.md").write_text(
            "# EVIDENCE LOG\n\n"
            "| Task ID | Timestamp UTC | Before state | After state | Verification | Result | Artifact or readback | Undo |\n"
            "|---|---|---|---|---|---|---|---|\n"
            "| DONE-1 | 2026-08-15T00:00:00Z | Draft absent | Draft stored | Compared the stored draft with all requested headings | PASS — safe local draft created | CAMPAIGN-DRAFT.md read back with all requested headings | Delete the synthetic draft file |\n",
            encoding="utf-8",
        )
        self.assertEqual(self.run_cli("validate", worker).returncode, 0)

        (worker / "TODAY.md").write_text(
            "# TODAY\n\n| ID | Task | Bounded batch | Next action | Status |\n"
            "|---|---|---|---|---|\n"
            "| DONE-1 | Safe local draft | One artifact | None | CLOSED |\n",
            encoding="utf-8",
        )
        failed = self.run_cli("validate", worker, expect=1)
        self.assertIn("completed task remains in TODAY.md: DONE-1", failed.stdout)

    def test_local_reversible_task_path_is_atomic_proportional_and_parser_safe(self):
        worker = self.base / "local-fast-path"
        self.install(worker)
        toolbox_before = (worker / "TOOLBOX.md").read_text(encoding="utf-8")
        facts_before = (worker / "FACTS.md").read_text(encoding="utf-8")
        decisions_before = (worker / "DECISIONS.md").read_text(encoding="utf-8")
        receipts_before = set((worker / ".ai-human/control/receipts").glob("*.json"))

        started = self.run_cli(
            "task-start", worker,
            "--title", "Create `ACTION-LIST.md` for A | B",
            "--source", "Current owner request and `SOURCE-NOTES.md`",
        )
        task_id = self.output_value(started.stdout, "task id")
        self.assertEqual(task_id, "LOCAL-001")
        self.assertEqual(AI_HUMAN.live_task_id(worker), task_id)
        self.assertNotIn("expected-state hash", started.stdout)
        self.assertNotIn("receipt", started.stdout.casefold())
        register_row = next(
            row for row in AI_HUMAN.parse_table_rows(worker / "OPEN_REGISTER.md")
            if row[0] == task_id
        )
        today_row = next(
            row for row in AI_HUMAN.parse_table_rows(worker / "TODAY.md")
            if row[0] == task_id
        )
        self.assertEqual(len(register_row), 7)
        self.assertEqual(len(today_row), 5)
        self.assertEqual(register_row[2], "Create `ACTION-LIST.md` for A | B")
        self.assertEqual(today_row[1], "Create `ACTION-LIST.md` for A | B")
        self.assertNotIn("No live work.", (worker / "TODAY.md").read_text(encoding="utf-8"))
        self.assertIn("Worker-local reversible artifact write", toolbox_before)

        (worker / "ACTION-LIST.md").write_text(
            "# Action list\n\n1. Confirm owner.\n2. Prepare draft.\n3. Read it back.\n",
            encoding="utf-8",
        )
        completed = self.run_cli(
            "task-complete", worker,
            "--task-id", task_id,
            "--artifact", "ACTION-LIST.md",
            "--outcome", "ACTION-LIST.md contains the three requested action rows",
            "--verification", "Read back all three numbered rows and compared them with the owner request",
            "--undo", "Delete ACTION-LIST.md to remove the local reversible result",
        )
        self.assertIn("AI-HUMAN TASK COMPLETE: PASS", completed.stdout)
        self.assertIn("response guidance: return the requested result only", completed.stdout)
        self.assertNotIn("task id:", completed.stdout.casefold())
        self.assertNotIn("artifact readback:", completed.stdout.casefold())
        self.assertNotIn("final worker validation:", completed.stdout.casefold())
        self.assertNotIn("state hash", completed.stdout.casefold())
        self.assertNotIn("receipt", completed.stdout.casefold())
        self.assertEqual(AI_HUMAN.live_task_id(worker), "")
        self.assertNotIn(task_id, AI_HUMAN.parse_table_ids(worker / "OPEN_REGISTER.md"))
        self.assertNotIn(task_id, AI_HUMAN.parse_table_ids(worker / "TODAY.md"))
        self.assertIn("No live work.", (worker / "TODAY.md").read_text(encoding="utf-8"))
        self.assertIn(task_id, AI_HUMAN.parse_table_ids(worker / "COMPLETED_LEDGER.md"))
        ledger_row = next(
            row for row in AI_HUMAN.parse_table_rows(worker / "COMPLETED_LEDGER.md")
            if row[0] == task_id
        )
        self.assertEqual(len(ledger_row), 7)
        self.assertEqual(ledger_row[1], "Create `ACTION-LIST.md` for A | B")
        evidence_rows = [
            row for row in AI_HUMAN.parse_table_rows(worker / "EVIDENCE_LOG.md")
            if row[0] == task_id
        ]
        self.assertEqual(len(evidence_rows), 1)
        self.assertEqual(evidence_rows[0][5], "PASS")
        self.assertEqual(self.run_cli("validate", worker).returncode, 0)
        self.assertEqual((worker / "TOOLBOX.md").read_text(encoding="utf-8"), toolbox_before)
        self.assertEqual((worker / "FACTS.md").read_text(encoding="utf-8"), facts_before)
        self.assertEqual((worker / "DECISIONS.md").read_text(encoding="utf-8"), decisions_before)
        receipts_after = set((worker / ".ai-human/control/receipts").glob("*.json"))
        self.assertEqual(len(receipts_after - receipts_before), 2)
        self.assertFalse((worker / ".ai-human/control/session-lease.json").exists())

    def test_concurrent_task_starts_have_one_winner_without_state_loss(self):
        worker = self.base / "concurrent-task-start"
        self.install(worker)

        def start(label):
            AI_HUMAN.task_start(
                SimpleNamespace(
                    worker=str(worker),
                    task_id=None,
                    title="Concurrent local task " + label,
                    source=None,
                    next_action=None,
                    exit_evidence=None,
                )
            )

        results = self.run_serialized_acquire_race(start)
        winners = [result for result in results if result[1] == "PASS"]
        losers = [result for result in results if result[1] == "FAIL"]
        self.assertEqual(len(winners), 1, results)
        self.assertEqual(len(losers), 1, results)
        self.assertIn("another task is live", losers[0][2])
        winner_label = winners[0][0]
        self.assertEqual(AI_HUMAN.live_task_id(worker), "LOCAL-001")
        register_rows = [
            row for row in AI_HUMAN.parse_table_rows(worker / "OPEN_REGISTER.md")
            if row[0] == "LOCAL-001"
        ]
        today_rows = [
            row for row in AI_HUMAN.parse_table_rows(worker / "TODAY.md")
            if row[0] == "LOCAL-001"
        ]
        self.assertEqual(len(register_rows), 1)
        self.assertEqual(len(today_rows), 1)
        self.assertEqual(register_rows[0][2], "Concurrent local task " + winner_label)
        self.assertEqual(today_rows[0][1], "Concurrent local task " + winner_label)
        self.assertNotIn("LOCAL-001", AI_HUMAN.parse_table_ids(worker / "COMPLETED_LEDGER.md"))
        self.assertEqual(len(list((worker / ".ai-human/control/receipts").glob("task-start-*.json"))), 1)
        self.assertFalse((worker / ".ai-human/control/session-lease.json").exists())
        self.assertEqual(self.run_cli("validate", worker).returncode, 0)

    def test_concurrent_task_completions_have_one_winner_without_state_loss(self):
        worker = self.base / "concurrent-task-complete"
        self.install(worker)
        started = self.run_cli(
            "task-start", worker, "--title", "Create one concurrency proof artifact"
        )
        task_id = self.output_value(started.stdout, "task id")
        (worker / "RACE-PROOF.md").write_text(
            "# Race proof\n\nOne verified local artifact.\n", encoding="utf-8"
        )
        receipts_before = set((worker / ".ai-human/control/receipts").glob("*.json"))

        def complete(label):
            AI_HUMAN.task_complete(
                SimpleNamespace(
                    worker=str(worker),
                    task_id=task_id,
                    artifact=["RACE-PROOF.md"],
                    outcome="Concurrent completion " + label + " stored the verified local result",
                    verification="Read back the heading and verified local artifact body",
                    undo="Delete RACE-PROOF.md to remove the requested local result",
                    before=None,
                )
            )

        results = self.run_serialized_acquire_race(complete)
        winners = [result for result in results if result[1] == "PASS"]
        losers = [result for result in results if result[1] == "FAIL"]
        self.assertEqual(len(winners), 1, results)
        self.assertEqual(len(losers), 1, results)
        self.assertIn("no live task is available to complete", losers[0][2])
        winner_label = winners[0][0]
        self.assertEqual(AI_HUMAN.live_task_id(worker), "")
        self.assertNotIn(task_id, AI_HUMAN.parse_table_ids(worker / "OPEN_REGISTER.md"))
        self.assertNotIn(task_id, AI_HUMAN.parse_table_ids(worker / "TODAY.md"))
        ledger_rows = [
            row for row in AI_HUMAN.parse_table_rows(worker / "COMPLETED_LEDGER.md")
            if row[0] == task_id
        ]
        evidence_rows = [
            row for row in AI_HUMAN.parse_table_rows(worker / "EVIDENCE_LOG.md")
            if row[0] == task_id
        ]
        self.assertEqual(len(ledger_rows), 1)
        self.assertEqual(len(evidence_rows), 1)
        self.assertIn("Concurrent completion " + winner_label, ledger_rows[0][4])
        self.assertEqual(evidence_rows[0][5], "PASS")
        receipts_after = set((worker / ".ai-human/control/receipts").glob("*.json"))
        self.assertEqual(len(receipts_after - receipts_before), 1)
        self.assertFalse((worker / ".ai-human/control/session-lease.json").exists())
        self.assertEqual(self.run_cli("validate", worker).returncode, 0)

    def test_local_task_close_failure_stays_open_and_truthful(self):
        worker = self.base / "local-fast-path-failure"
        self.install(worker)
        started = self.run_cli(
            "task-start", worker, "--title", "Create one local campaign draft"
        )
        task_id = self.output_value(started.stdout, "task id")
        before = state_hashes(worker)
        failed = self.run_cli(
            "task-complete", worker,
            "--task-id", task_id,
            "--artifact", "MISSING-DRAFT.md",
            "--outcome", "Campaign draft contains the requested safe local structure",
            "--verification", "Read back every requested section from the local campaign draft",
            "--undo", "Delete MISSING-DRAFT.md to remove the local reversible result",
            expect=1,
        )
        self.assertIn("local artifact does not exist", failed.stderr)
        self.assertEqual(state_hashes(worker), before)
        self.assertEqual(AI_HUMAN.live_task_id(worker), task_id)
        self.assertNotIn(task_id, AI_HUMAN.parse_table_ids(worker / "COMPLETED_LEDGER.md"))
        self.assertEqual(self.run_cli("validate", worker).returncode, 0)
        self.assertFalse((worker / ".ai-human/control/session-lease.json").exists())

    def test_local_task_close_rejects_false_no_other_files_undo_claim(self):
        worker = self.base / "local-fast-path-false-undo"
        self.install(worker)
        started = self.run_cli(
            "task-start", worker, "--title", "Create one local review draft"
        )
        task_id = self.output_value(started.stdout, "task id")
        (worker / "REVIEW-DRAFT.md").write_text(
            "# Review draft\n\nSafe local review content.\n", encoding="utf-8"
        )
        before = state_hashes(worker)
        failed = self.run_cli(
            "task-complete", worker,
            "--task-id", task_id,
            "--artifact", "REVIEW-DRAFT.md",
            "--outcome", "Created the requested safe local review draft",
            "--verification", "Read back the review heading and safe local content",
            "--undo", "Delete REVIEW-DRAFT.md to revert; no other files touched",
            expect=1,
        )
        self.assertIn("lifecycle state and internal receipts change by design", failed.stderr)
        self.assertEqual(state_hashes(worker), before)
        self.assertEqual(AI_HUMAN.live_task_id(worker), task_id)
        self.assertNotIn(task_id, AI_HUMAN.parse_table_ids(worker / "COMPLETED_LEDGER.md"))
        self.assertEqual(self.run_cli("validate", worker).returncode, 0)

        completed = self.run_cli(
            "task-complete", worker,
            "--task-id", task_id,
            "--artifact", "REVIEW-DRAFT.md",
            "--outcome", "Created the requested safe local review draft",
            "--verification", "Read back the review heading and safe local content",
            "--undo", "Delete REVIEW-DRAFT.md to remove the requested local artifact",
        )
        self.assertIn("AI-HUMAN TASK COMPLETE: PASS", completed.stdout)
        self.assertEqual(self.run_cli("validate", worker).returncode, 0)

    def test_weak_completion_evidence_placeholders_are_rejected(self):
        for weak_value in (
            "done", "Done!", "done.", "changed", "ok", "OK.", "ok!", "yes",
            "yes.", "n/a", "N.A.", "n/a.", "N/A (see log)", "na", "x", "?",
            "0", "see above", "nil", "none.", "complete", "fine", "verified",
            "passed", "...", "--", "y", "✓", "completed successfully",
            "verified and done", "no issues found", "verified: passed",
            "done done done", "N/A not applicable", "nothing to report", "all fine",
            "aaaaaaaaaaaa", "123456789012",
            "completed as expected", "finished as expected", "task completed fully",
            "checked and completed", "reviewed and approved", "looks correct to me",
            "everything works fine", "no problems detected", "output matches expected",
            "confirmed working correctly", "did the task properly", "all steps completed",
            "work has been completed", "successfully completed task",
        ):
            with self.subTest(weak_value=weak_value):
                self.assertTrue(AI_HUMAN.placeholder(weak_value))
        for detailed_value in (
            "Compared the stored artifact with the requested output",
            "artifact://verified-result",
            "Reran validator: PASS, 0 failures",
            "Restore backup-1.zip and re-run step 3",
            "കയറ്റുമതി ഫയലിലെ 412 വരികൾ ഉറവിടവുമായി താരതമ്യം ചെയ്തു",
        ):
            with self.subTest(detailed_value=detailed_value):
                self.assertFalse(AI_HUMAN.placeholder(detailed_value))
        malayalam = "സ്ഥിരീകരിച്ചു"
        normalized_malayalam, _tokens = AI_HUMAN.completion_evidence_parts(malayalam)
        self.assertEqual(normalized_malayalam, malayalam)
        self.assertEqual(len(normalized_malayalam), len(malayalam))
        self.assertIn(
            "cannot prove a written claim is true",
            " ".join((ROOT / "core/SESSION-END.md").read_text(encoding="utf-8").split()),
        )

        worker = self.base / "punctuated-weak-evidence"
        self.install(worker)
        (worker / "COMPLETED_LEDGER.md").write_text(
            "# COMPLETED LEDGER\n\n"
            "| ID | Task | Closed UTC | Before | After | Evidence refs | Undo |\n"
            "|---|---|---|---|---|---|---|\n"
            "| WEAK-1 | Synthetic completion | 2026-08-15T00:00:00Z | Open | Closed | Done! | Done! |\n",
            encoding="utf-8",
        )
        (worker / "EVIDENCE_LOG.md").write_text(
            "# EVIDENCE LOG\n\n"
            "| Task ID | Timestamp UTC | Before state | After state | Verification | Result | Artifact or readback | Undo |\n"
            "|---|---|---|---|---|---|---|---|\n"
            "| WEAK-1 | 2026-08-15T00:00:00Z | Open | Closed | Done! | PASS | OK. | Done! |\n",
            encoding="utf-8",
        )
        failed = self.run_cli("validate", worker, expect=1)
        self.assertIn("lacks evidence references", failed.stdout)
        self.assertIn("lacks a passing detailed evidence row", failed.stdout)

    def test_table_content_with_three_hyphens_is_not_dropped(self):
        worker = self.base / "three-hyphen-content"
        self.install(worker)
        (worker / "COMPLETED_LEDGER.md").write_text(
            "# COMPLETED LEDGER\n\n"
            "| ID | Task | Closed UTC | Before | After | Evidence refs | Undo |\n"
            "|---|---|---|---|---|---|---|\n"
            "| DONE-1 | Synthetic completion | 2026-08-15T00:00:00Z | Open | Closed | EVIDENCE_LOG.md DONE-1 | Reopen the task row |\n",
            encoding="utf-8",
        )
        (worker / "EVIDENCE_LOG.md").write_text(
            "# EVIDENCE LOG\n\n"
            "| Task ID | Timestamp UTC | Before state | After state | Verification | Result | Artifact or readback | Undo |\n"
            "|---|---|---|---|---|---|---|---|\n"
            "| DONE-1 | 2026-08-15T00:00:00Z | Open | Closed | Compared 412 rows with the source ledger | PASS | export---final.csv read back with 412 rows | Restore backup-1.zip and re-run step 3 |\n",
            encoding="utf-8",
        )
        (worker / "OPEN_REGISTER.md").write_text(
            "# OPEN REGISTER\n\n"
            "| ID | Task |\n|---|---|\n"
            "| DONE-1 | Synthetic completion --- phase 2 |\n",
            encoding="utf-8",
        )
        failed = self.run_cli("validate", worker, expect=1)
        self.assertIn("completed task remains in OPEN_REGISTER.md: DONE-1", failed.stdout)

    def test_historical_material_is_labelled_as_a_lead_not_gate_authority(self):
        worker = self.base / "historical-lead"
        profile = self.write_gate_profile(
            unverified_leads=["Old internal compliance chart — date and authority unconfirmed"],
        )
        self.install(worker, gate_profile=profile)
        sources = (worker / "COMPLIANCE-SOURCES.md").read_text(encoding="utf-8")
        self.assertIn("Unverified leads", sources)
        self.assertIn("cannot support an active gate", sources)
        self.assertIn("Old internal compliance chart", sources)

    def test_missing_artifact_fields_remain_explicitly_unknown(self):
        rules = (ROOT / "core/AGENT-RULES.md").read_text(encoding="utf-8")
        self.assertIn("Not provided in source", rules)
        for field in ("audience", "objective", "channel", "date", "claim", "owner"):
            self.assertIn(field, rules)

    def test_windows_manifest_separator_normalizes_for_required_targets(self):
        self.assertEqual(
            AI_HUMAN.portable_key(r".ai-human\system\AI-HUMAN.md"),
            ".ai-human/system/AI-HUMAN.md",
        )

    def test_timezone_id_validation_does_not_require_an_os_timezone_database(self):
        self.assertEqual(AI_HUMAN.validate_timezone("Asia/Kolkata"), "Asia/Kolkata")
        with self.assertRaises(ValueError):
            AI_HUMAN.validate_timezone("not a time zone")

    def test_automatic_update_requires_scheduler_supplied_worker_local_time(self):
        with self.assertRaisesRegex(ValueError, "scheduler.*worker-local"):
            AI_HUMAN.parse_local(None)
        result = self.run_cli(
            "automatic-update", self.base / "missing-worker-local-time",
            "--source", self.release, expect=2,
        )
        self.assertIn("--now-local", result.stderr)

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
            *self.required_install_arguments(),
            "--batch-cap", "26", expect=1,
        )
        self.assertIn("between 1 and 25", result.stderr)
        self.assertFalse(worker.exists())

    def test_one_artifact_with_150_embedded_issues_is_one_batch_unit(self):
        plan = AI_HUMAN.plan_batches("artifact-upload", 1, embedded_entries=150)
        self.assertEqual(plan["batch_sizes"], [1])
        self.assertEqual(plan["embedded_entries"], 150)
        self.assertFalse(plan["embedded_entries_are_batch_units"])
        self.assertTrue(plan["preserve_artifact_intact"])

        result = self.run_cli(
            "batch-plan", "artifact-upload", "--units", "1",
            "--embedded-entries", "150",
        )
        self.assertIn("independent batch units: 1", result.stdout)
        self.assertIn("embedded entries: 150 (not batch units)", result.stdout)
        self.assertIn("preserve artifact intact: YES", result.stdout)

    def test_separate_github_issue_writes_remain_capped_at_25(self):
        plan = AI_HUMAN.plan_batches("external-record-write", 150)
        self.assertEqual(sum(plan["batch_sizes"]), 150)
        self.assertEqual(max(plan["batch_sizes"]), 25)
        self.assertGreater(len(plan["batch_sizes"]), 1)
        self.assertFalse(plan["preserve_artifact_intact"])

    def test_adoption_preserves_existing_project_files(self):
        worker = self.base / "existing-project"
        worker.mkdir()
        sentinel = "# Existing rules\n\nDo not overwrite me.\n"
        (worker / "AGENTS.md").write_text(sentinel, encoding="utf-8")
        work_gates = "# WORK GATES\n\nCustom task-specific lock.\n"
        (worker / "WORK-GATES.md").write_text(work_gates, encoding="utf-8")
        self.install(worker, adopt=True)
        self.assertEqual((worker / "AGENTS.md").read_text(encoding="utf-8"), sentinel)
        self.assertEqual(
            (worker / "WORK-GATES.md").read_text(encoding="utf-8"), work_gates
        )
        self.assertIn(
            "EXAMPLE-REG-001", (worker / "GATES.md").read_text(encoding="utf-8")
        )
        notice = (worker / ".ai-human/ADOPTION-NOTICE.md").read_text(encoding="utf-8")
        self.assertIn("AGENTS.md", notice)
        self.assertIn("WORK-GATES.md", notice)

    def test_homework_adoption_keeps_task_locks_separate_from_entity_gate_zero(self):
        worker = self.base / "email-homework-worker"
        source = (
            self.release
            / "packages/kairali/homework/AI-HUMAN-STARTERS/01-Email-Triage-AI-Human"
        )
        shutil.copytree(source, worker)
        purpose = (
            "Save the employee time by building a durable, employee-controlled "
            "understanding of their role, priorities, people, communication "
            "preferences, recurring work, commitments and confirmed decisions; "
            "deliver a neat fixed-time daily email EA brief; and, only when explicitly "
            "approved, file clearly low-risk mail under reversible rules with a "
            "monthly false-positive audit"
        )
        before_work_gates = (worker / "WORK-GATES.md").read_text(encoding="utf-8")
        self.install(
            worker, adopt=True, purpose=purpose, user_relationship="employee",
        )
        self.assertEqual((worker / "WORK-GATES.md").read_text(encoding="utf-8"), before_work_gates)
        self.assertIn("DAILY EMAIL TRIAGE", before_work_gates)
        entity_gates = (worker / "GATES.md").read_text(encoding="utf-8")
        self.assertIn("EXAMPLE-REG-001", entity_gates)
        self.assertNotIn("DAILY EMAIL TRIAGE", entity_gates)
        self.assertEqual(self.run_cli("validate", worker).returncode, 0)

    def test_gate_profile_migration_archives_legacy_gate_zero_and_preserves_work_locks(self):
        worker = self.base / "legacy-gate-worker"
        self.install(worker)
        legacy = (
            "# GATES\n\n"
            "## Gate 0 — old universal list\n\n"
            "Stop medical, dosage, certification, legal and spend work.\n\n"
            "## Gate 1 — legacy task lock\n\n"
            "- Preserve the user's task-specific review step.\n"
        )
        (worker / "GATES.md").write_text(legacy, encoding="utf-8")
        for relative in (
            "WORK-GATES.md", "COMPLIANCE-SOURCES.md", "WORKSPACE-MAP.md",
            ".ai-human/control/gate-profile.json",
        ):
            (worker / relative).unlink()
        (worker / "COMPANY.md").write_text("# COMPANY\n\n| Field | Value |\n|---|---|\n| Company | Example Holdings |\n", encoding="utf-8")
        (worker / "PARAMETERS.md").write_text(
            "# PARAMETERS\n\n| Parameter | Value |\n|---|---|\n"
            "| Purpose | Run one controlled mission |\n",
            encoding="utf-8",
        )
        metadata_path = worker / ".ai-human/install.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        for key in (
            "company", "legal_entity", "operating_units", "jurisdictions",
            "purpose_scope", "user_relationship", "compliance_owner", "gate_profile_id",
            "gate_profile_sha256", "gate_rendered_hashes", "gate_profile_configured_utc",
        ):
            metadata.pop(key, None)
        metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        profile = self.write_gate_profile()
        base_args = [
            "configure-gate-profile", worker, "--source", self.release,
            "--company", "Example Holdings",
            "--legal-entity", "Example Holdings Private Limited",
            "--operating-unit", "Example Operations Unit",
            "--jurisdiction", "India / Karnataka",
            "--purpose", "Run one controlled mission",
            "--user-relationship", "employee",
            "--compliance-owner", "Compliance Owner",
            "--gate-profile", profile,
        ]
        denied = self.run_cli(*base_args, expect=1)
        self.assertIn("requires --at-checkpoint", denied.stderr)
        configured = self.run_cli(*base_args, "--at-checkpoint")
        self.assertIn("GATE PROFILE CONFIGURATION: PASS", configured.stdout)
        recovery = Path(self.output_value(configured.stdout, "recovery archive"))
        self.assertEqual(
            (recovery / "before/GATES.md").read_text(encoding="utf-8"), legacy
        )
        work_gates = (worker / "WORK-GATES.md").read_text(encoding="utf-8")
        self.assertIn("legacy task lock", work_gates)
        self.assertNotIn("old universal list", work_gates)
        self.assertIn(
            "EXAMPLE-REG-001", (worker / "GATES.md").read_text(encoding="utf-8")
        )
        self.assertEqual(self.run_cli("validate", worker).returncode, 0)

        candidate_manifest = json.loads(
            (ROOT / "release-manifest.json").read_text(encoding="utf-8")
        )
        candidate_manifest["compatibility"] = {
            "classification": "SETUP_MIGRATION_REQUIRED",
            "migration": "Configure the exact local Gate 0 profile at a safe checkpoint.",
            "minimum_supported_version": "1.5.1",
            "preserves_user_state": True,
        }
        candidate_manifest["automatic_update_eligible"] = True
        eligible, reason = AI_HUMAN.automatic_release_eligible(candidate_manifest, "1.5.1")
        self.assertFalse(eligible)
        self.assertIn("backward-compatible", reason)

    def test_update_defers_then_preserves_state_and_rolls_back(self):
        worker = self.base / "worker"
        self.install(worker)

        new_release = self.base / "release-2.3.0"
        shutil.copytree(self.release, new_release, ignore=shutil.ignore_patterns(".git", "__pycache__", "release-proof.json", "portal"))
        agent_rules = new_release / "core/AGENT-RULES.md"
        agent_rules.write_text(
            agent_rules.read_text(encoding="utf-8") + "\nRelease-test marker 2.3.0.\n",
            encoding="utf-8",
        )
        refresh_release(new_release, "2.3.0")

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

        before_defer_version = (worker / ".ai-human/VERSION").read_text(encoding="utf-8")
        deferred = self.run_cli("update", worker, "--source", new_release)
        self.assertIn("AI-HUMAN UPDATE: DEFERRED", deferred.stdout)
        self.assertEqual(
            (worker / ".ai-human/VERSION").read_text(encoding="utf-8"),
            before_defer_version,
        )
        self.assertIn("CORE-UPDATE-2.3.0", register.read_text(encoding="utf-8"))

        before_update_state = state_hashes(worker)
        updated = self.run_cli("update", worker, "--source", new_release, "--at-checkpoint")
        self.assertIn("AI-HUMAN UPDATE: PASS", updated.stdout)
        self.assertEqual(
            (worker / ".ai-human/VERSION").read_text(encoding="utf-8").strip(),
            "2.3.0",
        )
        self.assertEqual(state_hashes(worker), before_update_state)
        self.assertIn(
            "Release-test marker",
            (worker / ".ai-human/system/AGENT-RULES.md").read_text(encoding="utf-8"),
        )

        before_rollback_state = state_hashes(worker)
        rolled_back = self.run_cli("rollback", worker, "--version", CURRENT_VERSION)
        self.assertIn("AI-HUMAN ROLLBACK: PASS", rolled_back.stdout)
        self.assertEqual(
            (worker / ".ai-human/VERSION").read_text(encoding="utf-8").strip(),
            CURRENT_VERSION,
        )
        self.assertEqual(state_hashes(worker), before_rollback_state)
        self.assertNotIn(
            "Release-test marker",
            (worker / ".ai-human/system/AGENT-RULES.md").read_text(encoding="utf-8"),
        )

        repeated = self.run_cli("update", worker, "--source", new_release, "--at-checkpoint")
        self.assertIn("AI-HUMAN UPDATE: PASS", repeated.stdout)
        self.assertEqual(
            (worker / ".ai-human/VERSION").read_text(encoding="utf-8").strip(),
            "2.3.0",
        )
        matching_backups = list((worker / ".ai-human/backups").glob(f"{CURRENT_VERSION}-before-2.3.0-*"))
        self.assertEqual(len(matching_backups), 2)

    def test_component_catalog_skill_install_upgrade_and_remove(self):
        catalog = self.run_cli("components", "--source", self.release)
        self.assertIn("kairali-akshar-marketing-science", catalog.stdout)
        self.assertIn("kairali-rahul-sales-system", catalog.stdout)
        skills_root = self.base / "codex-skills"
        component = "kairali-akshar-marketing-science"
        self.run_cli(
            "install-skill", component, "--runtime", "codex",
            "--skills-root", skills_root, "--source", self.release,
        )
        target = skills_root / component
        self.assertTrue((target / "SKILL.md").is_file())
        self.assertTrue((target / ".ai-human-component.json").is_file())
        self.run_cli(
            "install-skill", component, "--runtime", "codex",
            "--skills-root", skills_root, "--source", self.release,
            expect=1,
        )
        self.run_cli(
            "install-skill", component, "--runtime", "codex",
            "--skills-root", skills_root, "--source", self.release, "--upgrade",
            expect=1,
        )
        self.run_cli(
            "install-skill", component, "--runtime", "codex",
            "--skills-root", skills_root, "--source", self.release, "--upgrade",
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
        self.run_cli("install-pack", "kairali-company-rollout", kit, "--source", self.release)
        self.assertEqual(len(list((kit / "people").glob("*.md"))), 12)
        self.assertTrue((kit / ".ai-human-component.json").is_file())
        self.assertTrue((kit / "homework/EVERYONE-ELSE-AI-HUMAN-HOMEWORK-VIDEO.mp4").is_file())
        self.assertTrue((kit / "skills/kairali-akshar-marketing-science/SKILL.md").is_file())
        starters = kit / "homework/AI-HUMAN-STARTERS"
        self.assertEqual(len([path for path in starters.iterdir() if path.is_dir()]), 3)
        for starter in (path for path in starters.iterdir() if path.is_dir()):
            self.assertTrue((starter / "WORK-GATES.md").is_file(), starter.name)
            self.assertFalse((starter / "GATES.md").exists(), starter.name)
        drive_start = (starters / "02-Drive-Inventory-AI-Human/START-HERE.md").read_text(encoding="utf-8")
        self.assertIn("TEST 25", drive_start)
        self.assertIn("FULL DRIVE INDEX", drive_start)
        self.assertIn("DRIVE-INDEX.jsonl", drive_start)
        self.assertIn("DRIVE-REGISTER.csv", drive_start)
        self.assertIn("generation ID", drive_start)
        self.assertIn("SET WEEKLY REFRESH", drive_start)
        self.assertIn("WEEKLY-DRIVE-REFRESH-PROMPT.md", drive_start)
        self.assertIn("DRIVE-INDEX-CURSOR.md", drive_start)
        self.assertIn("Use batches", drive_start)
        self.assertIn("no more than 25 items", drive_start)
        email_start = (starters / "01-Email-Triage-AI-Human/START-HERE.md").read_text(encoding="utf-8")
        email_daily = (starters / "01-Email-Triage-AI-Human/DAILY-TRIAGE-PROMPT.md").read_text(encoding="utf-8")
        email_daily_flat = " ".join(email_daily.split())
        self.assertIn("What fixed local time should your daily email brief", email_start)
        self.assertIn("BRIEF + SAFE FILING", email_start)
        self.assertIn("Daily Email Importance Brief", email_start)
        self.assertIn("PERSONAL-WORK-MEMORY.md", email_start)
        self.assertIn("SHOW MY MEMORY", email_start)
        self.assertIn("PROPOSED REPLIES", email_start)
        self.assertIn("NOT SENT", email_start)
        self.assertIn("batches of no more than 25", email_daily)
        self.assertIn("EMAIL-RULE-REVIEW.md", email_daily)
        self.assertIn("Do not unsubscribe or create/change a permanent Gmail filter", email_daily_flat)
        linkedin = starters / "03-LinkedIn-Message-Assistant-OPTIONAL"
        for name in (
            "SATURDAY-REVIEW-PROMPT.md", "LINKEDIN-TONE-AND-PRECEDENTS.md",
            "LINKEDIN-REPLY-QUEUE.md", "LINKEDIN-REVIEW-CURSOR.md",
            "LINKEDIN-INBOX-BATCH.md", "LINKEDIN-CONTROL-HANDOFF.md",
            "CONFIRMED-LINKEDIN-LEARNINGS.md",
        ):
            self.assertTrue((linkedin / name).is_file(), name)
        linkedin_start = (linkedin / "START-HERE.md").read_text(encoding="utf-8")
        linkedin_weekly = (linkedin / "SATURDAY-REVIEW-PROMPT.md").read_text(encoding="utf-8")
        linkedin_start_flat = " ".join(linkedin_start.split())
        linkedin_weekly_flat = " ".join(linkedin_weekly.split())
        self.assertIn("What local time every Saturday", linkedin_start_flat)
        self.assertIn("both Focused and Other", linkedin_start_flat)
        self.assertIn("no more than 25", linkedin_start_flat)
        self.assertIn("READY TO SEND", linkedin_weekly_flat)
        self.assertIn("NEEDS YOUR DECISION", linkedin_weekly_flat)
        self.assertIn("manually paste and send it in LinkedIn", linkedin_weekly_flat)
        self.assertIn("The employee alone performs every LinkedIn action", linkedin_weekly_flat)
        self.assertIn("YOUR TURN ON LINKEDIN", linkedin_weekly_flat)
        self.assertIn("stop every computer/browser tool", linkedin_weekly_flat)
        self.assertIn("explicitly approves it for future reuse", linkedin_weekly_flat)
        self.assertIn("correct or forget a learning row", linkedin_weekly_flat)
        handoff = (linkedin / "LINKEDIN-CONTROL-HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("@Computer", handoff)
        self.assertIn("@Chrome", handoff)
        self.assertIn("Never choose **Full access**, **Always allow**", handoff)
        self.assertIn("website button cannot grant", handoff)
        self.run_cli("remove-pack", kit, expect=1)
        self.run_cli("remove-pack", kit, "--at-checkpoint")
        self.assertFalse(kit.exists())
        removed = list(self.base.glob(".ai-human-component-archive/kairali-company-rollout-removed-*"))
        self.assertEqual(len(removed), 1)

    def test_personal_assistant_homework_contract_covers_adversarial_paths(self):
        starters = ROOT / "packages/kairali/homework/AI-HUMAN-STARTERS"
        email_root = starters / "01-Email-Triage-AI-Human"
        drive_root = starters / "02-Drive-Inventory-AI-Human"
        linkedin_root = starters / "03-LinkedIn-Message-Assistant-OPTIONAL"

        email = "\n".join(
            path.read_text(encoding="utf-8") for path in sorted(email_root.iterdir())
            if path.is_file()
        )
        email_flat = " ".join(email.split()).casefold()
        email_scenarios = {
            "ordinary neat brief": ("TODAY AT A GLANCE", "PROPOSED REPLIES", "NOT SENT"),
            "empty inbox": ("No action required",),
            "high volume": ("batches of no more than 25", "checkpoint"),
            "stale memory": ("Stale or contradicted items", "OBSERVED — VERIFY"),
            "conflicting memory": ("CORRECT MEMORY <ID>", "FORGET <ID>"),
            "privacy": ("Never copy a complete mailbox", "Never infer sensitive traits"),
            "gate zero": ("HUMAN REVIEW", "sender, subject and date only"),
            "newsletter": ("Never unsubscribe automatically",),
            "filter": ("permanent Gmail filter", "separate explicit employee approval"),
            "reply": ("local proposed-reply text", "never represented as sent"),
            "recovery": ("failed or partial run does not advance",),
        }
        for scenario, phrases in email_scenarios.items():
            with self.subTest(worker="email", scenario=scenario):
                for phrase in phrases:
                    self.assertIn(phrase.casefold(), email_flat)

        drive = "\n".join(
            path.read_text(encoding="utf-8") for path in sorted(drive_root.iterdir())
            if path.is_file()
        )
        drive_flat = " ".join(drive.split()).casefold()
        drive_scenarios = {
            "mode choice": ("TEST 25", "FULL DRIVE INDEX"),
            "dual register": ("DRIVE-INDEX.jsonl", "DRIVE-REGISTER.csv", "GOOGLE SHEET"),
            "generation reconciliation": ("generation ID", "reopen", "fails closed"),
            "malformed output": ("malformed JSON", "duplicate IDs"),
            "overlap": ("owned_or_created_by_me", "shared_with_me", "shared_by_me"),
            "temporary invisibility": ("NOT SEEN THIS RUN — VERIFY",),
            "weekly schedule": ("Sunday night", "exact local time", "time zone"),
            "missed run": ("RUN DRIVE REFRESH NOW", "last successful cursor"),
            "privacy": ("never a whole-life profile", "Never open or download file contents"),
        }
        for scenario, phrases in drive_scenarios.items():
            with self.subTest(worker="drive", scenario=scenario):
                for phrase in phrases:
                    self.assertIn(phrase.casefold(), drive_flat)

        linkedin = "\n".join(
            path.read_text(encoding="utf-8") for path in sorted(linkedin_root.iterdir())
            if path.is_file()
        )
        linkedin_flat = " ".join(linkedin.split()).casefold()
        for phrase in (
            "CONFIRMED-LINKEDIN-LEARNINGS.md", "explicitly approves it for future reuse",
            "CORRECT LINKEDIN LEARNING <ID>", "FORGET LINKEDIN LEARNING <ID>",
            "Never copy the full conversation", "employee alone performs every LinkedIn action",
        ):
            self.assertIn(phrase.casefold(), linkedin_flat)

    def test_tampered_component_release_is_rejected(self):
        corrupt = self.base / "corrupt-components"
        shutil.copytree(self.release, corrupt, ignore=shutil.ignore_patterns(".git", "__pycache__", "release-proof.json", "portal"))
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
        before = preserved_work_hashes(worker)
        self.run_cli("uninstall", worker, "--at-checkpoint")
        self.assertFalse((worker / ".ai-human").exists())
        removed = list(worker.glob(".ai-human-removed-*"))
        self.assertEqual(len(removed), 1)
        for adapter in ("AGENTS.md", "CLAUDE.md", "AI-HUMAN.md", "READ-ME-FIRST.txt", "START-HERE.md"):
            self.assertFalse((worker / adapter).exists(), adapter)
            self.assertTrue((removed[0] / "local-adapters" / adapter).is_file(), adapter)
        self.assertEqual(preserved_work_hashes(worker), before)
        verified = self.run_cli("verify-state", worker, "--expect", "UNINSTALLED")
        self.assertIn("AI-HUMAN STATE VERIFICATION: PASS", verified.stdout)
        self.assertIn("expected state: UNINSTALLED", verified.stdout)
        self.run_cli("verify-state", worker, "--expect", "ACTIVE", expect=1)
        self.install(worker, adopt=True)
        self.assertTrue((worker / ".ai-human").is_dir())
        self.assertEqual(preserved_work_hashes(worker), before)

    def test_suspend_resume_and_verification_disable_managed_work_reversibly(self):
        worker = self.base / "suspendable-worker"
        self.install(worker, automatic=True)
        self.run_cli("verify-state", worker, "--expect", "ACTIVE")

        suspended = self.run_cli(
            "suspend", worker, "--reason", "Owner wants unrestricted project work"
        )
        self.assertIn("AI-HUMAN SUSPEND: PASS", suspended.stdout)
        self.assertIn("mode: SUSPENDED", suspended.stdout)
        metadata = json.loads((worker / ".ai-human/install.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["automatic_updates"], "DISABLED")
        mode = json.loads((worker / ".ai-human/control/mode.json").read_text(encoding="utf-8"))
        self.assertEqual(mode["status"], "SUSPENDED")
        self.assertEqual(mode["previous_automatic_updates"], "ACTIVE")
        self.run_cli("verify-state", worker, "--expect", "SUSPENDED")
        blocked = self.run_cli("checkpoint", worker, expect=1)
        self.assertIn("system is suspended", blocked.stderr)

        resumed = self.run_cli("resume", worker)
        self.assertIn("AI-HUMAN RESUME: PASS", resumed.stdout)
        self.run_cli("verify-state", worker, "--expect", "ACTIVE")
        metadata = json.loads((worker / ".ai-human/install.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["automatic_updates"], "ACTIVE")

    def test_active_mode_pushback_is_polite_narrow_and_actionable(self):
        source_contract = (
            (ROOT / "core/AGENT-RULES.md").read_text(encoding="utf-8") + "\n" +
            (ROOT / "core/AI-HUMAN.md").read_text(encoding="utf-8")
        )
        normalized_source = re.sub(r"\s+", " ", source_contract).casefold()
        for phrase in (
            "push back politely", "refuse only the conflicting part",
            "nearest compliant", "Do not scold", "unrelated safe work",
            "pushback pattern, are off",
        ):
            self.assertIn(phrase.casefold(), normalized_source)

        worker = self.base / "polite-pushback-worker"
        self.install(worker)
        installed_contract = (
            (worker / ".ai-human/system/AGENT-RULES.md").read_text(encoding="utf-8") + "\n" +
            (worker / ".ai-human/system/AI-HUMAN.md").read_text(encoding="utf-8")
        )
        normalized_installed = re.sub(r"\s+", " ", installed_contract)
        self.assertIn("refuse only the conflicting part", normalized_installed)
        self.assertIn("nearest compliant", normalized_installed)
        self.run_cli("suspend", worker, "--reason", "Owner wants the system rules off")
        verified = self.run_cli("verify-state", worker, "--expect", "SUSPENDED")
        self.assertIn("managed rules and automations: OFF", verified.stdout)

    def test_uninstall_preserves_a_preexisting_project_agents_file(self):
        worker = self.base / "existing-project"
        worker.mkdir()
        custom_agents = "# Existing project rules\n\nKeep this independent project instruction.\n"
        (worker / "AGENTS.md").write_text(custom_agents, encoding="utf-8")
        (worker / "PROJECT-NOTES.md").write_text("Owner work stays here.\n", encoding="utf-8")
        self.install(worker, adopt=True)

        self.run_cli("uninstall", worker, "--at-checkpoint")

        self.assertEqual((worker / "AGENTS.md").read_text(encoding="utf-8"), custom_agents)
        self.assertEqual((worker / "PROJECT-NOTES.md").read_text(encoding="utf-8"), "Owner work stays here.\n")
        self.run_cli("verify-state", worker, "--expect", "UNINSTALLED")

    def test_uninstall_recovers_legacy_installs_without_adapter_metadata(self):
        worker = self.base / "legacy-worker"
        self.install(worker)
        metadata_path = worker / ".ai-human/install.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata.pop("created_starter_files", None)
        metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        self.run_cli("uninstall", worker, "--at-checkpoint")

        removed = list(worker.glob(".ai-human-removed-*"))
        self.assertEqual(len(removed), 1)
        for adapter in ("AGENTS.md", "CLAUDE.md", "AI-HUMAN.md", "READ-ME-FIRST.txt", "START-HERE.md"):
            self.assertFalse((worker / adapter).exists(), adapter)
            self.assertTrue((removed[0] / "local-adapters" / adapter).is_file(), adapter)
        self.run_cli("verify-state", worker, "--expect", "UNINSTALLED")

    def test_reusable_and_kairali_editions_are_separate_complete_downloads(self):
        downloads = ROOT / "portal/public/downloads"
        manifest = json.loads((ROOT / "release-manifest.json").read_text(encoding="utf-8"))
        lane = "PUBLIC-KIT" if manifest["release_status"] == "RELEASED" else "LOCAL-CANDIDATE"
        version_token = "v" + CURRENT_VERSION.replace(".", "")
        reusable = downloads / ("AI-HUMAN-" + version_token + "-REUSABLE-EDITION-" + lane + ".zip")
        kairali = downloads / ("KAIRALI-AI-HUMAN-" + version_token + "-EMPLOYEE-EDITION-" + lane + ".zip")
        forbidden = ("kairali", "abhilash", "ambuj")

        with zipfile.ZipFile(reusable) as archive:
            names = archive.namelist()
            edition = json.loads(archive.read("AI-HUMAN-REUSABLE-EDITION/EDITION.json"))
            self.assertEqual(edition["approval_status"], manifest["approval_status"])
            self.assertEqual(edition["release_status"], manifest["release_status"])
            self.assertIn("AI-HUMAN-REUSABLE-EDITION/START-HERE.md", names)
            self.assertIn("AI-HUMAN-REUSABLE-EDITION/INSTALL-DISABLE-REMOVE.md", names)
            self.assertIn("AI-HUMAN-REUSABLE-EDITION/workspace/scripts/ai_human.py", names)
            self.assertIn(
                "AI-HUMAN-REUSABLE-EDITION/workspace/company-profiles/template/GATE-PROFILE.example.json",
                names,
            )
            self.assertFalse(any("packages/kairali" in name.casefold() for name in names))
            for name in names:
                self.assertFalse(any(word in name.casefold() for word in forbidden), name)
                if name.endswith((".md", ".txt", ".json", ".py")):
                    text = archive.read(name).decode("utf-8", errors="replace").casefold()
                    self.assertFalse(any(word in text for word in forbidden), name)

        with zipfile.ZipFile(kairali) as archive:
            names = archive.namelist()
            edition = json.loads(archive.read("KAIRALI-EMPLOYEE-EDITION/EDITION.json"))
            self.assertEqual(edition["approval_status"], manifest["approval_status"])
            self.assertEqual(edition["release_status"], manifest["release_status"])
            self.assertIn("KAIRALI-EMPLOYEE-EDITION/START-HERE.md", names)
            self.assertIn("KAIRALI-EMPLOYEE-EDITION/INSTALL-DISABLE-REMOVE.md", names)
            self.assertIn(
                "KAIRALI-EMPLOYEE-EDITION/workspace/packages/kairali/people/ALL-EMPLOYEES.md",
                names,
            )
            self.assertIn("KAIRALI-EMPLOYEE-EDITION/workspace/scripts/ai_human.py", names)
            self.assertIn(
                "KAIRALI-EMPLOYEE-EDITION/workspace/company-profiles/template/GATE-PROFILE.example.json",
                names,
            )

    def test_public_edition_archives_install_and_validate_after_extraction(self):
        downloads = ROOT / "portal/public/downloads"
        manifest = json.loads((ROOT / "release-manifest.json").read_text(encoding="utf-8"))
        lane = "PUBLIC-KIT" if manifest["release_status"] == "RELEASED" else "LOCAL-CANDIDATE"
        version_token = "v" + CURRENT_VERSION.replace(".", "")
        editions = (
            (
                downloads / ("AI-HUMAN-" + version_token + "-REUSABLE-EDITION-" + lane + ".zip"),
                "AI-HUMAN-REUSABLE-EDITION",
                "standalone-local/ai-human-workspace",
                "reusable-archive-worker",
            ),
            (
                downloads / ("KAIRALI-AI-HUMAN-" + version_token + "-EMPLOYEE-EDITION-" + lane + ".zip"),
                "KAIRALI-EMPLOYEE-EDITION",
                "kairali-digital/ai-human-workspace",
                "kairali-archive-worker",
            ),
        )
        for archive, edition_root, repository, worker_name in editions:
            with self.subTest(archive=archive.name):
                extracted = self.base / (worker_name + "-source")
                extracted.mkdir()
                AI_HUMAN.safe_extract(archive, extracted)
                source = extracted / edition_root / "workspace"
                worker = self.base / worker_name
                if manifest["release_status"] == "LOCAL_BUILD_ONLY":
                    rejected = self.run_cli(
                        "install", worker, "--source", source,
                        *self.required_install_arguments(),
                        "--worker-id", worker_name, "--timezone", "Asia/Kolkata",
                        "--supervisor", "Supervisor One", expect=1,
                    )
                    self.assertIn("local candidate", rejected.stderr)
                    continue
                self.install(worker, release=source, worker_id=worker_name)
                self.assertEqual(self.run_cli("validate", worker).returncode, 0)
                metadata = json.loads(
                    (worker / ".ai-human/install.json").read_text(encoding="utf-8")
                )
                self.assertEqual(metadata["repository"], repository)

    def test_kairali_uses_canonical_abhilash_spelling_and_neutral_guards_both_variants(self):
        legacy = "Abi" + "lash"
        readable_roots = (
            ROOT / "editions/kairali",
            ROOT / "packages/kairali",
            ROOT / "company-profiles/kairali",
        )
        canonical_seen = False
        for directory in readable_roots:
            for path in directory.rglob("*"):
                if path.is_file() and path.suffix.casefold() in {".md", ".txt", ".json", ".py"}:
                    content = path.read_text(encoding="utf-8", errors="replace")
                    canonical_seen = canonical_seen or "Abhilash" in content
                    self.assertIsNone(re.search(r"\b" + legacy + r"\b", content), str(path))
        self.assertTrue(canonical_seen)
        for relative in ("scripts/build_editions.py", "scripts/validate_release.py"):
            guard = (ROOT / relative).read_text(encoding="utf-8").casefold()
            self.assertIn("abhilash", guard)
            self.assertIn(legacy.casefold(), guard)

    def test_beginner_guides_cover_mac_windows_extraction_and_local_source_copy(self):
        for relative in (
            "docs/BEGINNER-SETUP.md",
            "editions/kairali/START-HERE.md",
            "editions/reusable/START-HERE.md",
        ):
            guide = (ROOT / relative).read_text(encoding="utf-8")
            for required in ("Mac", "Windows", "Extract All"):
                self.assertIn(required, guide, relative)
        beginner = (ROOT / "docs/BEGINNER-SETUP.md").read_text(encoding="utf-8")
        self.assertNotIn("downloads the latest public release", beginner)
        workspace_map = (ROOT / "starter/WORKSPACE-MAP.md").read_text(encoding="utf-8")
        self.assertIn("`WORKSPACE-MAP.md`", workspace_map)
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("portal/next-env.d.ts", gitignore)

    def test_ci_validator_selects_candidate_or_public_lane_from_manifest(self):
        validator = ROOT / "scripts/validate_release.py"
        public_root = subprocess.run(
            [sys.executable, str(validator), str(ROOT), "--ci"],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(public_root.returncode, 0, public_root.stdout + public_root.stderr)
        root_manifest = json.loads((ROOT / "release-manifest.json").read_text(encoding="utf-8"))
        expected_root_lane = (
            "LOCAL CANDIDATE VALIDATION: PASS"
            if root_manifest["release_status"] == "LOCAL_BUILD_ONLY"
            else "PUBLIC RELEASE VALIDATION: PASS"
        )
        self.assertIn(expected_root_lane, public_root.stdout)

        self.build_release_proof()
        public = subprocess.run(
            [sys.executable, str(validator), str(self.release), "--ci"],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(public.returncode, 0, public.stdout + public.stderr)
        self.assertIn("PUBLIC RELEASE VALIDATION: PASS", public.stdout)

        candidate_tree = self.base / "candidate-ci"
        shutil.copytree(self.release, candidate_tree)
        candidate_manifest_path = candidate_tree / "release-manifest.json"
        candidate_manifest = json.loads(candidate_manifest_path.read_text(encoding="utf-8"))
        candidate_manifest["approval_status"] = "LOCAL_BUILD_ONLY"
        candidate_manifest["release_status"] = "LOCAL_BUILD_ONLY"
        candidate_manifest["automatic_update_eligible"] = False
        candidate_manifest_path.write_text(
            json.dumps(candidate_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        candidate_components_path = candidate_tree / "component-manifest.json"
        candidate_components = json.loads(candidate_components_path.read_text(encoding="utf-8"))
        candidate_components["approval_status"] = "LOCAL_BUILD_ONLY"
        candidate_components["release_status"] = "LOCAL_BUILD_ONLY"
        candidate_components_path.write_text(
            json.dumps(candidate_components, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        self.build_release_proof(candidate_tree)
        candidate = subprocess.run(
            [sys.executable, str(validator), str(candidate_tree), "--ci"],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(candidate.returncode, 0, candidate.stdout + candidate.stderr)
        self.assertIn("LOCAL CANDIDATE VALIDATION: PASS", candidate.stdout)

        validation_workflow = self.release / ".github/workflows/validate.yml"
        original_workflow = validation_workflow.read_text(encoding="utf-8")
        validation_workflow.write_text(
            "\n".join("# " + line if line.strip() else line for line in original_workflow.splitlines()) + "\n",
            encoding="utf-8",
        )
        commented = subprocess.run(
            [sys.executable, str(validator), str(self.release)],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(commented.returncode, 1, commented.stdout + commented.stderr)
        self.assertIn("lacks an active pull_request trigger", commented.stdout)
        self.assertIn("lacks active validate and secrets jobs", commented.stdout)

        conditional_workflow = original_workflow.replace(
            "  validate:\n",
            "  validate:\n    if: false\n",
            1,
        )
        validation_workflow.write_text(conditional_workflow, encoding="utf-8")
        conditional = subprocess.run(
            [sys.executable, str(validator), str(self.release)],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(conditional.returncode, 1, conditional.stdout + conditional.stderr)
        self.assertIn("may not be conditional", conditional.stdout)

        neutered_history = original_workflow.replace(
            "  pull_request:\n",
            "  pull_request:\n    types: [closed]\n",
        ).replace(
            "fetch-depth: 0",
            "fetch-depth: 1",
        ).replace(
            "git . --no-banner --redact",
            "git . --no-banner --redact --exit-code 0",
        )
        validation_workflow.write_text(neutered_history, encoding="utf-8")
        rejected_neutralizers = subprocess.run(
            [sys.executable, str(validator), str(self.release)],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(
            rejected_neutralizers.returncode, 1,
            rejected_neutralizers.stdout + rejected_neutralizers.stderr,
        )
        self.assertIn(
            "critical workflow differs from its governed canonical SHA-256",
            rejected_neutralizers.stdout,
        )

    def test_portal_production_deploy_requires_public_release_and_no_candidate_assets(self):
        workflow = (ROOT / ".github/workflows/portal-deploy.yml").read_text(encoding="utf-8")
        validator = self.release / "scripts/validate_release.py"
        release_workflow = self.release / ".github/workflows/portal-deploy.yml"
        self.build_release_proof()
        baseline = subprocess.run(
            [sys.executable, str(validator), str(self.release)], cwd=ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(baseline.returncode, 0, baseline.stdout + baseline.stderr)

        commented = workflow.replace(
            "          python3 scripts/validate_release.py .",
            "          # python3 scripts/validate_release.py .",
        ).replace(
            "          python3 scripts/validate_portal_deploy.py .",
            "          # python3 scripts/validate_portal_deploy.py .",
        )
        release_workflow.write_text(commented, encoding="utf-8")
        rejected_comment = subprocess.run(
            [sys.executable, str(validator), str(self.release)], cwd=ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(rejected_comment.returncode, 1, rejected_comment.stdout + rejected_comment.stderr)
        self.assertIn("lacks active release and candidate-asset gates", rejected_comment.stdout)

        gate_step_match = re.search(
            r"      - name: Refuse an unapproved release or candidate-only portal\n"
            r".*?(?=      - uses: actions/setup-node@[0-9a-f]{40})",
            workflow,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(gate_step_match)
        gate_step = gate_step_match.group(0)
        late_workflow = workflow.replace(gate_step, "").replace(
            "      - name: Deploy validated artifact\n",
            gate_step + "      - name: Deploy validated artifact\n",
        )
        release_workflow.write_text(late_workflow, encoding="utf-8")
        rejected_order = subprocess.run(
            [sys.executable, str(validator), str(self.release)], cwd=ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(rejected_order.returncode, 1, rejected_order.stdout + rejected_order.stderr)
        self.assertIn("before every Vercel production command", rejected_order.stdout)

        conditional_gate = workflow.replace(
            "        working-directory: ${{ github.workspace }}\n",
            "        if: always()\n        working-directory: ${{ github.workspace }}\n",
            1,
        )
        release_workflow.write_text(conditional_gate, encoding="utf-8")
        rejected_condition = subprocess.run(
            [sys.executable, str(validator), str(self.release)], cwd=ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(rejected_condition.returncode, 1, rejected_condition.stdout + rejected_condition.stderr)
        self.assertIn("may not be conditional", rejected_condition.stdout)

        always_deploy = workflow.replace(
            "      - name: Deploy validated artifact\n",
            "      - name: Deploy validated artifact\n        if: always()\n",
        )
        release_workflow.write_text(always_deploy, encoding="utf-8")
        rejected_always = subprocess.run(
            [sys.executable, str(validator), str(self.release)], cwd=ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(rejected_always.returncode, 1, rejected_always.stdout + rejected_always.stderr)
        self.assertIn("may not bypass", rejected_always.stdout)

        shell_override = workflow.replace(
            "        working-directory: ${{ github.workspace }}\n",
            "        working-directory: ${{ github.workspace }}\n        shell: bash {0}\n",
            1,
        )
        release_workflow.write_text(shell_override, encoding="utf-8")
        rejected_shell = subprocess.run(
            [sys.executable, str(validator), str(self.release)], cwd=ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(rejected_shell.returncode, 1, rejected_shell.stdout + rejected_shell.stderr)
        self.assertIn("may not override fail-closed shell behavior", rejected_shell.stdout)

        alternate_deploy = workflow.replace(
            "      - name: Refuse an unapproved release or candidate-only portal\n",
            "      - name: Ungated alternate deploy\n"
            "        if: always()\n"
            "        run: npx vercel deploy --prebuilt --prod\n"
            "      - name: Refuse an unapproved release or candidate-only portal\n",
        )
        release_workflow.write_text(alternate_deploy, encoding="utf-8")
        rejected_alternate = subprocess.run(
            [sys.executable, str(validator), str(self.release)], cwd=ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(rejected_alternate.returncode, 1, rejected_alternate.stdout + rejected_alternate.stderr)
        self.assertIn("may not bypass", rejected_alternate.stdout)

        second_job = workflow + (
            "\n  hotfix:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - name: Ungated hotfix deploy\n"
            "        run: ./node_modules/.bin/vercel deploy --prebuilt --prod\n"
        )
        release_workflow.write_text(second_job, encoding="utf-8")
        rejected_second_job = subprocess.run(
            [sys.executable, str(validator), str(self.release)], cwd=ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(rejected_second_job.returncode, 1, rejected_second_job.stdout + rejected_second_job.stderr)
        self.assertIn("only in the governed deploy job: hotfix", rejected_second_job.stdout)

        separate_workflow = self.release / ".github/workflows/hotfix.yml"
        separate_workflow.write_text(
            "name: Ungated hotfix\n"
            "on: workflow_dispatch\n"
            "jobs:\n"
            "  hotfix:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - run: bash -c \"vercel deploy --prebuilt --prod\"\n",
            encoding="utf-8",
        )
        release_workflow.write_text(workflow, encoding="utf-8")
        rejected_separate_workflow = subprocess.run(
            [sys.executable, str(validator), str(self.release)], cwd=ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(
            rejected_separate_workflow.returncode, 1,
            rejected_separate_workflow.stdout + rejected_separate_workflow.stderr,
        )
        self.assertIn("outside portal-deploy.yml: hotfix.yml", rejected_separate_workflow.stdout)

        separate_workflow.unlink()
        folded_gate = workflow.replace(
            "        run: |\n          python3 scripts/validate_release.py .",
            "        run: >-\n          python3 scripts/validate_release.py .",
        )
        release_workflow.write_text(folded_gate, encoding="utf-8")
        rejected_folded_gate = subprocess.run(
            [sys.executable, str(validator), str(self.release)], cwd=ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(
            rejected_folded_gate.returncode, 1,
            rejected_folded_gate.stdout + rejected_folded_gate.stderr,
        )
        self.assertIn(
            "critical workflow differs from its governed canonical SHA-256",
            rejected_folded_gate.stdout,
        )

        guard = ROOT / "scripts/validate_portal_deploy.py"
        allowed_root = subprocess.run(
            [sys.executable, str(guard), str(ROOT)], cwd=ROOT,
            text=True, capture_output=True, check=False,
        )
        if json.loads((ROOT / "release-manifest.json").read_text(encoding="utf-8"))["release_status"] == "RELEASED":
            self.assertEqual(allowed_root.returncode, 0, allowed_root.stdout + allowed_root.stderr)
        else:
            self.assertEqual(allowed_root.returncode, 1, allowed_root.stdout + allowed_root.stderr)
            self.assertIn("LOCAL_BUILD_ONLY", allowed_root.stdout)

        blocked_candidate = self.base / "blocked-candidate-portal"
        (blocked_candidate / "portal/app").mkdir(parents=True)
        (blocked_candidate / "portal/content").mkdir(parents=True)
        for name in ("release-manifest.json", "component-manifest.json"):
            (blocked_candidate / name).write_text(
                json.dumps({"approval_status": "LOCAL_BUILD_ONLY", "release_status": "LOCAL_BUILD_ONLY"}) + "\n",
                encoding="utf-8",
            )
        (blocked_candidate / "portal/app/page.tsx").write_text(
            "Local candidate - not live\n", encoding="utf-8"
        )
        (blocked_candidate / "portal/content/site-data.ts").write_text("candidate\n", encoding="utf-8")
        (blocked_candidate / "portal/content/download-manifest.json").write_text(
            json.dumps({"files": []}) + "\n", encoding="utf-8"
        )
        blocked = subprocess.run(
            [sys.executable, str(guard), str(blocked_candidate)], cwd=ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(blocked.returncode, 1, blocked.stdout + blocked.stderr)
        self.assertIn("LOCAL_BUILD_ONLY", blocked.stdout)

        approved = self.base / "approved-public-portal"
        (approved / "portal/app").mkdir(parents=True)
        (approved / "portal/content").mkdir(parents=True)
        (approved / "release-manifest.json").write_text(
            json.dumps({"approval_status": "APPROVED_BY_OWNER", "release_status": "RELEASED"}) + "\n",
            encoding="utf-8",
        )
        (approved / "component-manifest.json").write_text(
            json.dumps({"approval_status": "APPROVED_BY_OWNER", "release_status": "RELEASED"}) + "\n",
            encoding="utf-8",
        )
        (approved / "portal/app/page.tsx").write_text("Released public portal\n", encoding="utf-8")
        (approved / "portal/content/site-data.ts").write_text(
            "AI-HUMAN-v200-REUSABLE-EDITION-PUBLIC-KIT.zip\n", encoding="utf-8",
        )
        (approved / "portal/content/download-manifest.json").write_text(
            json.dumps({"files": [{"name": "AI-HUMAN-v200-REUSABLE-EDITION-PUBLIC-KIT.zip"}]}) + "\n",
            encoding="utf-8",
        )
        allowed = subprocess.run(
            [sys.executable, str(guard), str(approved)], cwd=ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(allowed.returncode, 0, allowed.stdout + allowed.stderr)

    def test_setup_migration_offer_is_a_safe_automatic_update_deferral(self):
        old_release = self.base / "release-1.5.1"
        shutil.copytree(self.release, old_release)
        refresh_release(old_release, "1.5.1")
        approve_test_release(old_release, automatic=True)

        worker = self.base / "setup-migration-worker"
        self.install(worker, release=old_release, automatic=True, worker_id="migration-001")
        migration_release = self.base / "setup-migration-release"
        shutil.copytree(self.release, migration_release)
        migration_manifest_path = migration_release / "release-manifest.json"
        migration_manifest = json.loads(migration_manifest_path.read_text(encoding="utf-8"))
        migration_manifest["automatic_update_eligible"] = False
        migration_manifest["compatibility"] = {
            "classification": "SETUP_MIGRATION_REQUIRED",
            "migration": "Configure the exact local Gate 0 profile at a safe checkpoint.",
            "minimum_supported_version": "1.5.1",
            "preserves_user_state": True,
        }
        migration_manifest_path.write_text(
            json.dumps(migration_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        result = self.run_cli(
            "automatic-update", worker, "--source", migration_release,
            "--now-local", "2026-09-01T10:00:00+05:30",
        )
        self.assertIn("AUTOMATIC UPDATE: DEFERRED", result.stdout)
        report = json.loads((worker / ".ai-human/version-report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["reason"], "SETUP_MIGRATION_REQUIRED")
        self.assertEqual(report["validator"], "PASS")
        self.assertEqual(
            (worker / ".ai-human/VERSION").read_text(encoding="utf-8").strip(),
            "1.5.1",
        )
        self.assertFalse((worker / ".ai-human/update-receipt.json").exists())

    def test_corrupt_release_is_rejected_before_worker_changes(self):
        corrupt = self.base / "corrupt-release"
        shutil.copytree(self.release, corrupt, ignore=shutil.ignore_patterns(".git", "__pycache__", "release-proof.json", "portal"))
        (corrupt / "core/AI-HUMAN.md").write_text("tampered\n", encoding="utf-8")
        worker = self.base / "should-not-exist"
        result = self.run_cli(
            "install", worker, "--source", corrupt,
            *self.required_install_arguments(),
            expect=1,
        )
        self.assertIn("hash mismatch", result.stderr)
        self.assertFalse(worker.exists())

    def test_worker_validation_rejects_tampered_managed_file(self):
        worker = self.base / "worker"
        self.install(worker)
        managed = worker / ".ai-human/system/AGENT-RULES.md"
        managed.write_text(
            managed.read_text(encoding="utf-8") + "\ntampered\n", encoding="utf-8"
        )
        result = self.run_cli("validate", worker, expect=1)
        self.assertIn("managed file integrity mismatch", result.stdout)

    def test_local_candidate_is_fail_closed_for_installation(self):
        candidate = self.base / "candidate-release"
        shutil.copytree(self.release, candidate)
        manifest_path = candidate / "release-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["approval_status"] = "LOCAL_BUILD_ONLY"
        manifest["release_status"] = "LOCAL_BUILD_ONLY"
        manifest["automatic_update_eligible"] = False
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        worker = self.base / "candidate-must-not-install"
        result = self.run_cli(
            "install", worker, "--source", candidate,
            *self.required_install_arguments(),
            expect=1,
        )
        self.assertIn("local candidate", result.stderr)
        self.assertFalse(worker.exists())

    def test_existing_idle_worker_can_receive_governed_control_configuration(self):
        worker = self.base / "existing-worker"
        self.run_cli(
            "install", worker, "--source", self.release,
            *self.required_install_arguments(),
        )
        before_state = state_hashes(worker)
        configured = self.run_cli(
            "configure-control", worker, "--worker-id", "email-existing-001",
            "--timezone", "Asia/Kolkata", "--supervisor", "Supervisor One",
            "--automatic-updates", "ACTIVE", "--approval-reference", "DECISIONS.md CONTROL-1",
        )
        self.assertIn("CONTROL CONFIGURATION: PASS", configured.stdout)
        self.assertEqual(state_hashes(worker), before_state)
        metadata = json.loads((worker / ".ai-human/install.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["worker_id"], "email-existing-001")
        self.assertEqual(metadata["timezone"], "Asia/Kolkata")
        self.assertEqual(metadata["supervisor_id"], "Supervisor One")
        self.assertEqual(metadata["automatic_updates"], "ACTIVE")

    def test_session_lease_rejects_second_writer_and_stale_state_commit(self):
        worker = self.base / "leased-worker"
        self.install(worker)
        acquired = self.run_cli(
            "session-acquire", worker, "--session-id", "session-a", "--actor", "Employee One"
        )
        initial_hash = self.output_value(acquired.stdout, "expected-state hash")
        second = self.run_cli(
            "session-acquire", worker, "--session-id", "session-b", "--actor", "Employee Two",
            expect=1,
        )
        self.assertIn("writer lease already active", second.stderr)
        changes = self.base / "state-change.json"
        changes.write_text(
            json.dumps(
                {
                    "schema": "ai-human.state-change/v1",
                    "files": {
                        "MASTER_CURSOR.md": "# MASTER CURSOR\n\n## LIVE TASK\n`TASK-1` — controlled test\n",
                        "OPEN_REGISTER.md": "# OPEN REGISTER\n\n| ID | Task |\n|---|---|\n| TASK-1 | controlled test |\n",
                        "TODAY.md": "# TODAY\n\n| ID | Task |\n|---|---|\n| TASK-1 | controlled test |\n",
                    },
                }
            ) + "\n",
            encoding="utf-8",
        )
        committed = self.run_cli(
            "state-commit", worker, "--session-id", "session-a",
            "--expected-state-hash", initial_hash, "--changes", changes,
        )
        new_hash = self.output_value(committed.stdout, "new expected-state hash")
        stale = self.run_cli(
            "state-commit", worker, "--session-id", "session-a",
            "--expected-state-hash", initial_hash, "--changes", changes, expect=1,
        )
        self.assertIn("expected-state hash mismatch", stale.stderr)
        released = self.run_cli(
            "session-release", worker, "--session-id", "session-a",
            "--expected-state-hash", new_hash,
        )
        self.assertIn("SESSION LEASE: RELEASED", released.stdout)

    def test_state_commit_rolls_back_when_live_task_is_incoherent(self):
        worker = self.base / "rollback-state-worker"
        self.install(worker)
        acquired = self.run_cli(
            "session-acquire", worker, "--session-id", "session-a", "--actor", "Employee One"
        )
        initial_hash = self.output_value(acquired.stdout, "expected-state hash")
        before = (worker / "MASTER_CURSOR.md").read_text(encoding="utf-8")
        changes = self.base / "bad-state-change.json"
        changes.write_text(
            json.dumps(
                {
                    "schema": "ai-human.state-change/v1",
                    "files": {"MASTER_CURSOR.md": "# MASTER CURSOR\n\n## LIVE TASK\n`MISSING-ROW` — invalid\n"},
                }
            ) + "\n",
            encoding="utf-8",
        )
        failed = self.run_cli(
            "state-commit", worker, "--session-id", "session-a",
            "--expected-state-hash", initial_hash, "--changes", changes, expect=1,
        )
        self.assertIn("state transaction validation failed", failed.stderr)
        self.assertEqual((worker / "MASTER_CURSOR.md").read_text(encoding="utf-8"), before)
        self.assertEqual(self.run_cli("validate", worker).returncode, 0)

    def test_abandoned_lease_recovery_requires_designated_supervisor(self):
        worker = self.base / "recover-worker"
        self.install(worker)
        acquired = self.run_cli(
            "session-acquire", worker, "--session-id", "abandoned-session", "--actor", "Employee One"
        )
        state_hash = self.output_value(acquired.stdout, "expected-state hash")
        denied = self.run_cli(
            "session-recover", worker, "--actor", "Not The Supervisor",
            "--expected-state-hash", state_hash, "--reason", "Synthetic recovery test",
            expect=1,
        )
        self.assertIn("only the designated supervisor", denied.stderr)
        recovered = self.run_cli(
            "session-recover", worker, "--actor", "Supervisor One",
            "--expected-state-hash", state_hash, "--reason", "Synthetic recovery test",
        )
        self.assertIn("SESSION LEASE: RECOVERED", recovered.stdout)
        self.assertIn("status: CLEAR", self.run_cli("session-status", worker).stdout)

    def test_capability_requires_user_proposal_local_gates_and_designated_supervisor(self):
        worker = self.base / "capability-worker"
        self.install(worker)
        acquired = self.run_cli(
            "session-acquire", worker, "--session-id", "cap-session", "--actor", "Employee One"
        )
        state_hash = self.output_value(acquired.stdout, "expected-state hash")
        proposal = self.base / "proposal.json"
        proposal.write_text(
            json.dumps(
                {
                    "allowed_tools": ["Approved email connector, read-only"],
                    "deterministic_steps": ["Load the approved triage rules"],
                    "evidence": ["EVIDENCE_LOG.md rows EMAIL-1 and EMAIL-2"],
                    "gates": ["EXAMPLE-REG-001 — stop and escalate to the configured compliance owner"],
                    "id": "email-importance-brief",
                    "judgment_steps": ["Rank messages against the approved role context"],
                    "owner": "Employee One",
                    "proof_tests": ["Read-only pilot passes", "Local Gate 0 is preserved"],
                    "purpose": "Prepare the proven daily importance brief",
                    "repetition_rationale": "The same evidenced sequence recurred in completed email runs.",
                    "retirement_rule": "Retire when the source workflow or owner approval is withdrawn.",
                    "secret_policy": "NO_SECRETS_OR_CREDENTIALS",
                    "source": "Local completed-ledger and evidence references only",
                    "usefulness_rationale": "The sequence removes repeated setup while preserving review.",
                    "version": "1.0.0",
                }
            ) + "\n",
            encoding="utf-8",
        )
        proposed = self.run_cli(
            "capability-propose", worker, "--session-id", "cap-session",
            "--expected-state-hash", state_hash, "--proposal", proposal,
        )
        state_hash = self.output_value(proposed.stdout, "new expected-state hash")
        chosen = self.run_cli(
            "capability-choice", worker, "email-importance-brief", "PROPOSE",
            "--session-id", "cap-session", "--expected-state-hash", state_hash,
        )
        state_hash = self.output_value(chosen.stdout, "new expected-state hash")
        proof = self.base / "capability-proof.json"
        proof.write_text(
            json.dumps(
                {
                    "capability_id": "email-importance-brief",
                    "results": {
                        "Local Gate 0 is preserved": "PASS",
                        "Read-only pilot passes": "PASS",
                    },
                    "schema": "ai-human.capability-proof/v1",
                }
            ) + "\n",
            encoding="utf-8",
        )
        denied = self.run_cli(
            "capability-activate", worker, "email-importance-brief",
            "--session-id", "cap-session", "--expected-state-hash", state_hash,
            "--actor", "Not The Supervisor", "--scope", "company", "--proof", proof,
            expect=1,
        )
        self.assertIn("only the designated supervisor", denied.stderr)
        activated = self.run_cli(
            "capability-activate", worker, "email-importance-brief",
            "--session-id", "cap-session", "--expected-state-hash", state_hash,
            "--actor", "Supervisor One", "--scope", "company", "--proof", proof,
        )
        self.assertIn("APPROVED_FOR_COMPANY_REUSE", activated.stdout)
        self.assertIn("NOT PUBLISHED", activated.stdout)

    def test_capability_cannot_replace_the_worker_local_gate_profile(self):
        worker = self.base / "capability-missing-local-gate"
        self.install(worker)
        acquired = self.run_cli(
            "session-acquire", worker, "--session-id", "cap-gate-session", "--actor", "User One"
        )
        state_hash = self.output_value(acquired.stdout, "expected-state hash")
        proposal = self.base / "proposal-with-wrong-gate.json"
        proposal.write_text(
            json.dumps(
                {
                    "allowed_tools": ["Read-only local files"],
                    "deterministic_steps": ["Read the approved source"],
                    "evidence": ["EVIDENCE_LOG.md TEST-1"],
                    "gates": ["ANOTHER-COMPANY-GATE-999"],
                    "id": "wrong-gate-proposal",
                    "judgment_steps": ["Summarize the approved source"],
                    "owner": "User One",
                    "proof_tests": ["Read-only pilot passes"],
                    "purpose": "Test local gate binding",
                    "repetition_rationale": "Synthetic repeated test sequence.",
                    "retirement_rule": "Retire when the source changes.",
                    "secret_policy": "NO_SECRETS_OR_CREDENTIALS",
                    "source": "Synthetic local fixture",
                    "usefulness_rationale": "Synthetic validation fixture.",
                    "version": "1.0.0",
                }
            ) + "\n",
            encoding="utf-8",
        )
        failed = self.run_cli(
            "capability-propose", worker, "--session-id", "cap-gate-session",
            "--expected-state-hash", state_hash, "--proposal", proposal, expect=1,
        )
        self.assertIn("missing active local gate id: EXAMPLE-REG-001", failed.stderr)

    def test_neutral_core_uses_user_not_employee_as_the_relationship_default(self):
        for directory in (ROOT / "core", ROOT / "starter", ROOT / "editions/reusable"):
            for path in directory.rglob("*"):
                if path.is_file() and path.suffix in {".md", ".txt"}:
                    self.assertNotIn("employee", path.read_text(encoding="utf-8").casefold(), str(path))

    def test_monthly_automatic_update_runs_at_ten_local_and_defers_live_task(self):
        new_release = self.base / "release-2.3.0-auto"
        shutil.copytree(self.release, new_release)
        rules = new_release / "core/AGENT-RULES.md"
        rules.write_text(rules.read_text(encoding="utf-8") + "\nAutomatic update marker.\n", encoding="utf-8")
        refresh_release(new_release, "2.3.0")
        approve_test_release(new_release, automatic=True)

        idle = self.base / "idle-worker"
        self.install(idle, automatic=True, worker_id="email-pilot-001")
        before_state = state_hashes(idle)
        updated = self.run_cli(
            "automatic-update", idle, "--source", new_release,
            "--now-local", "2026-09-01T10:00:00+05:30",
        )
        self.assertIn("AUTOMATIC UPDATE: UPDATED", updated.stdout)
        self.assertEqual(
            (idle / ".ai-human/VERSION").read_text(encoding="utf-8").strip(), "2.3.0"
        )
        self.assertEqual(state_hashes(idle), before_state)
        updated_metadata = json.loads((idle / ".ai-human/install.json").read_text(encoding="utf-8"))
        self.assertEqual(updated_metadata["timezone"], "Asia/Kolkata")
        self.assertEqual(updated_metadata["supervisor_id"], "Supervisor One")
        self.assertEqual(updated_metadata["automatic_updates"], "ACTIVE")
        repeated = self.run_cli(
            "automatic-update", idle, "--source", new_release,
            "--now-local", "2026-09-01T10:01:00+05:30",
        )
        self.assertIn("AUTOMATIC UPDATE: CURRENT", repeated.stdout)
        self.assertIn("ALREADY_CHECKED_THIS_MONTH", repeated.stdout)

        busy = self.base / "busy-worker"
        self.install(busy, automatic=True, worker_id="email-pilot-002")
        (busy / "MASTER_CURSOR.md").write_text("# MASTER CURSOR\n\n## LIVE TASK\n`EMAIL-1` — triage\n", encoding="utf-8")
        (busy / "OPEN_REGISTER.md").write_text("# OPEN REGISTER\n\n| ID | Task |\n|---|---|\n| EMAIL-1 | triage |\n", encoding="utf-8")
        (busy / "TODAY.md").write_text("# TODAY\n\n| ID | Task |\n|---|---|\n| EMAIL-1 | triage |\n", encoding="utf-8")
        deferred = self.run_cli(
            "automatic-update", busy, "--source", new_release,
            "--now-local", "2026-09-01T10:00:00+05:30",
        )
        self.assertIn("AUTOMATIC UPDATE: DEFERRED", deferred.stdout)
        self.assertEqual(
            (busy / ".ai-human/VERSION").read_text(encoding="utf-8").strip(),
            CURRENT_VERSION,
        )

    def test_suspended_worker_defers_direct_and_fleet_automatic_updates(self):
        new_release = self.base / "release-2.3.0-suspended"
        shutil.copytree(self.release, new_release)
        rules = new_release / "core/AGENT-RULES.md"
        rules.write_text(rules.read_text(encoding="utf-8") + "\nSuspended update marker.\n", encoding="utf-8")
        refresh_release(new_release, "2.3.0")
        approve_test_release(new_release, automatic=True)

        suspended = self.base / "suspended-worker"
        self.install(suspended, automatic=True, worker_id="suspended-001")
        self.run_cli("suspend", suspended, "--reason", "Owner disabled the system")
        before = preserved_work_hashes(suspended)

        direct = self.run_cli(
            "automatic-update", suspended, "--source", new_release,
            "--now-local", "2026-09-01T10:00:00+05:30",
        )
        self.assertIn("AUTOMATIC UPDATE: DEFERRED", direct.stdout)
        self.assertIn("SYSTEM_SUSPENDED", direct.stdout)
        self.assertEqual(
            (suspended / ".ai-human/VERSION").read_text(encoding="utf-8").strip(),
            CURRENT_VERSION,
        )

        fleet = self.base / "suspended-fleet.json"
        fleet.write_text(
            json.dumps(
                {
                    "batch_id": "suspended-batch",
                    "schema": "ai-human.fleet-batch/v1",
                    "timezone": "Asia/Kolkata",
                    "workers": [
                        {
                            "lane": "daily-email-triage", "path": str(suspended),
                            "phase": "pilot", "worker_id": "suspended-001",
                        }
                    ],
                }
            ) + "\n",
            encoding="utf-8",
        )
        state = self.base / "suspended-fleet-state.json"
        fleet_result = self.run_cli(
            "fleet-update", "--fleet", fleet, "--fleet-state", state,
            "--source", new_release, "--now-local", "2026-09-01T10:00:00+05:30",
        )
        self.assertIn("suspended-001: DEFERRED — SYSTEM_SUSPENDED", fleet_result.stdout)
        self.assertIn("Daily Email Triage pilot: NOT_VERIFIED", fleet_result.stdout)
        self.assertEqual(
            (suspended / ".ai-human/VERSION").read_text(encoding="utf-8").strip(),
            CURRENT_VERSION,
        )
        self.assertEqual(preserved_work_hashes(suspended), before)

    def test_fleet_pilots_email_then_isolates_a_general_worker_failure(self):
        new_release = self.base / "release-2.3.0-fleet"
        shutil.copytree(self.release, new_release)
        rules = new_release / "core/AGENT-RULES.md"
        rules.write_text(rules.read_text(encoding="utf-8") + "\nFleet update marker.\n", encoding="utf-8")
        refresh_release(new_release, "2.3.0")
        approve_test_release(new_release, automatic=True)
        pilot = self.base / "pilot"
        broken = self.base / "broken"
        safe = self.base / "safe"
        self.install(pilot, automatic=True, worker_id="email-pilot-001")
        self.install(broken, automatic=True, worker_id="general-001")
        self.install(safe, automatic=True, worker_id="general-002")
        managed = broken / ".ai-human/system/AGENT-RULES.md"
        managed.write_text(managed.read_text(encoding="utf-8") + "\ntampered\n", encoding="utf-8")
        fleet = self.base / "fleet.json"
        fleet.write_text(
            json.dumps(
                {
                    "batch_id": "batch-001",
                    "schema": "ai-human.fleet-batch/v1",
                    "timezone": "Asia/Kolkata",
                    "workers": [
                        {"lane": "daily-email-triage", "path": str(pilot), "phase": "pilot", "worker_id": "email-pilot-001"},
                        {"lane": "operations", "path": str(broken), "phase": "general", "worker_id": "general-001"},
                        {"lane": "operations", "path": str(safe), "phase": "general", "worker_id": "general-002"},
                    ],
                }
            ) + "\n",
            encoding="utf-8",
        )
        state = self.base / "fleet-state.json"
        result = self.run_cli(
            "fleet-update", "--fleet", fleet, "--fleet-state", state,
            "--source", new_release, "--now-local", "2026-09-01T10:00:00+05:30",
        )
        self.assertIn("Daily Email Triage pilot: PASS", result.stdout)
        self.assertIn("general-001: MISMATCH", result.stdout)
        self.assertIn("general-002: UPDATED", result.stdout)
        self.assertEqual(
            (safe / ".ai-human/VERSION").read_text(encoding="utf-8").strip(), "2.3.0"
        )
        self.assertEqual(
            (broken / ".ai-human/VERSION").read_text(encoding="utf-8").strip(),
            CURRENT_VERSION,
        )

    def test_automatic_update_failure_restores_backup_and_records_failed_receipt(self):
        worker = self.base / "rollback-update-worker"
        self.install(worker, automatic=True, worker_id="rollback-001")
        before_state = state_hashes(worker)
        before_rules = (worker / ".ai-human/system/AGENT-RULES.md").read_text(encoding="utf-8")
        new_release = self.base / "release-2.3.0-rollback"
        shutil.copytree(self.release, new_release)
        rules = new_release / "core/AGENT-RULES.md"
        rules.write_text(rules.read_text(encoding="utf-8") + "\nMust roll back.\n", encoding="utf-8")
        refresh_release(new_release, "2.3.0")
        approve_test_release(new_release, automatic=True)
        manifest = json.loads((new_release / "release-manifest.json").read_text(encoding="utf-8"))
        with mock.patch.object(
            AI_HUMAN,
            "validate_worker",
            side_effect=[
                (True, []),
                (False, ["forced post-update failure"]),
                (True, []),
            ],
        ):
            with self.assertRaises(ValueError):
                AI_HUMAN.apply_update(worker, new_release, manifest, automatic=True)
        self.assertEqual(
            (worker / ".ai-human/VERSION").read_text(encoding="utf-8").strip(),
            CURRENT_VERSION,
        )
        self.assertEqual((worker / ".ai-human/system/AGENT-RULES.md").read_text(encoding="utf-8"), before_rules)
        self.assertEqual(state_hashes(worker), before_state)
        receipt = json.loads((worker / ".ai-human/update-receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(receipt["status"], "FAILED")
        self.assertEqual(receipt["rollback"], "PASS")
        self.assertTrue(receipt["state_preserved"])

    def test_duplicate_json_keys_are_rejected_fail_closed(self):
        manifest_path = self.release / "release-manifest.json"
        content = manifest_path.read_text(encoding="utf-8")
        needle = '  "release_status": "RELEASED",\n'
        self.assertIn(needle, content)
        manifest_path.write_text(
            content.replace(needle, needle + needle, 1),
            encoding="utf-8",
        )
        result = self.run_cli(
            "install", self.base / "duplicate-json-worker", "--source", self.release,
            *self.required_install_arguments(),
            "--worker-id", "duplicate-json-001", "--timezone", "Asia/Kolkata",
            "--supervisor", "Supervisor One",
            expect=1,
        )
        self.assertIn("duplicate JSON key", result.stderr)

    def test_managed_target_cannot_enter_a_protected_state_subtree(self):
        manifest_path = self.release / "release-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        protected = dict(manifest["managed_files"][0])
        protected["target"] = ".ai-human/control/forged-policy.md"
        manifest["managed_files"].append(protected)
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        result = self.run_cli(
            "install", self.base / "protected-target-worker", "--source", self.release,
            *self.required_install_arguments(),
            "--worker-id", "protected-target-001", "--timezone", "Asia/Kolkata",
            "--supervisor", "Supervisor One",
            expect=1,
        )
        self.assertIn("protected local state", result.stderr)

        build = subprocess.run(
            [sys.executable, str(ROOT / "scripts/build_release.py"), str(self.release)],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
        failures = VALIDATOR.validate(self.release, candidate=False)
        self.assertTrue(
            any("protected local state" in failure for failure in failures),
            failures,
        )

    def test_managed_source_symlink_or_symlinked_parent_is_rejected(self):
        outside_core = self.base / "outside-core"
        shutil.move(str(self.release / "core"), outside_core)
        try:
            os.symlink(outside_core, self.release / "core", target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            self.skipTest("symbolic links are unavailable: " + str(error))
        result = self.run_cli(
            "install", self.base / "symlink-source-worker", "--source", self.release,
            *self.required_install_arguments(),
            "--worker-id", "symlink-source-001", "--timezone", "Asia/Kolkata",
            "--supervisor", "Supervisor One",
            expect=1,
        )
        self.assertIn("managed source may not use symbolic links", result.stderr)

    def test_update_refuses_a_symlinked_managed_parent_without_writing_outside(self):
        worker = self.base / "symlink-update-worker"
        self.install(worker)
        new_release = self.base / "release-2.3.0-symlink"
        shutil.copytree(self.release, new_release)
        rules = new_release / "core/AGENT-RULES.md"
        rules.write_text(rules.read_text(encoding="utf-8") + "\nSymlink attack marker.\n", encoding="utf-8")
        refresh_release(new_release, "2.3.0")

        outside_system = self.base / "outside-system"
        shutil.copytree(worker / ".ai-human/system", outside_system)
        before = (outside_system / "AGENT-RULES.md").read_bytes()
        shutil.rmtree(worker / ".ai-human/system")
        try:
            os.symlink(outside_system, worker / ".ai-human/system", target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            self.skipTest("symbolic links are unavailable: " + str(error))

        result = self.run_cli(
            "update", worker, "--source", new_release, "--at-checkpoint", expect=1,
        )
        self.assertIn("symbolic link", result.stderr)
        self.assertEqual((outside_system / "AGENT-RULES.md").read_bytes(), before)

    def test_safe_extract_rejects_duplicate_and_symbolic_link_members(self):
        duplicate_archive = self.base / "duplicate.zip"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(duplicate_archive, "w") as archive:
                archive.writestr("release/file.txt", b"first")
                archive.writestr("release/file.txt", b"second")
        duplicate_target = self.base / "duplicate-extracted"
        duplicate_target.mkdir()
        with self.assertRaisesRegex(ValueError, "duplicate archive member"):
            AI_HUMAN.safe_extract(duplicate_archive, duplicate_target)

        symlink_archive = self.base / "symlink.zip"
        link = zipfile.ZipInfo("release/link")
        link.create_system = 3
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        with zipfile.ZipFile(symlink_archive, "w") as archive:
            archive.writestr(link, "../../outside")
        symlink_target = self.base / "symlink-extracted"
        symlink_target.mkdir()
        with self.assertRaisesRegex(ValueError, "symbolic link"):
            AI_HUMAN.safe_extract(symlink_archive, symlink_target)

    def test_release_proof_matches_the_exact_non_portal_payload(self):
        build = subprocess.run(
            [sys.executable, str(ROOT / "scripts/build_release.py"), str(self.release)],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
        manifest = json.loads((self.release / "release-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(VALIDATOR.validate_release_proof(self.release, manifest), [])

        proof_path = self.release / "release-proof.json"
        proof = json.loads(proof_path.read_text(encoding="utf-8"))
        proof["files"]["AGENTS.md"] = "0" * 64
        proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        failures = VALIDATOR.validate_release_proof(self.release, manifest)
        self.assertTrue(any("hash mismatch" in failure for failure in failures), failures)

        proof_path.unlink()
        failures = VALIDATOR.validate_release_proof(self.release, manifest)
        self.assertTrue(any("release proof is missing" in failure for failure in failures), failures)

    def test_every_remote_github_action_has_an_immutable_commit_pin(self):
        workflows = ROOT / ".github/workflows"
        for path in sorted(workflows.glob("*.yml")):
            source = path.read_text(encoding="utf-8")
            self.assertEqual(VALIDATOR.action_pin_failures(source, path.name), [])
        checkout = (workflows / "validate.yml").read_text(encoding="utf-8")
        weakened = re.sub(
            r"actions/checkout@[0-9a-f]{40}",
            "actions/checkout@v4",
            checkout,
            count=1,
        )
        self.assertTrue(
            any(
                "immutable commit pin" in failure
                for failure in VALIDATOR.action_pin_failures(weakened, "validate.yml")
            )
        )


if __name__ == "__main__":
    unittest.main()
