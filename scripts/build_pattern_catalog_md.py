#!/usr/bin/env python3
"""Build PATTERN_CATALOG.md from catalog/patterns.json."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "catalog" / "patterns.json"
MD_PATH = ROOT / "PATTERN_CATALOG.md"
DOCS_MD_PATH = ROOT / "docs" / "PATTERN_CATALOG.md"

CATEGORY_ORDER = [
    "IN_CONTEXT_LEARNING",
    "REASONING",
    "OUTPUT_CONTROL",
    "CONTEXT_CONTROL",
    "META_DIRECTIVES",
]
CATEGORY_LABELS = {
    "IN_CONTEXT_LEARNING": "In-Context Learning",
    "REASONING": "Reasoning",
    "OUTPUT_CONTROL": "Output Control",
    "CONTEXT_CONTROL": "Context Control",
    "META_DIRECTIVES": "Meta-Directives",
}
COMPONENT_ORDER = [
    "PROFILE_ROLE",
    "DIRECTIVE",
    "CONTEXT",
    "PROCEDURAL_STEPS",
    "EXAMPLES",
    "OUTPUT_FORMAT",
    "CONSTRAINTS",
]


def read_catalog() -> dict[str, Any]:
    with JSON_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def components(values: list[str]) -> str:
    return ", ".join(f"`{value}`" for value in values)


def code_block(value: str | None) -> list[str]:
    if not value:
        return []
    cleaned = "\n".join(line.rstrip() for line in value.splitlines())
    return ["```", cleaned, "```", ""]


def promptspec_block(value: str | None) -> list[str]:
    if not value:
        return []
    return ["~~~promptspec", value.rstrip(), "~~~", ""]


def grouped_patterns(patterns: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pattern in patterns:
        grouped[pattern["category"]].append(pattern)
    for category in grouped:
        grouped[category].sort(key=lambda pattern: pattern["name"].lower())
    return grouped


def main() -> None:
    catalog = read_catalog()
    patterns = catalog["patterns"]
    grouped = grouped_patterns(patterns)

    lines = [
        "# PromptSpec Pattern Catalog",
        "",
        "> **Read this if you just want the taxonomy.** This is the MD view of the catalog. The method CSV is the source of truth; [`catalog/patterns.json`](catalog/patterns.json) is the generated machine-readable view.",
        "",
        f"The catalog contains **{len(patterns)} prompt-engineering patterns** across **5 categories**.",
        "",
        "All patterns in this catalog are derived from published prompt-engineering literature. They are taxonomy entries, not empirically observed corpus findings.",
        "",
        "Each pattern lists the **prompt component type(s)** it relates to in the PromptSpec model (`PROFILE_ROLE`, `DIRECTIVE`, `CONTEXT`, `PROCEDURAL_STEPS`, `EXAMPLES`, `OUTPUT_FORMAT`, `CONSTRAINTS`). The binding *semantics* (whether a pattern is primary in, modifies, or spans those components) are defined in the associated publication, not in this catalog.",
        "",
        "## Summary",
        "",
        "| Pattern | Category | Component(s) |",
        "|---|---|---|",
    ]

    for category in CATEGORY_ORDER:
        for pattern in grouped.get(category, []):
            lines.append(
                f"| {pattern['name']} | {CATEGORY_LABELS[category]} | {components(pattern['componentTypes'])} |"
            )

    lines.append("")

    for category in CATEGORY_ORDER:
        category_patterns = grouped.get(category, [])
        if not category_patterns:
            continue
        lines.extend(["", f"## {CATEGORY_LABELS[category]}", ""])
        for pattern in category_patterns:
            lines.extend(
                [
                    f"### {pattern['name']}",
                    "",
                    pattern.get("description") or "",
                    "",
                    f"**Component(s):** {components(pattern.get('componentTypes', []))}",
                    "",
                ]
            )
            if pattern.get("placeholderExample"):
                lines.extend(["*Placeholder form:*", ""])
                lines.extend(code_block(pattern.get("placeholderExample")))
            if pattern.get("example"):
                lines.extend(["*Example:*", ""])
                lines.extend(code_block(pattern.get("example")))
            if pattern.get("formalization"):
                lines.extend(["*Formalization:*", ""])
                lines.extend(promptspec_block(pattern.get("formalization")))
            if pattern.get("notes"):
                lines.extend([f"> {pattern['notes']}", ""])

    payload = "\n".join(lines).rstrip() + "\n"
    MD_PATH.write_text(payload, encoding="utf-8")
    DOCS_MD_PATH.write_text(payload, encoding="utf-8")
    print(
        "Built "
        f"{MD_PATH.relative_to(ROOT)} and {DOCS_MD_PATH.relative_to(ROOT)} "
        f"from {JSON_PATH.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
