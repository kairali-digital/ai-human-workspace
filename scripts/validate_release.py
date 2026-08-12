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
    "component-manifest.json",
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
    "docs/COMPONENTS.md",
    "docs/MULTI-COMPANY-ROLLOUT.md",
    "docs/RELEASE-PROCESS.md",
    "docs/SECURITY-AND-DATA-BOUNDARIES.md",
    "docs/TECHNICAL-SETUP.md",
    "docs/UPDATES-ROLLBACK-REMOVAL.md",
    "release-manifest.json",
    "packages/kairali/README.md",
    "packages/kairali/homework/COPY-PASTE-PROMPTS.txt",
    "packages/kairali/homework/EVERYONE-ELSE-AI-HUMAN-HOMEWORK-GUIDE.docx",
    "packages/kairali/homework/EVERYONE-ELSE-AI-HUMAN-HOMEWORK-GUIDE.pdf",
    "packages/kairali/homework/EVERYONE-ELSE-AI-HUMAN-HOMEWORK-VIDEO.mp4",
    "packages/kairali/homework/START-HERE.md",
    "packages/kairali/people/ALL-EMPLOYEES.md",
    "packages/kairali/people/SETUP-HELPER.md",
    "packages/kairali/skills/kairali-akshar-marketing-science/SKILL.md",
    "packages/kairali/skills/kairali-rahul-sales-system/SKILL.md",
    "roles/ROLE-TEMPLATE.md",
    "scripts/ai_human.py",
    "scripts/build_release.py",
    "scripts/validate_release.py",
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
    "packages/kairali/homework/EVERYONE-ELSE-AI-HUMAN-HOMEWORK-VIDEO.mp4",
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

    component_path = root / "component-manifest.json"
    try:
        component_manifest = json.loads(component_path.read_text(encoding="utf-8"))
    except Exception as exc:
        component_manifest = {}
        failures.append("invalid component-manifest.json: " + str(exc))
    if component_manifest.get("schema") != "ai-human.component-release/v1":
        failures.append("unsupported component manifest schema")
    if component_manifest.get("version") != version:
        failures.append("component manifest version differs from release version")
    if component_manifest.get("repository") != REPOSITORY:
        failures.append("component manifest repository must be " + REPOSITORY)
    if component_manifest.get("approval_status") != "APPROVED_BY_OWNER":
        failures.append("components are not owner-approved")
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
        component_root = root / source
        if component_root.is_symlink():
            failures.append("component source may not be a symbolic link: " + source)
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

    role_root = root / "packages/kairali/people"
    if role_root.is_dir():
        actual_roles = {path.name for path in role_root.glob("*.md")}
        if actual_roles != EXPECTED_ROLE_FILES:
            failures.append("Kairali people-prompt set is incomplete or contains an unexpected file")
    homework_root = root / "packages/kairali/homework/AI-HUMAN-STARTERS"
    expected_homework = {
        "01-Email-Triage-AI-Human",
        "02-Drive-Inventory-AI-Human",
        "03-LinkedIn-Draft-AI-Human-OPTIONAL",
    }
    if homework_root.is_dir():
        actual_homework = {path.name for path in homework_root.iterdir() if path.is_dir()}
        if actual_homework != expected_homework:
            failures.append("homework starter set is incomplete or unexpected")
        for folder in sorted(expected_homework):
            for required in ("AGENTS.md", "MASTER_CURSOR.md", "OPEN_REGISTER.md", "START-HERE.md", "GATES.md"):
                if not (homework_root / folder / required).is_file():
                    failures.append("homework starter missing " + folder + "/" + required)

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
        approved_prompt = prompt_block(helper)
        packaged_helper_path = root / "packages/kairali/people/SETUP-HELPER.md"
        if packaged_helper_path.is_file() and prompt_block(packaged_helper_path.read_text(encoding="utf-8")) != approved_prompt:
            failures.append("packaged Kairali Setup Helper prompt differs from the approved profile")
        for folder in (
            "01-Email-Triage-AI-Human",
            "02-Drive-Inventory-AI-Human",
            "03-LinkedIn-Draft-AI-Human-OPTIONAL",
        ):
            for name in ("START-HERE.md", "READ-ME-FIRST.txt"):
                path = root / "packages/kairali/homework/AI-HUMAN-STARTERS" / folder / name
                if path.is_file() and approved_prompt not in path.read_text(encoding="utf-8"):
                    failures.append("homework file lacks exact approved Setup Helper prompt: " + folder + "/" + name)

    all_employees_path = root / "packages/kairali/people/ALL-EMPLOYEES.md"
    if all_employees_path.is_file():
        all_employees = all_employees_path.read_text(encoding="utf-8")
        for required in ("Email Triage", "Drive Inventory", "LinkedIn Draft", "homework/START-HERE.md"):
            if required.casefold() not in all_employees.casefold():
                failures.append("all-employee prompt lacks fallback route: " + required)
    homework_prompts_path = root / "packages/kairali/homework/COPY-PASTE-PROMPTS.txt"
    if homework_prompts_path.is_file():
        homework_prompts = homework_prompts_path.read_text(encoding="utf-8")
        for required in (
            "EMAIL-HW-001", "DRIVE-HW-001", "LINKEDIN-BONUS-001",
            "No email was sent", "metadata only", "DRAFT - NOT PUBLISHED",
        ):
            if required.casefold() not in homework_prompts.casefold():
                failures.append("homework prompts lack: " + required)
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
    components = json.loads((root / "component-manifest.json").read_text(encoding="utf-8"))
    print("- approved components: " + str(len(components["components"])))
    print("- local company and employee state: excluded")
    print("- secret and absolute-path scan: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
