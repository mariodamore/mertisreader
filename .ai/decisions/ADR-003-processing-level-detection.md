# ADR-003: Processing level detection from filename prefixes

- **Status**: Active
- **Date**: 2026-06-05
- **Author**: Session 2026-06-05

## Context

MERTIS data exists at three processing levels: RAW (digital numbers, no geometry), CAL (calibrated, geometrically aligned), and PAR (physical units, with calibration targets). The API must enforce level-specific constraints (e.g., no geometry on RAW) and validate that input directories contain consistent data.

## Decision

- Detect processing level from filename prefixes: `mer_raw_*`, `mer_cal_*`, `mer_par_*`
- `detect_processing_level()` scans all files and raises if mixed levels are found
- Processing level is stored as instance attribute and checked before level-sensitive operations
- RAW level explicitly disables geometry access; CAL/PAR enable it

## Alternatives Considered

- **User-specified level parameter** — Rejected: Error-prone; users may specify incorrectly
- **Infer from file contents** — Rejected: Slower; FITS headers may not be reliable indicators
- **Directory-based convention** — Rejected: Already using filename convention; adding directory rules would be redundant

## Consequences

**Positive:**
- Automatic detection reduces user error
- Early validation catches mixed-level directories
- Clear error messages when operations are invalid for level

**Negative:**
- Relies on ESA naming convention being consistent
- New processing levels would require code changes

## Waiver

None.
