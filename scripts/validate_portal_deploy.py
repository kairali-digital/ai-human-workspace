#!/usr/bin/env python3
"""Refuse a production portal deploy unless release state and assets are public."""

import argparse
import json
from pathlib import Path


PUBLIC_APPROVAL = "APPROVED_BY_OWNER"
PUBLIC_RELEASE = "RELEASED"
PORTAL_FILES = (
    "portal/app/page.tsx",
    "portal/content/site-data.ts",
    "portal/content/download-manifest.json",
)
CANDIDATE_MARKERS = (
    "LOCAL_BUILD_ONLY",
    "LOCAL-CANDIDATE",
    "Local candidate - not live",
)


def reject_duplicate_json_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON key: " + repr(key))
        value[key] = item
    return value


def read_json(path):
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_json_keys,
        )
    except Exception as error:
        raise ValueError("cannot read " + str(path) + ": " + str(error)) from error


def validate(root):
    failures = []
    manifests = (
        ("release", root / "release-manifest.json"),
        ("component", root / "component-manifest.json"),
    )
    for label, path in manifests:
        if not path.is_file():
            failures.append(label + " manifest is missing")
            continue
        try:
            manifest = read_json(path)
        except ValueError as error:
            failures.append(str(error))
            continue
        approval = manifest.get("approval_status")
        release = manifest.get("release_status")
        if approval != PUBLIC_APPROVAL:
            failures.append(
                label + " approval_status is " + repr(approval) +
                "; production requires " + PUBLIC_APPROVAL
            )
        if release != PUBLIC_RELEASE:
            failures.append(
                label + " release_status is " + repr(release) +
                "; production requires " + PUBLIC_RELEASE
            )

    visible = []
    for relative in PORTAL_FILES:
        path = root / relative
        if not path.is_file():
            failures.append("production portal input is missing: " + relative)
            continue
        visible.append((relative, path.read_text(encoding="utf-8", errors="replace")))
    for relative, content in visible:
        folded = content.casefold()
        for marker in CANDIDATE_MARKERS:
            if marker.casefold() in folded:
                failures.append(
                    "candidate-only marker remains in production portal input " +
                    relative + ": " + marker
                )
    return failures


def main():
    parser = argparse.ArgumentParser(description="Validate an approved production portal deploy")
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    failures = validate(root)
    if failures:
        print("PORTAL PRODUCTION RELEASE GATE: FAIL")
        for failure in failures:
            print("- " + failure)
        return 1
    print("PORTAL PRODUCTION RELEASE GATE: PASS")
    print("- release and component status: owner-approved and RELEASED")
    print("- portal inputs: no local-candidate assets or labels")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
