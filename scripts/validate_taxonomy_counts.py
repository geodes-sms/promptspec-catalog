#!/usr/bin/env python3
"""Validate and print computed taxonomy extraction and decision counts."""

from __future__ import annotations

import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "method" / "master_raw_dataset.csv"
FINAL_PATH = ROOT / "method" / "prompt_taxonomy_final_29_patterns.csv"
SCOPE_STATUSES = {"INCLUDED", "EXCLUDED_WORKFLOW", "EXCLUDED_OUT_OF_SCOPE"}
MERGED_STATUS = "MERGED_CONSOLIDATION"
DECISION_CLASSES = {
    "variant",
    "optimization_option",
    "meta_directive_dimension",
    "multi_prompt",
    "workflow_orchestration",
    "prompting_example",
    "preprocessing",
    "non_textual",
    "training_method",
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        fail(f"missing dataset: {path}")
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def canonical_status(rows: list[dict[str, str]]) -> str:
    if any(row["status"] == "INCLUDED" for row in rows):
        return "INCLUDED"
    excluded = {
        row["status"]
        for row in rows
        if row["status"] != MERGED_STATUS
    }
    if len(excluded) != 1:
        fail(f"canonical status is ambiguous: {sorted(excluded)}")
    return next(iter(excluded))


def main() -> None:
    rows = read_rows(DATASET_PATH)
    final_rows = read_rows(FINAL_PATH)
    source_counts = Counter(row["source_key"] for row in rows)
    normalized_names = {row["normalized_name"] for row in rows}
    canonical_keys = {row["canonical_key"] for row in rows}

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["canonical_key"]].append(row)

    errors: list[str] = []
    status_counts: Counter[str] = Counter()
    non_retained_decision_counts: Counter[str] = Counter()
    for key, rows_for_key in grouped.items():
        status = canonical_status(rows_for_key)
        canonical_rows = [
            row for row in rows_for_key if row["status"] != MERGED_STATUS
        ]
        decisions = {row.get("decision_class", "") for row in canonical_rows}
        folds = {row.get("folds_into", "") for row in canonical_rows}
        if len(decisions) != 1 or len(folds) != 1:
            errors.append(
                f"{key}: inconsistent canonical decision_class/folds_into "
                f"{decisions}/{folds}"
            )
            continue
        decision = next(iter(decisions))
        if status not in SCOPE_STATUSES:
            errors.append(f"{key}: invalid status {status!r}")
            continue
        if status == "INCLUDED":
            status_counts[status] += 1
            if decision or next(iter(folds)):
                errors.append(f"{key}: INCLUDED concept has exclusion metadata")
        elif decision not in DECISION_CLASSES:
            errors.append(f"{key}: unclassified non-INCLUDED concept")
        else:
            status_counts[status] += 1
            if status == "EXCLUDED_OUT_OF_SCOPE":
                non_retained_decision_counts[decision] += 1

    variant_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row.get("decision_class") != "variant":
            continue
        merged_from_key = (row.get("merged_from_key") or "").strip()
        if not merged_from_key:
            errors.append(
                f"variant raw row {row.get('raw_id', '<missing raw_id>')} "
                "has no merged_from_key"
            )
            continue
        variant_groups[merged_from_key].append(row)

    for merged_from_key, merged_rows in variant_groups.items():
        statuses = {row["status"] for row in merged_rows}
        folds = {row.get("folds_into", "") for row in merged_rows}
        parent_keys = {row["canonical_key"] for row in merged_rows}
        if statuses != {MERGED_STATUS}:
            errors.append(
                f"{merged_from_key}: variant status must be {MERGED_STATUS}"
            )
        if len(folds) != 1 or not next(iter(folds)):
            errors.append(f"{merged_from_key}: variant must have one folds_into target")
        if len(parent_keys) != 1 or next(iter(parent_keys)) not in canonical_keys:
            errors.append(
                f"{merged_from_key}: variant must use one existing parent canonical_key"
            )

    included_names = {
        row["canonical_final_name"] for row in rows if row["status"] == "INCLUDED"
    }
    final_names = {row["Pattern Name"] for row in final_rows}
    if included_names != final_names:
        errors.append(
            "INCLUDED/final taxonomy mismatch: "
            f"only in raw={sorted(included_names-final_names)}, "
            f"only in final={sorted(final_names-included_names)}"
        )

    post_consolidation_concepts = len(canonical_keys)
    variant_merge_count = len(variant_groups)
    pre_variant_collapse_concepts = (
        post_consolidation_concepts + variant_merge_count
    )
    consolidation_merges = len(normalized_names) - post_consolidation_concepts
    retained_count = status_counts["INCLUDED"]
    workflow_count = status_counts["EXCLUDED_WORKFLOW"]
    non_retained_count = status_counts["EXCLUDED_OUT_OF_SCOPE"]
    single_prompt_candidates = post_consolidation_concepts - workflow_count
    accounted = retained_count + workflow_count + non_retained_count
    classified_non_retained = sum(non_retained_decision_counts.values())
    if accounted != post_consolidation_concepts:
        errors.append(
            "post-consolidation partition mismatch: "
            f"{accounted} != {post_consolidation_concepts}"
        )
    if classified_non_retained != non_retained_count:
        errors.append(
            "non-retained decision-class mismatch: "
            f"{classified_non_retained} != {non_retained_count}"
        )
    if errors:
        fail("; ".join(errors))

    print("Taxonomy count validation passed.")
    print("Per-source raw counts:")
    for source, count in sorted(source_counts.items()):
        print(f"  {source}: {count}")
    print(f"Raw rows total: {len(rows)}")
    print(f"Unique normalized names: {len(normalized_names)}")
    print(
        "Unique canonical_key before variant-key collapse: "
        f"{pre_variant_collapse_concepts}"
    )
    print(f"Unique canonical_key after collapse: {post_consolidation_concepts}")
    print(f"Consolidation merges: {consolidation_merges}")
    print(f"  Existing synonym merges: {consolidation_merges - variant_merge_count}")
    print(f"  Variant-key collapses: {variant_merge_count}")
    print(
        "Single-prompt candidates entering scope filtering: "
        f"{post_consolidation_concepts} - {workflow_count} = {single_prompt_candidates}"
    )
    print("Post-consolidation buckets:")
    print(f"  INCLUDED: {retained_count}")
    print(f"  EXCLUDED_WORKFLOW: {workflow_count}")
    print(f"  EXCLUDED_OUT_OF_SCOPE (non-retained): {non_retained_count}")
    print(
        "Partition assertion: "
        f"{retained_count} + {workflow_count} + {non_retained_count} "
        f"= {accounted} == {post_consolidation_concepts}"
    )
    print("Non-retained decision classes:")
    for decision, count in sorted(non_retained_decision_counts.items()):
        print(f"  {decision}: {count}")
    print("Canonical parent statuses:")
    for key in ("cot", "context_manager", "schema_specs"):
        print(f"  {key}: {canonical_status(grouped[key])}")


if __name__ == "__main__":
    main()
