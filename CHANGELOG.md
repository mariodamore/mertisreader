# v0.0.4 - 2026-06-16

### Features

- New SSD workflow, lazy loading, and PDS4 tool integration
- Full migration from nbdev to quarto+python; 100% test coverage

### Improvements

- deleted nbdev pre-commit hooks (now cleaned up)
- Increased test coverage across the suite to 99%
- Updated examples/ notebook to match latest package
- Removed leftover nbdev scaffold and switched to pure python + quarto documentation

### Bug Fixes

- `lazy_loading` crash on headerless data files treated as CSV
- Test data alignment: CSV files may contain headers (not in MERTIS data)

# v0.0.3 — 2025-10-01

- Can read RAW, PAR (new format) and CAL format introduced in pipeline v.0.2.6
- Extended examples with geometry variable

# v0.0.2 - 2024-12-06

- Can read CAL data level produced with pipeline <=v.0.2.5
