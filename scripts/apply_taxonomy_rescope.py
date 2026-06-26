#!/usr/bin/env python3
"""Apply the taxonomy-rescope-v2 decisions to the raw and final CSV sources."""

from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "method" / "master_raw_dataset.csv"
FINAL_PATH = ROOT / "method" / "prompt_taxonomy_final_29_patterns.csv"

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
FOLD_TARGET_CANONICAL_KEYS = {
    "ChainOfThought": "cot",
    "ContextManager": "context_manager",
    "SchemaSpecs": "schema_specs",
}

EXPLICIT_DECISIONS = {
    "style_prompting": (
        "meta_directive_dimension",
        "",
        "tone/voice/genre dimension",
    ),
    "emotion_prompting": (
        "meta_directive_dimension",
        "",
        "affective-emphasis dimension",
    ),
    "tab_cot": ("variant", "ChainOfThought", "Output-format variant of ChainOfThought."),
    "contrastive_cot": (
        "variant",
        "ChainOfThought",
        "Exemplar variant of ChainOfThought.",
    ),
    "cos": ("variant", "ChainOfThought", "Symbolic-notation variant of ChainOfThought."),
    "constrained_vocabulary": (
        "variant",
        "SchemaSpecs",
        "Vocabulary-constraint variant of SchemaSpecs.",
    ),
    "cross_disciplinary": (
        "variant",
        "ContextManager",
        "Cross-domain context-selection variant of ContextManager.",
    ),
    "in_context_prompting": (
        "multi_prompt",
        "",
        "Requires conversational context/history across turns.",
    ),
    "conversational_prompting": (
        "multi_prompt",
        "",
        "Requires a multi-turn conversational exchange.",
    ),
    "socratic_prompting": (
        "multi_prompt",
        "",
        "Requires a structured series of probing questions.",
    ),
    "prompt_macros": (
        "workflow_orchestration",
        "",
        "Coordinates multiple micro-queries toward an end goal.",
    ),
    "meta_prompting_simple": (
        "workflow_orchestration",
        "",
        "Orchestrates reflection on and improvement of prompting process.",
    ),
    "responsive_feedback": (
        "multi_prompt",
        "",
        "Requires a prior output and a subsequent feedback prompt.",
    ),
    "scratchpad": (
        "training_method",
        "",
        "Originally a fine-tuning/task-design method.",
    ),
    "basic_guideline_error": (
        "training_method",
        "",
        "Task-specific annotation-guideline and error-analysis method.",
    ),
    "multimodal_prompting": (
        "non_textual",
        "",
        "Uses non-text input modalities.",
    ),
    "show_tell": (
        "non_textual",
        "",
        "Demonstration-oriented framing is outside the text-only pattern spine.",
    ),
    "code_prompting": (
        "preprocessing",
        "",
        "Reformulates natural-language input as code before reasoning.",
    ),
    "chain_of_draft": (
        "preprocessing",
        "",
        "Compresses reasoning steps before final response generation.",
    ),
    "tar": (
        "preprocessing",
        "",
        "Transforms the requested response toward a target format or length.",
    ),
    "contrastive_prompting_simple": (
        "preprocessing",
        "",
        "Reframes source concepts as a comparison task.",
    ),
    "exemplar_ordering": (
        "meta_directive_dimension",
        "",
        "Exemplar sequence is a prompt-optimization choice.",
    ),
    "anticipatory_prompting": (
        "prompting_example",
        "",
        "Example of an anticipatory task instruction, not a retained pattern.",
    ),
    "prompt_to_code": (
        "prompting_example",
        "",
        "Example task type, not a structural prompt pattern.",
    ),
    "directional_stimulus": (
        "prompting_example",
        "",
        "Example of adding directional hints, not a retained pattern.",
    ),
    "ambiguous_prompting": (
        "prompting_example",
        "",
        "Example of deliberately vague instruction wording.",
    ),
    "historical_visual_modular": (
        "prompting_example",
        "",
        "Bundled examples rather than one independently retained pattern.",
    ),
    "grammar_correction": (
        "prompting_example",
        "",
        "Example task type, not a structural prompt pattern.",
    ),
    "instructed_prompting": (
        "prompting_example",
        "",
        "source not re-locatable; not retained",
    ),
    "basic_term_defs": (
        "prompting_example",
        "",
        "source not re-locatable; not retained",
    ),
}

TRAINING_METHODS = {
    "active_prompting",
    "echo",
    "prompt_paraphrasing",
    "r_cot_dataset_pipeline",
    "synthetic_prompting",
}
PREPROCESSING = {"eedp", "prompt_mining"}
OPTIMIZATION_OPTIONS = {
    "ape",
    "iap",
    "knn_selection",
    "max_mutual_info",
    "opro",
    "votek_selection",
}
WORKFLOW_ORCHESTRATION = {
    "art",
    "binder",
    "buffer_of_thoughts",
    "chain_of_table",
    "coc",
    "cok",
    "con",
    "dater",
    "decomp",
    "faithful_cot",
    "memory_of_thought",
    "pal",
    "program_of_thoughts",
    "rag",
    "react",
    "verify_and_edit",
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def workflow_decision(canonical_key: str) -> str:
    if canonical_key in TRAINING_METHODS:
        return "training_method"
    if canonical_key in PREPROCESSING:
        return "preprocessing"
    if canonical_key in OPTIMIZATION_OPTIONS:
        return "optimization_option"
    if canonical_key in WORKFLOW_ORCHESTRATION:
        return "workflow_orchestration"
    return "multi_prompt"


def apply_raw_decisions() -> None:
    fields, rows = read_csv(RAW_PATH)
    for field in ("decision_class", "folds_into", "merged_from_key"):
        if field not in fields:
            fields.append(field)

    keys = {
        (row.get("merged_from_key") or row["canonical_key"]).strip()
        for row in rows
    }
    missing = sorted(set(EXPLICIT_DECISIONS) - keys)
    if missing:
        fail(f"explicit canonical keys not found: {missing}")

    for row in rows:
        key = (row.get("merged_from_key") or row["canonical_key"]).strip()
        if key == "meta_language_creation":
            row["status"] = "INCLUDED"
            row["canonical_final_name"] = "MetaLanguageCreation"
            row["status_reason"] = (
                "Retained from White et al. 2023, Input Semantics: defines custom "
                "shorthand notation and semantics for subsequent prompt context."
            )
            row["decision_class"] = ""
            row["folds_into"] = ""
            row["merged_from_key"] = ""
            continue

        if key in EXPLICIT_DECISIONS:
            decision_class, folds_into, reason = EXPLICIT_DECISIONS[key]
            if decision_class == "variant":
                row["status"] = "MERGED_CONSOLIDATION"
                row["merged_from_key"] = key
                row["canonical_key"] = FOLD_TARGET_CANONICAL_KEYS[folds_into]
            elif key in {
                "in_context_prompting",
                "conversational_prompting",
                "socratic_prompting",
                "prompt_macros",
                "meta_prompting_simple",
                "responsive_feedback",
            }:
                row["status"] = "EXCLUDED_WORKFLOW"
            if decision_class != "variant":
                row["merged_from_key"] = ""
            row["decision_class"] = decision_class
            row["folds_into"] = folds_into
            row["status_reason"] = reason
        elif row["status"] == "INCLUDED":
            row["decision_class"] = ""
            row["folds_into"] = ""
            row["merged_from_key"] = ""
        else:
            row["decision_class"] = workflow_decision(key)
            row["folds_into"] = ""
            row["merged_from_key"] = ""

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        identity_key = (row.get("merged_from_key") or row["canonical_key"]).strip()
        grouped[identity_key].append(row)

    errors: list[str] = []
    for key, concept_rows in grouped.items():
        statuses = {row["status"] for row in concept_rows}
        decisions = {row["decision_class"] for row in concept_rows}
        folds = {row["folds_into"] for row in concept_rows}
        if len(statuses) != 1 or len(decisions) != 1 or len(folds) != 1:
            errors.append(
                f"{key}: inconsistent status/decision_class/folds_into "
                f"{statuses}/{decisions}/{folds}"
            )
            continue
        status = next(iter(statuses))
        decision = next(iter(decisions))
        if status == "INCLUDED" and (decision or next(iter(folds))):
            errors.append(f"{key}: INCLUDED concepts cannot have exclusion decisions")
        if status != "INCLUDED" and decision not in DECISION_CLASSES:
            errors.append(f"{key}: missing or invalid decision_class {decision!r}")

    if errors:
        fail("; ".join(errors))
    write_csv(RAW_PATH, fields, rows)


def snake_case(value: str) -> str:
    value = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", value)
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def apply_final_pattern() -> None:
    fields, rows = read_csv(FINAL_PATH)
    if any(row["Pattern Name"] == "MetaLanguageCreation" for row in rows):
        return

    context_index = next(
        index for index, row in enumerate(rows) if row["Pattern Name"] == "ContextManager"
    )
    rows.insert(
        context_index + 1,
        {
            "Pattern Name": "MetaLanguageCreation",
            "Category": "Context Control",
            "Component use": "Context, Directive",
            "Description": (
                "Define custom shorthand notation and its semantics for the model to "
                "apply in the rest of the prompt or conversation."
            ),
            "Example": "",
            "Placeholder example": "",
            "Subcategory": "Input semantics",
        },
    )
    write_csv(FINAL_PATH, fields, rows)
    print(f"Added MetaLanguageCreation as {snake_case('MetaLanguageCreation')}.")


def main() -> None:
    apply_raw_decisions()
    apply_final_pattern()
    print(f"Updated {RAW_PATH.relative_to(ROOT)} and {FINAL_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
