#!/usr/bin/env python3
"""Fail closed when a public AI-Human release is incomplete or unsafe."""

import argparse
import ast
import hashlib
import json
import re
import sys
import unicodedata
import zipfile
from pathlib import Path


SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
REPOSITORY = "kairali-digital/ai-human-workspace"
GOVERNED_WORKFLOW_SHA256 = {
    ".github/workflows/portal-deploy.yml": "a373f4a02abcbbccc73cd3d8954826ce801f5e588a2e5e27ced04b82bfee043c",
    ".github/workflows/portal.yml": "475f188109f987ec00072d235d704475ee09dc726e6eba1d688a46cb0ac69012",
    ".github/workflows/validate.yml": "6b8189e91548a5916839d8afb3b022990422b842987011d0d57cb4fffc433f0e",
}
REQUIRED_FILES = {
    ".github/CODEOWNERS",
    ".github/pull_request_template.md",
    ".github/workflows/portal-deploy.yml",
    ".github/workflows/validate.yml",
    ".gitattributes",
    ".gitignore",
    "AGENTS.md",
    "CHANGELOG.md",
    "README.md",
    "component-manifest.json",
    "company-profiles/kairali/PROFILE.md",
    "company-profiles/kairali/SETUP-HELPER.md",
    "company-profiles/template/COMPANY-PROFILE.md",
    "company-profiles/template/GATE-PROFILE.example.json",
    "company-profiles/template/SETUP-HELPER-TEMPLATE.md",
    "core/AGENT-RULES.md",
    "core/AUTONOMY-CONTROL.md",
    "core/AUTHORITY-REGISTRY.json",
    "core/AI-HUMAN.md",
    "core/GATES-SHARED.md",
    "core/OPERATING-LOOP.md",
    "core/QUARTERLY-IMPROVEMENT.md",
    "core/SESSION-END.md",
    "core/SESSION-START.md",
    "core/TOOLBOX-TEMPLATE.md",
    "core/VERSION",
    "docs/BEGINNER-SETUP.md",
    "docs/COMPONENTS.md",
    "docs/GOVERNED-CAPABILITIES-AND-FLEET.md",
    "docs/MULTI-COMPANY-ROLLOUT.md",
    "docs/RELEASE-PROCESS.md",
    "docs/SECURITY-AND-DATA-BOUNDARIES.md",
    "docs/TECHNICAL-SETUP.md",
    "docs/THREE-WORKER-GO-LIVE.md",
    "docs/UPDATES-ROLLBACK-REMOVAL.md",
    "editions/README.md",
    "editions/kairali/INSTALL-DISABLE-REMOVE.md",
    "editions/kairali/START-HERE.md",
    "editions/reusable/INSTALL-DISABLE-REMOVE.md",
    "editions/reusable/START-HERE.md",
    "release-manifest.json",
    "packages/kairali/README.md",
    "packages/kairali/homework/COPY-PASTE-PROMPTS.txt",
    "packages/kairali/homework/EVERYONE-ELSE-AI-HUMAN-HOMEWORK-GUIDE.docx",
    "packages/kairali/homework/EVERYONE-ELSE-AI-HUMAN-HOMEWORK-GUIDE.pdf",
    "packages/kairali/homework/EVERYONE-ELSE-AI-HUMAN-HOMEWORK-PACK.sha256",
    "packages/kairali/homework/EVERYONE-ELSE-AI-HUMAN-HOMEWORK-PACK.zip",
    "packages/kairali/homework/EVERYONE-ELSE-AI-HUMAN-HOMEWORK-VIDEO.mp4",
    "packages/kairali/homework/START-HERE.md",
    "packages/kairali/homework/THREE-WORKER-GO-LIVE-CHECKLIST.md",
    "packages/kairali/people/ALL-EMPLOYEES.md",
    "packages/kairali/people/SETUP-HELPER.md",
    "packages/kairali/skills/kairali-akshar-marketing-science/SKILL.md",
    "packages/kairali/skills/kairali-rahul-sales-system/SKILL.md",
    "roles/ROLE-TEMPLATE.md",
    "scripts/ai_human.py",
    "scripts/build_editions.py",
    "scripts/build_public_release.py",
    "scripts/build_release.py",
    "scripts/validate_portal_deploy.py",
    "scripts/validate_release.py",
    "starter/COMPLIANCE-SOURCES.md",
    "starter/WORKSPACE-MAP.md",
    "tests/test_lifecycle.py",
}
REQUIRED_COMPONENTS = {
    "kairali-company-rollout": "reference-pack",
    "kairali-akshar-marketing-science": "skill",
    "kairali-rahul-sales-system": "skill",
}
APPROVED_SKILLS = {
    "kairali-akshar-marketing-science",
    "kairali-rahul-sales-system",
}
EXPECTED_ROLE_FILES = {
    "ALL-EMPLOYEES.md", "SETUP-HELPER.md", "anupam.md", "astha.md", "deepu.md",
    "interns.md", "rohan.md", "satyam.md", "shadab.md", "sunaj.md", "trusha.md",
    "vikash.md",
}
ALLOWED_BINARY_FILES = {
    "packages/kairali/homework/EVERYONE-ELSE-AI-HUMAN-HOMEWORK-GUIDE.docx",
    "packages/kairali/homework/EVERYONE-ELSE-AI-HUMAN-HOMEWORK-GUIDE.pdf",
    "packages/kairali/homework/EVERYONE-ELSE-AI-HUMAN-HOMEWORK-PACK.zip",
    "packages/kairali/homework/EVERYONE-ELSE-AI-HUMAN-HOMEWORK-VIDEO.mp4",
}
REQUIRED_TARGETS = {
    ".ai-human/system/AI-HUMAN.md",
    ".ai-human/system/AGENT-RULES.md",
    ".ai-human/system/AUTONOMY-CONTROL.md",
    ".ai-human/system/AUTHORITY-REGISTRY.json",
    ".ai-human/system/OPERATING-LOOP.md",
    ".ai-human/system/GATES-SHARED.md",
    ".ai-human/system/SESSION-START.md",
    ".ai-human/system/SESSION-END.md",
    ".ai-human/system/QUARTERLY-IMPROVEMENT.md",
    ".ai-human/VERSION",
    ".ai-human/bin/ai_human.py",
}
LOCAL_STATE = {
    "AGENTS.md", "CLAUDE.md", "AI-HUMAN.md", "COMPANY.md", "PARAMETERS.md",
    "ROLE.md", "MASTER_CURSOR.md", "OPEN_REGISTER.md", "TODAY.md",
    "COMPLETED_LEDGER.md", "EVIDENCE_LOG.md", "FACTS.md", "DECISIONS.md",
    "TOOLBOX.md", "GATES.md", "WORK-GATES.md", "COMPLIANCE-SOURCES.md", "WORKSPACE-MAP.md",
    "AUTOMATIONS.md", "START-HERE.md", "READ-ME-FIRST.txt",
}
INTRINSIC_NEVER_MANAGED = LOCAL_STATE | {
    ".ai-human/control/",
    ".ai-human/capabilities/",
    ".ai-human/improvement/",
    ".ai-human/autonomy/",
    ".ai-human/backups/",
    ".ai-human/downgrade-exports/",
    ".ai-human/install.json",
    ".ai-human/release-manifest.json",
    ".ai-human/update-receipt.json",
    ".ai-human/version-report.json",
}
PROOF_IGNORED_PARTS = {
    ".git", ".next", ".pytest_cache", ".vercel", "__pycache__", "dist", "node_modules",
}
PROOF_REQUIRED_KEYS = {
    "approval_status", "automatic_update_eligible", "files", "release_status",
    "repository", "schema", "version",
}
PARAMETERS = {
    "{{COMPANY_NAME}}", "{{COMPANY_OWNER}}", "{{OWNER_NAME}}",
    "{{WORKER_NAME}}", "{{ROLE_NAME}}", "{{PURPOSE}}", "{{BRAIN}}",
    "{{TASK_SELECTION}}", "{{BATCH_CAP}}", "{{WORKER_ID}}", "{{TIMEZONE}}",
    "{{SUPERVISOR_ID}}", "{{AUTOMATIC_UPDATES}}", "{{LEGAL_ENTITY}}",
    "{{OPERATING_UNITS}}", "{{JURISDICTIONS}}", "{{USER_RELATIONSHIP}}",
    "{{COMPLIANCE_OWNER}}", "{{GATE_PROFILE_ID}}", "{{GATE_REVIEW_DUE}}",
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def reject_duplicate_json_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON key: " + repr(key))
        value[key] = item
    return value


def strict_json_loads(content):
    return json.loads(content, object_pairs_hook=reject_duplicate_json_keys)


def fixed_unavailable_handler(source, function_name, required_code):
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    matches = [
        node for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == function_name
    ]
    if len(matches) != 1:
        return False
    body = list(matches[0].body)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
        if isinstance(body[0].value.value, str):
            body.pop(0)
    if len(body) != 1 or not isinstance(body[0], ast.Raise) or body[0].cause is not None:
        return False
    expression = body[0].exc
    if not isinstance(expression, ast.Call) or expression.keywords or len(expression.args) != 1:
        return False
    if not isinstance(expression.func, ast.Name) or expression.func.id != "ValueError":
        return False
    return isinstance(expression.args[0], ast.Constant) and (
        isinstance(expression.args[0].value, str)
        and required_code in expression.args[0].value
    )


def handler_guard_precedes_effect(
    source, function_name, guard_name, effect_name, effect_target_position=3,
):
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    matches = [
        node for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == function_name
    ]
    if len(matches) != 1:
        return False
    function = matches[0]

    def direct_call(statement):
        if not isinstance(statement, ast.Expr) or not isinstance(statement.value, ast.Call):
            return None
        call = statement.value
        return call if isinstance(call.func, ast.Name) else None

    blocks = []

    def collect_blocks(statements):
        blocks.append(statements)
        for statement in statements:
            if isinstance(statement, ast.Try):
                collect_blocks(statement.body)
                collect_blocks(statement.orelse)
                collect_blocks(statement.finalbody)
                for handler in statement.handlers:
                    collect_blocks(handler.body)
            elif isinstance(statement, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.With, ast.AsyncWith)):
                collect_blocks(statement.body)
                collect_blocks(statement.orelse)

    collect_blocks(function.body)
    all_calls = [
        call for block in blocks for statement in block
        for call in [direct_call(statement)] if call is not None
    ]
    guards = [call for call in all_calls if call.func.id == guard_name]
    effects = [call for call in all_calls if call.func.id == effect_name]
    if len(guards) != 1 or len(effects) != 1:
        return False
    guard, effect = guards[0], effects[0]
    if guard.keywords or len(guard.args) != 1:
        return False
    if effect_target_position >= len(effect.args):
        return False
    guard_target = guard.args[0]
    effect_target = effect.args[effect_target_position]
    if not (
        isinstance(guard_target, ast.Name)
        and isinstance(effect_target, ast.Name)
        and guard_target.id == effect_target.id
    ):
        return False
    return any(
        guard in [direct_call(statement) for statement in block]
        and effect in [direct_call(statement) for statement in block]
        and block.index(next(statement for statement in block if direct_call(statement) is guard))
        < block.index(next(statement for statement in block if direct_call(statement) is effect))
        for block in blocks
    )


def validate_public_edition_runtime_parity(root, manifest):
    downloads = root / "portal/public/downloads"
    if not downloads.is_dir():
        return []
    version = str(manifest.get("version", ""))
    lane = (
        "PUBLIC-KIT"
        if manifest.get("release_status") == "RELEASED"
        else "LOCAL-CANDIDATE"
    )
    token = "v" + version.replace(".", "")
    source_path = root / "scripts/ai_human.py"
    if not source_path.is_file():
        return ["edition runtime parity source is missing"]
    source = source_path.read_bytes()
    reusable = source.replace(
        b"kairali-digital/ai-human-workspace", b"standalone-local/ai-human-workspace"
    ).replace(b"AbhilashKairali", b"standalone-local")
    editions = (
        (
            downloads / ("KAIRALI-AI-HUMAN-" + token + "-EMPLOYEE-EDITION-" + lane + ".zip"),
            "KAIRALI-EMPLOYEE-EDITION/workspace/scripts/ai_human.py",
            source,
        ),
        (
            downloads / ("AI-HUMAN-" + token + "-REUSABLE-EDITION-" + lane + ".zip"),
            "AI-HUMAN-REUSABLE-EDITION/workspace/scripts/ai_human.py",
            reusable,
        ),
    )
    failures = []
    for archive_path, member, expected in editions:
        if not archive_path.is_file():
            failures.append("current edition archive is missing: " + archive_path.name)
            continue
        try:
            with zipfile.ZipFile(archive_path) as archive:
                actual = archive.read(member)
        except Exception as exc:
            failures.append("cannot read edition runtime from " + archive_path.name + ": " + str(exc))
            continue
        if actual != expected:
            failures.append("edition runtime differs from the current source: " + archive_path.name)
    return failures


def read_json(path):
    return strict_json_loads(path.read_text(encoding="utf-8"))


def portable_path(value):
    return str(value).replace("\\", "/")


def canonical_path(value):
    portable = unicodedata.normalize("NFC", portable_path(value))
    return "/".join(part.casefold() for part in portable.split("/"))


def protected_managed_path(value, declared=()):
    target = canonical_path(value).rstrip("/")
    for protected in set(declared) | INTRINSIC_NEVER_MANAGED:
        base = canonical_path(protected).rstrip("/")
        if target == base or target.startswith(base + "/"):
            return True
    return False


def path_uses_symlink(root, relative):
    current = Path(root).resolve()
    for part in Path(portable_path(relative)).parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def release_inventory(root):
    files = {}
    failures = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root)
        if any(part in PROOF_IGNORED_PARTS for part in relative.parts):
            continue
        if path.name == "release-proof.json":
            continue
        if path.is_symlink():
            failures.append("symbolic link in release payload: " + relative.as_posix())
            continue
        if (
            not path.is_file()
            or path.suffix == ".pyc"
            or path.name.endswith((".write-temp", ".update-temp", ".build-temp"))
        ):
            continue
        files[relative.as_posix()] = sha256(path)
    return files, failures


def validate_release_proof(root, manifest):
    proof_path = root / "release-proof.json"
    if proof_path.is_symlink() or not proof_path.is_file():
        return ["release proof is missing or is a symbolic link"]
    try:
        proof = read_json(proof_path)
    except Exception as exc:
        return ["invalid release proof: " + str(exc)]
    failures = []
    if not isinstance(proof, dict):
        return ["release proof must be a JSON object"]
    if set(proof) != PROOF_REQUIRED_KEYS:
        failures.append("release proof fields differ from the required schema")
    if proof.get("schema") != "ai-human.workspace-release-proof/v1":
        failures.append("unsupported release proof schema")
    for field in (
        "approval_status", "automatic_update_eligible", "release_status",
        "repository", "version",
    ):
        expected = manifest.get(field)
        if proof.get(field) != expected:
            failures.append("release proof " + field + " differs from the release manifest")
    recorded = proof.get("files")
    if not isinstance(recorded, dict):
        failures.append("release proof files must be a JSON object")
        return failures
    actual, inventory_failures = release_inventory(root)
    failures.extend(inventory_failures)
    recorded_paths = set(recorded)
    actual_paths = set(actual)
    for relative in sorted(actual_paths - recorded_paths):
        failures.append("release proof is missing payload file: " + relative)
    for relative in sorted(recorded_paths - actual_paths):
        failures.append("release proof lists an absent or excluded file: " + relative)
    for relative in sorted(recorded_paths & actual_paths):
        expected_hash = recorded.get(relative)
        if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
            failures.append("release proof has an invalid hash: " + relative)
        elif expected_hash != actual[relative]:
            failures.append("release proof file hash mismatch: " + relative)
    return failures


def tree_sha256(root):
    digest = hashlib.sha256()
    count = 0
    paths = sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix())
    for path in paths:
        if path.is_symlink():
            raise ValueError("symbolic link in component: " + str(path))
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8") + b"\0")
        digest.update(bytes.fromhex(sha256(path)) + b"\n")
        count += 1
    return digest.hexdigest(), count


def workflow_run_commands(source):
    """Return active shell commands from YAML run fields without counting comments."""
    commands = []
    block_indent = None
    for line_number, line in enumerate(source.splitlines()):
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        if block_indent is not None:
            if stripped and indent <= block_indent:
                block_indent = None
            else:
                if stripped and not stripped.startswith("#"):
                    commands.append((line_number, stripped))
                continue
        if re.fullmatch(r"\s*(?:-\s*)?run:\s*\|\s*", line):
            block_indent = indent
            continue
        match = re.fullmatch(r"\s*(?:-\s*)?run:\s+(.+?)\s*", line)
        if match:
            command = match.group(1).strip()
            if command and not command.startswith("#"):
                commands.append((line_number, command))
    return commands


def workflow_job_blocks(source):
    """Return top-level GitHub Actions job blocks keyed by job id."""
    lines = source.splitlines()
    try:
        jobs_start = lines.index("jobs:")
    except ValueError:
        return {}
    jobs_end = len(lines)
    for index in range(jobs_start + 1, len(lines)):
        if lines[index].strip() and not lines[index].startswith((" ", "\t")):
            jobs_end = index
            break
    starts = []
    for index in range(jobs_start + 1, jobs_end):
        match = re.fullmatch(r"  ([A-Za-z0-9_-]+):\s*", lines[index])
        if match:
            starts.append((match.group(1), index))
    blocks = {}
    for position, (job_id, start) in enumerate(starts):
        end = starts[position + 1][1] if position + 1 < len(starts) else jobs_end
        blocks[job_id] = "\n".join(lines[start:end]) + "\n"
    return blocks


def workflow_step_blocks(job_source):
    """Return ordered step blocks from one two-space-indented job block."""
    lines = job_source.splitlines()
    try:
        steps_start = lines.index("    steps:")
    except ValueError:
        return []
    starts = [
        index for index in range(steps_start + 1, len(lines))
        if re.match(r"^      - ", lines[index])
    ]
    blocks = []
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
        blocks.append((start, "\n".join(lines[start:end]) + "\n"))
    return blocks


def action_pin_failures(source, workflow_name="workflow"):
    failures = []
    for line in source.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = re.match(r"-\s+uses:\s*([^\s#]+)", stripped)
        if not match:
            continue
        action = match.group(1)
        if action.startswith(("./", "docker://")):
            continue
        if "@" not in action or not re.fullmatch(r"[0-9a-f]{40}", action.rsplit("@", 1)[1]):
            failures.append(
                workflow_name + " uses an action without an immutable commit pin: " + action
            )
    return failures


def vercel_production_kind(command):
    """Recognize direct, npx, path, env-prefixed and shell-wrapped Vercel commands."""
    match = re.search(
        r"\bvercel(?:@[A-Za-z0-9._-]+)?\b[^\n;&|]*?\b(pull|build|deploy)\b",
        command,
        flags=re.I,
    )
    return match.group(1).casefold() if match else None


def validation_workflow_failures(source):
    """Require active, fail-closed pull-request validation and secret-scan jobs."""
    failures = []
    lines = source.splitlines()
    try:
        on_start = lines.index("on:")
    except ValueError:
        on_start = -1
    on_end = len(lines)
    if on_start >= 0:
        for index in range(on_start + 1, len(lines)):
            if lines[index].strip() and not lines[index].startswith((" ", "\t")):
                on_end = index
                break
    if on_start < 0 or "  pull_request:" not in lines[on_start + 1:on_end]:
        failures.append("validation workflow lacks an active pull_request trigger")

    jobs = workflow_job_blocks(source)
    required_jobs = {"validate", "secrets"}
    if not required_jobs.issubset(jobs):
        failures.append("validation workflow lacks active validate and secrets jobs")
        return failures
    if any(
        "shell:" in line.strip() and not line.strip().startswith("#")
        for line in lines
    ):
        failures.append("validation workflow may not override fail-closed shell behavior")

    validate_commands = [command for _line, command in workflow_run_commands(jobs["validate"])]
    required_validate = {
        "python scripts/validate_release.py . --ci",
        "python -m unittest discover -s tests -v",
    }
    if not required_validate.issubset(validate_commands):
        failures.append("validation workflow lacks active candidate/public validation or lifecycle tests")
    secret_commands = [command for _line, command in workflow_run_commands(jobs["secrets"])]
    if not any(re.search(r"gitleaks[\"']?\s+git\s+\.(?:\s|$)", command, flags=re.I) for command in secret_commands):
        failures.append("validation workflow lacks an active gitleaks Git-history scan")
    for job_id in required_jobs:
        if any(
            line.strip().startswith(("if:", "continue-on-error:"))
            for line in jobs[job_id].splitlines()
            if not line.strip().startswith("#")
        ):
            failures.append("validation workflow " + job_id + " job may not be conditional or continue on error")
    return failures


def portal_deploy_workflow_failures(source):
    """Validate the exact fail-closed gate step and its Vercel consumers."""
    failures = []
    jobs = workflow_job_blocks(source)
    if "deploy" not in jobs:
        return ["portal deployment workflow lacks the deploy job"]
    if any(
        "shell:" in line.strip() and not line.strip().startswith("#")
        for line in source.splitlines()
    ):
        failures.append("portal deployment workflow may not override fail-closed shell behavior")

    production_jobs = {}
    for job_id, job_source in jobs.items():
        kinds = [
            vercel_production_kind(command)
            for _line, command in workflow_run_commands(job_source)
        ]
        kinds = [kind for kind in kinds if kind]
        if kinds:
            production_jobs[job_id] = kinds
    unexpected_jobs = sorted(set(production_jobs) - {"deploy"})
    if unexpected_jobs:
        failures.append(
            "Vercel production commands may run only in the governed deploy job: " +
            ", ".join(unexpected_jobs)
        )

    deploy_source = jobs["deploy"]
    deploy_commands = workflow_run_commands(deploy_source)
    audit_lines = [
        line for line, command in deploy_commands
        if command == "npm audit --omit=dev"
    ]
    vercel_lines = [
        line for line, command in deploy_commands
        if vercel_production_kind(command)
    ]
    if len(audit_lines) != 1:
        failures.append("portal deployment workflow requires one production dependency audit")
    elif vercel_lines and audit_lines[0] >= min(vercel_lines):
        failures.append("production dependency audit must run before Vercel commands")
    if any(
        line.strip().startswith("continue-on-error:")
        for line in deploy_source.splitlines()
        if not line.strip().startswith("#")
    ):
        failures.append("portal deployment job may not continue on error")
    steps = workflow_step_blocks(deploy_source)
    if not steps:
        return ["portal deployment workflow deploy job lacks steps"]

    gate_name = "      - name: Refuse an unapproved release or candidate-only portal"
    gate_steps = [(start, block) for start, block in steps if block.splitlines()[0] == gate_name]
    if len(gate_steps) != 1:
        failures.append("portal deployment workflow must contain exactly one production gate step")
        gate_start = -1
    else:
        gate_start, gate_block = gate_steps[0]
        gate_commands = [command for _line, command in workflow_run_commands(gate_block)]
        expected_commands = [
            "python3 scripts/validate_release.py .",
            "python3 scripts/validate_portal_deploy.py .",
        ]
        if gate_commands != expected_commands:
            failures.append("portal deployment workflow lacks active release and candidate-asset gates")
        if "        working-directory: ${{ github.workspace }}" not in gate_block.splitlines():
            failures.append("portal deployment gate does not run from the repository root")
        if any(
            line.strip().startswith(("if:", "continue-on-error:", "shell:"))
            for line in gate_block.splitlines()[1:]
        ):
            failures.append("portal deployment gate may not be conditional, override its shell or continue on error")

    vercel_steps = []
    vercel_kinds = []
    for start, block in steps:
        commands = [command for _line, command in workflow_run_commands(block)]
        kinds = [vercel_production_kind(command) for command in commands]
        kinds = [kind for kind in kinds if kind]
        if not kinds:
            continue
        vercel_steps.append(start)
        vercel_kinds.extend(kinds)
        if any(
            line.strip().startswith(("if:", "continue-on-error:", "shell:"))
            for line in block.splitlines()[1:]
        ):
            failures.append("Vercel production steps may not bypass a failed release gate")
    if sorted(vercel_kinds) != ["build", "deploy", "pull"]:
        failures.append("portal deployment workflow requires exactly one active Vercel pull, build and deploy command")
    elif gate_start < 0 or gate_start >= min(vercel_steps):
        failures.append("portal deployment gates must run before every Vercel production command")
    return failures


def safe_relative(value):
    portable = portable_path(value)
    trimmed = portable.rstrip("/")
    parts = trimmed.split("/") if trimmed else []
    path = Path(trimmed)
    if not bool(trimmed) or (
        "\x00" in portable
        or portable.startswith("/")
        or re.match(r"^[A-Za-z]:", portable)
        or any(part in {"", ".", ".."} for part in parts)
        or path.is_absolute()
    ):
        return False
    reserved = {"con", "prn", "aux", "nul"} | {
        prefix + str(index) for prefix in ("com", "lpt") for index in range(1, 10)
    }
    return not any(
        part != unicodedata.normalize("NFC", part)
        or part.endswith((" ", "."))
        or any(ord(character) < 32 or character in '<>:"|?*' for character in part)
        or part.split(".", 1)[0].casefold() in reserved
        or len(part.encode("utf-8")) > 255
        for part in parts
    )


def text_files(root):
    # The portal is a separately validated Vercel application, not part of the
    # installable AI-Human workspace release.
    ignored = {".git", "__pycache__", "dist", "portal"}
    for path in root.rglob("*"):
        if not path.is_file() or any(part in ignored for part in path.parts):
            continue
        if path.stat().st_size > 2 * 1024 * 1024:
            yield path, None
            continue
        try:
            yield path, path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            yield path, None


def prompt_block(text):
    match = re.search(
        r"```text\n(I am stuck setting up my Kairali AI workspace\..*?Start now by checking what I already have\.)\n```",
        text,
        flags=re.S,
    )
    return match.group(1) if match else ""


def validate(root, candidate=False):
    failures = []

    for relative in sorted(REQUIRED_FILES):
        path = root / relative
        if not path.is_file() or path.stat().st_size == 0:
            failures.append("missing or empty required file: " + relative)

    manifest_path = root / "release-manifest.json"
    try:
        manifest = read_json(manifest_path)
    except Exception as exc:
        manifest = {}
        failures.append("invalid release-manifest.json: " + str(exc))

    version = str(manifest.get("version", ""))
    control_plane_version = bool(SEMVER.fullmatch(version)) and tuple(int(part) for part in version.split(".")) >= (1, 6, 0)
    if not SEMVER.fullmatch(version):
        failures.append("manifest version is not semantic: " + repr(version))
    else:
        for relative in (
            "docs/releases/RELEASE-NOTES-v" + version + ".md",
            "docs/releases/VET-v" + version + ".md",
        ):
            path = root / relative
            if not path.is_file() or path.stat().st_size == 0:
                failures.append("missing or empty current-version release evidence: " + relative)
    version_path = root / "core/VERSION"
    if version_path.is_file() and version_path.read_text(encoding="utf-8").strip() != version:
        failures.append("core/VERSION does not match the manifest")
    if manifest.get("schema") != "ai-human.workspace-release/v1":
        failures.append("unsupported manifest schema")
    if manifest.get("repository") != REPOSITORY:
        failures.append("manifest repository must be " + REPOSITORY)
    if candidate:
        if manifest.get("approval_status") != "LOCAL_BUILD_ONLY":
            failures.append("candidate approval status must be LOCAL_BUILD_ONLY")
        if manifest.get("release_status") != "LOCAL_BUILD_ONLY":
            failures.append("candidate release status must be LOCAL_BUILD_ONLY")
        if manifest.get("automatic_update_eligible") is not False:
            failures.append("a local candidate cannot be eligible for automatic updates")
    else:
        if manifest.get("approval_status") != "APPROVED_BY_OWNER":
            failures.append("release is not owner-approved")
        if manifest.get("release_status") != "RELEASED":
            failures.append("release status is not RELEASED")
    compatibility = manifest.get("compatibility") or {}
    classification = compatibility.get("classification")
    if control_plane_version and classification not in {
        "BACKWARD_COMPATIBLE", "SETUP_MIGRATION_REQUIRED",
    }:
        failures.append("release lacks a supported compatibility classification")
    if classification == "SETUP_MIGRATION_REQUIRED" and manifest.get("automatic_update_eligible") is not False:
        failures.append("a setup-migration release cannot be eligible for automatic updates")
    if classification == "SETUP_MIGRATION_REQUIRED" and not compatibility.get("migration"):
        failures.append("setup-migration classification lacks migration instructions")
    if control_plane_version and compatibility.get("preserves_user_state") is not True:
        failures.append("release does not declare user-state preservation")
    minimum = str(compatibility.get("minimum_supported_version", ""))
    if control_plane_version and not SEMVER.fullmatch(minimum):
        failures.append("release compatibility floor is not semantic")

    failures.extend(validate_release_proof(root, manifest))
    failures.extend(validate_public_edition_runtime_parity(root, manifest))

    component_path = root / "component-manifest.json"
    try:
        component_manifest = read_json(component_path)
    except Exception as exc:
        component_manifest = {}
        failures.append("invalid component-manifest.json: " + str(exc))
    if component_manifest.get("schema") != "ai-human.component-release/v1":
        failures.append("unsupported component manifest schema")
    if component_manifest.get("version") != version:
        failures.append("component manifest version differs from release version")
    if component_manifest.get("repository") != REPOSITORY:
        failures.append("component manifest repository must be " + REPOSITORY)
    expected_component_approval = "LOCAL_BUILD_ONLY" if candidate else "APPROVED_BY_OWNER"
    if component_manifest.get("approval_status") != expected_component_approval:
        failures.append("component approval status is wrong for this validation lane")
    expected_component_status = "LOCAL_BUILD_ONLY" if candidate else "RELEASED"
    if component_manifest.get("release_status", "RELEASED") != expected_component_status:
        failures.append("component release status is wrong for this validation lane")
    found_components = {}
    found_skills = set()
    for index, record in enumerate(component_manifest.get("components") or []):
        identifier = str(record.get("id", ""))
        kind = str(record.get("type", ""))
        source = str(record.get("source", ""))
        if identifier in found_components:
            failures.append("duplicate component id: " + identifier)
        found_components[identifier] = kind
        if kind == "skill":
            found_skills.add(identifier)
        if kind not in {"skill", "reference-pack"}:
            failures.append("unsupported component type at index " + str(index))
        if not safe_relative(source) or not source.replace("\\", "/").startswith("packages/"):
            failures.append("unsafe component source at index " + str(index))
            continue
        component_root = root / Path(portable_path(source))
        if path_uses_symlink(root, source):
            failures.append("component source may not use symbolic links: " + source)
            continue
        if not component_root.is_dir():
            failures.append("component source missing: " + source)
            continue
        try:
            digest, count = tree_sha256(component_root)
        except ValueError as exc:
            failures.append(str(exc))
            continue
        if digest != record.get("tree_sha256"):
            failures.append("component tree hash mismatch: " + identifier)
        if count != record.get("file_count"):
            failures.append("component file count mismatch: " + identifier)
        if kind == "skill":
            skill_text = (component_root / "SKILL.md").read_text(encoding="utf-8", errors="replace") if (component_root / "SKILL.md").is_file() else ""
            if not re.search(r"^name:\s*['\"]?" + re.escape(identifier) + r"['\"]?\s*$", skill_text, flags=re.M):
                failures.append("skill name differs from component id: " + identifier)
    if found_components != REQUIRED_COMPONENTS:
        failures.append("component catalog differs from the approved company-kit and two-skill set")
    if found_skills != APPROVED_SKILLS:
        failures.append("skill catalog contains an unapproved or missing skill")

    never_managed_value = manifest.get("never_managed") or []
    if not isinstance(never_managed_value, list) or any(
        not isinstance(value, str) or not value.strip() for value in never_managed_value
    ):
        failures.append("never_managed must be a list of non-empty paths or boundary labels")
        never_managed_value = []
    targets = set()
    for index, record in enumerate(manifest.get("managed_files") or []):
        if not isinstance(record, dict):
            failures.append("managed file record is not a JSON object at index " + str(index))
            continue
        source = str(record.get("source", ""))
        target = str(record.get("target", ""))
        if not safe_relative(source):
            failures.append("unsafe managed source at index " + str(index))
            continue
        target_key = portable_path(target)
        target_comparison = canonical_path(target)
        if not safe_relative(target) or not target_key.startswith(".ai-human/"):
            failures.append("unsafe managed target at index " + str(index))
            continue
        if protected_managed_path(target_key, never_managed_value):
            failures.append("release tries to manage protected local state: " + target_key)
            continue
        if target_comparison in targets:
            failures.append("duplicate managed target: " + target_key)
        targets.add(target_comparison)
        path = root / Path(portable_path(source))
        if path_uses_symlink(root, source):
            failures.append("managed source may not use symbolic links: " + source)
            continue
        if not path.is_file():
            failures.append("managed source missing: " + source)
        elif record.get("sha256") != sha256(path):
            failures.append("managed hash mismatch: " + source)
    for target in sorted(
        value for value in REQUIRED_TARGETS if canonical_path(value) not in targets
    ):
        failures.append("required managed target missing: " + target)
    local_state_keys = {canonical_path(value) for value in LOCAL_STATE}
    for target in sorted(targets.intersection(local_state_keys)):
        failures.append("release tries to manage local state: " + target)
    never_managed = set(never_managed_value)
    for local in sorted(LOCAL_STATE - never_managed):
        failures.append("local state absent from never_managed: " + local)
    if control_plane_version:
        for local in (
            ".ai-human/control/", ".ai-human/capabilities/", ".ai-human/improvement/",
            ".ai-human/autonomy/", ".ai-human/backups/", ".ai-human/version-report.json",
        ):
            if local not in never_managed:
                failures.append("local control state absent from never_managed: " + local)

    authority_registry_path = root / "core/AUTHORITY-REGISTRY.json"
    if authority_registry_path.is_file():
        try:
            authority_registry = read_json(authority_registry_path)
        except Exception as exc:
            authority_registry = None
            failures.append("invalid managed effect-authority registry: " + str(exc))
        if authority_registry != {
            "authorities": [], "schema": "ai-human.effect-authority-registry/v1",
        }:
            failures.append(
                "v2.4 must safe-disable external effects with an exactly empty authority registry"
            )
    else:
        failures.append("v2.4 safe-disabled authority registry is missing")
    runtime_path = root / "scripts/ai_human.py"
    if runtime_path.is_file():
        runtime_source = runtime_path.read_text(encoding="utf-8")
        for forbidden in (
            "AI_HUMAN_AUTHORITY_", "post_effect_authority", "executable_sha256",
            "Authorization\": \"Bearer ",
        ):
            if forbidden in runtime_source:
                failures.append("runtime contains a forbidden file/env external executor: " + forbidden)
        if not fixed_unavailable_handler(
            runtime_source, "action_execute", "UNAVAILABLE_NO_NATIVE_BROKER"
        ):
            failures.append("action-execute is not unconditionally safe-disabled before state/network")
        if not fixed_unavailable_handler(
            runtime_source, "autonomy_skill_install", "UNAVAILABLE_NO_TRUSTED_SKILL_LOADER"
        ):
            failures.append("silent project-skill installation is not unconditionally safe-disabled")
        if not fixed_unavailable_handler(
            runtime_source, "install_skill", "UNAVAILABLE_NO_HUMAN_PRESENCE_AUTHORITY"
        ):
            failures.append("generic managed skill installation is not unconditionally safe-disabled")
        if not fixed_unavailable_handler(
            runtime_source, "validate_autonomy_consent",
            "UNAVAILABLE_NO_TRUSTED_EFFECT_RUNTIME",
        ):
            failures.append("autonomy consent does not fail closed for every v2.4 silent effect")
        if not handler_guard_precedes_effect(
            runtime_source, "install_pack", "refuse_skill_discovery_target",
            "install_component_tree",
        ):
            failures.append(
                "reference-pack install is not guarded before a host skill-discovery write"
            )

    for local in sorted(LOCAL_STATE):
        if local == "AGENTS.md":
            continue
        if (root / local).exists():
            failures.append("live user state is present at repository root: " + local)

    core_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted((root / "core").glob("*")) if path.is_file()
    )
    for company_word in ("Kairali", "Abhilash", "Abilash", "Ambuj"):
        if company_word.casefold() in core_text.casefold():
            failures.append("company-specific name in neutral core: " + company_word)
    if re.search(r"\bemployee\b", core_text, flags=re.I):
        failures.append("neutral core uses employee instead of user")
    autonomy_doc_path = root / "core/AUTONOMY-CONTROL.md"
    if autonomy_doc_path.is_file():
        autonomy_doc = autonomy_doc_path.read_text(encoding="utf-8")
        autonomy_doc_words = " ".join(autonomy_doc.split()).casefold()
        for required in (
            "EMAIL AND LINKEDIN EXTERNAL EFFECTS ARE NOT AVAILABLE",
            "Silent project-skill installation is also unavailable",
            "managed `install-skill` entry point is also disabled",
            "No standing-permission channel executes an effect in v2.4",
        ):
            if " ".join(required.split()).casefold() not in autonomy_doc_words:
                failures.append("autonomy availability banner lacks: " + required)

    starter_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted((root / "starter").glob("*")) if path.is_file()
    )
    for parameter in sorted(PARAMETERS):
        if parameter not in starter_text:
            failures.append("starter parameter is unused: " + parameter)
    if re.search(r"\bemployee\b", starter_text, flags=re.I):
        failures.append("neutral starter uses employee instead of user")
    if "UNAVAILABLE IN v2.4" not in starter_text:
        failures.append("starter automation table does not show safe-disabled standing effects")
    workspace_map_path = root / "starter/WORKSPACE-MAP.md"
    if workspace_map_path.is_file():
        workspace_map = workspace_map_path.read_text(encoding="utf-8")
        for required in (
            "COMPANY.md", "PARAMETERS.md", "ROLE.md", "gate-profile.json", "GATES.md",
            "WORK-GATES.md", "COMPLIANCE-SOURCES.md", "FACTS.md", "DECISIONS.md", "TOOLBOX.md",
            "AUTOMATIONS.md", "MASTER_CURSOR.md", "OPEN_REGISTER.md", "TODAY.md",
            "COMPLETED_LEDGER.md", "EVIDENCE_LOG.md", "WORKSPACE-MAP.md", "credentials",
        ):
            if required.casefold() not in workspace_map.casefold():
                failures.append("workspace file-of-record map lacks: " + required)
    gate_example_path = root / "company-profiles/template/GATE-PROFILE.example.json"
    if gate_example_path.is_file():
        try:
            gate_example = read_json(gate_example_path)
        except Exception as exc:
            gate_example = {}
            failures.append("invalid Gate 0 profile example: " + str(exc))
        for required in (
            "company", "legal_entity", "operating_units", "jurisdictions",
            "purpose_scope", "user_relationship", "compliance_owner", "sources",
            "gates", "unknowns", "unverified_leads", "review_due",
        ):
            if required not in gate_example:
                failures.append("Gate 0 profile example lacks: " + required)
        if gate_example.get("status") != "DRAFT":
            failures.append("public Gate 0 profile example must remain DRAFT")

    role_root = root / "packages/kairali/people"
    if role_root.is_dir():
        actual_roles = {path.name for path in role_root.glob("*.md")}
        if actual_roles != EXPECTED_ROLE_FILES:
            failures.append("Kairali people-prompt set is incomplete or contains an unexpected file")
    homework_root = root / "packages/kairali/homework/AI-HUMAN-STARTERS"
    expected_homework = {
        "01-Email-Triage-AI-Human",
        "02-Drive-Inventory-AI-Human",
        "03-LinkedIn-Message-Assistant-OPTIONAL",
    }
    if homework_root.is_dir():
        actual_homework = {path.name for path in homework_root.iterdir() if path.is_dir()}
        if actual_homework != expected_homework:
            failures.append("homework starter set is incomplete or unexpected")
        for folder in sorted(expected_homework):
            for required in (
                "AGENTS.md", "MASTER_CURSOR.md", "OPEN_REGISTER.md", "START-HERE.md",
                "WORK-GATES.md",
            ):
                if not (homework_root / folder / required).is_file():
                    failures.append("homework starter missing " + folder + "/" + required)
            if (homework_root / folder / "GATES.md").exists():
                failures.append(
                    "public homework starter must not embed an entity Gate 0: "
                    + folder + "/GATES.md"
                )

    homework_pack = root / "packages/kairali/homework/EVERYONE-ELSE-AI-HUMAN-HOMEWORK-PACK.zip"
    homework_sidecar = root / "packages/kairali/homework/EVERYONE-ELSE-AI-HUMAN-HOMEWORK-PACK.sha256"
    if homework_pack.is_file() and homework_sidecar.is_file():
        fields = homework_sidecar.read_text(encoding="utf-8").strip().split()
        expected = fields[0] if fields else ""
        if not re.fullmatch(r"[0-9a-f]{64}", expected) or expected != sha256(homework_pack):
            failures.append("homework pack checksum sidecar does not match the ZIP")

    beginner_path = root / "docs/BEGINNER-SETUP.md"
    helper_path = root / "company-profiles/kairali/SETUP-HELPER.md"
    if beginner_path.is_file() and helper_path.is_file():
        beginner = beginner_path.read_text(encoding="utf-8")
        helper = helper_path.read_text(encoding="utf-8")
        if not prompt_block(beginner):
            failures.append("beginner guide lacks the complete Kairali Setup Helper prompt")
        elif prompt_block(beginner) != prompt_block(helper):
            failures.append("beginner and Kairali profile Setup Helper prompts differ")
        for required in (
            "Install in five visible steps", "DONE WHEN", "check what is already installed",
            "Never ask me to use Terminal", "Never choose Full access",
            "Kairali employee edition", "reusable edition", "SUSPENDED", "UNINSTALLED",
            "Troubleshooting", "Mac", "Windows", "Extract All",
        ):
            if required.casefold() not in beginner.casefold():
                failures.append("beginner guide lacks required phrase: " + required)
        if "downloads the latest public release" in beginner:
            failures.append("beginner guide bypasses the edition source copy selected during setup")
        approved_prompt = prompt_block(helper)
        packaged_helper_path = root / "packages/kairali/people/SETUP-HELPER.md"
        if packaged_helper_path.is_file() and prompt_block(packaged_helper_path.read_text(encoding="utf-8")) != approved_prompt:
            failures.append("packaged Kairali Setup Helper prompt differs from the approved profile")
        for folder in (
            "01-Email-Triage-AI-Human",
            "02-Drive-Inventory-AI-Human",
            "03-LinkedIn-Message-Assistant-OPTIONAL",
        ):
            for name in ("START-HERE.md", "READ-ME-FIRST.txt"):
                path = root / "packages/kairali/homework/AI-HUMAN-STARTERS" / folder / name
                if path.is_file() and approved_prompt not in path.read_text(encoding="utf-8"):
                    failures.append("homework file lacks exact approved Setup Helper prompt: " + folder + "/" + name)

    all_employees_path = root / "packages/kairali/people/ALL-EMPLOYEES.md"
    if all_employees_path.is_file():
        all_employees = all_employees_path.read_text(encoding="utf-8")
        all_employees_flat = re.sub(r"\s+", " ", all_employees)
        for required in (
            "Personal Work Memory + Daily Email EA", "Drive Master Index",
            "Weekly LinkedIn Message Assistant",
            "homework/START-HERE.md", "Assignment is not execution",
            "must not silently stop at row 25", "separate GitHub Issues",
        ):
            if required.casefold() not in all_employees_flat.casefold():
                failures.append("all-employee prompt lacks fallback route: " + required)
    homework_prompts_path = root / "packages/kairali/homework/COPY-PASTE-PROMPTS.txt"
    if homework_prompts_path.is_file():
        homework_prompts = homework_prompts_path.read_text(encoding="utf-8")
        homework_prompts_flat = re.sub(r"\s+", " ", homework_prompts)
        for required in (
            "EMAIL-HW-001", "DRIVE-HW-001", "LINKEDIN-WEEKLY-001",
            "What fixed local time should your daily email brief",
            "BRIEF + SAFE FILING", "Daily Email Importance Brief",
            "no Gmail filter was changed", "PERSONAL-WORK-MEMORY.md",
            "PROPOSED REPLIES", "NOT SENT", "NEWSLETTERS TO REVIEW",
            "SHOW MY MEMORY", "CORRECT MEMORY <ID>", "FORGET <ID>",
            "metadata only", "TEST 25", "FULL DRIVE INDEX",
            "DRIVE-INDEX.jsonl", "DRIVE-REGISTER.csv", "GOOGLE SHEET",
            "generation ID", "SET WEEKLY REFRESH", "Sunday night",
            "RUN DRIVE REFRESH NOW", "NOT SEEN THIS RUN",
            "UNKNOWN — CONNECTOR COVERAGE GAP",
            "What local time every Saturday", "Focused and Other",
            "READY TO SEND", "NEEDS YOUR DECISION", "manually press Send",
            "CONFIRMED-LINKEDIN-LEARNINGS.md",
        ):
            if required.casefold() not in homework_prompts_flat.casefold():
                failures.append("homework prompts lack: " + required)
    email_root = homework_root / "01-Email-Triage-AI-Human"
    if email_root.is_dir():
        email_required_files = {
            "DAILY-TRIAGE-PROMPT.md", "EMAIL-RULE-REVIEW.md",
            "EMAIL-TRIAGE-CURSOR.md", "EMAIL-TRIAGE-RULES.md",
            "PERSONAL-WORK-MEMORY.md", "MEMORY-REVIEW-QUEUE.md",
            "MEMORY-SOURCES.md", "ASK-MY-WORK-MEMORY.md",
        }
        for name in sorted(email_required_files):
            if not (email_root / name).is_file():
                failures.append("Email Triage starter missing " + name)
        email_text = "\n".join(
            path.read_text(encoding="utf-8", errors="replace")
            for path in sorted(email_root.iterdir()) if path.is_file()
        )
        for required in (
            "What fixed local time should your daily email brief",
            "BRIEF ONLY", "BRIEF + SAFE FILING",
            "Daily Email Importance Brief", "DAILY-TRIAGE-PROMPT.md",
            "no more than 25", "every connector-visible result", "checkpoint",
            "first successful daily run in a new calendar month",
            "AI Triage/Reviewed", "AI Filed/Promotions",
            "permanent Gmail filter", "computer is awake",
            "ChatGPT is running", "this exact project remains available",
            "PERSONAL-WORK-MEMORY.md", "MEMORY-REVIEW-QUEUE.md",
            "MEMORY-SOURCES.md", "ASK-MY-WORK-MEMORY.md",
            "TODAY AT A GLANCE", "PROPOSED REPLIES", "NOT SENT",
            "NEWSLETTERS TO REVIEW", "MEMORY LEARNED OR NEEDS CONFIRMATION",
            "SHOW MY MEMORY", "CORRECT MEMORY <ID>", "FORGET <ID>",
            "EXCLUDE <topic or person>", "REFRESH MEMORY",
            "CONFIRMED", "OBSERVED — VERIFY", "source reference",
            "Do not copy full message text", "Never unsubscribe",
        ):
            if required.casefold() not in email_text.casefold():
                failures.append("Email Triage starter lacks: " + required)
        for forbidden in (
            "send without approval", "delete low-risk mail",
            "change permanent Gmail filters automatically",
        ):
            if forbidden.casefold() in email_text.casefold():
                failures.append("Email Triage starter contains unsafe instruction: " + forbidden)
    drive_root = homework_root / "02-Drive-Inventory-AI-Human"
    if drive_root.is_dir():
        for required_file in (
            "DRIVE-REGISTER-SCHEMA.md", "WEEKLY-DRIVE-REFRESH-PROMPT.md",
            "validate_drive_register.py",
        ):
            if not (drive_root / required_file).is_file():
                failures.append("Drive Index starter missing " + required_file)
        drive_text = "\n".join(
            path.read_text(encoding="utf-8", errors="replace")
            for path in sorted(drive_root.iterdir()) if path.is_file()
        )
        for required in (
            "TEST 25", "FULL DRIVE INDEX", "DRIVE-INDEX.jsonl",
            "DRIVE-REGISTER.csv", "GOOGLE SHEET", "file of record",
            "DRIVE-INDEX-RECEIPT.json", "DRIVE-INDEX-CURSOR.json",
            "DRIVE-REGISTER-SCHEMA.md", "validate_drive_register.py",
            "no more than 25", "checkpoint",
            "connector coverage gap", "item ID", "never store a password",
            "generation ID", "reopen", "malformed JSON", "duplicate IDs",
            "owned_or_created_by_me", "shared_with_me", "shared_by_me",
            "NOT SEEN THIS RUN — VERIFY", "SET WEEKLY REFRESH", "Sunday night",
            "exact local time", "time zone", "WEEKLY-DRIVE-REFRESH-PROMPT.md",
            "RUN DRIVE REFRESH NOW", "exactly one human register", "does not advance",
        ):
            if required.casefold() not in drive_text.casefold():
                failures.append("Drive Index starter lacks: " + required)
        for forbidden in (
            "stop after 25 items", "never complete Drive inventory",
            "Call this “First bounded batch”",
        ):
            if forbidden.casefold() in drive_text.casefold():
                failures.append("Drive Index starter retains obsolete limit: " + forbidden)
    linkedin_root = homework_root / "03-LinkedIn-Message-Assistant-OPTIONAL"
    if linkedin_root.is_dir():
        linkedin_required_files = {
            "SATURDAY-REVIEW-PROMPT.md", "LINKEDIN-TONE-AND-PRECEDENTS.md",
            "LINKEDIN-REPLY-QUEUE.md", "LINKEDIN-REVIEW-CURSOR.md",
            "LINKEDIN-INBOX-BATCH.md", "CONFIRMED-LINKEDIN-LEARNINGS.md",
        }
        for name in sorted(linkedin_required_files):
            if not (linkedin_root / name).is_file():
                failures.append("LinkedIn Message Assistant missing " + name)
        linkedin_text = "\n".join(
            path.read_text(encoding="utf-8", errors="replace")
            for path in sorted(linkedin_root.iterdir()) if path.is_file()
        )
        linkedin_flat = re.sub(r"\s+", " ", linkedin_text)
        for required in (
            "LINKEDIN-WEEKLY-001", "What local time every Saturday",
            "Focused and Other", "no more than 25", "checkpoint",
            "READY TO SEND", "NEEDS YOUR DECISION", "NO REPLY / SKIP",
            "SENT AS WRITTEN", "EDITED AND SENT", "KEEP FOR LATER",
            "manually press Send", "employee's confirmation",
            "SATURDAY-REVIEW-PROMPT.md", "LINKEDIN-REPLY-QUEUE.md",
            "must never open, read, click, control, or send through LinkedIn",
            "CONFIRMED-LINKEDIN-LEARNINGS.md", "explicitly approves",
            "correct or forget", "Never copy the full conversation",
        ):
            if required.casefold() not in linkedin_flat.casefold():
                failures.append("LinkedIn Message Assistant lacks: " + required)
        for forbidden in (
            "open LinkedIn automatically", "send automatically through LinkedIn",
            "Codex sends the reply", "scrape the LinkedIn inbox",
        ):
            if forbidden.casefold() in linkedin_text.casefold():
                failures.append("LinkedIn Message Assistant contains unsafe instruction: " + forbidden)
    for skill_id in sorted(APPROVED_SKILLS):
        skill_path = root / "packages/kairali/skills" / skill_id / "SKILL.md"
        if skill_path.is_file():
            skill_text = skill_path.read_text(encoding="utf-8")
            for required in ("explicitly invoked", "Gate 0", "Never invent"):
                if required.casefold() not in skill_text.casefold():
                    failures.append(skill_id + " lacks governed skill boundary: " + required)

    workflow_path = root / ".github/workflows/validate.yml"
    if workflow_path.is_file():
        workflow = workflow_path.read_text(encoding="utf-8")
        failures.extend(validation_workflow_failures(workflow))
    deploy_workflow_path = root / ".github/workflows/portal-deploy.yml"
    if deploy_workflow_path.is_file():
        deploy_workflow = deploy_workflow_path.read_text(encoding="utf-8")
        failures.extend(portal_deploy_workflow_failures(deploy_workflow))
    workflows_root = root / ".github/workflows"
    if workflows_root.is_dir():
        governed_names = {Path(relative).name for relative in GOVERNED_WORKFLOW_SHA256}
        actual_names = {
            path.name for path in workflows_root.iterdir()
            if path.is_file() and path.suffix.casefold() in {".yml", ".yaml"}
        }
        if actual_names != governed_names:
            failures.append(
                "workflow inventory differs from the governed set: " +
                ", ".join(sorted(actual_names))
            )
        for other_workflow in sorted(workflows_root.iterdir()):
            if not other_workflow.is_file() or other_workflow.suffix.casefold() not in {".yml", ".yaml"}:
                continue
            workflow_source = other_workflow.read_text(encoding="utf-8", errors="replace")
            failures.extend(action_pin_failures(workflow_source, other_workflow.name))
            active_lines = [
                line for line in workflow_source.splitlines()
                if line.strip() and not line.strip().startswith("#")
            ]
            if other_workflow != deploy_workflow_path:
                alternate = [
                    command for _line, command in workflow_run_commands(workflow_source)
                    if vercel_production_kind(command)
                ]
                if alternate:
                    failures.append(
                        "Vercel production command exists outside portal-deploy.yml: " +
                        other_workflow.name
                    )
            if other_workflow.name == "portal.yml":
                commands = [command for _line, command in workflow_run_commands(workflow_source)]
                if commands.count("npm audit --omit=dev") != 1:
                    failures.append("portal validation workflow requires one production dependency audit")
            if any(re.search(r"\buses:\s*[^#\n]*vercel", line, flags=re.I) for line in active_lines):
                failures.append("workflow uses an ungoverned Vercel deployment action: " + other_workflow.name)
    for relative, expected_hash in GOVERNED_WORKFLOW_SHA256.items():
        workflow_file = root / relative
        if workflow_file.is_file() and sha256(workflow_file) != expected_hash:
            failures.append(
                "critical workflow differs from its governed canonical SHA-256: " + relative
            )
    gitignore_path = root / ".gitignore"
    if gitignore_path.is_file() and "portal/next-env.d.ts" not in gitignore_path.read_text(encoding="utf-8"):
        failures.append(".gitignore does not exclude generated portal/next-env.d.ts")
    codeowners_path = root / ".github/CODEOWNERS"
    if codeowners_path.is_file() and "@AbhilashKairali" not in codeowners_path.read_text(encoding="utf-8"):
        failures.append("CODEOWNERS does not name the owner")
    changelog_path = root / "CHANGELOG.md"
    if changelog_path.is_file() and ("[" + version + "]") not in changelog_path.read_text(encoding="utf-8"):
        failures.append("CHANGELOG lacks the release version")

    control_doc_path = root / "docs/GOVERNED-CAPABILITIES-AND-FLEET.md"
    if control_doc_path.is_file():
        control_doc = control_doc_path.read_text(encoding="utf-8")
        for required in (
            "expected-state", "PROPOSE", "LATER", "REJECT", "designated supervisor",
            "first calendar day", "10:00 AM", "BACKWARD_COMPATIBLE",
            "daily-email-triage", "no more than 25", "LOCAL_BUILD_ONLY",
            "Assignment is not execution", "Artifact upload", "External record write",
            "never truncate",
        ):
            if required.casefold() not in control_doc.casefold():
                failures.append("governed control-plane guide lacks: " + required)
    agent_rules_path = root / "core/AGENT-RULES.md"
    operating_loop_path = root / "core/OPERATING-LOOP.md"
    if agent_rules_path.is_file() and operating_loop_path.is_file() and control_plane_version:
        batch_contract = re.sub(r"\s+", " ", (
            agent_rules_path.read_text(encoding="utf-8") + "\n" +
            operating_loop_path.read_text(encoding="utf-8") + "\n" +
            (root / "core/GATES-SHARED.md").read_text(encoding="utf-8")
        ))
        for required in (
            "independent batch unit", "entries embedded", "Assignment intake",
            "Item execution", "External record write", "Never split, truncate",
            "mode.json", "SUSPENDED", "push back politely",
            "refuse only the conflicting part", "nearest compliant",
            "Do not scold", "unrelated safe work",
            ".ai-human/control/gate-profile.json", "not universal",
            "current authoritative", "historical charts", "compliance owner",
            "separate worker", "user relationship",
        ):
            if required.casefold() not in batch_contract.casefold():
                failures.append("core batch-unit contract lacks: " + required)
    lifecycle_test_path = root / "tests/test_lifecycle.py"
    if lifecycle_test_path.is_file() and control_plane_version:
        lifecycle_tests = lifecycle_test_path.read_text(encoding="utf-8")
        for required in (
            "test_session_lease_rejects_second_writer_and_stale_state_commit",
            "test_existing_idle_worker_can_receive_governed_control_configuration",
            "test_state_commit_rolls_back_when_live_task_is_incoherent",
            "test_capability_requires_user_proposal_local_gates_and_designated_supervisor",
            "test_gate_profile_must_match_exact_entity_and_have_no_unknowns",
            "test_company_gate_profiles_are_isolated_and_tamper_evident",
            "test_historical_material_is_labelled_as_a_lead_not_gate_authority",
            "test_capability_cannot_replace_the_worker_local_gate_profile",
            "test_homework_adoption_keeps_task_locks_separate_from_entity_gate_zero",
            "test_completion_requires_the_ledger_and_detailed_passing_evidence",
            "test_weak_completion_evidence_placeholders_are_rejected",
            "test_table_content_with_three_hyphens_is_not_dropped",
            "test_gate_profile_migration_archives_legacy_gate_zero_and_preserves_work_locks",
            "test_monthly_automatic_update_runs_at_ten_local_and_defers_live_task",
            "test_setup_migration_offer_is_a_safe_automatic_update_deferral",
            "test_fleet_pilots_email_then_isolates_a_general_worker_failure",
            "test_automatic_update_failure_restores_backup_and_records_failed_receipt",
            "test_timezone_id_validation_does_not_require_an_os_timezone_database",
            "test_automatic_update_requires_scheduler_supplied_worker_local_time",
            "test_one_artifact_with_150_embedded_issues_is_one_batch_unit",
            "test_separate_github_issue_writes_remain_capped_at_25",
            "test_suspend_resume_and_verification_disable_managed_work_reversibly",
            "test_uninstall_preserves_a_preexisting_project_agents_file",
            "test_uninstall_recovers_legacy_installs_without_adapter_metadata",
            "test_suspended_worker_defers_direct_and_fleet_automatic_updates",
            "test_reusable_and_kairali_editions_are_separate_complete_downloads",
            "test_kairali_uses_canonical_abhilash_spelling_and_neutral_guards_both_variants",
            "test_beginner_guides_cover_mac_windows_extraction_and_local_source_copy",
            "test_ci_validator_selects_candidate_or_public_lane_from_manifest",
            "test_portal_production_deploy_requires_public_release_and_no_candidate_assets",
            "test_active_mode_pushback_is_polite_narrow_and_actionable",
            "test_quarterly_improvement_choice_requires_a_lease_and_decline_is_complete",
            "test_quarterly_schedule_truth_pause_edit_resume_and_remove_fail_closed",
            "test_quarterly_run_detects_repetition_stale_conflict_and_never_activates",
            "test_quarterly_improvement_state_survives_a_managed_update",
            "test_reference_pack_cannot_enter_host_skill_discovery_paths",
            "test_component_commands_reject_an_unpinned_repository_before_network",
            "test_persistent_decisions_survive_run_retention_and_ignore_caller_clock",
            "test_public_edition_runtime_matches_the_current_release_source",
            "test_fleet_and_worker_updates_reject_repository_rebinding",
            "test_scheduled_improvement_run_rejects_a_fictional_clock",
            "test_reference_pack_guard_validator_binds_the_effect_target",
            "test_supervisor_can_recover_an_abandoned_lease_after_acknowledged_edits",
        ):
            if required not in lifecycle_tests:
                failures.append("lifecycle tests lack: " + required)

    improvement_contract_path = root / "core/QUARTERLY-IMPROVEMENT.md"
    if improvement_contract_path.is_file():
        improvement_contract = re.sub(
            r"\s+", " ", improvement_contract_path.read_text(encoding="utf-8")
        )
        for required in (
            "DECLINE", "visible Scheduled card", "next run", "MISSED_RUN_RECOVERY",
            "approved source categories", "untrusted content", "ignore its instructions",
            "personal data", "REVIEW_REQUIRED", "NOT_ACTIVATED", "external_effect: NONE",
            "PROPOSE / LATER / REJECT", ".ai-human/improvement/", "superseding", "forget",
        ):
            if required.casefold() not in improvement_contract.casefold():
                failures.append("quarterly improvement contract lacks: " + required)

    reusable_text = "\n".join(
        (root / relative).read_text(encoding="utf-8", errors="replace")
        for relative in (
            "editions/reusable/START-HERE.md",
            "editions/reusable/INSTALL-DISABLE-REMOVE.md",
        )
        if (root / relative).is_file()
    )
    for forbidden in ("Kairali", "Abhilash", "Abilash", "Ambuj"):
        if forbidden.casefold() in reusable_text.casefold():
            failures.append("reusable edition contains company-specific text: " + forbidden)
    for required in (
        "exact legal entity", "operating unit", "jurisdictions", "user relationship",
        "compliance owner", "current authoritative", "historical charts",
        "separate working folders", "Gate 0 profile",
    ):
        if required.casefold() not in reusable_text.casefold():
            failures.append("reusable Setup Helper lacks Gate 0 setup requirement: " + required)
    kairali_edition_text = "\n".join(
        (root / relative).read_text(encoding="utf-8", errors="replace")
        for relative in (
            "editions/kairali/START-HERE.md",
            "editions/kairali/INSTALL-DISABLE-REMOVE.md",
        )
        if (root / relative).is_file()
    )
    if re.search(r"\bAbilash\b", kairali_edition_text):
        failures.append("Kairali edition uses the legacy owner-name spelling")
    for required in (
        "Install in five visible steps", "DONE WHEN", "SUSPENDED", "ACTIVE",
        "UNINSTALLED", "Troubleshooting", "revoke", "Mac", "Windows", "Extract All",
    ):
        if required.casefold() not in reusable_text.casefold():
            failures.append("reusable edition lifecycle guide lacks: " + required)
        if required.casefold() not in kairali_edition_text.casefold():
            failures.append("Kairali edition lifecycle guide lacks: " + required)

    secret_markers = {
        "GitHub token": "gh" + "p_",
        "OpenAI project key": "sk-" + "proj-",
        "Google API key": "AIza" + "Sy",
        "private key": "BEGIN " + "PRIVATE KEY",
    }
    absolute_patterns = {
        "Mac home path": re.compile(r"/Users/[A-Za-z0-9._-]+/"),
        "Windows home path": re.compile(r"[A-Za-z]:\\\\Users\\\\[^\\\s]+", re.I),
    }
    for path, content in text_files(root):
        relative = path.relative_to(root).as_posix()
        if content is None:
            if relative in ALLOWED_BINARY_FILES and path.stat().st_size <= 25 * 1024 * 1024:
                continue
            failures.append("unapproved binary or oversized file in release: " + relative)
            continue
        for label, marker in secret_markers.items():
            if marker in content:
                failures.append(label + " marker found in " + relative)
        for label, pattern in absolute_patterns.items():
            if pattern.search(content):
                failures.append(label + " found in " + relative)
        if path.name.endswith((".write-temp", ".update-temp", ".build-temp")):
            failures.append("temporary file in release: " + relative)

    return failures


def main():
    parser = argparse.ArgumentParser(description="Validate an AI-Human release or local candidate")
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--candidate", action="store_true")
    parser.add_argument(
        "--ci", action="store_true",
        help="select the candidate or public validation lane from release-manifest.json",
    )
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if args.candidate and args.ci:
        parser.error("--candidate and --ci are mutually exclusive")
    candidate = args.candidate
    if args.ci:
        try:
            manifest = read_json(root / "release-manifest.json")
        except Exception:
            manifest = {}
        candidate = (
            manifest.get("approval_status") == "LOCAL_BUILD_ONLY"
            and manifest.get("release_status") == "LOCAL_BUILD_ONLY"
        )
    failures = validate(root, candidate=candidate)
    if failures:
        label = "LOCAL CANDIDATE" if candidate else "PUBLIC RELEASE"
        print("AI-HUMAN " + label + " VALIDATION: FAIL")
        for failure in failures:
            print("- " + failure)
        return 1
    manifest = read_json(root / "release-manifest.json")
    label = "LOCAL CANDIDATE" if candidate else "PUBLIC RELEASE"
    print("AI-HUMAN " + label + " VALIDATION: PASS")
    print("- version: " + manifest["version"])
    print("- managed files: " + str(len(manifest["managed_files"])))
    components = read_json(root / "component-manifest.json")
    print("- component catalog entries: " + str(len(components["components"])))
    print("- local company and user state: excluded")
    print("- secret and absolute-path scan: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
