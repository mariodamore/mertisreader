# Constraints

Hard rules. These are non-negotiable unless an ADR with a Waiver field explicitly overrides one.

## Core Workflow (NON-NEGOTIABLE)

- **Source of Truth**: All logic belongs in the maintained Python modules under `mertisreader/`; Quarto tutorial pages live in `docs_src/tutorials/`.
- **Cell-Ready Output**: When authoring tutorial content, provide executable code blocks that Quarto can run.
- **Verification**: Every logic change must include a test case or an `assert` suitable for pytest or a Quarto-executed example.

## Required Technologies

- **Quarto** — Reason: Project publishes tutorial documentation and the site is built with `quarto render`
- **quartodoc** — Reason: API reference is generated from Python docstrings
- **Python 3.7+** — Reason: Declared minimum version in `settings.ini`
- **NumPy, pandas, astropy, matplotlib, xmltodict, rich** — Reason: Core dependencies declared in `settings.ini`

## Forbidden Technologies

- **Direct edits to generated docs under `docs/`** — Reason: These are built artifacts from Quarto/quartodoc
- **`setup.py` manual edits** — Reason: Version and metadata come from `settings.ini` and `__init__.py`

## Forbidden Patterns

- **Editing `docs/` manually** — Reason: These are built artifacts from Quarto/quartodoc
- **Non-deterministic ordering in examples** — Reason: Keep outputs reproducible; sort lists by numeric suffix as current code does
- **Mixing processing levels in input directories** — Reason: `detect_processing_level()` raises if mixed RAW/CAL/PAR levels detected

## External Boundaries

- **RAW level lacks geometry** — Geometry-dependent code must guard on `processing_level != 'RAW'`
- **ESA/PDS4 naming convention** — Input directories should follow `mer_{level}_sc_{type}_{date}_{...}` pattern

## File Path Conventions

- **Output directory**: Defaults to `<input_dir>-analysis_products` sibling unless explicitly set
- **Plot output**: `save_plot()` writes to output_dir with configurable format/dpi

_Last updated: 2026-06-05_
