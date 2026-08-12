#!/usr/bin/env python3
"""Fail closed when a public AI-Human release is incomplete or unsafe."""

import hashlib
import json
import re
import sys
from pathlib import Path


SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
REPOSITORY = "kairali-digital/ai-human-workspace"
REQUIRED_FILES = {
    ".github/CODEOWNERS",
    ".github/pull_request_template.md",
    ".github/workflows/validate.yml",
    ".gitattributes",
    ".gitignore",
    "AGENTS.md",
    "CHANGELOG.md",
    "README.md",
    "company-profiles/kairali/PROFILE.md",
    "company-profiles/kairali/SETUP-HELPER.md",
    "company-profiles/template/COMPANY-PROFILE.md",
    "company-profiles/template/SETUP-HELPER-TEMPLATE.md",
    "core/AGENT-RULES.md",
    "core/AI-HUMAN.md",
    "core/GATES-SHARED.md",
    "core/OPERATING-LOOP.md",
    "core/SESSION-END.md",
    "core/SESSION-START.md",
    "core/TOOLBOX-TEMPLATE.md",
    "core/VERSION",
    "docs/BEGINNER-SETUP.md",
    "docs/MULTI-COMPANY-ROLLOUT.md",
    "docs/RELEASE-PROCESS.md",
    "docs/SECURITY-AND-DATA-BOUNDARIES.md",
    "docs/TECHNICAL-SETUP.md",
    "docs/UPDATES-ROLLBACK-REMOVAL.md",
    "release-manifest.json",
    "roles/ROLE-TEMPLATE.md",
    "scripts/ai_human.py",
    "scripts/build_release.py",
    "scripts/validate_release.py",
    "tests/test_lifecycle.py",
}
REQUIRED_TARGETS = {
    ".ai-human/system/AI-HUMAN.md",
    ".ai-human/system/AGENT-RULES.md",
    ".ai-human/system/OPERATING-LOOP.md",
    ".ai-human/system/GATES-SHARED.md",
    ".ai-human/system/SESSION-START.md",
    ".ai-human/system/SESSION-END.md",
    ".ai-human/VERSION",
    ".ai-human/bin/ai_human.py",
}
LOCAL_STATE = {
    "AGENTS.md", "CLAUDE.md", "AI-HUMAN.md", "COMPANY.md", "PARAMETERS.md",
    "ROLE.md", "MASTER_CURSOR.md", "OPEN_REGISTER.md", "TODAY.md",
    "COMPLETED_LEDGER.md", "EVIDENCE_LOG.md", "FACTS.md", "DECISIONS.md",
    "TOOLBOX.md", "GATES.md", "AUTOMATIONS.md", "START-HERE.md",
    "READ-ME-FIRST.txt",
}
PARAMETERS = {
    "{{COMPANY_NAME}}", "{{COMPANY_OWNER}}", "{{OWNER_NAME}}",
    "{{WORKER_NAME}}", "{{ROLE_NAME}}", "{{PURPOSE}}", "{{BRAIN}}",
    "{{TASK_SELECTION}}", "{{BATCH_CAP}}",
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_relative(value):
    path = Path(value)
    return bool(value) and not path.is_absolute() and ".." not in path.parts


def text_files(root):
    ignored = {".git", "__pycache__", "dist"}
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


def validate(root):
    failures = []

    for relative in sorted(REQUIRED_FILES):
        path = root / relative
        if not path.is_file() or path.stat().st_size == 0:
            failures.append("missing or empty required file: " + relative)

    manifest_path = root / "release-manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        manifest = {}
        failures.append("invalid release-manifest.json: " + str(exc))

    version = str(manifest.get("version", ""))
    if not SEMVER.fullmatch(version):
        failures.append("manifest version is not semantic: " + repr(version))
    version_path = root / "core/VERSION"
    if version_path.is_file() and version_path.read_text(encoding="utf-8").strip() != version:
        failures.append("core/VERSION does not match the manifest")
    if manifest.get("schema") != "ai-human.workspace-release/v1":
        failures.append("unsupported manifest schema")
    if manifest.get("repository") != REPOSITORY:
        failures.append("manifest repository must be " + REPOSITORY)
    if manifest.get("approval_status") != "APPROVED_BY_OWNER":
        failures.append("release is not owner-approved")

    targets = set()
    for index, record in enumerate(manifest.get("managed_files") or []):
        source = str(record.get("source", ""))
        target = str(record.get("target", ""))
        if not safe_relative(source):
            failures.append("unsafe managed source at index " + str(index))
            continue
        if not safe_relative(target) or not target.replace("\\", "/").startswith(".ai-human/"):
            failures.append("unsafe managed target at index " + str(index))
            continue
        if target in targets:
            failures.append("duplicate managed target: " + target)
        targets.add(target)
        path = root / source
        if not path.is_file():
            failures.append("managed source missing: " + source)
        elif record.get("sha256") != sha256(path):
            failures.append("managed hash mismatch: " + source)
    for target in sorted(REQUIRED_TARGETS - targets):
        failures.append("required managed target missing: " + target)
    for target in sorted(targets.intersection(LOCAL_STATE)):
        failures.append("release tries to manage local state: " + target)
    never_managed = set(manifest.get("never_managed") or [])
    for local in sorted(LOCAL_STATE - never_managed):
        failures.append("local state absent from never_managed: " + local)

    for local in sorted(LOCAL_STATE):
        if local == "AGENTS.md":
            continue
        if (root / local).exists():
            failures.append("live employee state is present at repository root: " + local)

    core_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted((root / "core").glob("*")) if path.is_file()
    )
    for company_word in ("Kairali", "Abhilash", "Ambuj"):
        if company_word.casefold() in core_text.casefold():
            failures.append("company-specific name in neutral core: " + company_word)

    starter_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted((root / "starter").glob("*")) if path.is_file()
    )
    for parameter in sorted(PARAMETERS):
        if parameter not in starter_text:
            failures.append("starter parameter is unused: " + parameter)

    beginner_path = root / "docs/BEGINNER-SETUP.md"
    helper_path = root / "company-profiles/kairali/SETUP-HELPER.md"
    if beginner_path.is_file() and helper_path.is_file():
        beginner = beginner_path.read_text(encoding="utf-8")
        helper = helper_path.read_text(encoding="utf-8")
        if not prompt_block(beginner):
            failures.append("beginner guide lacks the complete Kairali Setup Helper prompt")
        elif prompt_block(beginner) != prompt_block(helper):
            failures.append("beginner and Kairali profile Setup Helper prompts differ")
        for required in ("DONE WHEN", "check what is already installed", "Never ask me to use Terminal", "Never choose Full access"):
            if required.casefold() not in beginner.casefold():
                failures.append("beginner guide lacks required phrase: " + required)

    workflow_path = root / ".github/workflows/validate.yml"
    if workflow_path.is_file():
        workflow = workflow_path.read_text(encoding="utf-8")
        for required in ("pull_request:", "validate_release.py", "unittest", "gitleaks"):
            if required.casefold() not in workflow.casefold():
                failures.append("validation workflow lacks: " + required)
    codeowners_path = root / ".github/CODEOWNERS"
    if codeowners_path.is_file() and "@AbhilashKairali" not in codeowners_path.read_text(encoding="utf-8"):
        failures.append("CODEOWNERS does not name the owner")
    changelog_path = root / "CHANGELOG.md"
    if changelog_path.is_file() and ("[" + version + "]") not in changelog_path.read_text(encoding="utf-8"):
        failures.append("CHANGELOG lacks the release version")

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
        relative = str(path.relative_to(root))
        if content is None:
            failures.append("binary or oversized file in release: " + relative)
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
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    failures = validate(root)
    if failures:
        print("AI-HUMAN PUBLIC RELEASE VALIDATION: FAIL")
        for failure in failures:
            print("- " + failure)
        return 1
    manifest = json.loads((root / "release-manifest.json").read_text(encoding="utf-8"))
    print("AI-HUMAN PUBLIC RELEASE VALIDATION: PASS")
    print("- version: " + manifest["version"])
    print("- managed files: " + str(len(manifest["managed_files"])))
    print("- local company and employee state: excluded")
    print("- secret and absolute-path scan: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
