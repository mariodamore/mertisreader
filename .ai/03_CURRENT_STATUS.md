# Current Status

## NOW
- [x] MERTISDataPackReader core functionality implemented and working
- [x] Frame assembly with interpolation modes (match, up, down, none)
- [x] Geometry assembly for CAL/PAR levels
- [x] nbdev pre-commit hooks configured
- [x] Refactored frame utilities into separate `nbs/02_frame_utils.ipynb` module
- [x] ADR-007: RAW axis normalization implemented (`normalize_raw_axis_order()`)
- [x] ADR-008: PDS4 Tools Integration completed
  - Added `pds4_tools>=1.10.0` to dependencies
  - Created `nbs/03_pds4_validation.ipynb` with validation utilities
  - Implemented `validate_pds4_label()`, `extract_label_metadata()`, `get_csv_field_metadata()`
  - Updated `extract_mertis_hk_columns()` to use pds4tools with fallback

## NEXT
### Other
- [ ] Expand unit test coverage with fixtures from `data/` directory
- [ ] Performance profiling for large dataset handling

## KNOWN_ISSUES
- **Debt**: No formal unit tests present beyond pytest hook — Impact: medium (reliance on manual verification)
- **Note**: Generic wavelength vector computed by averaging; noted as "not precise enough for scientific analysis" — Impact: low (documented limitation)

## Version Status
- Package version: 0.0.3 (per `settings.ini`)
- MERTIS pipeline product version: v0.2.6 (supports RAW, CAL, PAR levels)

## Module Structure (Updated 2026-06-08)
| Module | Purpose |
|--------|---------|
| `nbs/00_core.ipynb` | `MERTISDataPackReader` class, HK extraction |
| `nbs/01_lazy_loading.ipynb` | `LazyArray`, `LazyCSVLoader` |
| `nbs/02_frame_utils.ipynb` | Frame assembly utilities, ADR-007 normalization |
| `nbs/03_pds4_validation.ipynb` | PDS4 label validation and metadata extraction (ADR-008) |

_Last updated: 2026-06-08_
