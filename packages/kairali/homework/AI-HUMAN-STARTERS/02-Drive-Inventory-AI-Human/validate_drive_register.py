#!/usr/bin/env python3
"""Fail-closed validator for generated Drive Inventory register artifacts."""

import argparse
import csv
import json
import re
import sys
from pathlib import Path


FIELDS = (
    "item_id", "name", "file_type", "owned_or_created_by_me", "shared_with_me",
    "shared_by_me", "modified_time", "parent_or_location", "sharing_status",
    "web_link", "source_scope", "first_indexed_at_utc", "last_seen_at_utc",
    "indexed_at_utc", "generation_id", "review_note",
)
RELATIONSHIPS = (
    "owned_or_created_by_me", "shared_with_me", "shared_by_me",
)
SCOPES = ("owned_or_created_by_me", "shared_with_me", "shared_by_me", "shared_drives")
UNCHANGED = (
    "No Drive file content was opened or downloaded, and no Drive item was created, "
    "edited, renamed, moved, shared, unshared, deleted or organized."
)


def reject_duplicate_json_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON key: " + repr(key))
        value[key] = item
    return value


def load_json(path):
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicate_json_keys,
    )


def human_cell(value):
    value = str(value)
    if value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def relation(value):
    if value is True:
        return "TRUE"
    if value is False:
        return "FALSE"
    if value == "UNKNOWN":
        return "UNKNOWN"
    raise ValueError("relationship flags must be true, false or UNKNOWN")


def validate(root):
    failures = []
    paths = {
        "jsonl": root / "DRIVE-INDEX.jsonl",
        "csv": root / "DRIVE-REGISTER.csv",
        "summary": root / "DRIVE-INDEX.md",
        "receipt": root / "DRIVE-INDEX-RECEIPT.json",
        "cursor": root / "DRIVE-INDEX-CURSOR.json",
    }
    for label, path in paths.items():
        if not path.is_file() or path.stat().st_size == 0:
            failures.append(label + " file is missing or empty: " + path.name)
    if failures:
        return failures

    records = []
    try:
        for number, line in enumerate(paths["jsonl"].read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                failures.append("JSONL contains a blank line at " + str(number))
                continue
            record = json.loads(line, object_pairs_hook=reject_duplicate_json_keys)
            missing = [field for field in FIELDS if field not in record]
            if missing:
                failures.append("JSONL line " + str(number) + " lacks: " + ", ".join(missing))
                continue
            for field in FIELDS:
                if record[field] is None or (
                    isinstance(record[field], str) and not record[field].strip()
                ):
                    failures.append(
                        "JSONL line " + str(number) + " has an empty required field: " + field
                    )
            for field in RELATIONSHIPS:
                try:
                    relation(record[field])
                except ValueError as exc:
                    failures.append("JSONL line " + str(number) + " " + str(exc))
            records.append(record)
    except Exception as exc:
        failures.append("JSONL cannot be read: " + str(exc))
        return failures
    if not records:
        failures.append("JSONL has no item records")
        return failures

    ids = [str(record["item_id"]) for record in records]
    if any(not item_id.strip() for item_id in ids):
        failures.append("JSONL contains an empty item_id")
    if len(set(ids)) != len(ids):
        failures.append("JSONL contains duplicate item_id values")
    generations = {str(record["generation_id"]) for record in records}
    if len(generations) != 1:
        failures.append("JSONL records do not share one generation_id")
    generation = next(iter(generations)) if generations else ""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,99}", generation):
        failures.append("generation_id is missing or unsafe")

    try:
        with paths["csv"].open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if tuple(reader.fieldnames or ()) != FIELDS:
                failures.append("CSV columns do not exactly match DRIVE-REGISTER-SCHEMA.md")
            csv_rows = list(reader)
        if len(csv_rows) != len(records):
            failures.append("CSV and JSONL row counts disagree")
        csv_by_id = {row.get("item_id", ""): row for row in csv_rows}
        if len(csv_by_id) != len(csv_rows):
            failures.append("CSV contains empty or duplicate item_id values")
        for record in records:
            row = csv_by_id.get(str(record["item_id"]))
            if row is None:
                failures.append("CSV lacks item_id " + str(record["item_id"]))
                continue
            for field in FIELDS:
                expected = relation(record[field]) if field in RELATIONSHIPS else human_cell(record[field])
                if row.get(field) != expected:
                    failures.append("CSV disagrees for item_id " + str(record["item_id"]) + " field " + field)
                    break
    except Exception as exc:
        failures.append("CSV cannot be read: " + str(exc))

    try:
        receipt = load_json(paths["receipt"])
        cursor = load_json(paths["cursor"])
    except Exception as exc:
        failures.append("receipt or cursor cannot be read: " + str(exc))
        return failures

    true_counts = {
        field: sum(record[field] is True for record in records) for field in RELATIONSHIPS
    }
    calculated = {
        **true_counts,
        "relationship_overlap_items": sum(
            sum(record[field] is True for field in RELATIONSHIPS) > 1 for record in records
        ),
        "relationship_unknown_items": sum(
            any(record[field] == "UNKNOWN" for field in RELATIONSHIPS) for record in records
        ),
        "unique_items": len(records),
    }
    if receipt.get("generation_id") != generation or cursor.get("generation_id") != generation:
        failures.append("JSONL, receipt and cursor generation IDs disagree")
    for key, value in calculated.items():
        if receipt.get("counts", {}).get(key) != value:
            failures.append("receipt count disagrees: " + key)
    if cursor.get("unique_items") != len(records):
        failures.append("cursor unique_items disagrees with JSONL")
    mode = receipt.get("mode")
    if mode not in {"TEST 25", "FULL DRIVE INDEX"} or cursor.get("mode") != mode:
        failures.append("receipt and cursor must share a valid mode")
    if mode == "TEST 25":
        if len(records) > 25 or receipt.get("status") != "TEST 25 COMPLETE — FULL DRIVE NOT INDEXED":
            failures.append("TEST 25 exceeds 25 rows or lacks the incomplete-full-drive label")
    if mode == "FULL DRIVE INDEX":
        if receipt.get("status") != "FULL DRIVE INDEX COMPLETE":
            failures.append("full mode lacks FULL DRIVE INDEX COMPLETE status")
        coverage = receipt.get("source_scopes", {})
        for scope in SCOPES:
            if coverage.get(scope) not in {"END", "UNKNOWN — CONNECTOR COVERAGE GAP"}:
                failures.append("full mode lacks terminal coverage for " + scope)

    human_register = receipt.get("human_register")
    if human_register not in {"CSV", "GOOGLE_SHEET"}:
        failures.append("human_register must be CSV or GOOGLE_SHEET")
    if human_register == "GOOGLE_SHEET":
        if not re.match(r"^https://docs\.google\.com/spreadsheets/d/", str(receipt.get("google_sheet_url", ""))):
            failures.append("Google Sheet mode lacks a resolved spreadsheet URL")
        if receipt.get("google_sheet_generation_id") != generation:
            failures.append("Google Sheet generation ID was not read back")
        if receipt.get("google_sheet_row_count") != len(records):
            failures.append("Google Sheet row count was not read back or disagrees")
        if not receipt.get("human_register_verified_utc"):
            failures.append("Google Sheet mode lacks readback time")

    serialized_cursor = json.dumps(cursor, sort_keys=True).casefold()
    for forbidden in ("password", "one-time code", "access_token", "refresh_token", "secret"):
        if forbidden in serialized_cursor:
            failures.append("cursor contains a forbidden secret field or value: " + forbidden)
    summary = paths["summary"].read_text(encoding="utf-8")
    summary_counts = (
        "Unique items: " + str(calculated["unique_items"]),
        "Owned or created by me: " + str(calculated["owned_or_created_by_me"]),
        "Shared with me: " + str(calculated["shared_with_me"]),
        "Shared by me: " + str(calculated["shared_by_me"]),
        "Relationship overlap items: " + str(calculated["relationship_overlap_items"]),
        "Relationship unknown items: " + str(calculated["relationship_unknown_items"]),
    )
    for required in (generation, "Mode: " + str(mode), *summary_counts, UNCHANGED):
        if required not in summary:
            failures.append("summary lacks required readback: " + required)
    return failures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    failures = validate(Path(args.root).expanduser().resolve())
    if failures:
        print("DRIVE REGISTER VALIDATION: FAIL")
        for failure in failures:
            print("- " + failure)
        return 1
    print("DRIVE REGISTER VALIDATION: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
