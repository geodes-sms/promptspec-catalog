# PromptSpec Pattern Catalog

This repository contains the PromptSpec prompt-pattern taxonomy: a catalog of 30 prompt-engineering patterns identified through literature review.

> **Scope:** This repository is the **pattern catalog only**. The broader PromptSpec model — including prompt-component structure, pattern-to-component bindings, chunk-level realizations, the queryable graph representation, the DSL compiler — is described in the associated publication and maintained in a separate repository.

## Start here

**If you just want to read the taxonomy:** [`PATTERN_CATALOG.md`](PATTERN_CATALOG.md) — a generated human-readable table of all 30 patterns, grouped by category. The taxonomy structure source of truth is [`method/prompt_taxonomy_final_29_patterns.csv`](method/prompt_taxonomy_final_29_patterns.csv), derived from [`method/master_raw_dataset.csv`](method/master_raw_dataset.csv). [`catalog/patterns.json`](catalog/patterns.json) is the generated machine-readable catalog. The `docs/` site renders the same catalog as a searchable category → subcategory → pattern tree.

## Overview

The PromptSpec project studies how prompt-engineering patterns combine and recur across real-world prompt templates. 

## Core Concepts

| Concept | Description |
|---------|-------------|
| **PatternCatalog** | A controlled, versioned collection of prompt patterns. |
| **PatternDefinition** | One reusable prompt pattern (e.g., Persona, FewShot, SchemaSpecs). Each pattern has a stable ID, name, description, category, the prompt **component type(s)** it relates to, a detection heuristic, and **illustrative examples** (a templated placeholder form and a concrete worked example). |

> **Related concepts (described in the publication, not included here):** PromptSpec also defines `PatternChunk`, `PromptComponent`, `PatternUse`, `PatternComponentBinding`, and `VariableDefinition`, which describe how patterns are realized and composed within prompt templates. These belong to the broader PromptSpec model and are not part of this catalog artifact.

## Repository Structure

```
promptspec-catalog/
  README.md                       # This file
  PATTERN_CATALOG.md              # Human-readable taxonomy (generated from patterns.json)
  requirements-dev.txt            # Dev/test dependencies

  catalog/
    patterns.json                 # Generated PatternDefinition records

  method/
    master_raw_dataset.csv        # Raw extraction dataset and count source
    prompt_taxonomy_final_29_patterns.csv
                                  # Taxonomy structure source of truth
    prompt_taxonomy_documentation.md
                                  # Method notes generated from the raw dataset
    formalizations/
      <pattern_id>.promptspec     # One PromptSpec formalization per pattern

  schema/
    pattern.schema.json           # JSON Schema for patterns.json

  docs/
    index.html                    # GitHub Pages catalog browser
    styles.css                    # Website styles
    app.js                        # Website catalog loader and filters
    catalog/patterns.json         # Generated deploy copy for the static site
    PATTERN_CATALOG.md            # Generated deploy copy for the static site
    terminology.md                # Vocabulary and term definitions
    methodology_summary.md        # Research methodology overview
    formalization_grammar.md      # PromptSpec formalization grammar reference

  scripts/
    build_catalog.py              # Generate catalog/patterns.json from method CSV
    build_pattern_catalog_md.py   # Generate PATTERN_CATALOG.md from patterns.json
    validate_taxonomy_counts.py   # Compute and validate taxonomy reduction counts
    validate_final_taxonomy.py    # Validate final taxonomy CSV schema/style
    validate_catalog.py           # Catalog schema/content validation
    validate_catalog_sync.py      # Check generated catalog agrees with method CSV
    validate_formalizations.py    # Validate .promptspec syntax/shape

  tests/
    test_catalog_integrity.py     # Integrity and schema-conformance tests
```

## Patterns

The catalog contains **30 patterns** organized into 5 categories:

| Category | Count | Examples |
|----------|-------|----------|
| IN_CONTEXT_LEARNING | 2 | ZeroShot, FewShot |
| REASONING | 6 | ChainOfThought, StructuredCoT, ComplexCoT, PlanAndSolve, LeastToMost, ReverseCoT |
| OUTPUT_CONTROL | 9 | Recipe, SchemaSpecs, OutputAutomater, Template, SelfVerification, SelfCalibration, FactCheckList, Reflection, VisualizationGenerator |
| CONTEXT_CONTROL | 3 | Persona, ContextManager, MetaLanguageCreation |
| META_DIRECTIVES | 10 | RefusalBreaker, FlippedInteraction, GamePlay, InfiniteGeneration, QuestionRefinement, RAR, AlternativeApproaches, RE2, InstructionSelection, CognitiveVerifier |

All patterns are derived from published prompt-engineering literature. For the full per-pattern table (definitions, examples, notes, and formalizations), see [`PATTERN_CATALOG.md`](PATTERN_CATALOG.md), which is generated from `catalog/patterns.json`. Taxonomy structure changes should be made in `method/prompt_taxonomy_final_29_patterns.csv`; formalization changes should be made in `method/formalizations/<pattern_id>.promptspec`; then regenerate `catalog/patterns.json` and `PATTERN_CATALOG.md`.

## Build Generated Catalog Artifacts

```bash
python3 scripts/build_catalog.py
python3 scripts/build_pattern_catalog_md.py
python3 scripts/build_taxonomy_artifacts.py
```

The build writes canonical artifacts at `catalog/patterns.json` and
`PATTERN_CATALOG.md`, plus deploy copies under `docs/` so the static site can
load them when GitHub Pages serves `docs/` as the web root.

## Validation

To validate the reproducible taxonomy counts, final taxonomy CSV schema/style, generated catalog, catalog sync, formalization files, and tests:

```bash
python3 scripts/validate_taxonomy_counts.py
python3 scripts/validate_final_taxonomy.py
python3 scripts/validate_catalog.py
python3 scripts/validate_catalog_sync.py
python3 scripts/validate_formalizations.py
python3 -m pytest tests/ -q
```

## Website

The `docs/` directory contains a lightweight static catalog browser for GitHub Pages. It loads generated `catalog/patterns.json`, then renders a searchable and filterable taxonomy tree.

To enable it on GitHub:

1. Open the repository settings.
2. Go to **Pages**.
3. Set the source to the `main` branch and the `/docs` folder.
4. Save the Pages settings.

No build step is required.

## Data Provenance

- All pattern definitions are literature-derived taxonomy entries
- **No raw production prompts** are included in this repository.
- **No company names, workflow names, prompt IDs, or proprietary business logic** are included.
- The `placeholderExample` and `example` fields are **generic, illustrative** examples (translation, simple arithmetic, etc.) carried over from the source taxonomy — they are **not** production prompts.
- Each pattern records the prompt **component type(s)** it relates to; the binding semantics (`PRIMARY_IN` / `MODIFIES` / `SPANS`) are defined in the publication, not here.
