# Roadmap

## Current Phase: Core Reader Maturity
**Goal**: Stabilize the MERTISDataPackReader API and ensure robust handling of all processing levels (RAW, CAL, PAR)
**Target date**: TBD

### In scope
- Frame assembly with interpolation modes ('match', 'up', 'down', 'none')
- Geometry assembly for non-RAW levels
- Housekeeping data integration (hk_default, hk_extended)
- Metadata indexing (space_index, bb7_index, bb3_index, planet_index)
- nbdev-based development workflow with pre-commit hooks

### Out of scope
- New instrument support (TIR quick-look data exists but is not actively developed)
- Web-based visualization or dashboarding
- Real-time data streaming or remote access
- Reprocessing or calibration routines (read-only access to ESA products)

## Upcoming Phases
- **Use official PDS4 Python Tools** - Currently data read is handled direclty with low level files (astropy FITS, Pandas CSV), we need to read the PDS4 xml label too with https://pdssbn.astro.umd.edu/tools/pds4_tools_docs/current/user_manual.html  
- **Analysis Tools** — Higher-level analysis routines (spectral fitting, time-series analysis)
- **Performance Optimization** — Memory-efficient streaming for large datasets
- **Testing Expansion** — Unit tests with realistic fixtures from `data/` directory

## Completed Phases
- **Initial Reader Implementation** — Completed; basic FITS/HK ingestion working
- **Processing Level Detection** — Completed; RAW/CAL/PAR auto-detection with validation
- **Frame Assembly Framework** — Completed; interpolation modes and caching implemented
- **Documentation Infrastructure** — Completed; nbdev + quarto + quarto-generated docs

_Last updated: 2026-06-05_
