# mertisreader - Copilot Instructions

This project uses the **`.ai/`** folder as the single source of truth for project context.

## Key Files

| File | Purpose |
|---|---|
| `.ai/03_CURRENT_STATUS.md` | Current state: what's in progress, blocked, or known issues |
| `.ai/00_CONSTRAINTS.md` | Hard rules: nbdev workflow, forbidden patterns, required tech |
| `.ai/00_PHILOSOPHY.md` | Design principles: lazy evaluation, explicit interpolation modes |
| `.ai/decisions/index.md` | Architectural decisions (ADRs) |

## Core Workflow

- **Source of Truth**: All code lives in `nbs/*.ipynb` notebooks; `mertisreader/*.py` is auto-generated
- **Export Pattern**: Mark code cells with `#| export` for inclusion in the Python module
- **Primary API**: `MERTISDataPackReader` class for reading ESA MERTIS instrument data

## Processing Levels

- **RAW**: Digital numbers, no geometry
- **CAL**: Calibrated, geometrically aligned
- **PAR**: Physical units, with calibration targets

Never call geometry operations on RAW level data.

## Quick Links

- **Notebook source**: `nbs/00_core.ipynb`
- **Sample data**: `data/bcmer_tm_all_*/`
- **Quick reference**: `ASSEMBLY_QUICK_REFERENCE.md`
