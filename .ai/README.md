# .ai/ — Project Memory

This folder is the single source of truth for project context for the **mertisreader** library.
It is read by AI coding agents (Claude Code, GitHub Copilot) and by human contributors.

## About the Project

**mertisreader** is an nbdev-based Python library for reading ESA BepiColombo MERTIS instrument data.
The library uses Jupyter notebooks (`nbs/`) as the source of truth, with code auto-generated
to `mertisreader/core.py` via nbdev.

## Files at a glance

| File | Read when |
|---|---|
| `00_CONSTRAINTS.md` | Every coding session — hard rules |
| `00_PHILOSOPHY.md` | Architecture work, onboarding, new patterns |
| `02_ROADMAP.md` | Planning, scope questions |
| `03_CURRENT_STATUS.md` | Start of every session — current state |
| `decisions/index.md` | Conflict checks, architecture decisions |
| `decisions/ADR-NNN-*.md` | When the index flags a relevant decision |
| `sessions/YYYY-MM-DD.md` | Debugging, "why did we do this" questions |
| `archive/` | Historical status — rarely needed |

## New contributor?

Start here: `00_PHILOSOPHY.md` → `02_ROADMAP.md` → `03_CURRENT_STATUS.md`

## New agent session?

Start here: `03_CURRENT_STATUS.md` → `00_CONSTRAINTS.md` → `02_ROADMAP.md` → `decisions/index.md`

## Quick Links

- **Core API**: `MERTISDataPackReader` class in `mertisreader/core.py` (generated from `nbs/00_core.ipynb`)
- **Source Notebooks**: `nbs/00_core.ipynb` (library code), `nbs/index.ipynb` (documentation)
- **Sample Data**: `data/bcmer_tm_all_START-20200409T000000_END-20200410T000000_CRE-20240717T132010-ParamEventBootSciHK-short/`
- **Quick Reference**: `ASSEMBLY_QUICK_REFERENCE.md` for frame assembly patterns
