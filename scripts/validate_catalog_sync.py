#!/usr/bin/env python3
"""Validate that generated catalog structure matches the final taxonomy CSV."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "method" / "prompt_taxonomy_final_29_patterns.csv"
RAW_DATASET_PATH = ROOT / "method" / "master_raw_dataset.csv"
JSON_PATH = ROOT / "catalog" / "patterns.json"

CATEGORY_TO_ENUM = {
    "In-context Learning": "IN_CONTEXT_LEARNING",
    "Reasoning": "REASONING",
    "Output Control": "OUTPUT_CONTROL",
    "Context Control": "CONTEXT_CONTROL",
    "Meta-Directives": "META_DIRECTIVES",
}
COMPONENT_TO_ENUM = {
    "Profile/Role": "PROFILE_ROLE",
    "Directive": "DIRECTIVE",
    "Context": "CONTEXT",
    "Procedural Steps": "PROCEDURAL_STEPS",
    "Examples": "EXAMPLES",
    "Output Format/Style": "OUTPUT_FORMAT",
    "Constraints": "CONSTRAINTS",
}


def normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def csv_match_keys(name: str) -> set[str]:
    keys = {normalize_name(name)}
    without_parenthetical = re.sub(r"\s*\([^)]*\)", "", name)
    keys.add(normalize_name(without_parenthetical))

    for key in list(keys):
        if key.endswith("prompting"):
            keys.add(key[: -len("prompting")])
        if key.endswith("cotcot"):
            keys.add(key[: -len("cot")])
        if key.endswith("scotscot"):
            keys.add(key[: -len("scot")])
        if key.endswith("psps"):
            keys.add(key[: -len("psps")])

    if "persona" in normalize_name(name):
        keys.add("persona")

    return {key for key in keys if key}


def fail_with_errors(errors: list[str]) -> None:
    print("ERROR: catalog sync validation failed:", file=sys.stderr)
    for error in errors:
        print(f"  - {error}", file=sys.stderr)
    raise SystemExit(1)


def read_csv_rows() -> list[dict[str, str]]:
    with CSV_PATH.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def read_raw_rows() -> list[dict[str, str]]:
    with RAW_DATASET_PATH.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def read_json_patterns() -> list[dict[str, Any]]:
    with JSON_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    return data.get("patterns", [])


def mapped_components(row: dict[str, str]) -> set[str]:
    values = set()
    for part in row["Component use"].split(","):
        value = part.strip()
        if value:
            values.add(COMPONENT_TO_ENUM[value])
    return values


def expected_extensions(
    rows: list[dict[str, str]], raw_rows: list[dict[str, str]], errors: list[str]
) -> dict[str, list[dict[str, str]]]:
    csv_names = {row["Pattern Name"] for row in rows}
    csv_index: dict[str, dict[str, str]] = {}
    for row in rows:
        for key in csv_match_keys(row["Pattern Name"]):
            csv_index[key] = row
    included_rows = [row for row in raw_rows if row["status"] == "INCLUDED"]
    by_final_name: dict[str, list[dict[str, str]]] = {name: [] for name in csv_names}

    for row in included_rows:
        final_name = row["canonical_final_name"]
        if final_name not in csv_names:
            errors.append(
                f"INCLUDED raw row {row.get('raw_id', '<missing raw_id>')} has "
                f"canonical_final_name {final_name!r}, which is not exactly one CSV Pattern Name"
            )
            continue
        by_final_name[final_name].append(
            {"name": row["raw_name"], "source": row["source_key"]}
        )

    variant_concepts: dict[str, list[dict[str, str]]] = {}
    for row in raw_rows:
        if row.get("decision_class") == "variant":
            merged_from_key = (row.get("merged_from_key") or "").strip()
            if not merged_from_key:
                errors.append(
                    f"variant raw row {row.get('raw_id', '<missing raw_id>')} "
                    "has no merged_from_key"
                )
                continue
            variant_concepts.setdefault(merged_from_key, []).append(row)

    for canonical_key, concept_rows in sorted(variant_concepts.items()):
        folds_into = {row.get("folds_into", "").strip() for row in concept_rows}
        if len(folds_into) != 1 or not next(iter(folds_into)):
            errors.append(
                f"variant concept {canonical_key!r} must have exactly one non-empty folds_into"
            )
            continue
        target_name = next(iter(folds_into))
        target_row = csv_index.get(normalize_name(target_name))
        if target_row is None:
            errors.append(
                f"variant concept {canonical_key!r} folds_into {target_name!r}, "
                "which does not match a retained pattern"
            )
            continue
        representative = min(
            concept_rows,
            key=lambda row: (
                int(row["raw_id"]) if row["raw_id"].isdigit() else sys.maxsize,
                row["source_key"],
                row["raw_name"],
            ),
        )
        by_final_name[target_row["Pattern Name"]].append(
            {"name": representative["raw_name"], "source": representative["source_key"]}
        )

    for final_name, extensions in by_final_name.items():
        if not extensions:
            errors.append(f"CSV Pattern Name {final_name!r} has no INCLUDED raw extensions")
        unique = {
            (extension["name"], extension["source"]): extension
            for extension in extensions
        }
        by_final_name[final_name] = sorted(
            unique.values(), key=lambda item: (item["source"], item["name"])
        )

    return by_final_name


def main() -> None:
    rows = read_csv_rows()
    raw_rows = read_raw_rows()
    patterns = read_json_patterns()
    errors: list[str] = []

    if len(rows) != len(patterns):
        errors.append(
            f"pattern count mismatch: CSV has {len(rows)}, JSON has {len(patterns)}"
        )

    csv_index: dict[str, dict[str, str]] = {}
    for row in rows:
        for key in csv_match_keys(row["Pattern Name"]):
            if key in csv_index:
                errors.append(
                    f"ambiguous CSV normalized key {key!r}: "
                    f"{csv_index[key]['Pattern Name']!r} and {row['Pattern Name']!r}"
                )
            csv_index[key] = row

    json_index = {normalize_name(pattern["name"]): pattern for pattern in patterns}

    only_in_json = sorted(key for key in json_index if key not in csv_index)
    matched_csv_names = {
        csv_index[key]["Pattern Name"] for key in json_index if key in csv_index
    }
    only_in_csv = sorted(row["Pattern Name"] for row in rows if row["Pattern Name"] not in matched_csv_names)

    if only_in_json:
        errors.append(f"patterns only in JSON: {only_in_json}")
    if only_in_csv:
        errors.append(f"patterns only in CSV: {only_in_csv}")

    for json_key, pattern in json_index.items():
        row = csv_index.get(json_key)
        if row is None:
            continue

        expected_category = CATEGORY_TO_ENUM[row["Category"].strip()]
        actual_category = pattern.get("category")
        if actual_category != expected_category:
            errors.append(
                f"{pattern['name']}: category expected {expected_category}, got {actual_category}"
            )

        expected_components = mapped_components(row)
        actual_components = set(pattern.get("componentTypes", []))
        if actual_components != expected_components:
            errors.append(
                f"{pattern['name']}: componentTypes expected {sorted(expected_components)}, "
                f"got {sorted(actual_components)}"
            )

    extensions_by_final_name = expected_extensions(rows, raw_rows, errors)
    expected_extension_count = sum(
        len(extensions) for extensions in extensions_by_final_name.values()
    )
    actual_extension_count = sum(
        len(pattern.get("extensions", [])) for pattern in patterns
    )
    if actual_extension_count != expected_extension_count:
        errors.append(
            f"extension total expected {expected_extension_count} retained-source and "
            f"folded-variant entries, got {actual_extension_count}"
        )

    for json_key, pattern in json_index.items():
        row = csv_index.get(json_key)
        if row is None:
            continue
        expected = extensions_by_final_name.get(row["Pattern Name"], [])
        actual = pattern.get("extensions", [])
        if actual != expected:
            errors.append(
                f"{pattern['name']}: extensions expected {expected!r}, got {actual!r}"
            )

    if errors:
        fail_with_errors(errors)

    print("Catalog sync validation passed.")
    print(f"  Patterns: {len(patterns)} JSON <-> {len(rows)} CSV")
    print("  Categories and componentTypes match the final taxonomy CSV.")
    print(
        f"  Extensions: {actual_extension_count} generated entries match retained "
        "sources and folded variants."
    )


if __name__ == "__main__":
    main()
