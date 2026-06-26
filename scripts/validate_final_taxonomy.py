#!/usr/bin/env python3
"""Validate final taxonomy CSV schema and component labels."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FINAL_TAXONOMY_PATH = ROOT / "method" / "prompt_taxonomy_final_29_patterns.csv"

EXPECTED_COLUMNS = [
    "Pattern Name",
    "Category",
    "Component use",
    "Description",
    "Example",
    "Placeholder example",
    "Subcategory",
]
ALLOWED_COMPONENTS = {
    "Profile/Role",
    "Directive",
    "Context",
    "Procedural Steps",
    "Examples",
    "Output Format/Style",
    "Constraints",
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def warn(message: str) -> None:
    print(f"WARNING: {message}", file=sys.stderr)


def read_rows() -> tuple[list[str], list[dict[str, str]]]:
    if not FINAL_TAXONOMY_PATH.exists():
        fail(f"missing final taxonomy: {FINAL_TAXONOMY_PATH}")
    with FINAL_TAXONOMY_PATH.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames or [], list(reader)


def assert_single_value(label: str, value: str, row_number: int) -> None:
    if "," in value or ";" in value:
        fail(f"row {row_number} {label} must be single-valued; got {value!r}")
    if "/" in value:
        warn(f"row {row_number} {label} contains slash; review manually: {value!r}")


def parse_components(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def main() -> None:
    columns, rows = read_rows()

    if columns != EXPECTED_COLUMNS:
        fail(f"columns changed: expected {EXPECTED_COLUMNS!r}, got {columns!r}")
    if not rows:
        fail("final taxonomy contains no patterns")

    categories: set[str] = set()
    subcategories: set[str] = set()
    component_values: set[str] = set()

    for index, row in enumerate(rows, start=2):
        category = row["Category"].strip()
        subcategory = row["Subcategory"].strip()
        components = parse_components(row["Component use"])

        assert_single_value("Category", category, index)
        assert_single_value("Subcategory", subcategory, index)

        if not components:
            fail(f"row {index} Component use is empty")

        for component in components:
            if component == "Workflow":
                fail(f"row {index} Component use contains deprecated value 'Workflow'")
            if component not in ALLOWED_COMPONENTS:
                fail(f"row {index} Component use has unsupported value {component!r}")
            component_values.add(component)

        categories.add(category)
        subcategories.add(subcategory)

    print("Final taxonomy validation passed.")
    print(f"Patterns: {len(rows)}")
    print("Categories:")
    for value in sorted(categories):
        print(f"  - {value}")
    print("Subcategories:")
    for value in sorted(subcategories):
        print(f"  - {value}")
    print("Component values:")
    for value in sorted(component_values):
        print(f"  - {value}")


if __name__ == "__main__":
    main()
