#!/usr/bin/env python3
"""Integrity tests for the PromptSpec pattern catalog."""
from __future__ import annotations

import json
import csv
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CATALOG_DIR = ROOT / "catalog"
SCHEMA_DIR = ROOT / "schema"


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def final_taxonomy_count() -> int:
    with (ROOT / "method" / "prompt_taxonomy_final_29_patterns.csv").open(
        newline="", encoding="utf-8-sig"
    ) as f:
        return sum(1 for _ in csv.DictReader(f))


@pytest.fixture
def patterns_data():
    return load_json(CATALOG_DIR / "patterns.json")


@pytest.fixture
def pattern_ids(patterns_data):
    return {p["id"] for p in patterns_data["patterns"]}


class TestPatterns:
    def test_patterns_file_exists(self):
        assert (CATALOG_DIR / "patterns.json").exists()

    def test_docs_catalog_copy_matches(self):
        assert (ROOT / "docs" / "catalog" / "patterns.json").exists()
        assert (ROOT / "docs" / "catalog" / "patterns.json").read_text(
            encoding="utf-8"
        ) == (CATALOG_DIR / "patterns.json").read_text(encoding="utf-8")

    def test_pattern_count_matches_final_taxonomy(self, patterns_data):
        assert len(patterns_data["patterns"]) == final_taxonomy_count()

    def test_declared_count_matches(self, patterns_data):
        assert patterns_data["count"] == len(patterns_data["patterns"])

    def test_all_pattern_ids_unique(self, patterns_data):
        ids = [p["id"] for p in patterns_data["patterns"]]
        assert len(ids) == len(set(ids)), f"Duplicate IDs: {[x for x in ids if ids.count(x) > 1]}"

    def test_all_pattern_names_unique(self, patterns_data):
        names = [p["name"] for p in patterns_data["patterns"]]
        assert len(names) == len(set(names))

    def test_extensions_are_unique_by_name_and_source(self, patterns_data):
        for pattern in patterns_data["patterns"]:
            extensions = [
                (extension["name"], extension["source"])
                for extension in pattern.get("extensions", [])
            ]
            assert len(extensions) == len(set(extensions)), (
                f"Duplicate extensions for {pattern['name']}: {extensions}"
            )

    def test_folded_variants_are_catalog_extensions(self, patterns_data):
        with (ROOT / "method" / "master_raw_dataset.csv").open(
            newline="", encoding="utf-8-sig"
        ) as f:
            rows = list(csv.DictReader(f))

        variants = {}
        for row in rows:
            if row.get("decision_class") == "variant":
                variants.setdefault(row["merged_from_key"], []).append(row)

        patterns = {pattern["name"]: pattern for pattern in patterns_data["patterns"]}
        for canonical_key, concept_rows in variants.items():
            representative = min(
                concept_rows,
                key=lambda row: (
                    int(row["raw_id"]),
                    row["source_key"],
                    row["raw_name"],
                ),
            )
            target = representative["folds_into"]
            expected = (representative["raw_name"], representative["source_key"])
            actual = [
                (extension["name"], extension["source"])
                for extension in patterns[target]["extensions"]
            ]
            assert actual.count(expected) == 1, (
                f"Folded variant {canonical_key} expected once in {target}: {expected}"
            )

    def test_variant_folds_are_consolidation_merges(self):
        with (ROOT / "method" / "master_raw_dataset.csv").open(
            newline="", encoding="utf-8-sig"
        ) as f:
            rows = list(csv.DictReader(f))

        variant_rows = [row for row in rows if row.get("decision_class") == "variant"]
        assert variant_rows
        assert {row["status"] for row in variant_rows} == {"MERGED_CONSOLIDATION"}
        assert all(row["folds_into"] for row in variant_rows)
        assert all(row["merged_from_key"] for row in variant_rows)

        canonical_keys = {row["canonical_key"] for row in rows}
        merged_from_keys = {row["merged_from_key"] for row in variant_rows}
        assert canonical_keys.isdisjoint(merged_from_keys)

        concepts = {}
        for row in rows:
            if row.get("decision_class") != "variant":
                concepts.setdefault(row["canonical_key"], row)
        assert set(concepts) == canonical_keys
        assert all(
            row["status"]
            in {"INCLUDED", "EXCLUDED_WORKFLOW", "EXCLUDED_OUT_OF_SCOPE"}
            for row in concepts.values()
        )

    def test_included_status_wins_for_fold_targets(self):
        with (ROOT / "method" / "master_raw_dataset.csv").open(
            newline="", encoding="utf-8-sig"
        ) as f:
            rows = list(csv.DictReader(f))

        grouped = {}
        for row in rows:
            grouped.setdefault(row["canonical_key"], []).append(row)

        for key in ("cot", "context_manager", "schema_specs"):
            statuses = {row["status"] for row in grouped[key]}
            assert "INCLUDED" in statuses
            assert "MERGED_CONSOLIDATION" in statuses
            resolved = (
                "INCLUDED"
                if any(row["status"] == "INCLUDED" for row in grouped[key])
                else next(
                    row["status"]
                    for row in grouped[key]
                    if row["status"] != "MERGED_CONSOLIDATION"
                )
            )
            assert resolved == "INCLUDED"

    def test_all_patterns_have_required_fields(self, patterns_data):
        for p in patterns_data["patterns"]:
            assert p.get("id"), f"Missing id for pattern: {p}"
            assert p.get("name"), f"Missing name for pattern: {p}"
            assert p.get("description"), f"Missing description for {p.get('name')}"

    def test_pattern_ids_follow_convention(self, patterns_data):
        import re
        for p in patterns_data["patterns"]:
            assert re.match(r"^[a-z0-9_]+$", p["id"]), (
                f"Pattern ID '{p['id']}' doesn't match [a-z0-9_]+ convention"
            )


class TestSchemaFiles:
    def test_pattern_schema_exists(self):
        assert (SCHEMA_DIR / "pattern.schema.json").exists()

    def test_pattern_schema_is_valid_json(self):
        data = load_json(SCHEMA_DIR / "pattern.schema.json")
        assert "$schema" in data or "type" in data


class TestSchemaConformance:
    """Validate catalog data against the JSON Schema (skipped if jsonschema absent)."""

    @pytest.fixture(autouse=True)
    def _check_jsonschema(self):
        pytest.importorskip("jsonschema")

    def test_patterns_conform_to_schema(self):
        from jsonschema import validate
        schema = load_json(SCHEMA_DIR / "pattern.schema.json")
        data = load_json(CATALOG_DIR / "patterns.json")
        validate(instance=data, schema=schema)


class TestArtifactProvenance:
    def test_no_production_prompt_ids(self):
        """Ensure no production-style prompt IDs (UUIDs) appear."""
        import re
        for path in CATALOG_DIR.glob("*.json"):
            content = path.read_text(encoding="utf-8")
            uuids = re.findall(
                r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
                content,
                re.IGNORECASE,
            )
            assert not uuids, f"Possible production UUID found in {path.name}: {uuids}"


class TestPatternCatalogMarkdown:
    """Guard against the human-readable table drifting from the JSON source."""

    def test_markdown_exists(self):
        assert (ROOT / "PATTERN_CATALOG.md").exists()

    def test_docs_markdown_copy_matches(self):
        assert (ROOT / "docs" / "PATTERN_CATALOG.md").exists()
        assert (ROOT / "docs" / "PATTERN_CATALOG.md").read_text(
            encoding="utf-8"
        ) == (ROOT / "PATTERN_CATALOG.md").read_text(encoding="utf-8")

    def test_every_pattern_name_appears(self, patterns_data):
        md = (ROOT / "PATTERN_CATALOG.md").read_text(encoding="utf-8")
        missing = [p["name"] for p in patterns_data["patterns"] if p["name"] not in md]
        assert not missing, f"Patterns missing from PATTERN_CATALOG.md: {missing}"


class TestDocumentation:
    def test_readme_exists(self):
        assert (ROOT / "README.md").exists()

    def test_terminology_exists(self):
        assert (ROOT / "docs" / "terminology.md").exists()

    def test_methodology_exists(self):
        assert (ROOT / "docs" / "methodology_summary.md").exists()

    def test_formalization_grammar_exists(self):
        assert (ROOT / "docs" / "formalization_grammar.md").exists()

    def test_catalog_filter_controls_exist(self):
        html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        for control_id in (
            "search-input",
            "category-filter",
            "subcategory-filter",
            "clear-filters",
        ):
            assert f'id="{control_id}"' in html
