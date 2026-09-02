#!/usr/bin/env python3
"""Install and manage a durable, company-neutral AI-human workspace."""

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unicodedata
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path


SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
COMPONENT_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DEFAULT_REPOSITORY = "kairali-digital/ai-human-workspace"
COMPONENT_RECEIPT = ".ai-human-component.json"
RELEASED = "RELEASED"
BATCH_CAP = 25
BATCH_KINDS = (
    "artifact-upload",
    "assignment-intake",
    "item-execution",
    "external-record-write",
)
INTACT_ARTIFACT_BATCH_KINDS = {"artifact-upload", "assignment-intake"}
LEASE_PATH = Path(".ai-human/control/session-lease.json")
CONTROL_RECEIPTS = Path(".ai-human/control/receipts")
CAPABILITY_ROOT = Path(".ai-human/capabilities")
IMPROVEMENT_ROOT = Path(".ai-human/improvement")
IMPROVEMENT_CONFIG_PATH = IMPROVEMENT_ROOT / "config.json"
IMPROVEMENT_SCHEDULE_PATH = IMPROVEMENT_ROOT / "schedule.json"
MODE_PATH = Path(".ai-human/control/mode.json")
GATE_PROFILE_PATH = Path(".ai-human/control/gate-profile.json")
MODE_ACTIVE = "ACTIVE"
MODE_SUSPENDED = "SUSPENDED"
PROFILE_RENDERED_FILES = ("GATES.md", "COMPLIANCE-SOURCES.md")
LOCAL_ADAPTER_FILES = (
    "AGENTS.md", "CLAUDE.md", "AI-HUMAN.md", "READ-ME-FIRST.txt", "START-HERE.md",
)
ADAPTER_MARKERS = {
    "AGENTS.md": (".ai-human/system/AGENT-RULES.md", ".ai-human/system/AI-HUMAN.md"),
    "CLAUDE.md": (".ai-human/system/AGENT-RULES.md", ".ai-human/system/AI-HUMAN.md"),
    "AI-HUMAN.md": ("The shared operating system is installed under `.ai-human/system/`",),
    "READ-ME-FIRST.txt": ("YOUR AI HUMAN — START HERE",),
    "START-HERE.md": (
        "This folder is one bounded AI human",
    ),
}
MODE_GUARDED_COMMANDS = {
    "checkpoint", "update", "rollback", "session-acquire", "session-recover",
    "configure-control", "state-commit", "capability-propose", "capability-choice",
    "capability-activate", "task-start", "task-complete", "improvement-choice",
    "improvement-schedule", "improvement-control", "improvement-research-record",
    "improvement-run", "improvement-forget", "improvement-show",
}
COORDINATION_STATE_FILES = (
    "MASTER_CURSOR.md", "OPEN_REGISTER.md", "TODAY.md",
    "COMPLETED_LEDGER.md", "EVIDENCE_LOG.md",
)
CAPABILITY_REQUIRED = {
    "id", "owner", "purpose", "source", "allowed_tools", "gates",
    "deterministic_steps", "judgment_steps", "proof_tests", "version",
    "secret_policy", "retirement_rule", "evidence", "repetition_rationale",
    "usefulness_rationale",
}
SAFE_ID = re.compile(r"^[A-Za-z0-9]+(?:[A-Za-z0-9._-]*[A-Za-z0-9])?$")
TIMEZONE_ID = re.compile(r"^(?:UTC|[A-Za-z_+-]+(?:/[A-Za-z0-9._+-]+)+)$")
STATE_FILES = (
    "AGENTS.md", "CLAUDE.md", "AI-HUMAN.md", "COMPANY.md", "PARAMETERS.md",
    "ROLE.md", "MASTER_CURSOR.md", "OPEN_REGISTER.md", "TODAY.md",
    "COMPLETED_LEDGER.md", "EVIDENCE_LOG.md", "FACTS.md", "DECISIONS.md",
    "TOOLBOX.md", "GATES.md", "WORK-GATES.md", "COMPLIANCE-SOURCES.md", "WORKSPACE-MAP.md",
    "AUTOMATIONS.md", "START-HERE.md", "READ-ME-FIRST.txt",
)
INTRINSIC_NEVER_MANAGED = set(STATE_FILES) | {
    ".ai-human/control/",
    ".ai-human/capabilities/",
    ".ai-human/improvement/",
    ".ai-human/backups/",
    ".ai-human/install.json",
    ".ai-human/release-manifest.json",
    ".ai-human/update-receipt.json",
    ".ai-human/version-report.json",
}
REQUIRED_MANAGED = {
    ".ai-human/system/AI-HUMAN.md",
    ".ai-human/system/AGENT-RULES.md",
    ".ai-human/system/OPERATING-LOOP.md",
    ".ai-human/system/GATES-SHARED.md",
    ".ai-human/system/SESSION-START.md",
    ".ai-human/system/SESSION-END.md",
    ".ai-human/VERSION",
    ".ai-human/bin/ai_human.py",
}
GATE_PROFILE_REQUIRED = {
    "schema", "profile_id", "status", "company", "legal_entity",
    "operating_units", "jurisdictions", "purpose_scope", "user_relationship",
    "compliance_owner", "confirmed_by", "confirmed_utc", "review_due", "sources",
    "gates", "unknowns", "unverified_leads",
}
GATE_SOURCE_REQUIRED = {
    "source_id", "title", "authority", "kind", "locator", "checked_utc", "status",
}
GATE_RULE_REQUIRED = {
    "gate_id", "name", "trigger", "requirement", "source_ids", "approval_owner",
    "evidence_required", "action",
}
GATE_SOURCE_KINDS = {
    "LAW_OR_REGULATION", "LICENCE_OR_CERTIFICATION", "COMPANY_POLICY",
    "OWNER_RULING", "PROFESSIONAL_ADVICE",
}
ISO_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LOCAL_CLOCK = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")
IMPROVEMENT_SOURCES = {
    "CAPABILITY_PROPOSALS", "COMPLETED_LEDGER", "DECISIONS", "EVIDENCE_LOG",
    "FACTS", "OPEN_REGISTER", "APPROVED_RESEARCH",
}
IMPROVEMENT_CATEGORIES = {
    "CAPABILITY_PROPOSAL", "KNOWLEDGE_REFRESH", "SKILL_GAP",
    "SOURCE_CONFLICT", "TOOLING", "WORKFLOW_SIMPLIFICATION",
}
IMPROVEMENT_RESEARCH_TRUST = {"OFFICIAL", "PRIMARY", "REPUTABLE_SECONDARY"}
MAX_ARCHIVE_MEMBERS = 10_000
MAX_ARCHIVE_UNCOMPRESSED_BYTES = 512 * 1024 * 1024


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def clean(value, label):
    value = " ".join(value.split()).replace("|", "\\|").strip()
    if not value:
        raise ValueError(label + " cannot be empty")
    return value


def plan_batches(kind, independent_units, embedded_entries=0):
    """Plan bounded work using actions, not rows inside an intact artifact."""
    if kind not in BATCH_KINDS:
        raise ValueError("unsupported batch kind: " + repr(kind))
    if isinstance(independent_units, bool) or not isinstance(independent_units, int):
        raise ValueError("independent units must be an integer")
    if independent_units < 1:
        raise ValueError("independent units must be at least 1")
    if isinstance(embedded_entries, bool) or not isinstance(embedded_entries, int):
        raise ValueError("embedded entries must be an integer")
    if embedded_entries < 0:
        raise ValueError("embedded entries cannot be negative")

    preserve_artifact = kind in INTACT_ARTIFACT_BATCH_KINDS
    if embedded_entries and not preserve_artifact:
        raise ValueError(
            "embedded entries apply only to artifact-upload or assignment-intake; "
            "count separately executed items or external writes as independent units"
        )

    remaining = independent_units
    batch_sizes = []
    while remaining:
        size = min(remaining, BATCH_CAP)
        batch_sizes.append(size)
        remaining -= size
    return {
        "schema": "ai-human.batch-plan/v1",
        "kind": kind,
        "batch_cap": BATCH_CAP,
        "independent_units": independent_units,
        "embedded_entries": embedded_entries,
        "embedded_entries_are_batch_units": False,
        "preserve_artifact_intact": preserve_artifact,
        "batch_sizes": batch_sizes,
    }


def show_batch_plan(args):
    plan = plan_batches(args.kind, args.units, args.embedded_entries)
    print("AI-HUMAN BATCH PLAN: PASS")
    print("- action kind: " + plan["kind"])
    print("- independent batch units: " + str(plan["independent_units"]))
    if plan["preserve_artifact_intact"]:
        print("- embedded entries: " + str(plan["embedded_entries"]) + " (not batch units)")
        print("- preserve artifact intact: YES")
    else:
        print("- embedded entries: NOT APPLICABLE")
        print("- preserve artifact intact: NO")
    print("- batch cap: " + str(plan["batch_cap"]))
    print("- batch sizes: " + ", ".join(str(size) for size in plan["batch_sizes"]))


def safe_worker(raw, must_exist=True):
    path = Path(raw).expanduser().resolve()
    if path == Path(path.anchor).resolve() or path == Path.home().resolve():
        raise ValueError("refusing a filesystem or home root")
    if must_exist and not path.is_dir():
        raise ValueError("worker is not a directory: " + str(path))
    if path.exists() and not path.is_dir():
        raise ValueError("target exists and is not a directory: " + str(path))
    return path


def safe_relative(value, label):
    portable = str(value).replace("\\", "/")
    trimmed = portable.rstrip("/")
    raw_parts = trimmed.split("/") if trimmed else []
    path = Path(trimmed)
    if (
        not trimmed
        or "\x00" in portable
        or portable.startswith("/")
        or re.match(r"^[A-Za-z]:", portable)
        or any(part in {"", ".", ".."} for part in raw_parts)
        or path.is_absolute()
    ):
        raise ValueError("unsafe " + label + ": " + repr(value))
    return path


def portable_key(value):
    """Use one comparison form even when Windows Path renders backslashes."""
    return str(value).replace("\\", "/")


def is_protected_managed_path(value, declared=()):
    target = portable_key(value).rstrip("/")
    for protected in set(declared) | INTRINSIC_NEVER_MANAGED:
        base = portable_key(protected).rstrip("/")
        if target == base or target.startswith(base + "/"):
            return True
    return False


def path_without_symlinks(root, relative, label):
    root = Path(root).resolve()
    relative = safe_relative(str(relative), label)
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(label + " may not use symbolic links: " + portable_key(relative))
    try:
        current.resolve(strict=False).relative_to(root)
    except ValueError as error:
        raise ValueError(label + " escapes its root: " + portable_key(relative)) from error
    return current


def release_file(root, relative, label="managed source"):
    path = path_without_symlinks(root, relative, label)
    if not path.is_file():
        raise ValueError(label + " missing: " + portable_key(relative))
    return path


def release_directory(root, relative, label="component source"):
    path = path_without_symlinks(root, relative, label)
    if not path.is_dir():
        raise ValueError(label + " missing: " + portable_key(relative))
    return path


def worker_target(worker, relative, label="worker target"):
    return path_without_symlinks(worker, relative, label)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_sha256(root, ignore_receipt=False):
    root = Path(root)
    digest = hashlib.sha256()
    count = 0
    paths = sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix())
    for path in paths:
        if path.is_symlink():
            raise ValueError("component trees may not contain symbolic links: " + str(path))
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if ignore_receipt and relative == COMPONENT_RECEIPT:
            continue
        digest.update(relative.encode("utf-8") + b"\0")
        digest.update(bytes.fromhex(sha256(path)) + b"\n")
        count += 1
    return digest.hexdigest(), count


def atomic_text(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".write-temp")
    temp.write_text(content, encoding="utf-8")
    os.replace(temp, path)


def atomic_json(path, value):
    atomic_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def reject_duplicate_json_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON key: " + repr(key))
        value[key] = item
    return value


def strict_json_loads(content):
    return json.loads(content, object_pairs_hook=reject_duplicate_json_keys)


def read_json(path):
    return strict_json_loads(path.read_text(encoding="utf-8"))


def mode_file(worker):
    return worker / MODE_PATH


def worker_mode(worker):
    if not (worker / ".ai-human").is_dir():
        return "UNINSTALLED"
    path = mode_file(worker)
    if not path.is_file():
        return MODE_ACTIVE
    data = read_json(path)
    if data.get("schema") != "ai-human.mode/v1":
        raise ValueError("unsupported AI-human mode schema")
    status = str(data.get("status", ""))
    if status not in {MODE_ACTIVE, MODE_SUSPENDED}:
        raise ValueError("invalid AI-human mode: " + repr(status))
    return status


def active_system_adapters(worker):
    active = []
    for name, markers in ADAPTER_MARKERS.items():
        path = worker / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if all(marker in text for marker in markers):
            active.append(name)
    return active


def preserved_work_hashes(worker):
    excluded = set(LOCAL_ADAPTER_FILES)
    return {
        name: sha256(worker / name)
        for name in STATE_FILES
        if name not in excluded and (worker / name).is_file()
    }


def version_tuple(value):
    if not SEMVER.fullmatch(str(value)):
        raise ValueError("invalid semantic version: " + repr(value))
    return tuple(int(part) for part in str(value).split("."))


def release_status(manifest):
    """Treat legacy manifests as released while failing closed for explicit candidates."""
    return manifest.get("release_status", RELEASED)


def validate_timezone(value):
    if not isinstance(value, str) or not TIMEZONE_ID.fullmatch(value):
        raise ValueError("invalid IANA timezone: " + repr(value))
    return value


def safe_identity(value, label):
    value = clean(value, label)
    if not SAFE_ID.fullmatch(value):
        raise ValueError(label + " must contain only letters, numbers, dot, underscore or hyphen")
    return value


def clean_text_list(values, label):
    if not isinstance(values, list) or not values:
        raise ValueError(label + " must be a non-empty list")
    cleaned = []
    seen = set()
    for value in values:
        if not isinstance(value, str):
            raise ValueError(label + " entries must be text")
        item = clean(value, label + " entry")
        key = item.casefold()
        if key in seen:
            raise ValueError(label + " contains a duplicate: " + item)
        seen.add(key)
        cleaned.append(item)
    return cleaned


def validate_iso_utc(value, label):
    if not isinstance(value, str) or not ISO_UTC.fullmatch(value):
        raise ValueError(label + " must use YYYY-MM-DDTHH:MM:SSZ")
    try:
        datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise ValueError(label + " is not a valid UTC timestamp") from exc
    return value


def validate_iso_date(value, label):
    if not isinstance(value, str) or not ISO_DATE.fullmatch(value):
        raise ValueError(label + " must use YYYY-MM-DD")
    try:
        return datetime.date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(label + " is not a valid date") from exc


def require_exact_fields(data, expected, label):
    missing = expected - set(data)
    if missing:
        raise ValueError(label + " is missing: " + ", ".join(sorted(missing)))
    extra = set(data) - expected
    if extra:
        raise ValueError(label + " contains unexpected fields: " + ", ".join(sorted(extra)))


def validate_gate_profile(data, expected=None):
    """Validate one confirmed, exact-scope local Gate 0 profile."""
    if not isinstance(data, dict):
        raise ValueError("gate profile must be a JSON object")
    require_exact_fields(data, GATE_PROFILE_REQUIRED, "gate profile")
    if data.get("schema") != "ai-human.gate-profile/v1":
        raise ValueError("unsupported gate profile schema")
    if data.get("status") != "CONFIRMED":
        raise ValueError("gate profile status must be CONFIRMED before ACTIVE setup")
    safe_identity(str(data.get("profile_id", "")), "gate profile id")

    text_fields = (
        "company", "legal_entity", "purpose_scope", "user_relationship",
        "compliance_owner", "confirmed_by",
    )
    for field in text_fields:
        if not isinstance(data[field], str):
            raise ValueError("gate profile field must be text: " + field)
        clean(data[field], "gate profile " + field.replace("_", " "))
    operating_units = clean_text_list(data["operating_units"], "gate profile operating units")
    jurisdictions = clean_text_list(data["jurisdictions"], "gate profile jurisdictions")
    validate_iso_utc(data["confirmed_utc"], "gate profile confirmed_utc")
    review_due = validate_iso_date(data["review_due"], "gate profile review_due")
    if review_due < datetime.datetime.now(datetime.timezone.utc).date():
        raise ValueError("gate profile review is overdue; re-check current authoritative sources")

    unknowns = data["unknowns"]
    if not isinstance(unknowns, list):
        raise ValueError("gate profile unknowns must be a list")
    if unknowns:
        raise ValueError("gate profile unknowns must be empty before the worker can be ACTIVE")
    leads = data["unverified_leads"]
    if not isinstance(leads, list) or not all(isinstance(item, str) and item.strip() for item in leads):
        raise ValueError("gate profile unverified_leads must be a text list")

    sources = data["sources"]
    if not isinstance(sources, list) or not sources:
        raise ValueError("gate profile needs at least one verified current source")
    source_ids = set()
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("gate profile sources must be JSON objects")
        require_exact_fields(source, GATE_SOURCE_REQUIRED, "gate profile source")
        source_id = safe_identity(str(source["source_id"]), "gate source id")
        if source_id in source_ids:
            raise ValueError("duplicate gate source id: " + source_id)
        source_ids.add(source_id)
        for field in ("title", "authority", "locator"):
            if not isinstance(source[field], str):
                raise ValueError("gate source field must be text: " + field)
            clean(source[field], "gate source " + field)
        if source["kind"] not in GATE_SOURCE_KINDS:
            raise ValueError("unsupported gate source kind: " + repr(source["kind"]))
        if source["status"] != "VERIFIED_CURRENT":
            raise ValueError(
                "only VERIFIED_CURRENT sources may support an ACTIVE gate; "
                "put historical or uncertain material in unverified_leads"
            )
        validate_iso_utc(source["checked_utc"], "gate source checked_utc")

    gates = data["gates"]
    if not isinstance(gates, list) or not gates:
        raise ValueError("gate profile needs at least one stop-and-escalate gate")
    gate_ids = set()
    for gate in gates:
        if not isinstance(gate, dict):
            raise ValueError("gate profile gates must be JSON objects")
        require_exact_fields(gate, GATE_RULE_REQUIRED, "gate profile rule")
        gate_id = safe_identity(str(gate["gate_id"]), "gate id")
        if gate_id in gate_ids:
            raise ValueError("duplicate gate id: " + gate_id)
        gate_ids.add(gate_id)
        for field in ("name", "trigger", "requirement", "approval_owner"):
            if not isinstance(gate[field], str):
                raise ValueError("gate field must be text: " + field)
            clean(gate[field], "gate " + field.replace("_", " "))
        references = clean_text_list(gate["source_ids"], "gate source_ids")
        missing_sources = set(references) - source_ids
        if missing_sources:
            raise ValueError(
                "gate references unknown source ids: " + ", ".join(sorted(missing_sources))
            )
        clean_text_list(gate["evidence_required"], "gate evidence_required")
        if gate["action"] != "STOP_AND_ESCALATE":
            raise ValueError("every active Gate 0 rule must use STOP_AND_ESCALATE")

    if expected:
        comparisons = (
            ("company", "company"),
            ("legal_entity", "legal entity"),
            ("purpose_scope", "purpose scope"),
            ("user_relationship", "user relationship"),
            ("compliance_owner", "compliance owner"),
        )
        for field, label in comparisons:
            if data[field] != expected[field]:
                raise ValueError("gate profile " + label + " does not match setup")
        expected_units = clean_text_list(expected["operating_units"], "setup operating units")
        if {item.casefold() for item in operating_units} != {item.casefold() for item in expected_units}:
            raise ValueError("gate profile operating units do not match setup")
        expected_jurisdictions = clean_text_list(expected["jurisdictions"], "setup jurisdictions")
        if {item.casefold() for item in jurisdictions} != {
            item.casefold() for item in expected_jurisdictions
        }:
            raise ValueError("gate profile jurisdictions do not match setup")
    return data


def markdown_cell(value):
    return " ".join(str(value).split()).replace("|", "\\|")


def render_gate_files(profile):
    identity_rows = (
        ("Company or group", profile["company"]),
        ("Exact legal entity", profile["legal_entity"]),
        ("Operating unit(s)", "; ".join(profile["operating_units"])),
        ("Jurisdiction(s)", "; ".join(profile["jurisdictions"])),
        ("Purpose scope", profile["purpose_scope"]),
        ("User relationship", profile["user_relationship"]),
        ("Compliance owner", profile["compliance_owner"]),
        ("Profile ID", profile["profile_id"]),
        ("Review due", profile["review_due"]),
    )
    gate_lines = [
        "# GATES",
        "",
        "> Machine-readable file of record: `.ai-human/control/gate-profile.json`",
        "> Status: `CONFIRMED`. These gates apply only to the exact identity and scope below.",
        "",
        "| Binding field | Confirmed value |",
        "|---|---|",
    ]
    gate_lines.extend(
        "| " + markdown_cell(label) + " | " + markdown_cell(value) + " |"
        for label, value in identity_rows
    )
    gate_lines.extend(
        [
            "",
            "## Gate 0 — local stop-and-escalate rules",
            "",
            "| Gate ID | Name | Trigger | Required action | Approval owner | Evidence | Sources |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for gate in profile["gates"]:
        gate_lines.append(
            "| " + " | ".join(
                markdown_cell(value)
                for value in (
                    gate["gate_id"], gate["name"], gate["trigger"], gate["requirement"],
                    gate["approval_owner"], "; ".join(gate["evidence_required"]),
                    "; ".join(gate["source_ids"]),
                )
            ) + " |"
        )
    gate_lines.extend(
        [
            "",
            "If the company, legal entity, operating unit, jurisdiction or purpose changes,",
            "stop regulated or consequential work and create a separately confirmed profile.",
            "Do not borrow another company or unit's Gate 0. The shared core defines the",
            "process; this local profile defines the active gates.",
            "",
            "For a crossed gate, name the gate ID, refuse only the conflicting part, preserve",
            "safe work and guide the user to the stated approval owner and evidence path.",
            "Task-specific operating locks live separately in `WORK-GATES.md`; they may narrow",
            "work but never replace or weaken this confirmed company profile.",
            "",
        ]
    )

    source_lines = [
        "# COMPLIANCE SOURCES",
        "",
        "> Machine-readable file of record: `.ai-human/control/gate-profile.json`",
        "> Profile: `" + markdown_cell(profile["profile_id"]) + "`",
        "",
        "## Verified current sources",
        "",
        "| Source ID | Title | Authority | Kind | Locator | Checked UTC |",
        "|---|---|---|---|---|---|",
    ]
    for source in profile["sources"]:
        source_lines.append(
            "| " + " | ".join(
                markdown_cell(source[field])
                for field in ("source_id", "title", "authority", "kind", "locator", "checked_utc")
            ) + " |"
        )
    source_lines.extend(
        [
            "",
            "## Unverified leads",
            "",
            "Historical charts, old internal lists and recalled requirements are planning leads",
            "only. They cannot support an active gate until checked against a current",
            "authoritative source and confirmed by the compliance owner.",
            "",
        ]
    )
    if profile["unverified_leads"]:
        source_lines.extend("- " + markdown_cell(item) for item in profile["unverified_leads"])
    else:
        source_lines.append("- NONE")
    source_lines.extend(
        [
            "",
            "## Unresolved compliance questions",
            "",
            "- NONE — required for `CONFIRMED` / `ACTIVE` status.",
            "",
            "Next mandatory review: `" + markdown_cell(profile["review_due"]) + "`.",
            "",
        ]
    )
    return {
        "GATES.md": "\n".join(gate_lines),
        "COMPLIANCE-SOURCES.md": "\n".join(source_lines),
    }


def installed_gate_profile(worker):
    path = worker / GATE_PROFILE_PATH
    if not path.is_file():
        raise ValueError("local gate profile is missing: " + str(GATE_PROFILE_PATH))
    return validate_gate_profile(read_json(path))


def gate_setup_from_args(args):
    expected = {
        "company": clean(args.company, "company"),
        "legal_entity": clean(args.legal_entity, "legal entity"),
        "operating_units": clean_text_list(args.operating_unit, "operating units"),
        "jurisdictions": clean_text_list(args.jurisdiction, "jurisdictions"),
        "purpose_scope": clean(args.purpose, "purpose"),
        "user_relationship": clean(args.user_relationship, "user relationship"),
        "compliance_owner": clean(args.compliance_owner, "compliance owner"),
    }
    source_profile_path = Path(args.gate_profile).expanduser().resolve()
    profile = validate_gate_profile(read_json(source_profile_path), expected=expected)
    return expected, profile


def parse_offset_datetime(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(label + " must be an offset-aware ISO date-time")
    try:
        moment = datetime.datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(label + " must be an offset-aware ISO date-time") from error
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise ValueError(label + " must include its UTC offset")
    return moment


def parse_recorded_utc(value, label):
    if not isinstance(value, str):
        raise ValueError(label + " must be a UTC timestamp")
    for pattern in ("%Y%m%dT%H%M%SZ", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.datetime.strptime(value, pattern).replace(tzinfo=datetime.timezone.utc)
        except ValueError:
            pass
    raise ValueError(label + " must be a UTC timestamp")


def contains_secret_material(value):
    serialized = json.dumps(value, sort_keys=True)
    patterns = (
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
        r"\b(?:api[_-]?key|password|secret|token)\s*[:=]\s*[^\s,}\]]+",
        r"\bgh" + r"p_[A-Za-z0-9]+",
        r"\bsk-" + r"proj-[A-Za-z0-9_-]+",
    )
    return any(re.search(pattern, serialized, flags=re.I) for pattern in patterns)


def improvement_target(worker, relative, label):
    relative = safe_relative(relative, label)
    key = portable_key(relative)
    prefix = portable_key(IMPROVEMENT_ROOT) + "/"
    if not key.startswith(prefix):
        raise ValueError(label + " is outside the improvement state")
    return worker_target(worker, relative, label)


def improvement_config(worker, required=True):
    path = worker / IMPROVEMENT_CONFIG_PATH
    if not path.is_file():
        if required:
            raise ValueError("quarterly improvement choice is not configured")
        return None
    value = read_json(path)
    if value.get("schema") != "ai-human.improvement-config/v1":
        raise ValueError("unsupported quarterly improvement config schema")
    status = value.get("status")
    if status not in {"DECLINED", "ENABLED", "PAUSED", "REMOVED"}:
        raise ValueError("invalid quarterly improvement status")
    required_fields = {
        "schema", "status", "owner", "created_utc", "updated_utc",
    }
    if status in {"ENABLED", "PAUSED", "REMOVED"}:
        required_fields.update(
            {
                "approved_sources", "frequency", "freshness_days", "local_time",
                "research", "retention_days", "timezone",
            }
        )
    missing = required_fields - set(value)
    if missing:
        raise ValueError(
            "quarterly improvement config is missing: " + ", ".join(sorted(missing))
        )
    for field in ("owner", "created_utc", "updated_utc"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            raise ValueError("quarterly improvement config has invalid " + field)
    parse_recorded_utc(value["created_utc"], "improvement created_utc")
    parse_recorded_utc(value["updated_utc"], "improvement updated_utc")
    if status in {"ENABLED", "PAUSED", "REMOVED"}:
        validate_timezone(str(value["timezone"]))
        if not LOCAL_CLOCK.fullmatch(str(value["local_time"])):
            raise ValueError("quarterly improvement local time must be HH:MM")
        if value["frequency"] != "QUARTERLY":
            raise ValueError("quarterly improvement frequency must be QUARTERLY")
        if value["research"] not in {"DISABLED", "APPROVED_LINKED_SOURCES"}:
            raise ValueError("invalid quarterly improvement research choice")
        for field in ("freshness_days", "retention_days"):
            if not isinstance(value[field], int) or isinstance(value[field], bool) or value[field] < 1:
                raise ValueError("quarterly improvement " + field + " must be a positive integer")
        sources = value["approved_sources"]
        if (
            not isinstance(sources, list) or not sources
            or len(sources) != len(set(sources))
            or any(source not in IMPROVEMENT_SOURCES for source in sources)
        ):
            raise ValueError("quarterly improvement approved sources are invalid")
        research_enabled = value["research"] == "APPROVED_LINKED_SOURCES"
        if research_enabled != ("APPROVED_RESEARCH" in sources):
            raise ValueError(
                "APPROVED_RESEARCH must be selected exactly when linked research is enabled"
            )
    return value


def improvement_schedule(worker, required=False):
    path = worker / IMPROVEMENT_SCHEDULE_PATH
    if not path.is_file():
        if required:
            raise ValueError("quarterly improvement schedule has not been verified")
        return None
    value = read_json(path)
    if value.get("schema") != "ai-human.improvement-schedule/v1":
        raise ValueError("unsupported quarterly improvement schedule schema")
    status = value.get("status")
    allowed = {
        "STALE_AFTER_CONFIGURATION_CHANGE", "UNAVAILABLE", "VERIFIED_ACTIVE",
        "VERIFIED_PAUSED", "VERIFIED_REMOVED",
    }
    if status not in allowed:
        raise ValueError("invalid quarterly improvement schedule status")
    if not isinstance(value.get("verified_utc"), str):
        raise ValueError("quarterly improvement schedule lacks verified_utc")
    parse_recorded_utc(value["verified_utc"], "schedule verified_utc")
    if status == "UNAVAILABLE" and (
        not isinstance(value.get("reason"), str) or not value["reason"].strip()
    ):
        raise ValueError("unavailable schedule requires a reason")
    if status == "STALE_AFTER_CONFIGURATION_CHANGE":
        if value.get("previous_status") not in allowed - {"STALE_AFTER_CONFIGURATION_CHANGE"}:
            raise ValueError("stale schedule lacks a valid previous status")
        if not isinstance(value.get("reason"), str) or not value["reason"].strip():
            raise ValueError("stale schedule requires a reason")
    if status.startswith("VERIFIED_"):
        for field in ("adapter", "external_id", "local_time", "timezone"):
            if not isinstance(value.get(field), str) or not value[field].strip():
                raise ValueError("verified schedule lacks " + field)
        safe_identity(value["external_id"], "schedule external id")
        validate_timezone(value["timezone"])
        if not LOCAL_CLOCK.fullmatch(value["local_time"]):
            raise ValueError("verified schedule local time must be HH:MM")
        if value.get("visible_card") is not True:
            raise ValueError("verified schedule requires a visible Scheduled card")
    if status == "VERIFIED_ACTIVE":
        parse_offset_datetime(value.get("next_run_local"), "schedule next run")
    return value


def validate_research_payload(data):
    required = {
        "accessed_utc", "claim_summary", "instruction_content_ignored",
        "personal_data_excluded", "published_or_updated", "receipt_id", "schema",
        "source_title", "source_url", "trust",
    }
    if not isinstance(data, dict) or set(data) != required:
        raise ValueError("research receipt fields differ from the required schema")
    if data.get("schema") != "ai-human.research-receipt/v1":
        raise ValueError("unsupported research receipt schema")
    safe_identity(str(data["receipt_id"]), "research receipt id")
    parse_recorded_utc(data["accessed_utc"], "research accessed_utc")
    published = data["published_or_updated"]
    if published != "NOT_PROVIDED_BY_SOURCE" and not ISO_DATE.fullmatch(str(published)):
        raise ValueError("research publication date must be YYYY-MM-DD or NOT_PROVIDED_BY_SOURCE")
    parsed = urllib.parse.urlparse(str(data["source_url"]))
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.username or parsed.password:
        raise ValueError("research source URL must be a public HTTP(S) URL without credentials")
    if data["trust"] not in IMPROVEMENT_RESEARCH_TRUST:
        raise ValueError("research trust classification is invalid")
    if data["instruction_content_ignored"] is not True:
        raise ValueError("research must record that source instructions were ignored")
    if data["personal_data_excluded"] is not True:
        raise ValueError("research receipt must exclude personal data")
    clean(data["source_title"], "research source title")
    claims = data["claim_summary"]
    if (
        not isinstance(claims, list) or not claims or len(claims) > BATCH_CAP
        or any(not isinstance(item, str) or not item.strip() or len(item) > 500 for item in claims)
    ):
        raise ValueError("research claim summary must contain 1 to 25 concise text claims")
    if contains_secret_material(data):
        raise ValueError("research receipt appears to contain secret material")
    return data


def validate_improvement_state(worker):
    failures = []
    root = worker / IMPROVEMENT_ROOT
    if not root.exists():
        return failures
    if root.is_symlink() or not root.is_dir():
        return ["quarterly improvement state must be a real directory"]
    for path in root.rglob("*"):
        if path.is_symlink():
            failures.append(
                "quarterly improvement state may not contain a symbolic link: "
                + path.relative_to(worker).as_posix()
            )
    try:
        config = improvement_config(worker)
    except Exception as exc:
        config = None
        failures.append("invalid quarterly improvement config: " + str(exc))
    try:
        schedule = improvement_schedule(worker)
    except Exception as exc:
        schedule = None
        failures.append("invalid quarterly improvement schedule: " + str(exc))
    if schedule and not config:
        failures.append("quarterly improvement schedule exists without a valid config")
    if config:
        try:
            automation_path = worker / "AUTOMATIONS.md"
            if automation_path.read_text(encoding="utf-8") != render_improvement_automation(
                worker, config, schedule
            ):
                failures.append(
                    "visible quarterly automation row differs from private improvement state"
                )
        except Exception as exc:
            failures.append("invalid visible quarterly automation row: " + str(exc))
    research_root = root / "research"
    if research_root.is_dir():
        for path in research_root.glob("*.json"):
            try:
                record = read_json(path)
                payload = {key: record[key] for key in (
                    "accessed_utc", "claim_summary", "instruction_content_ignored",
                    "personal_data_excluded", "published_or_updated", "receipt_id", "schema",
                    "source_title", "source_url", "trust",
                )}
                validate_research_payload(payload)
                if path.stem != record["receipt_id"]:
                    raise ValueError("research receipt filename differs from its id")
                if record.get("status") not in {"ACTIVE", "SUPERSEDED"}:
                    raise ValueError("research receipt status is invalid")
                parse_recorded_utc(record.get("recorded_utc"), "research recorded_utc")
            except Exception as exc:
                failures.append(
                    "invalid quarterly improvement research receipt " + path.name + ": " + str(exc)
                )
    runs_root = root / "runs"
    if runs_root.is_dir():
        for path in runs_root.glob("*.json"):
            try:
                record = read_json(path)
                if record.get("schema") != "ai-human.improvement-run/v1":
                    raise ValueError("unsupported run schema")
                if record.get("status") != "COMPLETED_READ_ONLY":
                    raise ValueError("run is not read-only complete")
                parse_recorded_utc(record.get("created_utc"), "run created_utc")
                recommendations = record.get("recommendations")
                if not isinstance(recommendations, list) or len(recommendations) > BATCH_CAP:
                    raise ValueError("run recommendations exceed the batch cap")
                if any(item.get("decision") != "REVIEW_REQUIRED" for item in recommendations):
                    raise ValueError("run contains a recommendation without human review")
                if any(item.get("activation") != "NOT_ACTIVATED" for item in recommendations):
                    raise ValueError("run contains an activated recommendation")
            except Exception as exc:
                failures.append(
                    "invalid quarterly improvement run " + path.name + ": " + str(exc)
                )
    return failures


def controlled_state_paths(worker):
    paths = [worker / name for name in COORDINATION_STATE_FILES]
    paths.append(worker / "AUTOMATIONS.md")
    capability_root = worker / CAPABILITY_ROOT
    if capability_root.is_dir():
        paths.extend(path for path in capability_root.rglob("*.json") if path.is_file())
    improvement_root = worker / IMPROVEMENT_ROOT
    if improvement_root.is_dir():
        paths.extend(path for path in improvement_root.rglob("*.json") if path.is_file())
    return sorted(paths, key=lambda path: path.relative_to(worker).as_posix())


def controlled_state_hash(worker):
    digest = hashlib.sha256()
    for path in controlled_state_paths(worker):
        relative = path.relative_to(worker).as_posix()
        digest.update(relative.encode("utf-8") + b"\0")
        if path.is_file():
            digest.update(bytes.fromhex(sha256(path)))
        else:
            digest.update(b"MISSING")
        digest.update(b"\n")
    return digest.hexdigest()


def lease_file(worker):
    return worker / LEASE_PATH


def read_lease(worker, required=True):
    path = lease_file(worker)
    if not path.is_file():
        if required:
            raise ValueError("no active session lease")
        return None
    try:
        lease = read_json(path)
    except Exception as exc:
        raise ValueError("invalid session lease: " + str(exc))
    if lease.get("schema") != "ai-human.session-lease/v1":
        raise ValueError("unsupported session lease schema")
    return lease


def require_lease(worker, session_id, expected_state_hash=None):
    lease = read_lease(worker)
    if lease.get("session_id") != session_id:
        raise ValueError("session lease belongs to another writer")
    current = controlled_state_hash(worker)
    recorded = str(lease.get("state_hash", ""))
    if current != recorded:
        raise ValueError("controlled state changed outside the lease transaction")
    if expected_state_hash is not None and current != expected_state_hash:
        raise ValueError("expected-state hash mismatch; refresh before writing")
    return lease, current


def refresh_lease_state(worker, lease):
    updated = dict(lease)
    updated["state_hash"] = controlled_state_hash(worker)
    updated["updated_utc"] = now_utc()
    atomic_json(lease_file(worker), updated)
    return updated


def unique_receipt(worker, prefix):
    parent = worker / CONTROL_RECEIPTS
    parent.mkdir(parents=True, exist_ok=True)
    stem = prefix + "-" + now_utc()
    path = parent / (stem + ".json")
    counter = 2
    while path.exists():
        path = parent / (stem + "-" + str(counter) + ".json")
        counter += 1
    return path


def state_hashes(worker):
    return {name: sha256(worker / name) for name in STATE_FILES if (worker / name).is_file()}


def release_root_from_script():
    candidate = Path(__file__).resolve().parents[1]
    if (candidate / "release-manifest.json").is_file() and (candidate / "starter").is_dir():
        return candidate
    raise ValueError("install must run from a checked-out or extracted release")


def load_release(root):
    root = Path(root).expanduser().resolve()
    manifest_path = root / "release-manifest.json"
    if not manifest_path.is_file():
        raise ValueError("release manifest missing: " + str(manifest_path))
    manifest = read_json(manifest_path)
    if manifest.get("schema") != "ai-human.workspace-release/v1":
        raise ValueError("unsupported release manifest schema")
    version_tuple(manifest.get("version", ""))
    if release_status(manifest) != RELEASED:
        raise ValueError("release is a local candidate and cannot be installed")
    if manifest.get("approval_status") != "APPROVED_BY_OWNER":
        raise ValueError("release is not owner-approved")
    records = manifest.get("managed_files") or []
    declared_protected = manifest.get("never_managed") or []
    if not isinstance(declared_protected, list) or any(
        not isinstance(value, str) or not value.strip() for value in declared_protected
    ):
        raise ValueError("never_managed must be a list of non-empty paths or boundary labels")
    targets = set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("managed file records must be JSON objects")
        source_rel = safe_relative(str(record.get("source", "")), "managed source")
        target_rel = safe_relative(str(record.get("target", "")), "managed target")
        target_key = portable_key(target_rel)
        if not target_key.startswith(".ai-human/"):
            raise ValueError("managed target is outside .ai-human: " + str(target_rel))
        if is_protected_managed_path(target_key, declared_protected):
            raise ValueError("release tries to manage protected local state: " + target_key)
        if target_key in targets:
            raise ValueError("duplicate managed target: " + str(target_rel))
        targets.add(target_key)
        source = release_file(root, source_rel)
        if sha256(source) != record.get("sha256"):
            raise ValueError("managed source hash mismatch: " + str(source_rel))
    if not REQUIRED_MANAGED.issubset(targets):
        raise ValueError("release is missing required managed targets")
    return root, manifest


def load_components(root, release_manifest):
    path = root / "component-manifest.json"
    if not path.is_file():
        raise ValueError("component manifest missing: " + str(path))
    manifest = read_json(path)
    if manifest.get("schema") != "ai-human.component-release/v1":
        raise ValueError("unsupported component manifest schema")
    if release_status(manifest) != RELEASED:
        raise ValueError("components are local candidates and cannot be installed")
    if manifest.get("approval_status") != "APPROVED_BY_OWNER":
        raise ValueError("component release is not owner-approved")
    if manifest.get("version") != release_manifest.get("version"):
        raise ValueError("component and release versions differ")
    if manifest.get("repository") != release_manifest.get("repository"):
        raise ValueError("component and release repositories differ")
    records = manifest.get("components") or []
    identifiers = set()
    for record in records:
        identifier = str(record.get("id", ""))
        if not COMPONENT_ID.fullmatch(identifier):
            raise ValueError("invalid component id: " + repr(identifier))
        if identifier in identifiers:
            raise ValueError("duplicate component id: " + identifier)
        identifiers.add(identifier)
        if record.get("type") not in {"skill", "reference-pack"}:
            raise ValueError("unsupported component type: " + repr(record.get("type")))
        source_rel = safe_relative(str(record.get("source", "")), "component source")
        source_key = portable_key(source_rel)
        if not source_key.startswith("packages/"):
            raise ValueError("component source is outside packages/: " + source_key)
        source = release_directory(root, source_rel)
        digest, count = tree_sha256(source)
        if digest != record.get("tree_sha256"):
            raise ValueError("component tree hash mismatch: " + identifier)
        if count != record.get("file_count"):
            raise ValueError("component file count mismatch: " + identifier)
        if record.get("type") == "skill":
            validate_skill_source(source, identifier)
    return manifest


def validate_skill_source(source, identifier):
    skill = source / "SKILL.md"
    if not skill.is_file():
        raise ValueError("skill component lacks SKILL.md: " + identifier)
    text = skill.read_text(encoding="utf-8")
    frontmatter = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, flags=re.S)
    if not frontmatter:
        raise ValueError("skill frontmatter missing: " + identifier)
    match = re.search(r"^name:\s*['\"]?([^'\"\n]+)", frontmatter.group(1), flags=re.M)
    if not match or match.group(1).strip() != identifier:
        raise ValueError("skill frontmatter name differs from component id: " + identifier)


def live_task(worker):
    path = worker / "MASTER_CURSOR.md"
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"^## LIVE TASK\s*$\n(.*?)(?=^## |\Z)", text, flags=re.M | re.S)
    value = match.group(1).strip() if match else ""
    if not value or "NOT SET" in value.upper() or value.upper() in {"NONE", "NO LIVE TASK"}:
        return ""
    return value


def live_task_id(worker):
    """Return the declared task ID without treating description backticks as the ID."""
    value = live_task(worker)
    if not value:
        return ""
    explicit = re.search(r"^Task ID:\s*`([^`]+)`\s*$", value, flags=re.M | re.I)
    if explicit:
        return explicit.group(1).strip()
    first_line = next((line.strip() for line in value.splitlines() if line.strip()), "")
    legacy = re.match(r"^(?:[-*]\s*)?`([^`]+)`(?:\s|$)", first_line)
    if legacy:
        return legacy.group(1).strip()
    return first_line.split()[0].strip("*`-") if first_line else ""


def render(content, replacements):
    for token, value in replacements.items():
        content = content.replace(token, value)
    return content


def managed_targets(manifest):
    return [str(record["target"]) for record in manifest.get("managed_files", [])]


def install_metadata(worker):
    path = worker / ".ai-human/install.json"
    if not path.is_file():
        raise ValueError("install metadata missing")
    return read_json(path)


def write_install_metadata(worker, manifest, settings=None):
    path = worker_target(worker, ".ai-human/install.json", "install metadata target")
    preserved = read_json(path) if path.is_file() else {}
    if settings:
        preserved.update(settings)
    preserved.update(
        {
            "installed_version": manifest["version"],
            "managed_targets": managed_targets(manifest),
            "repository": manifest["repository"],
            "schema": "ai-human.workspace-install/v1",
        }
    )
    atomic_json(
        path,
        preserved,
    )
    atomic_json(
        worker_target(worker, ".ai-human/release-manifest.json", "installed manifest target"),
        manifest,
    )


def copy_release_files(worker, release, manifest):
    for record in manifest["managed_files"]:
        source = release_file(release, record["source"])
        target = worker_target(worker, record["target"], "managed worker target")
        target.parent.mkdir(parents=True, exist_ok=True)
        temp = target.with_name(target.name + ".update-temp")
        shutil.copy2(source, temp)
        os.replace(temp, target)


def parse_table_rows(path):
    rows = []
    if not path.is_file():
        return rows
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [
            cell.replace("\\|", "|").strip()
            for cell in re.split(r"(?<!\\)\|", line.strip().strip("|"))
        ]
        if cells and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        if cells and cells[0] not in {"ID", "Task ID", "—", ""}:
            rows.append(cells)
    return rows


def parse_table_ids(path):
    return [row[0] for row in parse_table_rows(path)]


def markdown_table_row(cells):
    return "| " + " | ".join(
        clean(str(cell).replace("\\|", "|"), "table cell") for cell in cells
    ) + " |"


def update_task_table(content, task_id, replacement=None):
    """Remove one task row and optionally insert its deterministic replacement."""
    lines = content.rstrip("\n").splitlines()
    table_start = next(
        (
            index for index, line in enumerate(lines)
            if line.strip().startswith("|")
            and re.split(r"(?<!\\)\|", line.strip().strip("|"))[0].strip()
            in {"ID", "Task ID"}
        ),
        None,
    )
    if table_start is None:
        raise ValueError("task-state table is missing")
    table_end = table_start
    while table_end < len(lines) and lines[table_end].strip().startswith("|"):
        table_end += 1
    kept = []
    for line in lines[table_start:table_end]:
        cells = [
            cell.replace("\\|", "|").strip()
            for cell in re.split(r"(?<!\\)\|", line.strip().strip("|"))
        ]
        if cells and cells[0] == task_id:
            continue
        kept.append(line)
    if replacement is not None:
        kept.append(markdown_table_row(replacement))
    lines[table_start:table_end] = kept
    return "\n".join(lines) + "\n"


def replace_markdown_section(content, heading, body):
    pattern = r"(^## " + re.escape(heading) + r"\s*$\n).*?(?=^## |\Z)"
    updated, count = re.subn(
        pattern,
        lambda match: match.group(1) + "\n" + body.strip() + "\n\n",
        content,
        count=1,
        flags=re.M | re.S,
    )
    if count != 1:
        raise ValueError("missing Markdown section: " + heading)
    return updated.rstrip() + "\n"


def parameter_value(worker, name):
    for row in parse_table_rows(worker / "PARAMETERS.md"):
        if len(row) >= 2 and row[0] == name:
            return row[1]
    return ""


def next_local_task_id(worker):
    used = set()
    for name in COORDINATION_STATE_FILES:
        used.update(parse_table_ids(worker / name))
    current = live_task_id(worker)
    if current:
        used.add(current)
    number = max(
        (int(match.group(1)) for value in used if (match := re.fullmatch(r"LOCAL-(\d+)", value))),
        default=0,
    ) + 1
    while "LOCAL-" + str(number).zfill(3) in used:
        number += 1
    return "LOCAL-" + str(number).zfill(3)


WEAK_COMPLETION_EVIDENCE = {
    "0", "asexpected", "changed", "complete", "completed", "done", "fine",
    "good", "missing", "na", "nil", "noissues", "none", "notset", "ok",
    "okay", "pass", "passed", "seeabove", "tbd", "todo", "verified", "x",
    "y", "yes",
}
WEAK_COMPLETION_TOKENS = WEAK_COMPLETION_EVIDENCE | {
    "a", "after", "all", "and", "applicable", "approved", "as", "been", "checked",
    "confirmed", "correct", "correctly", "detected", "did", "everything", "expected",
    "finished", "found", "fully", "has", "issues", "looks", "matches", "me", "n",
    "no", "not", "nothing", "output", "problems", "properly", "report", "reviewed",
    "see", "steps", "success", "successful", "successfully", "task", "the", "to",
    "verification", "with", "work", "working", "works",
}
MIN_COMPLETION_EVIDENCE_CHARACTERS = 12


def normalized_evidence_result(value):
    """Normalize a leading PASS token while keeping explanatory text out of logic."""
    text = unicodedata.normalize("NFKC", str(value)).strip().upper()
    return "PASS" if re.match(r"^PASS(?:\s|[-—:;,.])", text + " ") else text


def completion_evidence_parts(value):
    text = unicodedata.normalize("NFKC", value).casefold()
    normalized = "".join(
        character for character in text
        if character.isalnum() or unicodedata.category(character).startswith("M")
    )
    tokens = []
    current = []
    for character in text:
        if character.isalnum() or unicodedata.category(character).startswith("M"):
            current.append(character)
        elif current:
            tokens.append("".join(current))
            current = []
    if current:
        tokens.append("".join(current))
    return normalized, tokens


def placeholder(value):
    normalized, tokens = completion_evidence_parts(value)
    return (
        not normalized
        or normalized in WEAK_COMPLETION_EVIDENCE
        or (tokens and all(token in WEAK_COMPLETION_TOKENS for token in tokens))
        or normalized.isdigit()
        or len(set(normalized)) == 1
        or len(normalized) < MIN_COMPLETION_EVIDENCE_CHARACTERS
    )


def validate_completion_records(worker):
    failures = []
    evidence_by_task = {}
    for row in parse_table_rows(worker / "EVIDENCE_LOG.md"):
        if len(row) < 8:
            failures.append("EVIDENCE_LOG.md row has fewer than 8 required columns: " + row[0])
            continue
        evidence_by_task.setdefault(row[0], []).append(row)
    completed_ids = set()
    for row in parse_table_rows(worker / "COMPLETED_LEDGER.md"):
        task_id = row[0]
        if task_id in completed_ids:
            failures.append("duplicate completed task id: " + task_id)
        completed_ids.add(task_id)
        if len(row) < 7:
            failures.append("COMPLETED_LEDGER.md row has fewer than 7 required columns: " + task_id)
            continue
        if placeholder(row[5]):
            failures.append("completed task lacks evidence references: " + task_id)
        evidence_rows = evidence_by_task.get(task_id, [])
        passing = [
            evidence for evidence in evidence_rows
            if normalized_evidence_result(evidence[5]) == "PASS"
            and not placeholder(evidence[4])
            and not placeholder(evidence[6])
            and not placeholder(evidence[7])
        ]
        if not passing:
            failures.append(
                "completed task lacks a passing detailed evidence row with verification, "
                "artifact/readback and undo: " + task_id
            )
    for state_name in ("OPEN_REGISTER.md", "TODAY.md"):
        overlap = completed_ids.intersection(parse_table_ids(worker / state_name))
        for task_id in sorted(overlap):
            failures.append("completed task remains in " + state_name + ": " + task_id)
    return failures


def validate_worker(worker, quiet=False):
    failures = []
    if (worker / ".ai-human").is_symlink():
        failures.append(".ai-human may not be a symbolic link")
    for name in STATE_FILES:
        path = worker / name
        if path.is_symlink():
            failures.append("local state may not be a symbolic link: " + name)
        elif not path.is_file() or path.stat().st_size == 0:
            failures.append("missing or empty local file: " + name)

    version_path = worker / ".ai-human/VERSION"
    version = version_path.read_text(encoding="utf-8").strip() if version_path.is_file() else ""
    try:
        version_tuple(version)
    except ValueError as exc:
        failures.append(str(exc))

    metadata = {}
    metadata_path = worker / ".ai-human/install.json"
    try:
        metadata = read_json(metadata_path)
    except Exception as exc:
        failures.append("invalid install metadata: " + str(exc))
    manifest = {}
    manifest_path = worker / ".ai-human/release-manifest.json"
    try:
        manifest = read_json(manifest_path)
    except Exception as exc:
        failures.append("invalid installed release manifest: " + str(exc))

    if metadata:
        if metadata.get("schema") != "ai-human.workspace-install/v1":
            failures.append("unsupported install metadata schema")
        try:
            version_tuple(str(metadata.get("installed_version", "")))
        except ValueError as exc:
            failures.append("install metadata " + str(exc))
        if metadata.get("timezone"):
            try:
                validate_timezone(str(metadata["timezone"]))
            except ValueError as exc:
                failures.append(str(exc))
        if metadata.get("automatic_updates") not in {None, "DISABLED", "ACTIVE"}:
            failures.append("invalid automatic update setting")
        required_identity = {
            "company", "legal_entity", "operating_units", "jurisdictions",
            "purpose_scope", "user_relationship", "compliance_owner",
            "gate_profile_id", "gate_profile_sha256", "gate_rendered_hashes",
        }
        missing_identity = required_identity - set(metadata)
        if missing_identity:
            failures.append(
                "install metadata is missing gate-profile identity: "
                + ", ".join(sorted(missing_identity))
            )
    mode = None
    try:
        mode = worker_mode(worker)
    except Exception as exc:
        failures.append("invalid AI-human mode: " + str(exc))
    if mode == MODE_SUSPENDED and metadata.get("automatic_updates") != "DISABLED":
        failures.append("suspended worker must have automatic updates disabled")
    if manifest:
        if manifest.get("schema") != "ai-human.workspace-release/v1":
            failures.append("unsupported installed release manifest schema")
        if manifest.get("approval_status") != "APPROVED_BY_OWNER":
            failures.append("installed release is not owner-approved")
        if release_status(manifest) != RELEASED:
            failures.append("installed release status is not RELEASED")
        try:
            version_tuple(str(manifest.get("version", "")))
        except ValueError as exc:
            failures.append("installed manifest " + str(exc))

    if metadata and manifest:
        installed_version = str(metadata.get("installed_version", ""))
        manifest_version = str(manifest.get("version", ""))
        if version != installed_version or version != manifest_version:
            failures.append("VERSION, install metadata and manifest versions differ")
        if not metadata.get("repository") or metadata.get("repository") != manifest.get("repository"):
            failures.append("install metadata and manifest repositories differ")

        declared_protected = manifest.get("never_managed") or []
        if not isinstance(declared_protected, list) or any(
            not isinstance(value, str) or not value.strip() for value in declared_protected
        ):
            failures.append("installed never_managed must be a list of non-empty values")
            declared_protected = []
        targets = set()
        for record in manifest.get("managed_files") or []:
            if not isinstance(record, dict):
                failures.append("installed managed file record is not a JSON object")
                continue
            target_value = str(record.get("target", ""))
            try:
                target_rel = safe_relative(target_value, "installed managed target")
            except ValueError as exc:
                failures.append(str(exc))
                continue
            target_key = portable_key(target_rel)
            if not target_key.startswith(".ai-human/"):
                failures.append("installed managed target is outside .ai-human: " + target_key)
                continue
            if is_protected_managed_path(target_key, declared_protected):
                failures.append("installed release tries to manage protected local state: " + target_key)
                continue
            if target_key in targets:
                failures.append("duplicate installed managed target: " + target_key)
                continue
            targets.add(target_key)
            try:
                target = worker_target(worker, target_rel, "installed managed target")
            except ValueError as exc:
                failures.append(str(exc))
                continue
            if not target.is_file() or target.stat().st_size == 0:
                failures.append("missing or empty managed file: " + target_key)
            elif sha256(target) != record.get("sha256"):
                failures.append("managed file integrity mismatch: " + target_key)
        for target in sorted(REQUIRED_MANAGED - targets):
            failures.append("required installed managed target missing: " + target)
        metadata_targets = {portable_key(value) for value in metadata.get("managed_targets") or []}
        if metadata_targets != targets:
            failures.append("install metadata managed targets differ from the manifest")

    profile = None
    profile_path = worker / GATE_PROFILE_PATH
    if profile_path.is_file() and metadata.get("gate_profile_sha256") != sha256(profile_path):
        failures.append("gate-profile integrity mismatch")
    try:
        raw_profile = read_json(profile_path)
        expected_profile = None
        expected_fields = {
            "company", "legal_entity", "operating_units", "jurisdictions",
            "purpose_scope", "user_relationship", "compliance_owner",
        }
        if metadata and expected_fields.issubset(metadata):
            expected_profile = {field: metadata[field] for field in expected_fields}
        profile = validate_gate_profile(raw_profile, expected=expected_profile)
    except Exception as exc:
        failures.append("invalid local gate profile: " + str(exc))
    if profile:
        if metadata.get("gate_profile_id") != profile["profile_id"]:
            failures.append("install metadata gate profile id differs from the local profile")
        rendered = render_gate_files(profile)
        recorded_hashes = metadata.get("gate_rendered_hashes")
        if not isinstance(recorded_hashes, dict) or set(recorded_hashes) != set(PROFILE_RENDERED_FILES):
            failures.append("install metadata gate-rendered hashes are incomplete")
            recorded_hashes = {}
        for name, expected_content in rendered.items():
            path = worker / name
            if path.is_file():
                if path.read_text(encoding="utf-8") != expected_content:
                    failures.append("gate-rendered file differs from the local profile: " + name)
                if recorded_hashes.get(name) != sha256(path):
                    failures.append("gate-rendered file integrity mismatch: " + name)
        identity_files = {
            "COMPANY.md": [
                profile["company"], profile["legal_entity"], profile["compliance_owner"],
                profile["profile_id"], *profile["operating_units"], *profile["jurisdictions"],
            ],
            "PARAMETERS.md": [profile["purpose_scope"], profile["user_relationship"]],
        }
        for name, values in identity_files.items():
            path = worker / name
            if path.is_file():
                content = path.read_text(encoding="utf-8")
                for value in values:
                    if value not in content:
                        failures.append(name + " is missing gate-profile identity: " + value)

    for name in ("AI-HUMAN.md", "COMPANY.md", "PARAMETERS.md", "ROLE.md"):
        path = worker / name
        if path.is_file() and re.search(r"\{\{[A-Z0-9_]+\}\}", path.read_text(encoding="utf-8")):
            failures.append("unresolved parameter in " + name)
    live = live_task(worker)
    if live:
        task_id = live_task_id(worker)
        if task_id and task_id not in parse_table_ids(worker / "OPEN_REGISTER.md"):
            failures.append("live task is missing from OPEN_REGISTER.md: " + task_id)
        if task_id and task_id not in parse_table_ids(worker / "TODAY.md"):
            failures.append("live task is missing from TODAY.md: " + task_id)
    failures.extend(validate_improvement_state(worker))
    failures.extend(validate_completion_records(worker))
    lease = None
    try:
        lease = read_lease(worker, required=False)
    except ValueError as exc:
        failures.append(str(exc))
    if lease:
        if not SAFE_ID.fullmatch(str(lease.get("session_id", ""))):
            failures.append("invalid session id in lease")
        if lease.get("state_hash") != controlled_state_hash(worker):
            failures.append("controlled state differs from the active lease hash")
    if failures:
        if not quiet:
            print("AI-HUMAN WORKER VALIDATION: FAIL")
            for failure in failures:
                print("- " + failure)
        return False, failures
    if not quiet:
        print("AI-HUMAN WORKER VALIDATION: PASS")
        print("- worker: " + str(worker))
        print("- shared system version: " + version)
        print("- company, role and user state are separate from managed files")
        if profile:
            print("- local gate profile: " + profile["profile_id"] + " (CONFIRMED)")
    return True, []


def install(args):
    worker = safe_worker(args.worker, must_exist=False)
    release, manifest = load_release(args.source or release_root_from_script())
    timezone = validate_timezone(args.timezone) if args.timezone else None
    expected_profile, gate_profile = gate_setup_from_args(args)
    company = expected_profile["company"]
    legal_entity = expected_profile["legal_entity"]
    operating_units = expected_profile["operating_units"]
    jurisdictions = expected_profile["jurisdictions"]
    purpose = expected_profile["purpose_scope"]
    user_relationship = expected_profile["user_relationship"]
    compliance_owner = expected_profile["compliance_owner"]
    rendered_gate_files = render_gate_files(gate_profile)
    settings = {
        "automatic_updates": "ACTIVE" if args.automatic_updates else "DISABLED",
        **expected_profile,
        "gate_profile_id": gate_profile["profile_id"],
    }
    if args.worker_id:
        settings["worker_id"] = safe_identity(args.worker_id, "worker id")
    if args.supervisor:
        settings["supervisor_id"] = clean(args.supervisor, "supervisor")
    if timezone:
        settings["timezone"] = timezone
    existed = worker.exists()
    if existed and any(worker.iterdir()) and not args.adopt:
        raise ValueError("target is not empty; use --adopt to preserve existing files")
    if (worker / ".ai-human").exists():
        raise ValueError("the system is already installed; use update instead")
    worker.mkdir(parents=True, exist_ok=True)
    replacements = {
        "{{COMPANY_NAME}}": company,
        "{{LEGAL_ENTITY}}": legal_entity,
        "{{OPERATING_UNITS}}": "; ".join(operating_units),
        "{{JURISDICTIONS}}": "; ".join(jurisdictions),
        "{{COMPANY_OWNER}}": clean(args.company_owner, "company owner"),
        "{{OWNER_NAME}}": clean(args.owner, "owner"),
        "{{WORKER_NAME}}": clean(args.name, "worker name"),
        "{{ROLE_NAME}}": clean(args.role, "role"),
        "{{PURPOSE}}": purpose,
        "{{USER_RELATIONSHIP}}": user_relationship,
        "{{COMPLIANCE_OWNER}}": compliance_owner,
        "{{GATE_PROFILE_ID}}": gate_profile["profile_id"],
        "{{GATE_REVIEW_DUE}}": gate_profile["review_due"],
        "{{BRAIN}}": args.brain,
        "{{TASK_SELECTION}}": "Owner promotes the live task" if args.task_selection == "owner" else "AI may select the highest-priority unblocked row",
        "{{BATCH_CAP}}": str(args.batch_cap),
        "{{WORKER_ID}}": args.worker_id or "NOT SET",
        "{{TIMEZONE}}": timezone or "NOT SET",
        "{{SUPERVISOR_ID}}": args.supervisor or "NOT SET",
        "{{AUTOMATIC_UPDATES}}": "ACTIVE" if args.automatic_updates else "DISABLED",
    }
    created = []
    skipped = []
    try:
        for source in sorted((release / "starter").iterdir()):
            if not source.is_file():
                continue
            if source.name in PROFILE_RENDERED_FILES:
                continue
            target = worker / source.name
            if target.exists():
                skipped.append(source.name)
                continue
            content = render(source.read_text(encoding="utf-8"), replacements)
            atomic_text(target, content)
            created.append(source.name)
        for name, content in rendered_gate_files.items():
            target = worker / name
            if target.exists():
                if target.read_text(encoding="utf-8") != content:
                    raise ValueError(
                        "existing " + name + " conflicts with the confirmed gate profile; "
                        "reconcile it explicitly before adoption"
                    )
                skipped.append(name)
                continue
            atomic_text(target, content)
            created.append(name)
        copy_release_files(worker, release, manifest)
        atomic_json(worker / GATE_PROFILE_PATH, gate_profile)
        settings["gate_profile_sha256"] = sha256(worker / GATE_PROFILE_PATH)
        settings["gate_rendered_hashes"] = {
            name: sha256(worker / name) for name in PROFILE_RENDERED_FILES
        }
        settings["created_starter_files"] = {
            name: sha256(worker / name) for name in created
        }
        atomic_json(
            mode_file(worker),
            {
                "changed_utc": now_utc(),
                "schema": "ai-human.mode/v1",
                "status": MODE_ACTIVE,
            },
        )
        write_install_metadata(worker, manifest, settings)
        if skipped:
            atomic_text(
                worker / ".ai-human/ADOPTION-NOTICE.md",
                "# Adoption notice\n\nPreserved existing project files: " + ", ".join(skipped) +
                ". Ask the project owner to reconcile any existing adapter instructions with `.ai-human/system/AGENT-RULES.md`.\n",
            )
        ok, failures = validate_worker(worker, quiet=True)
        if not ok:
            raise ValueError("installed worker validation failed: " + "; ".join(failures))
    except Exception:
        if (worker / ".ai-human").exists():
            shutil.rmtree(worker / ".ai-human")
        for name in created:
            path = worker / name
            if path.is_file():
                path.unlink()
        if not existed and worker.exists() and not any(worker.iterdir()):
            worker.rmdir()
        raise
    print("AI-HUMAN INSTALL: PASS")
    print("- worker: " + str(worker))
    print("- version: " + manifest["version"])
    print("- created local files: " + str(len(created)))
    print("- preserved existing files: " + str(len(skipped)))
    print("- local gate profile: " + gate_profile["profile_id"] + " (CONFIRMED)")
    print("- unattended updates: " + settings["automatic_updates"].lower())


GATE_BINDING_START = "<!-- AI-HUMAN GATE PROFILE BINDING START -->"
GATE_BINDING_END = "<!-- AI-HUMAN GATE PROFILE BINDING END -->"


def gate_binding_section(profile, target):
    if target == "COMPANY.md":
        rows = (
            ("Company or group", profile["company"]),
            ("Exact legal entity", profile["legal_entity"]),
            ("Operating unit(s)", "; ".join(profile["operating_units"])),
            ("Jurisdiction(s)", "; ".join(profile["jurisdictions"])),
            ("Compliance owner", profile["compliance_owner"]),
            ("Active Gate 0 profile", profile["profile_id"]),
            ("Gate profile review due", profile["review_due"]),
        )
    elif target == "PARAMETERS.md":
        rows = (
            ("Purpose bound to Gate 0", profile["purpose_scope"]),
            ("User relationship to the company", profile["user_relationship"]),
        )
    else:
        raise ValueError("unsupported gate-binding target: " + target)
    lines = [
        GATE_BINDING_START,
        "## Confirmed Gate 0 binding",
        "",
        "| Field | Value |",
        "|---|---|",
    ]
    lines.extend(
        "| " + markdown_cell(label) + " | " + markdown_cell(value) + " |"
        for label, value in rows
    )
    lines.extend((GATE_BINDING_END, ""))
    return "\n".join(lines)


def upsert_gate_binding(path, profile):
    content = path.read_text(encoding="utf-8") if path.is_file() else "# " + path.stem + "\n"
    section = gate_binding_section(profile, path.name)
    start = content.find(GATE_BINDING_START)
    end = content.find(GATE_BINDING_END)
    if (start < 0) != (end < 0):
        raise ValueError("incomplete Gate 0 binding markers in " + path.name)
    if start >= 0:
        end += len(GATE_BINDING_END)
        content = content[:start].rstrip() + "\n\n" + section + content[end:].lstrip("\n")
    else:
        content = content.rstrip() + "\n\n" + section
    atomic_text(path, content)


def migrated_work_gates(legacy_text):
    body = re.sub(
        r"^## Gate 0[^\n]*\n.*?(?=^## |\Z)",
        "",
        legacy_text,
        count=1,
        flags=re.M | re.S | re.I,
    ).strip()
    body = re.sub(r"^# GATES\s*", "", body, count=1, flags=re.I)
    return (
        "# WORK GATES — MIGRATED\n\n"
        "These task-specific locks were recoverably separated from the legacy "
        "GATES.md. They may narrow work but never replace or weaken the confirmed "
        "entity profile. Review them with the role owner.\n\n" + body + "\n"
    )


def configure_gate_profile(args):
    worker = safe_worker(args.worker)
    if not args.at_checkpoint:
        raise ValueError("Gate 0 configuration requires --at-checkpoint")
    if live_task(worker):
        raise ValueError("Gate 0 configuration requires no live task")
    if read_lease(worker, required=False):
        raise ValueError("Gate 0 configuration requires no active writer lease")
    release, _release_manifest = load_release(args.source)
    expected, profile = gate_setup_from_args(args)
    rendered = render_gate_files(profile)

    relative_paths = [
        Path("COMPANY.md"), Path("PARAMETERS.md"), Path("GATES.md"),
        Path("WORK-GATES.md"), Path("COMPLIANCE-SOURCES.md"), Path("WORKSPACE-MAP.md"),
        GATE_PROFILE_PATH, Path(".ai-human/install.json"),
    ]
    migration_root = (
        worker / ".ai-human/control/gate-profile-migrations" / ("profile-" + now_utc())
    )
    counter = 2
    while migration_root.exists():
        migration_root = migration_root.with_name(migration_root.name + "-" + str(counter))
        counter += 1
    before_root = migration_root / "before"
    backup_records = []
    for relative in relative_paths:
        source = worker / relative
        existed = source.is_file()
        backup_records.append({"path": relative.as_posix(), "existed": existed})
        if existed:
            backup = before_root / relative
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, backup)
    atomic_json(
        migration_root / "before.json",
        {"files": backup_records, "schema": "ai-human.gate-profile-migration-before/v1"},
    )

    try:
        legacy_gates = (worker / "GATES.md").read_text(encoding="utf-8") if (worker / "GATES.md").is_file() else ""
        if not (worker / "WORK-GATES.md").is_file():
            if legacy_gates.strip():
                atomic_text(worker / "WORK-GATES.md", migrated_work_gates(legacy_gates))
            else:
                atomic_text(
                    worker / "WORK-GATES.md",
                    (release / "starter/WORK-GATES.md").read_text(encoding="utf-8"),
                )
        if not (worker / "WORKSPACE-MAP.md").is_file():
            atomic_text(
                worker / "WORKSPACE-MAP.md",
                (release / "starter/WORKSPACE-MAP.md").read_text(encoding="utf-8"),
            )
        upsert_gate_binding(worker / "COMPANY.md", profile)
        upsert_gate_binding(worker / "PARAMETERS.md", profile)
        for name, content in rendered.items():
            atomic_text(worker / name, content)
        atomic_json(worker / GATE_PROFILE_PATH, profile)

        metadata = install_metadata(worker)
        metadata.update(expected)
        metadata.update(
            {
                "gate_profile_configured_utc": now_utc(),
                "gate_profile_id": profile["profile_id"],
                "gate_profile_sha256": sha256(worker / GATE_PROFILE_PATH),
                "gate_rendered_hashes": {
                    name: sha256(worker / name) for name in PROFILE_RENDERED_FILES
                },
            }
        )
        atomic_json(worker / ".ai-human/install.json", metadata)
        ok, failures = validate_worker(worker, quiet=True)
        if not ok:
            raise ValueError("configured worker validation failed: " + "; ".join(failures))
    except Exception:
        for record in backup_records:
            relative = Path(record["path"])
            target = worker / relative
            backup = before_root / relative
            if record["existed"]:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup, target)
            elif target.is_file() or target.is_symlink():
                target.unlink()
        raise

    atomic_json(
        migration_root / "receipt.json",
        {
            "configured_utc": now_utc(),
            "gate_profile_id": profile["profile_id"],
            "legal_entity": profile["legal_entity"],
            "preserved_work_gates": True,
            "schema": "ai-human.gate-profile-configuration/v1",
            "validator": "PASS",
        },
    )
    print("AI-HUMAN GATE PROFILE CONFIGURATION: PASS")
    print("- profile: " + profile["profile_id"])
    print("- exact legal entity: " + profile["legal_entity"])
    print("- mode preserved: " + worker_mode(worker))
    print("- recovery archive: " + str(migration_root))


def acquire_worker_lease(worker, session_id, actor):
    ok, failures = validate_worker(worker, quiet=True)
    if not ok:
        raise ValueError("cannot acquire a lease on an invalid worker: " + "; ".join(failures))
    session_id = safe_identity(session_id, "session id")
    actor = clean(actor, "actor")
    path = lease_file(worker)
    path.parent.mkdir(parents=True, exist_ok=True)
    lease = {
        "acquired_utc": now_utc(),
        "actor": actor,
        "schema": "ai-human.session-lease/v1",
        "session_id": session_id,
        "state_hash": controlled_state_hash(worker),
        "updated_utc": now_utc(),
    }
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        current = read_lease(worker)
        raise ValueError(
            "writer lease already active for session " + str(current.get("session_id", "UNKNOWN"))
        )
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        json.dump(lease, stream, indent=2, sort_keys=True)
        stream.write("\n")
    return lease


def session_acquire(args):
    worker = safe_worker(args.worker)
    lease = acquire_worker_lease(worker, args.session_id, args.actor)
    print("AI-HUMAN SESSION LEASE: ACQUIRED")
    print("- session id: " + lease["session_id"])
    print("- expected-state hash: " + lease["state_hash"])


def session_status(args):
    worker = safe_worker(args.worker)
    lease = read_lease(worker, required=False)
    print("AI-HUMAN SESSION LEASE")
    if not lease:
        print("- status: CLEAR")
        print("- controlled-state hash: " + controlled_state_hash(worker))
        return
    current = controlled_state_hash(worker)
    print("- status: " + ("ACTIVE" if current == lease.get("state_hash") else "MISMATCH"))
    print("- session id: " + str(lease.get("session_id", "UNKNOWN")))
    print("- actor: " + str(lease.get("actor", "UNKNOWN")))
    print("- expected-state hash: " + str(lease.get("state_hash", "")))
    print("- current-state hash: " + current)


def session_release(args):
    worker = safe_worker(args.worker)
    _lease, current = require_lease(worker, args.session_id, args.expected_state_hash)
    receipt = unique_receipt(worker, "session-release")
    atomic_json(
        receipt,
        {
            "released_utc": now_utc(), "schema": "ai-human.session-release/v1",
            "session_id": args.session_id, "state_hash": current,
        },
    )
    lease_file(worker).unlink()
    print("AI-HUMAN SESSION LEASE: RELEASED")
    print("- session id: " + args.session_id)
    print("- final-state hash: " + current)
    print("- receipt: " + str(receipt))


def session_recover(args):
    worker = safe_worker(args.worker)
    metadata = install_metadata(worker)
    supervisor = str(metadata.get("supervisor_id", ""))
    if not supervisor or clean(args.actor, "actor") != supervisor:
        raise ValueError("only the designated supervisor may recover an abandoned lease")
    lease = read_lease(worker)
    current = controlled_state_hash(worker)
    if current != args.expected_state_hash or current != lease.get("state_hash"):
        raise ValueError("expected-state hash mismatch; do not recover over changed state")
    receipt = unique_receipt(worker, "session-recovery")
    atomic_json(
        receipt,
        {
            "abandoned_session_id": lease.get("session_id"), "reason": clean(args.reason, "reason"),
            "recovered_by": supervisor, "recovered_utc": now_utc(),
            "schema": "ai-human.session-recovery/v1", "state_hash": current,
        },
    )
    lease_file(worker).unlink()
    print("AI-HUMAN SESSION LEASE: RECOVERED")
    print("- abandoned session id: " + str(lease.get("session_id", "UNKNOWN")))
    print("- controlled-state hash: " + current)
    print("- receipt: " + str(receipt))


def configure_control_plane(args):
    worker = safe_worker(args.worker)
    if live_task(worker):
        raise ValueError("control-plane configuration requires an idle worker")
    if read_lease(worker, required=False):
        raise ValueError("control-plane configuration requires no active writer lease")
    worker_id = safe_identity(args.worker_id, "worker id")
    timezone = validate_timezone(args.timezone)
    supervisor = clean(args.supervisor, "supervisor")
    approval_reference = clean(args.approval_reference, "approval reference")
    path = worker / ".ai-human/install.json"
    before = read_json(path)
    updated = dict(before)
    updated.update(
        {
            "automatic_updates": args.automatic_updates,
            "supervisor_id": supervisor,
            "timezone": timezone,
            "worker_id": worker_id,
        }
    )
    atomic_json(path, updated)
    ok, failures = validate_worker(worker, quiet=True)
    if not ok:
        atomic_json(path, before)
        raise ValueError("control-plane configuration validation failed: " + "; ".join(failures))
    receipt = unique_receipt(worker, "control-configuration")
    atomic_json(
        receipt,
        {
            "approval_reference": approval_reference,
            "automatic_updates": args.automatic_updates,
            "configured_utc": now_utc(), "schema": "ai-human.control-configuration/v1",
            "supervisor_id": supervisor, "timezone": timezone,
            "validator": "PASS", "worker_id": worker_id,
        },
    )
    print("AI-HUMAN CONTROL CONFIGURATION: PASS")
    print("- worker id: " + worker_id)
    print("- time zone: " + timezone)
    print("- designated supervisor: " + supervisor)
    print("- automatic updates: " + args.automatic_updates)
    print("- receipt: " + str(receipt))


def load_state_changes(path):
    data = read_json(Path(path).expanduser().resolve())
    if data.get("schema") != "ai-human.state-change/v1":
        raise ValueError("unsupported state-change schema")
    files = data.get("files")
    if not isinstance(files, dict) or not files:
        raise ValueError("state change must contain a non-empty files object")
    if len(files) > BATCH_CAP:
        raise ValueError("state change exceeds the batch cap of " + str(BATCH_CAP) + " files")
    allowed = set(COORDINATION_STATE_FILES)
    for name, content in files.items():
        if name not in allowed:
            raise ValueError("state change targets a non-coordination file: " + str(name))
        if not isinstance(content, str) or not content.strip():
            raise ValueError("state change content must be non-empty text: " + str(name))
    return files


def commit_state_changes(
    worker, lease, session_id, before_hash, changes, receipt_prefix="state-commit",
    receipt_extra=None,
):
    transaction = worker / ".ai-human/control/transactions" / ("state-" + now_utc())
    counter = 2
    while transaction.exists():
        transaction = transaction.with_name(transaction.name + "-" + str(counter))
        counter += 1
    backup_root = transaction / "before"
    staged_root = transaction / "staged"
    for name, content in changes.items():
        current = worker / name
        backup = backup_root / name
        backup.parent.mkdir(parents=True, exist_ok=True)
        if current.is_file():
            shutil.copy2(current, backup)
        staged = staged_root / name
        staged.parent.mkdir(parents=True, exist_ok=True)
        staged.write_text(content, encoding="utf-8")
    atomic_json(
        transaction / "transaction.json",
        {
            "before_state_hash": before_hash, "files": sorted(changes),
            "schema": "ai-human.state-transaction/v1", "session_id": session_id,
            "status": "PREPARED",
        },
    )
    try:
        for name in sorted(changes):
            os.replace(staged_root / name, worker / name)
        refreshed = refresh_lease_state(worker, lease)
        ok, failures = validate_worker(worker, quiet=True)
        if not ok:
            raise ValueError("state transaction validation failed: " + "; ".join(failures))
    except Exception:
        for name in sorted(changes):
            backup = backup_root / name
            if backup.is_file():
                shutil.copy2(backup, worker / name)
        atomic_json(lease_file(worker), lease)
        raise
    after_hash = refreshed["state_hash"]
    atomic_json(
        transaction / "transaction.json",
        {
            "after_state_hash": after_hash, "before_state_hash": before_hash,
            "files": sorted(changes), "schema": "ai-human.state-transaction/v1",
            "session_id": session_id, "status": "COMMITTED",
        },
    )
    receipt = None
    if receipt_prefix:
        receipt = unique_receipt(worker, receipt_prefix)
        payload = {
            "after_state_hash": after_hash, "before_state_hash": before_hash,
            "files": sorted(changes), "schema": "ai-human.state-commit/v1",
            "session_id": session_id, "transaction": str(transaction),
            "validator": "PASS",
        }
        if receipt_extra:
            payload.update(receipt_extra)
        atomic_json(receipt, payload)
    return after_hash, receipt, transaction


def state_commit(args):
    worker = safe_worker(args.worker)
    lease, before_hash = require_lease(worker, args.session_id, args.expected_state_hash)
    changes = load_state_changes(args.changes)
    after_hash, receipt, _transaction = commit_state_changes(
        worker, lease, args.session_id, before_hash, changes
    )
    print("AI-HUMAN STATE COMMIT: PASS")
    print("- files: " + str(len(changes)))
    print("- previous-state hash: " + before_hash)
    print("- new expected-state hash: " + after_hash)
    print("- receipt: " + str(receipt))


def run_task_state_change(worker, action, prepare_changes):
    session_id = safe_identity(
        "task-" + action + "-" + now_utc() + "-" + str(os.getpid()), "session id"
    )
    lease = acquire_worker_lease(worker, session_id, "deterministic task " + action)
    before_hash = lease["state_hash"]
    try:
        task_id, changes, result = prepare_changes()
        lease, _current_hash = require_lease(worker, session_id, before_hash)
        after_hash, _receipt, transaction = commit_state_changes(
            worker, lease, session_id, before_hash, changes, receipt_prefix=None
        )
        require_lease(worker, session_id, after_hash)
        ok, failures = validate_worker(worker, quiet=True)
        if not ok:
            raise ValueError("final worker validation failed: " + "; ".join(failures))
        lease_file(worker).unlink()
        receipt = unique_receipt(worker, "task-" + action)
        atomic_json(
            receipt,
            {
                "action": action.upper(),
                "after_state_hash": after_hash,
                "before_state_hash": before_hash,
                "files": sorted(changes),
                "lease_released": True,
                "schema": "ai-human.task-state-change/v1",
                "session_id": session_id,
                "task_id": task_id,
                "transaction": str(transaction),
                "validator": "PASS",
            },
        )
        return task_id, receipt, result
    except Exception:
        active = read_lease(worker, required=False)
        if active and active.get("session_id") == session_id:
            lease_file(worker).unlink()
        raise


def all_task_ids(worker):
    identifiers = set()
    for name in COORDINATION_STATE_FILES:
        identifiers.update(parse_table_ids(worker / name))
    current = live_task_id(worker)
    if current:
        identifiers.add(current)
    return identifiers


def task_start(args):
    worker = safe_worker(args.worker)
    def prepare_changes():
        if live_task(worker):
            raise ValueError(
                "another task is live; capture the new idea without interrupting it or close the live task first"
            )
        task_id = safe_identity(args.task_id or next_local_task_id(worker), "task id")
        if task_id in all_task_ids(worker):
            raise ValueError("task id already exists: " + task_id)
        title = clean(args.title, "task title")
        source = clean(args.source or "Current user request", "task source")
        owner = clean(parameter_value(worker, "Human owner"), "human owner")
        next_action = clean(
            args.next_action
            or "Perform the requested local work, read it back, then close it with the lifecycle tool",
            "next action",
        )
        exit_evidence = clean(
            args.exit_evidence
            or "Requested local artifact exists, its contents are read back, and final worker validation passes",
            "exit evidence",
        )
        cursor = (worker / "MASTER_CURSOR.md").read_text(encoding="utf-8")
        cursor = replace_markdown_section(
            cursor,
            "LIVE TASK",
            "Task ID: `" + task_id + "`\nPath: `LOCAL REVERSIBLE`\nMission: " + title,
        )
        cursor = replace_markdown_section(cursor, "NEXT ACTION", next_action)
        cursor = replace_markdown_section(cursor, "EXIT EVIDENCE", exit_evidence)
        cursor = replace_markdown_section(
            cursor,
            "LAST CHECKPOINT",
            "Task promoted from the mission owner's current request. No consequential or external authority was added.",
        )
        register = update_task_table(
            (worker / "OPEN_REGISTER.md").read_text(encoding="utf-8"),
            task_id,
            [task_id, "Current", title, source, owner, "LIVE — LOCAL REVERSIBLE", exit_evidence],
        )
        today_source = (worker / "TODAY.md").read_text(encoding="utf-8")
        today_source = re.sub(r"\nNo live work\.\s*\n", "\n", today_source, count=1)
        today = update_task_table(
            today_source,
            task_id,
            [
                task_id,
                title,
                "Declared task; separately executed units remain capped at 25",
                next_action,
                "LIVE",
            ],
        )
        return (
            task_id,
            {"MASTER_CURSOR.md": cursor, "OPEN_REGISTER.md": register, "TODAY.md": today},
            {"next_action": next_action},
        )

    task_id, _receipt, result = run_task_state_change(worker, "start", prepare_changes)
    print("AI-HUMAN TASK START: PASS")
    print("- task id: " + task_id)
    print("- path: LOCAL REVERSIBLE")
    print("- next action: " + result["next_action"])


def validate_local_artifacts(worker, values):
    if not values or len(values) > BATCH_CAP:
        raise ValueError("task completion requires between 1 and 25 local artifact paths")
    verified = []
    seen = set()
    for value in values:
        relative = safe_relative(value, "local artifact")
        key = portable_key(relative)
        if key in seen:
            raise ValueError("duplicate local artifact: " + key)
        seen.add(key)
        if relative.parts[0] == ".ai-human" or (len(relative.parts) == 1 and key in STATE_FILES):
            raise ValueError("controlled state is not a local task artifact: " + key)
        path = path_without_symlinks(worker, relative, "local artifact")
        if path.is_file():
            if path.stat().st_size == 0:
                raise ValueError("local artifact is empty: " + key)
        elif path.is_dir():
            files = []
            for child in sorted(path.rglob("*")):
                if child.is_symlink():
                    raise ValueError("local artifact directory contains a symbolic link: " + key)
                if child.is_file() and child.stat().st_size > 0:
                    files.append(child)
            if not files:
                raise ValueError("local artifact directory has no non-empty files: " + key)
        else:
            raise ValueError("local artifact does not exist: " + key)
        verified.append(key)
    return verified


def task_complete(args):
    worker = safe_worker(args.worker)
    def prepare_changes():
        task_id = safe_identity(args.task_id, "task id")
        current = live_task_id(worker)
        if not current:
            raise ValueError("no live task is available to complete")
        if current != task_id:
            raise ValueError("live task differs: expected " + current)
        register_rows = {
            row[0]: row
            for row in parse_table_rows(worker / "OPEN_REGISTER.md")
            if len(row) >= 7
        }
        if task_id not in register_rows:
            raise ValueError("live task is missing its open-register row: " + task_id)
        artifacts = validate_local_artifacts(worker, args.artifact)
        outcome = clean(args.outcome, "task outcome")
        verification = clean(args.verification, "verification")
        undo = clean(args.undo, "undo")
        before = clean(
            args.before or "Task was live; the requested local result had not yet been verified",
            "before state",
        )
        if placeholder(outcome) or placeholder(verification) or placeholder(undo):
            raise ValueError("outcome, verification and undo must contain concrete task-specific proof")
        normalized_undo = " ".join(undo.casefold().split())
        if (
            re.search(r"\bno other (?:files?|artifacts?|changes?)\b", normalized_undo)
            or re.search(r"\bnothing else (?:changed|was changed|touched|was touched)\b", normalized_undo)
            or re.search(
                r"\bonly (?:this |the )?(?:file|artifact) (?:changed|was changed|was touched)\b",
                normalized_undo,
            )
        ):
            raise ValueError(
                "undo must describe reversing the requested artifact without claiming that "
                "no other files changed; lifecycle state and internal receipts change by design"
            )
        timestamp = now_utc()
        title = register_rows[task_id][2]
        artifact_proof = "Local readback: " + "; ".join(artifacts) + " exists and is non-empty"
        cursor = (worker / "MASTER_CURSOR.md").read_text(encoding="utf-8")
        cursor = replace_markdown_section(cursor, "LIVE TASK", "**NOT SET**")
        cursor = replace_markdown_section(
            cursor, "NEXT ACTION", "None. Await the mission owner's next request."
        )
        cursor = replace_markdown_section(
            cursor, "EXIT EVIDENCE", "See `EVIDENCE_LOG.md` row `" + task_id + "`."
        )
        cursor = replace_markdown_section(
            cursor,
            "LAST CHECKPOINT",
            "`" + task_id + "` closed atomically after artifact readback and final worker validation.",
        )
        register = update_task_table(
            (worker / "OPEN_REGISTER.md").read_text(encoding="utf-8"), task_id
        )
        today = update_task_table((worker / "TODAY.md").read_text(encoding="utf-8"), task_id)
        remaining_today_ids = [
            row[0]
            for line in today.splitlines()
            if line.strip().startswith("|")
            for row in [[
                cell.replace("\\|", "|").strip()
                for cell in re.split(r"(?<!\\)\|", line.strip().strip("|"))
            ]]
            if row and row[0] not in {"ID", "Task ID", "---"}
            and not all(re.fullmatch(r":?-{3,}:?", cell) for cell in row)
        ]
        if not remaining_today_ids and "No live work." not in today:
            today = today.replace("# TODAY\n", "# TODAY\n\nNo live work.\n", 1)
        evidence = update_task_table(
            (worker / "EVIDENCE_LOG.md").read_text(encoding="utf-8"),
            task_id,
            [task_id, timestamp, before, outcome, verification, "PASS", artifact_proof, undo],
        )
        ledger = update_task_table(
            (worker / "COMPLETED_LEDGER.md").read_text(encoding="utf-8"),
            task_id,
            [task_id, title, timestamp, before, outcome, "EVIDENCE_LOG.md " + task_id, undo],
        )
        return (
            task_id,
            {
                "COMPLETED_LEDGER.md": ledger,
                "EVIDENCE_LOG.md": evidence,
                "MASTER_CURSOR.md": cursor,
                "OPEN_REGISTER.md": register,
                "TODAY.md": today,
            },
            {"outcome": outcome},
        )

    _task_id, _receipt, result = run_task_state_change(worker, "complete", prepare_changes)
    print("AI-HUMAN TASK COMPLETE: PASS")
    print("- result: " + result["outcome"])
    print(
        "- response guidance: return the requested result only; omit internal process "
        "details and no-network housekeeping unless the user asked; "
        "never claim that nothing else changed"
    )


def capability_path(worker, identifier):
    identifier = safe_identity(identifier, "capability id")
    return worker / CAPABILITY_ROOT / "proposals" / (identifier + ".json")


def validate_capability_payload(data):
    if not isinstance(data, dict):
        raise ValueError("capability proposal must be a JSON object")
    missing = CAPABILITY_REQUIRED - set(data)
    if missing:
        raise ValueError("capability proposal is missing: " + ", ".join(sorted(missing)))
    extra = set(data) - CAPABILITY_REQUIRED
    if extra:
        raise ValueError("capability proposal contains unexpected fields: " + ", ".join(sorted(extra)))
    safe_identity(str(data["id"]), "capability id")
    version_tuple(str(data["version"]))
    for field in (
        "owner", "purpose", "source", "secret_policy", "retirement_rule",
        "repetition_rationale", "usefulness_rationale",
    ):
        if not isinstance(data[field], str) or not data[field].strip():
            raise ValueError("capability field must be non-empty text: " + field)
    if data["secret_policy"] != "NO_SECRETS_OR_CREDENTIALS":
        raise ValueError("capability secret policy must be NO_SECRETS_OR_CREDENTIALS")
    serialized = json.dumps(data, sort_keys=True)
    secret_patterns = (
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
        r"\b(?:api[_-]?key|password|secret|token)\s*[:=]\s*[^\s,}\]]+",
        r"\bgh" + r"p_[A-Za-z0-9]+",
        r"\bsk-" + r"proj-[A-Za-z0-9_-]+",
    )
    if any(re.search(pattern, serialized, flags=re.I) for pattern in secret_patterns):
        raise ValueError("capability proposal appears to contain secret material")
    for field in (
        "allowed_tools", "gates", "deterministic_steps", "judgment_steps",
        "proof_tests", "evidence",
    ):
        values = data[field]
        if not isinstance(values, list) or not values or not all(isinstance(value, str) and value.strip() for value in values):
            raise ValueError("capability field must be a non-empty text list: " + field)
    return data


def capability_propose(args):
    worker = safe_worker(args.worker)
    lease, _before = require_lease(worker, args.session_id, args.expected_state_hash)
    proposal = validate_capability_payload(read_json(Path(args.proposal).expanduser().resolve()))
    profile = installed_gate_profile(worker)
    proposal_gate_text = " ".join(proposal["gates"]).casefold()
    for gate in profile["gates"]:
        gate_id = str(gate["gate_id"])
        if gate_id.casefold() not in proposal_gate_text:
            raise ValueError("capability is missing active local gate id: " + gate_id)
    target = capability_path(worker, str(proposal["id"]))
    if target.exists():
        raise ValueError("capability proposal already exists: " + str(proposal["id"]))
    record = dict(proposal)
    record.update(
        {
            "created_utc": now_utc(), "user_choice": None,
            "schema": "ai-human.capability-proposal/v1", "scope": None,
            "status": "PROPOSED_TO_USER", "supervisor_activation": "NOT_ACTIVATED",
        }
    )
    atomic_json(target, record)
    refreshed = refresh_lease_state(worker, lease)
    print("AI-HUMAN CAPABILITY PROPOSAL: READY")
    print("- id: " + str(proposal["id"]))
    print("- user choices: PROPOSE | LATER | REJECT")
    print("- activation: NOT ACTIVATED")
    print("- new expected-state hash: " + refreshed["state_hash"])


def capability_choice(args):
    worker = safe_worker(args.worker)
    lease, _before = require_lease(worker, args.session_id, args.expected_state_hash)
    target = capability_path(worker, args.capability)
    if not target.is_file():
        raise ValueError("capability proposal missing: " + args.capability)
    record = read_json(target)
    if record.get("status") not in {"PROPOSED_TO_USER", "PROPOSED_TO_EMPLOYEE"}:
        raise ValueError("capability is not awaiting the user choice")
    status = {
        "PROPOSE": "AWAITING_SUPERVISOR",
        "LATER": "DEFERRED_BY_USER",
        "REJECT": "REJECTED_BY_USER",
    }[args.choice]
    record.update({"choice_utc": now_utc(), "user_choice": args.choice, "status": status})
    atomic_json(target, record)
    refreshed = refresh_lease_state(worker, lease)
    print("AI-HUMAN CAPABILITY CHOICE: RECORDED")
    print("- id: " + args.capability)
    print("- choice: " + args.choice)
    print("- status: " + status)
    print("- new expected-state hash: " + refreshed["state_hash"])


def capability_activate(args):
    worker = safe_worker(args.worker)
    lease, _before = require_lease(worker, args.session_id, args.expected_state_hash)
    metadata = install_metadata(worker)
    supervisor = str(metadata.get("supervisor_id", ""))
    if not supervisor:
        raise ValueError("no designated supervisor is configured")
    if clean(args.actor, "actor") != supervisor:
        raise ValueError("only the designated supervisor may activate or share a capability")
    target = capability_path(worker, args.capability)
    if not target.is_file():
        raise ValueError("capability proposal missing: " + args.capability)
    record = read_json(target)
    choice = record.get("user_choice", record.get("employee_choice"))
    if record.get("status") != "AWAITING_SUPERVISOR" or choice != "PROPOSE":
        raise ValueError("capability has not been proposed to the supervisor by the user")
    proof = read_json(Path(args.proof).expanduser().resolve())
    if proof.get("schema") != "ai-human.capability-proof/v1" or proof.get("capability_id") != args.capability:
        raise ValueError("capability proof does not match the proposal")
    results = proof.get("results")
    required = set(record.get("proof_tests") or [])
    if not isinstance(results, dict) or set(results) != required or any(value != "PASS" for value in results.values()):
        raise ValueError("every declared capability proof test must pass")
    status = "ACTIVE_FOR_WORKER" if args.scope == "worker" else "APPROVED_FOR_COMPANY_REUSE"
    record.update(
        {
            "activated_utc": now_utc(), "activation_proof": proof,
            "scope": args.scope, "status": status,
            "supervisor_activation": "APPROVED", "supervisor_id": supervisor,
        }
    )
    atomic_json(target, record)
    refreshed = refresh_lease_state(worker, lease)
    print("AI-HUMAN CAPABILITY ACTIVATION: PASS")
    print("- id: " + args.capability)
    print("- scope: " + args.scope)
    print("- status: " + status)
    if args.scope == "company":
        print("- distribution: NOT PUBLISHED; include in a separately approved release")
    print("- new expected-state hash: " + refreshed["state_hash"])


def render_improvement_automation(worker, config, schedule, last_run=None):
    path = worker / "AUTOMATIONS.md"
    content = path.read_text(encoding="utf-8")
    existing_rows = {
        row[0]: row for row in parse_table_rows(path) if len(row) >= 7
    }
    previous = existing_rows.get("USER-QUARTERLY-IMPROVEMENT-001")
    previous_last_run = previous[6] if previous else "NOT RUN"
    if config["status"] == "DECLINED":
        trigger = "No unattended trigger"
        source = "None; user declined"
        allowed = "No run authorized"
        status = "NOT ENABLED BY CHOICE"
    else:
        trigger = "Quarterly at " + config["local_time"] + " in " + config["timezone"]
        source = "Approved categories: " + ", ".join(config["approved_sources"])
        allowed = "Read-only evidence scan and recommendations awaiting human review"
        schedule_status = schedule["status"] if schedule else None
        if config["status"] == "REMOVED":
            status = "REMOVED"
        elif config["status"] == "PAUSED" and schedule_status == "VERIFIED_ACTIVE":
            status = "VERIFIED_ACTIVE — LOCAL RESUME PENDING"
        elif config["status"] == "ENABLED" and schedule_status == "VERIFIED_PAUSED":
            status = "VERIFIED_PAUSED — LOCAL PAUSE PENDING"
        elif config["status"] in {"ENABLED", "PAUSED"} and schedule_status == "VERIFIED_REMOVED":
            status = "VERIFIED_REMOVED — LOCAL REMOVE PENDING"
        elif config["status"] == "PAUSED":
            status = "PAUSED"
        elif not schedule:
            status = "CONFIGURED — NOT SCHEDULED"
        else:
            status = schedule["status"]
    stop = (
        "Declined, paused, removed, unavailable or stale schedule; missing visible card "
        "or next run; permission denial; Gate 0; hostile source; failed validator"
    )
    return update_task_table(
        content,
        "USER-QUARTERLY-IMPROVEMENT-001",
        [
            "USER-QUARTERLY-IMPROVEMENT-001", trigger, source, allowed, stop, status,
            last_run or previous_last_run,
        ],
    )


def commit_improvement_files(
    worker, lease, session_id, before_hash, writes=None, deletes=None,
    local_writes=None, action="change",
):
    writes = writes or {}
    deletes = deletes or []
    local_writes = local_writes or {}
    if set(local_writes) - {"AUTOMATIONS.md"}:
        raise ValueError("quarterly improvement may update only its visible automation row")
    if len(writes) + len(deletes) + len(local_writes) > BATCH_CAP:
        raise ValueError("quarterly improvement change exceeds the batch cap")
    normalized_writes = {}
    normalized_deletes = []
    for relative, value in writes.items():
        target = improvement_target(worker, relative, "improvement write target")
        normalized_writes[target.relative_to(worker)] = value
    for relative in deletes:
        target = improvement_target(worker, relative, "improvement delete target")
        normalized_deletes.append(target.relative_to(worker))
    normalized_local_writes = {}
    for name, content in local_writes.items():
        if not isinstance(content, str) or not content.strip():
            raise ValueError("quarterly improvement local state write must be non-empty text")
        normalized_local_writes[Path(name)] = content
    overlap = set(normalized_writes).intersection(normalized_deletes)
    if overlap:
        raise ValueError("quarterly improvement change writes and deletes the same path")
    transaction = worker / ".ai-human/control/transactions" / (
        "improvement-" + action + "-" + now_utc()
    )
    counter = 2
    while transaction.exists():
        transaction = transaction.with_name(transaction.name + "-" + str(counter))
        counter += 1
    backup_root = transaction / "before"
    staged_root = transaction / "staged"
    existed = {}
    changed_paths = set(normalized_writes) | set(normalized_deletes) | set(normalized_local_writes)
    for relative in sorted(changed_paths, key=str):
        target = worker / relative
        existed[relative] = target.is_file()
        if target.is_symlink():
            raise ValueError("quarterly improvement target may not be a symbolic link")
        if target.is_file():
            backup = backup_root / relative
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, backup)
    for relative, value in normalized_writes.items():
        staged = staged_root / relative
        staged.parent.mkdir(parents=True, exist_ok=True)
        staged.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for relative, content in normalized_local_writes.items():
        staged = staged_root / relative
        staged.parent.mkdir(parents=True, exist_ok=True)
        staged.write_text(content, encoding="utf-8")
    atomic_json(
        transaction / "transaction.json",
        {
            "action": action, "before_state_hash": before_hash,
            "deletes": sorted(path.as_posix() for path in normalized_deletes),
            "schema": "ai-human.improvement-transaction/v1", "session_id": session_id,
            "status": "PREPARED",
            "writes": sorted(
                path.as_posix() for path in set(normalized_writes) | set(normalized_local_writes)
            ),
        },
    )
    try:
        for relative in sorted(normalized_writes, key=str):
            target = worker / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            os.replace(staged_root / relative, target)
        for relative in sorted(normalized_local_writes, key=str):
            os.replace(staged_root / relative, worker / relative)
        for relative in sorted(normalized_deletes, key=str):
            target = worker / relative
            if target.is_file():
                target.unlink()
        refreshed = refresh_lease_state(worker, lease)
        ok, failures = validate_worker(worker, quiet=True)
        if not ok:
            raise ValueError("quarterly improvement validation failed: " + "; ".join(failures))
    except Exception:
        for relative in sorted(changed_paths, key=str):
            target = worker / relative
            backup = backup_root / relative
            if existed[relative]:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup, target)
            elif target.is_file() or target.is_symlink():
                target.unlink()
        atomic_json(lease_file(worker), lease)
        raise
    after_hash = refreshed["state_hash"]
    atomic_json(
        transaction / "transaction.json",
        {
            "action": action, "after_state_hash": after_hash,
            "before_state_hash": before_hash,
            "deletes": sorted(path.as_posix() for path in normalized_deletes),
            "schema": "ai-human.improvement-transaction/v1", "session_id": session_id,
            "status": "COMMITTED",
            "writes": sorted(
                path.as_posix() for path in set(normalized_writes) | set(normalized_local_writes)
            ),
        },
    )
    receipt = unique_receipt(worker, "improvement-" + action)
    atomic_json(
        receipt,
        {
            "action": action.upper(), "after_state_hash": after_hash,
            "before_state_hash": before_hash,
            "deleted_files": len(normalized_deletes), "schema": "ai-human.improvement-change/v1",
            "session_id": session_id, "transaction": str(transaction),
            "validator": "PASS",
            "written_files": len(normalized_writes) + len(normalized_local_writes),
        },
    )
    return after_hash, receipt


def improvement_choice(args):
    worker = safe_worker(args.worker)
    lease, before_hash = require_lease(worker, args.session_id, args.expected_state_hash)
    existing = improvement_config(worker, required=False)
    schedule = improvement_schedule(worker)
    timestamp = now_utc()
    owner = clean(parameter_value(worker, "Human owner"), "human owner")
    writes = {}
    if args.choice == "DECLINE":
        if schedule and schedule["status"] not in {"UNAVAILABLE", "VERIFIED_REMOVED"}:
            raise ValueError("remove the visible external schedule before declining the loop")
        record = {
            "created_utc": existing.get("created_utc", timestamp) if existing else timestamp,
            "owner": owner, "schema": "ai-human.improvement-config/v1",
            "status": "DECLINED", "updated_utc": timestamp,
        }
    else:
        if not args.timezone or not args.local_time:
            raise ValueError("enabling requires an exact time zone and local time")
        timezone = validate_timezone(args.timezone)
        if not LOCAL_CLOCK.fullmatch(args.local_time):
            raise ValueError("quarterly improvement local time must be HH:MM")
        if args.freshness_days is None or args.freshness_days < 1:
            raise ValueError("enabling requires positive freshness-days")
        if args.retention_days is None or args.retention_days < 1:
            raise ValueError("enabling requires positive retention-days")
        sources = sorted(set(args.source or []))
        if not sources or any(source not in IMPROVEMENT_SOURCES for source in sources):
            raise ValueError("enabling requires one or more approved sources")
        research = args.research or "DISABLED"
        if (research == "APPROVED_LINKED_SOURCES") != ("APPROVED_RESEARCH" in sources):
            raise ValueError(
                "APPROVED_RESEARCH must be selected exactly when linked research is enabled"
            )
        record = {
            "approved_sources": sources,
            "created_utc": existing.get("created_utc", timestamp) if existing else timestamp,
            "frequency": "QUARTERLY", "freshness_days": args.freshness_days,
            "local_time": args.local_time, "owner": owner, "research": research,
            "retention_days": args.retention_days,
            "schema": "ai-human.improvement-config/v1", "status": "ENABLED",
            "timezone": timezone, "updated_utc": timestamp,
        }
        if schedule:
            comparable = ("timezone", "local_time")
            reenabled = existing and existing.get("status") in {"DECLINED", "REMOVED"}
            if reenabled or any(schedule.get(field) != record[field] for field in comparable):
                writes[IMPROVEMENT_SCHEDULE_PATH] = {
                    "previous_status": schedule["status"],
                    "reason": "Configuration changed; verify the visible Scheduled card again.",
                    "schema": "ai-human.improvement-schedule/v1",
                    "status": "STALE_AFTER_CONFIGURATION_CHANGE", "verified_utc": timestamp,
                }
    writes[IMPROVEMENT_CONFIG_PATH] = record
    current_schedule = writes.get(IMPROVEMENT_SCHEDULE_PATH, schedule)
    after_hash, _receipt = commit_improvement_files(
        worker, lease, args.session_id, before_hash, writes=writes,
        local_writes={
            "AUTOMATIONS.md": render_improvement_automation(worker, record, current_schedule)
        },
        action="choice",
    )
    schedule_status = current_schedule["status"] if current_schedule else "NOT_VERIFIED"
    print("AI-HUMAN QUARTERLY IMPROVEMENT CHOICE: RECORDED")
    print("- choice: " + args.choice)
    print("- schedule: " + schedule_status)
    print("- recommendations: READ ONLY; human review required")
    print("- new expected-state hash: " + after_hash)


def improvement_schedule_record(args):
    worker = safe_worker(args.worker)
    lease, before_hash = require_lease(worker, args.session_id, args.expected_state_hash)
    config = improvement_config(worker)
    previous_schedule = improvement_schedule(worker)
    if config["status"] not in {"ENABLED", "PAUSED"}:
        raise ValueError("quarterly improvement is not enabled")
    timestamp = now_utc()
    mapped = {
        "ACTIVE": "VERIFIED_ACTIVE", "PAUSED": "VERIFIED_PAUSED",
        "REMOVED": "VERIFIED_REMOVED", "UNAVAILABLE": "UNAVAILABLE",
    }
    status = mapped[args.status]
    if status == "UNAVAILABLE":
        potentially_live = {"VERIFIED_ACTIVE", "VERIFIED_PAUSED"}
        if previous_schedule and (
            previous_schedule.get("status") in potentially_live
            or (
                previous_schedule.get("status") == "STALE_AFTER_CONFIGURATION_CHANGE"
                and previous_schedule.get("previous_status") in potentially_live
            )
        ):
            raise ValueError(
                "scheduler unavailability cannot erase a known external schedule; "
                "verify it paused or removed first"
            )
        record = {
            "reason": clean(args.reason or "Scheduler unavailable", "unavailable reason"),
            "schema": "ai-human.improvement-schedule/v1", "status": status,
            "verified_utc": timestamp,
        }
    else:
        if not args.adapter or not args.external_id or not args.visible_card:
            raise ValueError(
                "verified schedule state requires adapter, external id and visible Scheduled card proof"
            )
        record = {
            "adapter": clean(args.adapter, "schedule adapter"),
            "external_id": safe_identity(args.external_id, "schedule external id"),
            "local_time": config["local_time"], "schema": "ai-human.improvement-schedule/v1",
            "status": status, "timezone": config["timezone"],
            "verified_utc": timestamp, "visible_card": True,
        }
        if status == "VERIFIED_ACTIVE":
            moment = parse_offset_datetime(args.next_run_local, "schedule next run")
            if moment.strftime("%H:%M") != config["local_time"]:
                raise ValueError("visible next run does not match the configured local time")
            if moment.astimezone(datetime.timezone.utc) <= datetime.datetime.now(datetime.timezone.utc):
                raise ValueError("visible next run must be in the future")
            record["next_run_local"] = moment.isoformat()
    after_hash, _receipt = commit_improvement_files(
        worker, lease, args.session_id, before_hash,
        writes={IMPROVEMENT_SCHEDULE_PATH: record},
        local_writes={
            "AUTOMATIONS.md": render_improvement_automation(worker, config, record)
        },
        action="schedule",
    )
    print("AI-HUMAN QUARTERLY IMPROVEMENT SCHEDULE: " + status)
    if status == "VERIFIED_ACTIVE":
        print("- next run: " + record["next_run_local"])
    if status == "UNAVAILABLE":
        print("- activation: NOT ACTIVE; no schedule was claimed")
    print("- new expected-state hash: " + after_hash)


def improvement_control(args):
    worker = safe_worker(args.worker)
    lease, before_hash = require_lease(worker, args.session_id, args.expected_state_hash)
    config = improvement_config(worker)
    schedule = improvement_schedule(worker)
    action = args.action
    if action == "PAUSE":
        if config["status"] != "ENABLED":
            raise ValueError("only an enabled quarterly loop can be paused")
        if schedule and schedule["status"] not in {
            "UNAVAILABLE", "VERIFIED_PAUSED", "VERIFIED_REMOVED",
        }:
            raise ValueError("pause and verify the visible external schedule first")
        status = "PAUSED"
    elif action == "RESUME":
        if config["status"] != "PAUSED":
            raise ValueError("only a paused quarterly loop can be resumed")
        if not schedule or schedule["status"] != "VERIFIED_ACTIVE":
            raise ValueError("resume requires a visible active schedule and verified next run")
        status = "ENABLED"
    else:
        if config["status"] not in {"ENABLED", "PAUSED"}:
            raise ValueError("quarterly improvement is not active or paused")
        if schedule and schedule["status"] not in {"UNAVAILABLE", "VERIFIED_REMOVED"}:
            raise ValueError("remove and verify the visible external schedule first")
        status = "REMOVED"
    updated = dict(config)
    updated.update({"status": status, "updated_utc": now_utc()})
    after_hash, _receipt = commit_improvement_files(
        worker, lease, args.session_id, before_hash,
        writes={IMPROVEMENT_CONFIG_PATH: updated},
        local_writes={
            "AUTOMATIONS.md": render_improvement_automation(worker, updated, schedule)
        },
        action=action.casefold(),
    )
    print("AI-HUMAN QUARTERLY IMPROVEMENT: " + status)
    print("- retained reports: inspect or forget by exact id")
    print("- new expected-state hash: " + after_hash)


def improvement_research_record(args):
    worker = safe_worker(args.worker)
    lease, before_hash = require_lease(worker, args.session_id, args.expected_state_hash)
    config = improvement_config(worker)
    if config["status"] != "ENABLED":
        raise ValueError("quarterly improvement research requires an enabled loop")
    if (
        config["research"] != "APPROVED_LINKED_SOURCES"
        or "APPROVED_RESEARCH" not in config["approved_sources"]
    ):
        raise ValueError("linked research was not approved by the owner")
    payload = validate_research_payload(read_json(Path(args.receipt).expanduser().resolve()))
    identifier = payload["receipt_id"]
    target = IMPROVEMENT_ROOT / "research" / (identifier + ".json")
    if (worker / target).exists():
        raise ValueError("research receipt already exists: " + identifier)
    timestamp = now_utc()
    record = dict(payload)
    record.update({"recorded_utc": timestamp, "status": "ACTIVE"})
    writes = {target: record}
    if args.supersedes:
        old_id = safe_identity(args.supersedes, "superseded research receipt id")
        old_path = IMPROVEMENT_ROOT / "research" / (old_id + ".json")
        if not (worker / old_path).is_file():
            raise ValueError("superseded research receipt is missing: " + old_id)
        old = read_json(worker / old_path)
        if old.get("status") != "ACTIVE":
            raise ValueError("only an active research receipt can be corrected")
        old.update({"status": "SUPERSEDED", "superseded_by": identifier})
        record["supersedes"] = old_id
        writes[old_path] = old
    after_hash, _receipt = commit_improvement_files(
        worker, lease, args.session_id, before_hash, writes=writes, action="research",
    )
    print("AI-HUMAN IMPROVEMENT RESEARCH: RECORDED")
    print("- receipt id: " + identifier)
    print("- raw page content: NOT STORED")
    print("- new expected-state hash: " + after_hash)


def normalized_subject(value):
    value = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(re.findall(r"[\w]+", value, flags=re.UNICODE))


def improvement_source_snapshot(worker, source, path, records):
    return {
        "records": records, "sha256": sha256(path), "source": source,
    }


def collect_improvement_evidence(worker, config, moment_utc, excluded_research=()):
    snapshots = []
    refs = set()
    findings = {
        "conflicting_facts": [], "existing_capabilities": [], "open_friction": [],
        "repeated_work": [], "stale_facts": [], "unknown_fact_freshness": [],
    }
    sources = set(config["approved_sources"])
    if "COMPLETED_LEDGER" in sources:
        path = worker / "COMPLETED_LEDGER.md"
        rows = [row for row in parse_table_rows(path) if len(row) >= 7]
        snapshots.append(improvement_source_snapshot(worker, "COMPLETED_LEDGER", path, len(rows)))
        groups = {}
        for row in rows:
            reference = "COMPLETED_LEDGER:" + row[0]
            refs.add(reference)
            groups.setdefault(normalized_subject(row[1]), []).append(reference)
        for key, evidence in sorted(groups.items()):
            if key and len(evidence) >= 2:
                findings["repeated_work"].append(
                    {
                        "evidence_refs": evidence,
                        "subject_key_sha256": hashlib.sha256(key.encode("utf-8")).hexdigest(),
                    }
                )
    if "EVIDENCE_LOG" in sources:
        path = worker / "EVIDENCE_LOG.md"
        rows = [row for row in parse_table_rows(path) if len(row) >= 8]
        snapshots.append(improvement_source_snapshot(worker, "EVIDENCE_LOG", path, len(rows)))
        refs.update("EVIDENCE_LOG:" + row[0] for row in rows)
    if "OPEN_REGISTER" in sources:
        path = worker / "OPEN_REGISTER.md"
        rows = [row for row in parse_table_rows(path) if len(row) >= 7]
        snapshots.append(improvement_source_snapshot(worker, "OPEN_REGISTER", path, len(rows)))
        friction = re.compile(r"blocked|deferred|fail|overdue|stalled|waiting", flags=re.I)
        for row in rows:
            reference = "OPEN_REGISTER:" + row[0]
            refs.add(reference)
            if friction.search(row[5]):
                findings["open_friction"].append({"evidence_refs": [reference]})
    if "FACTS" in sources:
        path = worker / "FACTS.md"
        rows = [row for row in parse_table_rows(path) if len(row) >= 6]
        snapshots.append(improvement_source_snapshot(worker, "FACTS", path, len(rows)))
        fact_groups = {}
        cutoff = moment_utc - datetime.timedelta(days=config["freshness_days"])
        for row in rows:
            reference = "FACTS:" + row[0]
            refs.add(reference)
            fact_groups.setdefault(normalized_subject(row[1]), []).append((reference, row[2], row[5]))
            try:
                verified = parse_recorded_utc(row[4], "fact verification date")
                if verified < cutoff:
                    findings["stale_facts"].append({"evidence_refs": [reference]})
            except ValueError:
                findings["unknown_fact_freshness"].append({"evidence_refs": [reference]})
        for key, values in sorted(fact_groups.items()):
            active = [value for value in values if "supersed" not in value[2].casefold()]
            distinct = {normalized_subject(value[1]) for value in active}
            if key and len(distinct) > 1:
                findings["conflicting_facts"].append(
                    {"evidence_refs": [value[0] for value in active]}
                )
    if "DECISIONS" in sources:
        path = worker / "DECISIONS.md"
        rows = [row for row in parse_table_rows(path) if len(row) >= 5]
        snapshots.append(improvement_source_snapshot(worker, "DECISIONS", path, len(rows)))
        refs.update("DECISIONS:row-" + str(index) for index in range(1, len(rows) + 1))
    if "CAPABILITY_PROPOSALS" in sources:
        root = worker / CAPABILITY_ROOT / "proposals"
        records = []
        if root.is_dir():
            for path in sorted(root.glob("*.json")):
                value = read_json(path)
                reference = "CAPABILITY:" + str(value.get("id", path.stem))
                refs.add(reference)
                records.append(reference)
                findings["existing_capabilities"].append(
                    {"evidence_refs": [reference], "status": value.get("status", "UNKNOWN")}
                )
        snapshots.append(
            {
                "records": len(records), "sha256": tree_sha256(root) if root.is_dir() else None,
                "source": "CAPABILITY_PROPOSALS",
            }
        )
    if "APPROVED_RESEARCH" in sources:
        root = worker / IMPROVEMENT_ROOT / "research"
        records = []
        excluded = {Path(path) for path in excluded_research}
        if root.is_dir():
            for path in sorted(root.glob("*.json")):
                if path.relative_to(worker) in excluded:
                    continue
                value = read_json(path)
                if value.get("status") == "ACTIVE":
                    reference = "RESEARCH:" + value["receipt_id"]
                    refs.add(reference)
                    records.append(reference)
        snapshots.append(
            {
                "records": len(records),
                "sha256": tree_sha256(root) if root.is_dir() else None,
                "source": "APPROVED_RESEARCH",
            }
        )
    return snapshots, refs, findings


def validate_recommendations(path, allowed_refs, active_gate_ids):
    data = read_json(Path(path).expanduser().resolve())
    if not isinstance(data, dict) or set(data) != {"recommendations", "schema"}:
        raise ValueError("recommendation input fields differ from the required schema")
    if data.get("schema") != "ai-human.improvement-recommendations/v1":
        raise ValueError("unsupported improvement recommendations schema")
    values = data["recommendations"]
    if not isinstance(values, list) or len(values) > BATCH_CAP:
        raise ValueError("recommendations must be a list of no more than 25 items")
    expected_fields = {
        "category", "evidence_refs", "gate_ids", "id", "proposed_next_step",
        "rationale", "title",
    }
    seen = set()
    output = []
    for item in values:
        if not isinstance(item, dict) or set(item) != expected_fields:
            raise ValueError("recommendation fields differ from the required schema")
        identifier = safe_identity(str(item["id"]), "recommendation id")
        if identifier in seen:
            raise ValueError("duplicate recommendation id: " + identifier)
        seen.add(identifier)
        if item["category"] not in IMPROVEMENT_CATEGORIES:
            raise ValueError("recommendation category is invalid: " + str(item["category"]))
        for field in ("title", "rationale", "proposed_next_step"):
            clean(item[field], "recommendation " + field)
        evidence = item["evidence_refs"]
        if (
            not isinstance(evidence, list) or not evidence
            or len(evidence) != len(set(evidence))
            or any(reference not in allowed_refs for reference in evidence)
        ):
            raise ValueError("recommendation contains absent or unapproved evidence references")
        gates = item["gate_ids"]
        if not isinstance(gates, list) or set(gates) != active_gate_ids:
            raise ValueError("every recommendation must preserve every active local gate id")
        record = dict(item)
        record.update(
            {
                "activation": "NOT_ACTIVATED", "decision": "REVIEW_REQUIRED",
                "decision_route": "PROPOSE_LATER_REJECT", "external_effect": "NONE",
            }
        )
        output.append(record)
    if contains_secret_material(output):
        raise ValueError("recommendations appear to contain secret material")
    return output


def expired_improvement_paths(worker, config, moment_utc):
    cutoff = moment_utc - datetime.timedelta(days=config["retention_days"])
    candidates = []
    for directory, field in (("research", "recorded_utc"), ("runs", "created_utc")):
        root = worker / IMPROVEMENT_ROOT / directory
        if not root.is_dir():
            continue
        for path in sorted(root.glob("*.json")):
            try:
                if parse_recorded_utc(read_json(path).get(field), field) < cutoff:
                    candidates.append(path.relative_to(worker))
            except ValueError:
                continue
    retained_capacity = BATCH_CAP - 2  # one run JSON plus the visible automation row
    return candidates[:retained_capacity], max(0, len(candidates) - retained_capacity)


def improvement_run(args):
    worker = safe_worker(args.worker)
    lease, before_hash = require_lease(worker, args.session_id, args.expected_state_hash)
    config = improvement_config(worker)
    if config["status"] != "ENABLED":
        raise ValueError("quarterly improvement must be enabled before a run")
    schedule = improvement_schedule(worker)
    if args.mode in {"SCHEDULED", "MISSED_RUN_RECOVERY"}:
        if not schedule or schedule["status"] != "VERIFIED_ACTIVE":
            raise ValueError("scheduled execution requires a visible active schedule and next run")
    reason = None
    if args.mode == "MISSED_RUN_RECOVERY":
        reason = clean(args.reason or "", "missed-run recovery reason")
    moment = parse_offset_datetime(args.now_local, "run local time")
    if args.mode == "SCHEDULED" and moment.strftime("%H:%M") != config["local_time"]:
        raise ValueError("scheduled run local time differs from the configured local time")
    moment_utc = moment.astimezone(datetime.timezone.utc)
    expired, retention_remaining = expired_improvement_paths(worker, config, moment_utc)
    snapshots, allowed_refs, findings = collect_improvement_evidence(
        worker, config, moment_utc, excluded_research=expired,
    )
    profile = installed_gate_profile(worker)
    gate_ids = {str(gate["gate_id"]) for gate in profile["gates"]}
    recommendations = validate_recommendations(args.recommendations, allowed_refs, gate_ids)
    timestamp = now_utc()
    identifier = "run-" + timestamp
    target = IMPROVEMENT_ROOT / "runs" / (identifier + ".json")
    counter = 2
    while (worker / target).exists():
        identifier = "run-" + timestamp + "-" + str(counter)
        target = IMPROVEMENT_ROOT / "runs" / (identifier + ".json")
        counter += 1
    record = {
        "activation": "NONE", "approved_sources": config["approved_sources"],
        "created_utc": timestamp, "findings": findings, "mode": args.mode,
        "missed_run_reason": reason, "next_run_local": (
            schedule.get("next_run_local") if schedule and schedule["status"] == "VERIFIED_ACTIVE" else None
        ),
        "privacy": {
            "credentials_stored": False, "personal_source_content_copied": False,
            "research_raw_pages_stored": False,
        },
        "recommendations": recommendations,
        "retention": {
            "days": config["retention_days"], "purged_files": len(expired),
            "remaining_expired_files": retention_remaining,
        },
        "run_id": identifier, "schema": "ai-human.improvement-run/v1",
        "source_snapshots": snapshots, "status": "COMPLETED_READ_ONLY",
    }
    after_hash, _receipt = commit_improvement_files(
        worker, lease, args.session_id, before_hash,
        writes={target: record}, deletes=expired,
        local_writes={
            "AUTOMATIONS.md": render_improvement_automation(
                worker, config, schedule, last_run=timestamp
            )
        },
        action="run",
    )
    print("AI-HUMAN QUARTERLY IMPROVEMENT RUN: PASS")
    print("- run id: " + identifier)
    print("- recommendations awaiting review: " + str(len(recommendations)))
    print("- capability activation: NONE")
    print("- external effects: NONE")
    if retention_remaining:
        print("- retention cleanup remaining after batch cap: " + str(retention_remaining))
    print("- new expected-state hash: " + after_hash)


def improvement_forget(args):
    worker = safe_worker(args.worker)
    lease, before_hash = require_lease(worker, args.session_id, args.expected_state_hash)
    improvement_config(worker)
    identifier = safe_identity(args.identifier, "forgotten item id")
    directory = "research" if args.kind == "RESEARCH" else "runs"
    target = IMPROVEMENT_ROOT / directory / (identifier + ".json")
    if not (worker / target).is_file():
        raise ValueError("quarterly improvement item is missing: " + identifier)
    after_hash, _receipt = commit_improvement_files(
        worker, lease, args.session_id, before_hash, deletes=[target], action="forget",
    )
    print("AI-HUMAN QUARTERLY IMPROVEMENT FORGET: PASS")
    print("- kind: " + args.kind)
    print("- id: " + identifier)
    print("- recoverability: DELETED FROM IMPROVEMENT STATE")
    print("- new expected-state hash: " + after_hash)


def improvement_show(args):
    worker = safe_worker(args.worker)
    config = improvement_config(worker, required=False)
    schedule = improvement_schedule(worker)
    root = worker / IMPROVEMENT_ROOT
    research = len(list((root / "research").glob("*.json"))) if (root / "research").is_dir() else 0
    runs = len(list((root / "runs").glob("*.json"))) if (root / "runs").is_dir() else 0
    print("AI-HUMAN QUARTERLY IMPROVEMENT STATUS")
    print("- choice: " + (config["status"] if config else "NOT CONFIGURED"))
    if config and config["status"] in {"ENABLED", "PAUSED", "REMOVED"}:
        print("- cadence: quarterly at " + config["local_time"] + " in " + config["timezone"])
        print("- approved sources: " + ", ".join(config["approved_sources"]))
        print("- research: " + config["research"])
        print("- fact freshness days: " + str(config["freshness_days"]))
        print("- private retention days: " + str(config["retention_days"]))
    print("- schedule: " + (schedule["status"] if schedule else "NOT VERIFIED"))
    if schedule and schedule["status"] == "VERIFIED_ACTIVE":
        print("- next run: " + schedule["next_run_local"])
    print("- retained research receipts: " + str(research))
    print("- retained read-only runs: " + str(runs))


def record_deferred(worker, version):
    register = worker / "OPEN_REGISTER.md"
    task_id = "CORE-UPDATE-" + version
    text = register.read_text(encoding="utf-8")
    if task_id not in text:
        newline = "" if text.endswith("\n") else "\n"
        row = "| " + task_id + " | High | Validated shared-system update available; wait for checkpoint | release check | owner | Deferred | local validator PASS |\n"
        atomic_text(register, text + newline + row)


def backup_for_update(worker, old_manifest, new_manifest):
    old_version = install_metadata(worker)["installed_version"]
    new_version = new_manifest["version"]
    backup_parent = worker_target(worker, ".ai-human/backups", "update backup directory")
    stem = old_version + "-before-" + new_version + "-" + now_utc()
    backup = backup_parent / stem
    counter = 2
    while backup.exists():
        backup = backup_parent / (stem + "-" + str(counter))
        counter += 1
    backup = worker_target(
        worker, backup.relative_to(worker), "update backup directory"
    )
    records = []
    targets = set(managed_targets(old_manifest)) | set(managed_targets(new_manifest))
    targets.update({".ai-human/install.json", ".ai-human/release-manifest.json"})
    for relative in sorted(targets):
        target = worker_target(worker, relative, "update backup source")
        existed = target.is_file()
        records.append({"target": relative, "existed": existed})
        if existed:
            destination = path_without_symlinks(
                backup, Path("files") / safe_relative(relative, "backup record target"),
                "update backup destination",
            )
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, destination)
    atomic_json(
        backup / "backup-manifest.json",
        {
            "created_utc": now_utc(), "from_version": old_version,
            "to_version": new_version, "files": records,
        },
    )
    return backup


def restore_backup(worker, backup):
    backup = Path(backup)
    try:
        backup_relative = backup.relative_to(worker)
    except ValueError as error:
        raise ValueError("rollback backup is outside the worker") from error
    backup = worker_target(worker, backup_relative, "rollback backup directory")
    data = read_json(path_without_symlinks(backup, "backup-manifest.json", "backup manifest"))
    for record in data["files"]:
        target = worker_target(worker, record["target"], "rollback target")
        if record["existed"]:
            source = release_file(
                backup / "files", record["target"], "rollback backup source"
            )
            target.parent.mkdir(parents=True, exist_ok=True)
            temp = target.with_name(target.name + ".rollback-temp")
            shutil.copy2(source, temp)
            os.replace(temp, target)
        elif target.is_file() or target.is_symlink():
            target.unlink()


def automatic_release_eligible(manifest, installed_version):
    if manifest.get("automatic_update_eligible") is not True:
        return False, "release is not marked eligible for automatic updates"
    compatibility = manifest.get("compatibility") or {}
    if compatibility.get("classification") != "BACKWARD_COMPATIBLE":
        return False, "release lacks backward-compatible classification"
    minimum = str(compatibility.get("minimum_supported_version", ""))
    try:
        minimum_version = version_tuple(minimum)
    except ValueError:
        return False, "release has an invalid minimum supported version"
    if version_tuple(installed_version) < minimum_version:
        return False, "installed version is below the declared compatibility floor"
    if compatibility.get("preserves_user_state") is not True:
        return False, "release does not declare user-state preservation"
    return True, "eligible"


def apply_update(worker, release, manifest, at_checkpoint=False, automatic=False):
    worker = Path(worker).resolve()
    release = Path(release).resolve()
    worker_ok, worker_failures = validate_worker(worker, quiet=True)
    if not worker_ok:
        raise ValueError(
            "pre-update worker validation failed: " + "; ".join(worker_failures)
        )
    metadata = install_metadata(worker)
    old_version = metadata["installed_version"]
    new_version = manifest["version"]
    if version_tuple(new_version) <= version_tuple(old_version):
        print("AI-HUMAN UPDATE: NO UPDATE")
        print("- local version: " + old_version)
        print("- release version: " + new_version)
        return {"status": "CURRENT", "from_version": old_version, "to_version": old_version}
    if automatic:
        eligible, reason = automatic_release_eligible(manifest, old_version)
        if not eligible:
            raise ValueError("automatic update refused: " + reason)
    if read_lease(worker, required=False):
        print("AI-HUMAN UPDATE: DEFERRED")
        print("- version: " + new_version)
        print("- reason: an active writer lease exists; the version report records the deferral")
        return {"status": "DEFERRED", "from_version": old_version, "to_version": new_version, "reason": "ACTIVE_WRITER"}
    if live_task(worker) and (automatic or not at_checkpoint):
        record_deferred(worker, new_version)
        print("AI-HUMAN UPDATE: DEFERRED")
        print("- version: " + new_version)
        print("- reason: live task exists; update recorded for a checkpoint")
        return {"status": "DEFERRED", "from_version": old_version, "to_version": new_version, "reason": "LIVE_TASK"}
    before_state = state_hashes(worker)
    old_manifest = read_json(worker / ".ai-human/release-manifest.json")
    backup = backup_for_update(worker, old_manifest, manifest)
    try:
        copy_release_files(worker, release, manifest)
        obsolete = set(managed_targets(old_manifest)) - set(managed_targets(manifest))
        for relative in obsolete:
            target = worker_target(worker, relative, "obsolete managed target")
            if target.is_file() or target.is_symlink():
                target.unlink()
        write_install_metadata(worker, manifest)
        if before_state != state_hashes(worker):
            raise ValueError("update changed company, role or user state")
        ok, failures = validate_worker(worker, quiet=True)
        if not ok:
            raise ValueError("updated worker validation failed: " + "; ".join(failures))
    except Exception as exc:
        restore_backup(worker, backup)
        rollback_ok, rollback_failures = validate_worker(worker, quiet=True)
        atomic_json(
            worker / ".ai-human/update-receipt.json",
            {
                "automatic": automatic, "backup": str(backup),
                "failure": str(exc), "from_version": old_version,
                "rollback": "PASS" if rollback_ok else "FAIL",
                "rollback_failures": rollback_failures,
                "schema": "ai-human.update-receipt/v2", "state_preserved": before_state == state_hashes(worker),
                "status": "FAILED", "to_version": new_version, "validator": "FAIL",
            },
        )
        raise
    atomic_json(
        worker / ".ai-human/update-receipt.json",
        {
            "automatic": automatic, "backup": str(backup), "from_version": old_version,
            "schema": "ai-human.update-receipt/v2", "state_preserved": True,
            "status": "UPDATED", "to_version": new_version, "validator": "PASS",
        },
    )
    print("AI-HUMAN UPDATE: PASS")
    print("- previous version: " + old_version)
    print("- new version: " + new_version)
    print("- company, role and user state hashes: preserved")
    print("- rollback backup: " + str(backup))
    return {"status": "UPDATED", "from_version": old_version, "to_version": new_version}


def safe_extract(archive, destination):
    destination = Path(destination).resolve()
    if not destination.is_dir():
        raise ValueError("archive destination must be an existing directory")
    with zipfile.ZipFile(archive) as bundle:
        members = bundle.infolist()
        if len(members) > MAX_ARCHIVE_MEMBERS:
            raise ValueError("archive contains too many members")
        total_size = sum(item.file_size for item in members)
        if total_size > MAX_ARCHIVE_UNCOMPRESSED_BYTES:
            raise ValueError("archive expands beyond the allowed size")
        seen = set()
        validated = []
        for item in members:
            if item.flag_bits & 0x1:
                raise ValueError("encrypted archive members are not supported")
            relative = safe_relative(item.filename, "archive member")
            member_key = unicodedata.normalize("NFC", portable_key(relative)).casefold()
            if member_key in seen:
                raise ValueError("duplicate archive member: " + portable_key(relative))
            seen.add(member_key)
            unix_mode = item.external_attr >> 16
            file_type = stat.S_IFMT(unix_mode)
            if file_type == stat.S_IFLNK:
                raise ValueError(
                    "archive member may not be a symbolic link: " + portable_key(relative)
                )
            if file_type not in {0, stat.S_IFREG, stat.S_IFDIR}:
                raise ValueError(
                    "archive member has an unsupported file type: " + portable_key(relative)
                )
            target = (destination / relative).resolve()
            if destination not in target.parents and target != destination:
                raise ValueError("archive member escapes extraction root")
            validated.append((item, relative, target))
        for item, relative, target in validated:
            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with bundle.open(item, "r") as source, target.open("xb") as output:
                shutil.copyfileobj(source, output)


def latest_release(repository):
    request = urllib.request.Request(
        "https://api.github.com/repos/" + repository + "/releases/latest",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "ai-human-workspace"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)
    version = str(data.get("tag_name", "")).lstrip("v")
    version_tuple(version)
    return version, data["zipball_url"]


def download_release(repository):
    version, url = latest_release(repository)
    temp = tempfile.TemporaryDirectory(prefix="ai-human-release-")
    root = Path(temp.name)
    archive = root / "release.zip"
    request = urllib.request.Request(url, headers={"User-Agent": "ai-human-workspace"})
    with urllib.request.urlopen(request, timeout=60) as response, archive.open("wb") as stream:
        shutil.copyfileobj(response, stream)
    extracted = root / "extracted"
    extracted.mkdir()
    safe_extract(archive, extracted)
    manifests = list(extracted.glob("*/release-manifest.json"))
    if len(manifests) != 1:
        temp.cleanup()
        raise ValueError("downloaded release has no unique manifest")
    release, manifest = load_release(manifests[0].parent)
    if manifest["repository"] != repository or manifest["version"] != version:
        temp.cleanup()
        raise ValueError("release repository or tag does not match its manifest")
    return temp, release, manifest


def update(args):
    worker = safe_worker(args.worker)
    if args.latest:
        repository = install_metadata(worker)["repository"]
        temp, release, manifest = download_release(repository)
        try:
            apply_update(worker, release, manifest, args.at_checkpoint)
        finally:
            temp.cleanup()
    else:
        if not args.source:
            raise ValueError("provide --source or --latest")
        release, manifest = load_release(args.source)
        apply_update(worker, release, manifest, args.at_checkpoint)


def rollback(args):
    worker = safe_worker(args.worker)
    current = install_metadata(worker)["installed_version"]
    version_tuple(args.version)
    candidates = []
    backup_parent = worker / ".ai-human/backups"
    for manifest_path in backup_parent.glob("*/backup-manifest.json"):
        try:
            data = read_json(manifest_path)
        except Exception:
            continue
        if data.get("from_version") == args.version and data.get("to_version") == current:
            candidates.append(manifest_path.parent)
    if not candidates:
        raise ValueError("rollback backup missing for " + args.version + " before " + current)
    backup = max(candidates, key=lambda path: (path.stat().st_mtime_ns, path.name))
    before = state_hashes(worker)
    restore_backup(worker, backup)
    if before != state_hashes(worker):
        raise ValueError("rollback changed company, role or user state")
    ok, failures = validate_worker(worker, quiet=True)
    if not ok:
        raise ValueError("rollback validation failed: " + "; ".join(failures))
    atomic_json(
        worker / ".ai-human/rollback-receipt.json",
        {"from_version": current, "state_preserved": True, "to_version": args.version, "validator": "PASS"},
    )
    print("AI-HUMAN ROLLBACK: PASS")
    print("- restored version: " + args.version)
    print("- company, role and user state hashes: preserved")


def check(args):
    worker = safe_worker(args.worker)
    metadata = install_metadata(worker)
    local = metadata["installed_version"]
    latest, _ = latest_release(metadata["repository"])
    print("AI-HUMAN UPDATE CHECK: PASS")
    print("- local version: " + local)
    print("- latest release: " + latest)
    print("- update available: " + ("yes" if version_tuple(latest) > version_tuple(local) else "no"))


def parse_local(value):
    if not value:
        raise ValueError(
            "the approved scheduler must supply an offset-aware worker-local date-time"
        )
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        moment = datetime.datetime.fromisoformat(normalized)
    except ValueError:
        raise ValueError("invalid ISO date-time: " + repr(value))
    if moment.tzinfo is None:
        raise ValueError("local date-time must include a UTC offset")
    return moment


def scheduled_monthly_check(metadata, moment_local, previous_report):
    timezone = str(metadata.get("timezone", ""))
    if not timezone:
        return False, "TIMEZONE_MISSING", None
    validate_timezone(timezone)
    local = moment_local
    month_key = local.strftime("%Y-%m")
    if previous_report and previous_report.get("checked_month") == month_key:
        if previous_report.get("status") == "DEFERRED" and previous_report.get("reason") in {"ACTIVE_WRITER", "LIVE_TASK"}:
            return True, "DEFERRED_RETRY", local
        return False, "ALREADY_CHECKED_THIS_MONTH", local
    if local.day != 1 or local.hour != 10:
        return False, "NOT_FIRST_DAY_AT_10_LOCAL", local
    return True, "DUE", local


def write_version_report(worker, report):
    atomic_json(worker / ".ai-human/version-report.json", report)


def safe_worker_report(metadata, installed, latest, status, validator, moment, due, reason):
    return {
        "checked_month": moment.strftime("%Y-%m") if moment and due else None,
        "installed_version": installed,
        "last_check_utc": moment.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if moment and due else None,
        "latest_version": latest,
        "reason": reason,
        "scheduled_check": "DUE" if due else "NOT_DUE",
        "schema": "ai-human.version-report/v1",
        "status": status,
        "validator": validator,
        "worker_id": metadata.get("worker_id"),
    }


def run_automatic_update(worker, release, manifest, moment_local):
    try:
        metadata = install_metadata(worker)
    except Exception:
        return {
            "checked_month": None, "installed_version": None, "last_check_utc": None,
            "latest_version": manifest.get("version"), "reason": "INSTALL_METADATA_MISSING",
            "scheduled_check": "NOT_DUE", "schema": "ai-human.version-report/v1",
            "status": "MISSING", "validator": "FAIL", "worker_id": None,
        }
    installed = str(metadata.get("installed_version", ""))
    worker_id = metadata.get("worker_id")
    if not worker_id or not SAFE_ID.fullmatch(str(worker_id)):
        report = safe_worker_report(metadata, installed, manifest["version"], "MISSING", "FAIL", None, False, "WORKER_ID_MISSING")
        write_version_report(worker, report)
        return report
    if worker_mode(worker) == MODE_SUSPENDED:
        report = safe_worker_report(
            metadata, installed, manifest["version"], "DEFERRED", "PASS",
            moment_local, False, "SYSTEM_SUSPENDED",
        )
        write_version_report(worker, report)
        return report
    previous_path = worker / ".ai-human/version-report.json"
    try:
        previous = read_json(previous_path) if previous_path.is_file() else None
    except Exception:
        report = safe_worker_report(metadata, installed, manifest["version"], "MISMATCH", "FAIL", None, False, "VERSION_REPORT_INVALID")
        write_version_report(worker, report)
        return report
    try:
        due, reason, local = scheduled_monthly_check(metadata, moment_local, previous)
    except Exception:
        report = safe_worker_report(metadata, installed, manifest["version"], "MISSING", "FAIL", None, False, "TIMEZONE_INVALID")
        write_version_report(worker, report)
        return report
    if not due:
        if reason == "TIMEZONE_MISSING":
            status, validator = "MISSING", "FAIL"
        elif reason == "ALREADY_CHECKED_THIS_MONTH" and previous:
            previous_status = previous.get("status", "MISMATCH")
            status = "CURRENT" if previous_status in {"CURRENT", "UPDATED"} else previous_status
            validator = previous.get("validator", "FAIL")
        else:
            status = "UPDATE AVAILABLE" if version_tuple(manifest["version"]) > version_tuple(installed) else "CURRENT"
            validator = "NOT_RUN"
        report = safe_worker_report(metadata, installed, manifest["version"], status, validator, local, False, reason)
        if previous and reason == "ALREADY_CHECKED_THIS_MONTH":
            report["checked_month"] = previous.get("checked_month")
            report["last_check_utc"] = previous.get("last_check_utc")
        write_version_report(worker, report)
        return report
    ok, _failures = validate_worker(worker, quiet=True)
    if not ok:
        report = safe_worker_report(metadata, installed, manifest["version"], "MISMATCH", "FAIL", local, True, "WORKER_VALIDATION_FAILED")
        write_version_report(worker, report)
        return report
    if metadata.get("automatic_updates") != "ACTIVE":
        report = safe_worker_report(metadata, installed, manifest["version"], "DEFERRED", "PASS", local, True, "AUTOMATIC_UPDATES_NOT_ACTIVE")
        write_version_report(worker, report)
        return report
    eligible, eligibility_reason = automatic_release_eligible(manifest, installed)
    if version_tuple(manifest["version"]) > version_tuple(installed) and not eligible:
        compatibility = manifest.get("compatibility") or {}
        reason = (
            "SETUP_MIGRATION_REQUIRED"
            if compatibility.get("classification") == "SETUP_MIGRATION_REQUIRED"
            else "AUTOMATIC_UPDATE_INELIGIBLE: " + eligibility_reason
        )
        report = safe_worker_report(
            metadata, installed, manifest["version"], "DEFERRED", "PASS", local, True, reason,
        )
        write_version_report(worker, report)
        return report
    try:
        result = apply_update(worker, release, manifest, automatic=True)
    except Exception:
        report = safe_worker_report(metadata, installed, manifest["version"], "FAILED", "FAIL", local, True, "UPDATE_FAILED_AND_ROLLBACK_ATTEMPTED")
        write_version_report(worker, report)
        return report
    status = result["status"]
    current_metadata = install_metadata(worker)
    validator = "PASS" if validate_worker(worker, quiet=True)[0] else "FAIL"
    report = safe_worker_report(
        current_metadata, current_metadata["installed_version"], manifest["version"],
        status, validator, local, True, result.get("reason", "CHECK_COMPLETE"),
    )
    write_version_report(worker, report)
    return report


def automatic_update(args):
    worker = safe_worker(args.worker)
    moment = parse_local(args.now_local)
    temp = None
    if args.latest:
        repository = install_metadata(worker)["repository"]
        temp, release, manifest = download_release(repository)
    else:
        if not args.source:
            raise ValueError("provide --source or --latest")
        release, manifest = load_release(args.source)
    try:
        report = run_automatic_update(worker, release, manifest, moment)
    finally:
        if temp:
            temp.cleanup()
    print("AI-HUMAN AUTOMATIC UPDATE: " + report["status"])
    print("- worker id: " + str(report.get("worker_id") or "MISSING"))
    print("- installed version: " + str(report.get("installed_version") or "MISSING"))
    print("- latest version: " + str(report.get("latest_version") or "MISSING"))
    print("- validator: " + report["validator"])
    print("- reason: " + report["reason"])


def load_fleet(path):
    data = read_json(Path(path).expanduser().resolve())
    if data.get("schema") != "ai-human.fleet-batch/v1":
        raise ValueError("unsupported fleet-batch schema")
    batch_id = safe_identity(str(data.get("batch_id", "")), "batch id")
    timezone = validate_timezone(str(data.get("timezone", "")))
    workers = data.get("workers")
    if not isinstance(workers, list) or not workers:
        raise ValueError("fleet batch must contain workers")
    if len(workers) > BATCH_CAP:
        raise ValueError("fleet batch exceeds the cap of " + str(BATCH_CAP) + " workers")
    identities = set()
    normalized = []
    for record in workers:
        if not isinstance(record, dict):
            raise ValueError("fleet worker record must be an object")
        identity = safe_identity(str(record.get("worker_id", "")), "worker id")
        if identity in identities:
            raise ValueError("duplicate fleet worker id: " + identity)
        identities.add(identity)
        phase = record.get("phase")
        lane = record.get("lane")
        if phase not in {"pilot", "general"}:
            raise ValueError("fleet phase must be pilot or general")
        if phase == "pilot" and lane != "daily-email-triage":
            raise ValueError("the automatic pilot lane must be daily-email-triage")
        normalized.append(
            {"lane": str(lane), "path": str(record.get("path", "")), "phase": phase, "worker_id": identity}
        )
    return batch_id, timezone, normalized


def fleet_update(args):
    batch_id, timezone, records = load_fleet(args.fleet)
    moment = parse_local(args.now_local)
    if not args.source:
        raise ValueError("fleet demo requires a verified local --source; production uses the approved scheduler adapter")
    release, manifest = load_release(args.source)
    fleet_state_path = Path(args.fleet_state).expanduser().resolve()
    fleet_state = read_json(fleet_state_path) if fleet_state_path.is_file() else {}
    prior_pilot = (
        fleet_state.get("pilot_status") == "PASS"
        and fleet_state.get("pilot_release_version") == manifest["version"]
    )
    pilot_records = [record for record in records if record["phase"] == "pilot"]
    general_records = [record for record in records if record["phase"] == "general"]
    results = []
    for record in pilot_records:
        try:
            worker = safe_worker(record["path"])
            metadata = install_metadata(worker)
            if metadata.get("worker_id") != record["worker_id"] or metadata.get("timezone") != timezone:
                report = safe_worker_report(metadata, metadata.get("installed_version"), manifest["version"], "MISMATCH", "FAIL", None, False, "FLEET_IDENTITY_MISMATCH")
            else:
                report = run_automatic_update(worker, release, manifest, moment)
        except Exception:
            report = {
                "checked_month": None, "installed_version": None, "last_check_utc": None,
                "latest_version": manifest["version"], "reason": "WORKER_LOCAL_FAILURE",
                "scheduled_check": "NOT_DUE", "schema": "ai-human.version-report/v1",
                "status": "FAILED", "validator": "FAIL", "worker_id": record["worker_id"],
            }
        results.append({"lane": record["lane"], "phase": "pilot", "report": report, "worker_id": record["worker_id"]})
    if pilot_records:
        pilot_pass = all(
            item["report"]["scheduled_check"] == "DUE"
            and item["report"]["status"] in {"CURRENT", "UPDATED"}
            and item["report"]["validator"] == "PASS"
            for item in results
        )
    else:
        pilot_pass = prior_pilot
    if pilot_pass:
        for record in general_records:
            try:
                worker = safe_worker(record["path"])
                metadata = install_metadata(worker)
                if metadata.get("worker_id") != record["worker_id"] or metadata.get("timezone") != timezone:
                    report = safe_worker_report(metadata, metadata.get("installed_version"), manifest["version"], "MISMATCH", "FAIL", None, False, "FLEET_IDENTITY_MISMATCH")
                else:
                    report = run_automatic_update(worker, release, manifest, moment)
            except Exception:
                report = {
                    "checked_month": None, "installed_version": None, "last_check_utc": None,
                    "latest_version": manifest["version"], "reason": "WORKER_LOCAL_FAILURE",
                    "scheduled_check": "NOT_DUE", "schema": "ai-human.version-report/v1",
                    "status": "FAILED", "validator": "FAIL", "worker_id": record["worker_id"],
                }
            results.append({"lane": record["lane"], "phase": "general", "report": report, "worker_id": record["worker_id"]})
    else:
        for record in general_records:
            report = {
                "checked_month": None, "installed_version": None, "last_check_utc": None,
                "latest_version": manifest["version"], "reason": "PILOT_NOT_YET_VERIFIED",
                "scheduled_check": "NOT_DUE", "schema": "ai-human.version-report/v1",
                "status": "DEFERRED", "validator": "NOT_RUN", "worker_id": record["worker_id"],
            }
            results.append({"lane": record["lane"], "phase": "general", "report": report, "worker_id": record["worker_id"]})
    state = {
        "batch_id": batch_id, "pilot_release_version": manifest["version"],
        "pilot_status": "PASS" if pilot_pass else "NOT_VERIFIED",
        "results": results, "schema": "ai-human.fleet-state/v1",
    }
    atomic_json(fleet_state_path, state)
    print("AI-HUMAN FLEET BATCH")
    print("- batch id: " + batch_id)
    print("- worker count: " + str(len(records)))
    print("- confirmed time-zone cohort: " + timezone)
    print("- Daily Email Triage pilot: " + state["pilot_status"])
    for item in results:
        print("- " + item["worker_id"] + ": " + item["report"]["status"] + " — " + item["report"]["reason"])
    print("- state: " + str(fleet_state_path))


def checkpoint(args):
    worker = safe_worker(args.worker)
    ok, failures = validate_worker(worker, quiet=True)
    if not ok:
        raise ValueError("checkpoint validation failed: " + "; ".join(failures))
    atomic_json(
        worker / ".ai-human/checkpoint-receipt.json",
        {"created_utc": now_utc(), "live_task": live_task(worker), "state_hashes": state_hashes(worker), "validator": "PASS"},
    )
    print("AI-HUMAN CHECKPOINT: PASS")
    print("- durable state validated and hashed")


def suspend(args):
    worker = safe_worker(args.worker)
    current = worker_mode(worker)
    if current == "UNINSTALLED":
        raise ValueError("AI-human system is not installed")
    if current == MODE_SUSPENDED:
        print("AI-HUMAN SUSPEND: PASS")
        print("- mode: SUSPENDED")
        print("- result: already suspended; no additional change")
        return
    reason = clean(args.reason, "reason")
    metadata_path = worker / ".ai-human/install.json"
    before_metadata = read_json(metadata_path)
    before_mode = read_json(mode_file(worker)) if mode_file(worker).is_file() else None
    previous_updates = str(before_metadata.get("automatic_updates") or "DISABLED")
    updated_metadata = dict(before_metadata)
    updated_metadata["automatic_updates"] = "DISABLED"
    mode = {
        "changed_utc": now_utc(),
        "previous_automatic_updates": previous_updates,
        "reason": reason,
        "schema": "ai-human.mode/v1",
        "status": MODE_SUSPENDED,
    }
    atomic_json(metadata_path, updated_metadata)
    atomic_json(mode_file(worker), mode)
    ok, failures = validate_worker(worker, quiet=True)
    if not ok:
        atomic_json(metadata_path, before_metadata)
        if before_mode is None:
            mode_file(worker).unlink(missing_ok=True)
        else:
            atomic_json(mode_file(worker), before_mode)
        raise ValueError("suspend validation failed: " + "; ".join(failures))
    receipt = unique_receipt(worker, "suspend")
    atomic_json(
        receipt,
        {
            "automatic_updates": "DISABLED", "mode": MODE_SUSPENDED,
            "reason": reason, "schema": "ai-human.suspend/v1",
            "suspended_utc": now_utc(), "validator": "PASS",
        },
    )
    print("AI-HUMAN SUSPEND: PASS")
    print("- mode: SUSPENDED")
    print("- managed rules and automations: OFF")
    print("- automatic updates: DISABLED")
    print("- project and user files: preserved")
    print("- receipt: " + str(receipt))


def resume(args):
    worker = safe_worker(args.worker)
    current = worker_mode(worker)
    if current == "UNINSTALLED":
        raise ValueError("AI-human system is not installed")
    if current == MODE_ACTIVE:
        print("AI-HUMAN RESUME: PASS")
        print("- mode: ACTIVE")
        print("- result: already active; no additional change")
        return
    path = mode_file(worker)
    before_mode = read_json(path)
    metadata_path = worker / ".ai-human/install.json"
    before_metadata = read_json(metadata_path)
    previous_updates = str(before_mode.get("previous_automatic_updates") or "DISABLED")
    if previous_updates not in {"ACTIVE", "DISABLED"}:
        previous_updates = "DISABLED"
    updated_metadata = dict(before_metadata)
    updated_metadata["automatic_updates"] = previous_updates
    active_mode = {
        "changed_utc": now_utc(),
        "schema": "ai-human.mode/v1",
        "status": MODE_ACTIVE,
    }
    atomic_json(metadata_path, updated_metadata)
    atomic_json(path, active_mode)
    ok, failures = validate_worker(worker, quiet=True)
    if not ok:
        atomic_json(metadata_path, before_metadata)
        atomic_json(path, before_mode)
        raise ValueError("resume validation failed: " + "; ".join(failures))
    receipt = unique_receipt(worker, "resume")
    atomic_json(
        receipt,
        {
            "automatic_updates": previous_updates, "mode": MODE_ACTIVE,
            "resumed_utc": now_utc(), "schema": "ai-human.resume/v1",
            "validator": "PASS",
        },
    )
    print("AI-HUMAN RESUME: PASS")
    print("- mode: ACTIVE")
    print("- automatic updates: " + previous_updates)
    print("- validator: PASS")
    print("- receipt: " + str(receipt))


def verify_state(args):
    worker = safe_worker(args.worker)
    expected = args.expect
    actual = worker_mode(worker)
    failures = []
    receipt = None
    if expected == "UNINSTALLED":
        if actual != "UNINSTALLED":
            failures.append("managed .ai-human folder still exists")
        adapters = active_system_adapters(worker)
        if adapters:
            failures.append("active AI-human adapters remain: " + ", ".join(adapters))
        receipt_path = worker / "AI-HUMAN-REMOVAL-RECEIPT.json"
        try:
            receipt = read_json(receipt_path)
            if receipt.get("schema") != "ai-human.removal/v1" or receipt.get("validator") != "PASS":
                failures.append("removal receipt is not valid")
        except Exception:
            failures.append("removal receipt is missing or invalid")
    else:
        if actual != expected:
            failures.append("actual mode is " + actual)
        ok, worker_failures = validate_worker(worker, quiet=True)
        if not ok:
            failures.extend(worker_failures)
        if expected == MODE_SUSPENDED:
            try:
                metadata = install_metadata(worker)
                if metadata.get("automatic_updates") != "DISABLED":
                    failures.append("automatic updates remain active")
            except Exception as exc:
                failures.append(str(exc))
    if failures:
        raise ValueError("; ".join(failures))
    print("AI-HUMAN STATE VERIFICATION: PASS")
    print("- expected state: " + expected)
    print("- actual state: " + actual)
    if expected == MODE_ACTIVE:
        print("- managed rules: ON")
        print("- validator: PASS")
    elif expected == MODE_SUSPENDED:
        print("- managed rules and automations: OFF")
        print("- automatic updates: DISABLED")
        print("- project files: preserved")
    else:
        print("- managed .ai-human folder: ABSENT")
        print("- active AI-human adapters: ABSENT")
        print("- project and user files: preserved")
        print("- archived system: " + str(receipt.get("archived_system", "MISSING")))


def uninstall(args):
    worker = safe_worker(args.worker)
    system = worker / ".ai-human"
    if not system.is_dir():
        raise ValueError("AI-human system is not installed")
    if live_task(worker) and not args.at_checkpoint:
        raise ValueError("live task exists; reach a checkpoint before uninstalling")
    metadata = install_metadata(worker)
    before = preserved_work_hashes(worker)
    created = metadata.get("created_starter_files") or {}
    if not isinstance(created, dict):
        created = {}
    adapters = []
    marker_adapters = set(active_system_adapters(worker))
    for name in LOCAL_ADAPTER_FILES:
        if (worker / name).is_file() and (name in created or name in marker_adapters):
            adapters.append(name)
    destination = worker / (".ai-human-removed-" + now_utc())
    if destination.exists():
        raise ValueError("removal destination already exists")
    archived = []
    try:
        shutil.move(str(system), str(destination))
        adapter_archive = destination / "local-adapters"
        for name in adapters:
            adapter_archive.mkdir(parents=True, exist_ok=True)
            shutil.move(str(worker / name), str(adapter_archive / name))
            archived.append(name)
        if before != preserved_work_hashes(worker):
            raise ValueError("uninstall changed company, role or user work state")
    except Exception:
        for name in reversed(archived):
            archived_path = destination / "local-adapters" / name
            if archived_path.exists():
                shutil.move(str(archived_path), str(worker / name))
        adapter_root = destination / "local-adapters"
        if adapter_root.is_dir() and not any(adapter_root.iterdir()):
            adapter_root.rmdir()
        if destination.exists() and not system.exists():
            shutil.move(str(destination), str(system))
        raise
    receipt_path = worker / "AI-HUMAN-REMOVAL-RECEIPT.json"
    atomic_json(
        receipt_path,
        {
            "active_adapters_remaining": active_system_adapters(worker),
            "archived_adapters": archived,
            "archived_system": destination.name,
            "preserved_work_hashes": before,
            "removed_utc": now_utc(),
            "schema": "ai-human.removal/v1",
            "validator": "PASS",
        },
    )
    if active_system_adapters(worker):
        raise ValueError("uninstall could not remove every active AI-human adapter")
    atomic_text(
        worker / "AI-HUMAN-UNINSTALLED.txt",
        "The managed AI-human system and its active local adapters were removed reversibly.\n"
        "Preserved system: " + destination.name + "\n"
        "Project, company and user work files were not deleted.\n"
        "Verification: PASS — state is UNINSTALLED.\n",
    )
    print("AI-HUMAN UNINSTALL: PASS")
    print("- removed system moved to: " + str(destination))
    print("- active local adapters archived: " + str(len(archived)))
    print("- project, company and user work state: preserved")
    print("- verification: UNINSTALLED")
    print("- receipt: " + str(receipt_path))


def status(args):
    worker = safe_worker(args.worker)
    metadata = install_metadata(worker)
    ok, failures = validate_worker(worker, quiet=True)
    print("AI-HUMAN STATUS")
    print("- worker: " + str(worker))
    print("- version: " + metadata["installed_version"])
    print("- repository: " + metadata["repository"])
    print("- mode: " + worker_mode(worker))
    print("- live task: " + (live_task(worker) or "NOT SET"))
    print("- validation: " + ("PASS" if ok else "FAIL"))
    if failures:
        for failure in failures:
            print("  - " + failure)


def component_release(args):
    if getattr(args, "latest", False):
        temp, release, release_manifest = download_release(args.repository)
        try:
            component_manifest = load_components(release, release_manifest)
        except Exception:
            temp.cleanup()
            raise
        return temp, release, release_manifest, component_manifest
    source = getattr(args, "source", None)
    release, release_manifest = load_release(source or release_root_from_script())
    component_manifest = load_components(release, release_manifest)
    return None, release, release_manifest, component_manifest


def component_by_id(component_manifest, identifier):
    if not COMPONENT_ID.fullmatch(identifier):
        raise ValueError("invalid component id: " + repr(identifier))
    for record in component_manifest["components"]:
        if record["id"] == identifier:
            return record
    raise ValueError("unknown component: " + identifier)


def safe_component_parent(raw):
    path = Path(raw).expanduser().resolve()
    if path == Path(path.anchor).resolve() or path == Path.home().resolve():
        raise ValueError("refusing a filesystem or home root for components")
    if path.exists() and not path.is_dir():
        raise ValueError("component parent exists and is not a directory: " + str(path))
    return path


def default_skills_root(runtime):
    folder = ".codex" if runtime == "codex" else ".claude"
    return Path.home() / folder / "skills"


def component_receipt(target):
    path = target / COMPONENT_RECEIPT
    if not path.is_file():
        raise ValueError("component install receipt missing: " + str(path))
    receipt = read_json(path)
    if receipt.get("schema") != "ai-human.component-install/v1":
        raise ValueError("unsupported component install receipt")
    if not COMPONENT_ID.fullmatch(str(receipt.get("component_id", ""))):
        raise ValueError("invalid component id in install receipt")
    if receipt.get("component_type") not in {"skill", "reference-pack"}:
        raise ValueError("invalid component type in install receipt")
    return receipt


def unique_component_archive(parent, prefix):
    archive_root = parent / ".ai-human-component-archive"
    archive_root.mkdir(parents=True, exist_ok=True)
    stem = prefix + "-" + now_utc()
    target = archive_root / stem
    counter = 2
    while target.exists():
        target = archive_root / (stem + "-" + str(counter))
        counter += 1
    return target


def install_component_tree(release, release_manifest, record, target, upgrade=False, at_checkpoint=False):
    source = release / safe_relative(record["source"], "component source")
    expected_digest = record["tree_sha256"]
    expected_count = record["file_count"]
    digest, count = tree_sha256(source)
    if digest != expected_digest or count != expected_count:
        raise ValueError("component source changed after validation: " + record["id"])
    if target.exists() and not upgrade:
        raise ValueError("component target already exists; use --upgrade at a checkpoint")
    if target.exists() and not at_checkpoint:
        raise ValueError("component upgrade requires --at-checkpoint")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.parent / ("." + target.name + ".install-" + now_utc())
    if temporary.exists():
        raise ValueError("component temporary target already exists: " + str(temporary))
    backup = None
    try:
        shutil.copytree(source, temporary)
        copied_digest, copied_count = tree_sha256(temporary)
        if copied_digest != expected_digest or copied_count != expected_count:
            raise ValueError("copied component integrity mismatch: " + record["id"])
        if record["type"] == "skill":
            validate_skill_source(temporary, record["id"])
        atomic_json(
            temporary / COMPONENT_RECEIPT,
            {
                "component_id": record["id"],
                "component_type": record["type"],
                "installed_version": release_manifest["version"],
                "repository": release_manifest["repository"],
                "schema": "ai-human.component-install/v1",
                "source_tree_sha256": expected_digest,
            },
        )
        if target.exists():
            backup = unique_component_archive(
                target.parent, record["id"] + "-before-" + release_manifest["version"]
            )
            shutil.move(str(target), str(backup))
        os.replace(temporary, target)
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary)
        if backup and backup.exists() and not target.exists():
            shutil.move(str(backup), str(target))
        raise
    print("AI-HUMAN COMPONENT INSTALL: PASS")
    print("- component: " + record["id"])
    print("- type: " + record["type"])
    print("- release version: " + release_manifest["version"])
    print("- target: " + str(target))
    print("- previous copy: " + (str(backup) if backup else "none"))


def remove_component_target(target, expected_id, expected_type, at_checkpoint=False):
    if not COMPONENT_ID.fullmatch(expected_id):
        raise ValueError("invalid component id: " + repr(expected_id))
    if not at_checkpoint:
        raise ValueError("component removal requires --at-checkpoint")
    if not target.is_dir():
        raise ValueError("installed component missing: " + str(target))
    receipt = component_receipt(target)
    if receipt.get("component_id") != expected_id or receipt.get("component_type") != expected_type:
        raise ValueError("component receipt does not match the requested removal")
    destination = unique_component_archive(target.parent, expected_id + "-removed")
    shutil.move(str(target), str(destination))
    print("AI-HUMAN COMPONENT REMOVE: PASS")
    print("- component: " + expected_id)
    print("- preserved at: " + str(destination))
    print("- deleted files: 0")


def list_components(args):
    temp, _release, release_manifest, component_manifest = component_release(args)
    try:
        print("AI-HUMAN COMPONENT CATALOG: PASS")
        print("- release version: " + release_manifest["version"])
        for record in component_manifest["components"]:
            print(
                "- " + record["id"] + " | " + record["type"] + " | " +
                record["install_policy"] + " | " + str(record["file_count"]) + " files"
            )
    finally:
        if temp:
            temp.cleanup()


def install_skill(args):
    temp, release, release_manifest, component_manifest = component_release(args)
    try:
        record = component_by_id(component_manifest, args.component)
        if record["type"] != "skill":
            raise ValueError("component is not a skill: " + args.component)
        skills_root = safe_component_parent(args.skills_root or default_skills_root(args.runtime))
        target = skills_root / record["id"]
        install_component_tree(
            release, release_manifest, record, target, args.upgrade, args.at_checkpoint
        )
    finally:
        if temp:
            temp.cleanup()


def remove_skill(args):
    if not COMPONENT_ID.fullmatch(args.component):
        raise ValueError("invalid component id: " + repr(args.component))
    skills_root = safe_component_parent(args.skills_root or default_skills_root(args.runtime))
    target = skills_root / args.component
    remove_component_target(target, args.component, "skill", args.at_checkpoint)


def install_pack(args):
    temp, release, release_manifest, component_manifest = component_release(args)
    try:
        record = component_by_id(component_manifest, args.component)
        if record["type"] != "reference-pack":
            raise ValueError("component is not a reference pack: " + args.component)
        target = safe_worker(args.target, must_exist=False)
        install_component_tree(
            release, release_manifest, record, target, args.upgrade, args.at_checkpoint
        )
    finally:
        if temp:
            temp.cleanup()


def remove_pack(args):
    target = safe_worker(args.target)
    receipt = component_receipt(target)
    identifier = str(receipt.get("component_id", ""))
    remove_component_target(target, identifier, "reference-pack", args.at_checkpoint)


def add_component_source_options(command):
    source = command.add_mutually_exclusive_group()
    source.add_argument("--source")
    source.add_argument("--latest", action="store_true")
    command.add_argument("--repository", default=DEFAULT_REPOSITORY)


def parser():
    root = argparse.ArgumentParser(description="AI-Human workspace lifecycle")
    sub = root.add_subparsers(dest="command", required=True)
    install_p = sub.add_parser("install")
    install_p.add_argument("worker")
    install_p.add_argument("--source")
    install_p.add_argument("--company", required=True)
    install_p.add_argument("--legal-entity", required=True)
    install_p.add_argument("--operating-unit", action="append", required=True)
    install_p.add_argument("--jurisdiction", action="append", required=True)
    install_p.add_argument("--company-owner", required=True)
    install_p.add_argument("--owner", required=True)
    install_p.add_argument("--name", required=True)
    install_p.add_argument("--role", required=True)
    install_p.add_argument("--purpose", required=True)
    install_p.add_argument("--user-relationship", required=True)
    install_p.add_argument("--compliance-owner", required=True)
    install_p.add_argument("--gate-profile", required=True)
    install_p.add_argument("--brain", choices=("Codex", "Claude", "Codex or Claude"), default="Codex or Claude")
    install_p.add_argument("--task-selection", choices=("owner", "agent"), default="owner")
    install_p.add_argument("--batch-cap", type=int, default=BATCH_CAP)
    install_p.add_argument("--worker-id")
    install_p.add_argument("--timezone")
    install_p.add_argument("--supervisor")
    install_p.add_argument("--automatic-updates", action="store_true")
    install_p.add_argument("--adopt", action="store_true")
    install_p.set_defaults(handler=install)

    gate_p = sub.add_parser("configure-gate-profile")
    gate_p.add_argument("worker")
    gate_p.add_argument("--source", required=True)
    gate_p.add_argument("--company", required=True)
    gate_p.add_argument("--legal-entity", required=True)
    gate_p.add_argument("--operating-unit", action="append", required=True)
    gate_p.add_argument("--jurisdiction", action="append", required=True)
    gate_p.add_argument("--purpose", required=True)
    gate_p.add_argument("--user-relationship", required=True)
    gate_p.add_argument("--compliance-owner", required=True)
    gate_p.add_argument("--gate-profile", required=True)
    gate_p.add_argument("--at-checkpoint", action="store_true")
    gate_p.set_defaults(handler=configure_gate_profile)

    for name, handler in (("status", status), ("validate", None), ("check", check), ("checkpoint", checkpoint)):
        item = sub.add_parser(name)
        item.add_argument("worker")
        item.set_defaults(handler=handler)
    update_p = sub.add_parser("update")
    update_p.add_argument("worker")
    update_p.add_argument("--source")
    update_p.add_argument("--latest", action="store_true")
    update_p.add_argument("--at-checkpoint", action="store_true")
    update_p.set_defaults(handler=update)
    rollback_p = sub.add_parser("rollback")
    rollback_p.add_argument("worker")
    rollback_p.add_argument("--version", required=True)
    rollback_p.set_defaults(handler=rollback)
    uninstall_p = sub.add_parser("uninstall")
    uninstall_p.add_argument("worker")
    uninstall_p.add_argument("--at-checkpoint", action="store_true")
    uninstall_p.set_defaults(handler=uninstall)
    suspend_p = sub.add_parser("suspend")
    suspend_p.add_argument("worker")
    suspend_p.add_argument("--reason", required=True)
    suspend_p.set_defaults(handler=suspend)
    resume_p = sub.add_parser("resume")
    resume_p.add_argument("worker")
    resume_p.set_defaults(handler=resume)
    verify_state_p = sub.add_parser("verify-state")
    verify_state_p.add_argument("worker")
    verify_state_p.add_argument(
        "--expect", choices=(MODE_ACTIVE, MODE_SUSPENDED, "UNINSTALLED"), required=True
    )
    verify_state_p.set_defaults(handler=verify_state)

    acquire_p = sub.add_parser("session-acquire")
    acquire_p.add_argument("worker")
    acquire_p.add_argument("--session-id", required=True)
    acquire_p.add_argument("--actor", required=True)
    acquire_p.set_defaults(handler=session_acquire)
    session_status_p = sub.add_parser("session-status")
    session_status_p.add_argument("worker")
    session_status_p.set_defaults(handler=session_status)
    release_p = sub.add_parser("session-release")
    release_p.add_argument("worker")
    release_p.add_argument("--session-id", required=True)
    release_p.add_argument("--expected-state-hash", required=True)
    release_p.set_defaults(handler=session_release)
    recover_p = sub.add_parser("session-recover")
    recover_p.add_argument("worker")
    recover_p.add_argument("--actor", required=True)
    recover_p.add_argument("--expected-state-hash", required=True)
    recover_p.add_argument("--reason", required=True)
    recover_p.set_defaults(handler=session_recover)
    configure_p = sub.add_parser("configure-control")
    configure_p.add_argument("worker")
    configure_p.add_argument("--worker-id", required=True)
    configure_p.add_argument("--timezone", required=True)
    configure_p.add_argument("--supervisor", required=True)
    configure_p.add_argument("--automatic-updates", choices=("ACTIVE", "DISABLED"), required=True)
    configure_p.add_argument("--approval-reference", required=True)
    configure_p.set_defaults(handler=configure_control_plane)
    state_commit_p = sub.add_parser("state-commit")
    state_commit_p.add_argument("worker")
    state_commit_p.add_argument("--session-id", required=True)
    state_commit_p.add_argument("--expected-state-hash", required=True)
    state_commit_p.add_argument("--changes", required=True)
    state_commit_p.set_defaults(handler=state_commit)

    task_start_p = sub.add_parser("task-start")
    task_start_p.add_argument("worker")
    task_start_p.add_argument("--title", required=True)
    task_start_p.add_argument("--task-id")
    task_start_p.add_argument("--source")
    task_start_p.add_argument("--next-action")
    task_start_p.add_argument("--exit-evidence")
    task_start_p.set_defaults(handler=task_start)
    task_complete_p = sub.add_parser("task-complete")
    task_complete_p.add_argument("worker")
    task_complete_p.add_argument("--task-id", required=True)
    task_complete_p.add_argument("--artifact", action="append", required=True)
    task_complete_p.add_argument("--outcome", required=True)
    task_complete_p.add_argument("--verification", required=True)
    task_complete_p.add_argument("--undo", required=True)
    task_complete_p.add_argument("--before")
    task_complete_p.set_defaults(handler=task_complete)

    proposal_p = sub.add_parser("capability-propose")
    proposal_p.add_argument("worker")
    proposal_p.add_argument("--session-id", required=True)
    proposal_p.add_argument("--expected-state-hash", required=True)
    proposal_p.add_argument("--proposal", required=True)
    proposal_p.set_defaults(handler=capability_propose)
    choice_p = sub.add_parser("capability-choice")
    choice_p.add_argument("worker")
    choice_p.add_argument("capability")
    choice_p.add_argument("choice", choices=("PROPOSE", "LATER", "REJECT"))
    choice_p.add_argument("--session-id", required=True)
    choice_p.add_argument("--expected-state-hash", required=True)
    choice_p.set_defaults(handler=capability_choice)
    activate_p = sub.add_parser("capability-activate")
    activate_p.add_argument("worker")
    activate_p.add_argument("capability")
    activate_p.add_argument("--session-id", required=True)
    activate_p.add_argument("--expected-state-hash", required=True)
    activate_p.add_argument("--actor", required=True)
    activate_p.add_argument("--scope", choices=("worker", "company"), required=True)
    activate_p.add_argument("--proof", required=True)
    activate_p.set_defaults(handler=capability_activate)

    improvement_show_p = sub.add_parser("improvement-show")
    improvement_show_p.add_argument("worker")
    improvement_show_p.set_defaults(handler=improvement_show)

    improvement_choice_p = sub.add_parser("improvement-choice")
    improvement_choice_p.add_argument("worker")
    improvement_choice_p.add_argument("choice", choices=("ENABLE", "DECLINE"))
    improvement_choice_p.add_argument("--session-id", required=True)
    improvement_choice_p.add_argument("--expected-state-hash", required=True)
    improvement_choice_p.add_argument("--timezone")
    improvement_choice_p.add_argument("--local-time")
    improvement_choice_p.add_argument("--source", action="append", choices=sorted(IMPROVEMENT_SOURCES))
    improvement_choice_p.add_argument(
        "--research", choices=("DISABLED", "APPROVED_LINKED_SOURCES"), default="DISABLED"
    )
    improvement_choice_p.add_argument("--freshness-days", type=int)
    improvement_choice_p.add_argument("--retention-days", type=int)
    improvement_choice_p.set_defaults(handler=improvement_choice)

    improvement_schedule_p = sub.add_parser("improvement-schedule")
    improvement_schedule_p.add_argument("worker")
    improvement_schedule_p.add_argument(
        "--status", choices=("ACTIVE", "PAUSED", "REMOVED", "UNAVAILABLE"), required=True
    )
    improvement_schedule_p.add_argument("--session-id", required=True)
    improvement_schedule_p.add_argument("--expected-state-hash", required=True)
    improvement_schedule_p.add_argument("--adapter")
    improvement_schedule_p.add_argument("--external-id")
    improvement_schedule_p.add_argument("--visible-card", action="store_true")
    improvement_schedule_p.add_argument("--next-run-local")
    improvement_schedule_p.add_argument("--reason")
    improvement_schedule_p.set_defaults(handler=improvement_schedule_record)

    improvement_control_p = sub.add_parser("improvement-control")
    improvement_control_p.add_argument("worker")
    improvement_control_p.add_argument("action", choices=("PAUSE", "RESUME", "REMOVE"))
    improvement_control_p.add_argument("--session-id", required=True)
    improvement_control_p.add_argument("--expected-state-hash", required=True)
    improvement_control_p.set_defaults(handler=improvement_control)

    improvement_research_p = sub.add_parser("improvement-research-record")
    improvement_research_p.add_argument("worker")
    improvement_research_p.add_argument("--session-id", required=True)
    improvement_research_p.add_argument("--expected-state-hash", required=True)
    improvement_research_p.add_argument("--receipt", required=True)
    improvement_research_p.add_argument("--supersedes")
    improvement_research_p.set_defaults(handler=improvement_research_record)

    improvement_run_p = sub.add_parser("improvement-run")
    improvement_run_p.add_argument("worker")
    improvement_run_p.add_argument(
        "--mode", choices=("MANUAL", "MISSED_RUN_RECOVERY", "SCHEDULED"), required=True
    )
    improvement_run_p.add_argument("--session-id", required=True)
    improvement_run_p.add_argument("--expected-state-hash", required=True)
    improvement_run_p.add_argument("--now-local", required=True)
    improvement_run_p.add_argument("--recommendations", required=True)
    improvement_run_p.add_argument("--reason")
    improvement_run_p.set_defaults(handler=improvement_run)

    improvement_forget_p = sub.add_parser("improvement-forget")
    improvement_forget_p.add_argument("worker")
    improvement_forget_p.add_argument("kind", choices=("RESEARCH", "RUN"))
    improvement_forget_p.add_argument("identifier")
    improvement_forget_p.add_argument("--session-id", required=True)
    improvement_forget_p.add_argument("--expected-state-hash", required=True)
    improvement_forget_p.set_defaults(handler=improvement_forget)

    automatic_p = sub.add_parser("automatic-update")
    automatic_p.add_argument("worker")
    automatic_source = automatic_p.add_mutually_exclusive_group(required=True)
    automatic_source.add_argument("--source")
    automatic_source.add_argument("--latest", action="store_true")
    automatic_p.add_argument(
        "--now-local", required=True,
        help="offset-aware worker-local date-time supplied by the approved scheduler",
    )
    automatic_p.set_defaults(handler=automatic_update)
    fleet_p = sub.add_parser("fleet-update")
    fleet_p.add_argument("--fleet", required=True)
    fleet_p.add_argument("--fleet-state", required=True)
    fleet_p.add_argument("--source", required=True)
    fleet_p.add_argument(
        "--now-local", required=True,
        help="offset-aware worker-local date-time for the confirmed fleet cohort",
    )
    fleet_p.set_defaults(handler=fleet_update)

    batch_plan_p = sub.add_parser("batch-plan")
    batch_plan_p.add_argument("kind", choices=BATCH_KINDS)
    batch_plan_p.add_argument("--units", type=int, required=True)
    batch_plan_p.add_argument("--embedded-entries", type=int, default=0)
    batch_plan_p.set_defaults(handler=show_batch_plan)

    components_p = sub.add_parser("components")
    add_component_source_options(components_p)
    components_p.set_defaults(handler=list_components)

    install_skill_p = sub.add_parser("install-skill")
    install_skill_p.add_argument("component")
    install_skill_p.add_argument("--runtime", choices=("codex", "claude"), required=True)
    install_skill_p.add_argument("--skills-root")
    install_skill_p.add_argument("--upgrade", action="store_true")
    install_skill_p.add_argument("--at-checkpoint", action="store_true")
    add_component_source_options(install_skill_p)
    install_skill_p.set_defaults(handler=install_skill)

    remove_skill_p = sub.add_parser("remove-skill")
    remove_skill_p.add_argument("component")
    remove_skill_p.add_argument("--runtime", choices=("codex", "claude"), required=True)
    remove_skill_p.add_argument("--skills-root")
    remove_skill_p.add_argument("--at-checkpoint", action="store_true")
    remove_skill_p.set_defaults(handler=remove_skill)

    install_pack_p = sub.add_parser("install-pack")
    install_pack_p.add_argument("component")
    install_pack_p.add_argument("target")
    install_pack_p.add_argument("--upgrade", action="store_true")
    install_pack_p.add_argument("--at-checkpoint", action="store_true")
    add_component_source_options(install_pack_p)
    install_pack_p.set_defaults(handler=install_pack)

    remove_pack_p = sub.add_parser("remove-pack")
    remove_pack_p.add_argument("target")
    remove_pack_p.add_argument("--at-checkpoint", action="store_true")
    remove_pack_p.set_defaults(handler=remove_pack)
    return root


def main():
    args = parser().parse_args()
    try:
        if args.command == "validate":
            ok, _ = validate_worker(safe_worker(args.worker))
            return 0 if ok else 1
        if args.command == "install" and not 1 <= args.batch_cap <= BATCH_CAP:
            raise ValueError("batch cap must be between 1 and " + str(BATCH_CAP))
        if args.command in MODE_GUARDED_COMMANDS:
            worker = safe_worker(args.worker)
            if worker_mode(worker) == MODE_SUSPENDED:
                raise ValueError(
                    "AI-human system is suspended; resume it before managed work, "
                    "or uninstall it to remove the system"
                )
        args.handler(args)
        return 0
    except Exception as exc:
        print("AI-HUMAN " + args.command.upper() + ": FAIL - " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
