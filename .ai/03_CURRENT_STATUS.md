# Current Status

## NOW
- [ ] ADR-009 migration in progress: switch packaging/docs workflow from nbdev to Quarto + plain Python
- [x] Compatibility docs reduced to workflow-only pointers in `CLAUDE.md` and `.github/copilot-instructions.md`
- [x] Removed nbdev hooks from packaging metadata, Makefile, pre-commit, and GitLab CI
- [x] Removed generated nbdev file banners from the maintained Python modules
- [x] Removed remaining nbdev cell markers and support modules from `mertisreader/`
- [x] Root Quarto site now renders tutorial QMD pages plus quartodoc API pages
- [x] Migrated the converted percent scripts into `docs_src/tutorials/`
- [x] Removed the legacy notebook source tree and its scaffolding
- [x] Added a Quarto-backed README generation target (`make readme`)
- [x] MERTISDataPackReader core functionality implemented and working
- [x] Frame assembly with interpolation modes (match, up, down, none)
- [x] Geometry assembly for CAL/PAR levels
- [x] nbdev pre-commit hooks configured
- [x] Refactored frame utilities into separate tutorial/docs modules
- [x] ADR-007: RAW axis normalization implemented (`normalize_raw_axis_order()`)
- [x] ADR-008: PDS4 Tools Integration completed
  - Added `pds4_tools>=1.10.0` to dependencies
  - Added PDS4 validation utilities and metadata extraction support
  - Implemented `validate_pds4_label()`, `extract_label_metadata()`, `get_csv_field_metadata()`
  - Updated `extract_mertis_hk_columns()` to use pds4tools with fallback

## NEXT
### Other
- [ ] Finish polishing the tutorial pages and add more focused examples where needed
- [ ] Expand unit test coverage with fixtures from `data/` directory
- [ ] Performance profiling for large dataset handling

## KNOWN_ISSUES
- **Debt**: No formal unit tests present beyond pytest hook — Impact: medium (reliance on manual verification)
- **Note**: Generic wavelength vector computed by averaging; noted as "not precise enough for scientific analysis" — Impact: low (documented limitation)

## Version Status
- Package version: 0.0.3 (per `settings.ini`)
- MERTIS pipeline product version: v0.2.6 (supports RAW, CAL, PAR levels)

## Tutorial Structure (Updated 2026-06-11)
| Page | Purpose |
|------|---------|
| `docs_src/tutorials/getting-started.qmd` | Full reader walkthrough and quick start |
| `docs_src/tutorials/read-example.qmd` | End-to-end example workflow and plotting |
| `docs_src/tutorials/core-reader.qmd` | Core reader lifecycle and cached frames |
| `docs_src/tutorials/lazy-loading.qmd` | FITS and CSV lazy-loading helpers |
| `docs_src/tutorials/frame-utils.qmd` | Frame assembly and interpolation helpers |
| `docs_src/tutorials/pds4-validation.qmd` | PDS4 metadata extraction and validation |

## Docs Build
- README source: `docs_src/readme.qmd`
- Tutorial source: `docs_src/tutorials/`
- API source: `mertisreader/`

_Last updated: 2026-06-11_
