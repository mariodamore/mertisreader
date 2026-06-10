# Constraints

Hard rules. These are non-negotiable unless an ADR with a Waiver field explicitly overrides one.

## Core Workflow (NON-NEGOTIABLE)

- **Source of Truth**: All logic belongs in Jupyter Notebooks (`nbs/`). Never edit `mertisreader/*.py` files directly — they are read-only auto-generated artifacts.
- **Cell-Ready Output**: Always provide code in blocks formatted for notebooks. Start library code with `#| export`.
- **Verification**: Every logic change must include a test case or an `assert` suitable for an nbdev test cell.

## Required Technologies

- **nbdev** — Reason: Project uses Jupyter notebooks as source code; exports must go through `#| export` cells
- **Python 3.7+** — Reason: Declared minimum version in `settings.ini`
- **NumPy, pandas, astropy, matplotlib, xmltodict, rich** — Reason: Core dependencies declared in `settings.ini`

## Forbidden Technologies

- **Direct edits to `mertisreader/core.py`** — Reason: Auto-generated from `nbs/00_core.ipynb`; changes will be overwritten on export
- **`setup.py` manual edits** — Reason: Version and metadata come from `settings.ini` and `__init__.py`

## Forbidden Patterns

- **Editing `docs/` or `nbs/docs/` manually** — Reason: These are built artifacts from nbdev/quarto
- **Non-deterministic ordering in notebook exports** — Reason: Keep outputs reproducible; sort lists by numeric suffix as current code does
- **Mixing processing levels in input directories** — Reason: `detect_processing_level()` raises if mixed RAW/CAL/PAR levels detected

## External Boundaries

- **RAW level lacks geometry** — Geometry-dependent code must guard on `processing_level != 'RAW'`
- **ESA/PDS4 naming convention** — Input directories should follow `mer_{level}_sc_{type}_{date}_{...}` pattern

## File Path Conventions

- **Output directory**: Defaults to `<input_dir>-analysis_products` sibling unless explicitly set
- **Plot output**: `save_plot()` writes to output_dir with configurable format/dpi

_Last updated: 2026-06-05_
