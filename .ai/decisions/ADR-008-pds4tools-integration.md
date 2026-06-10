# ADR-008: Integration of PDS4 Python Tools for Label Validation and Metadata Access

- **Status:** Proposed
- **Date:** 2026-06-05
- **Author:** Session 2026-06-05

## Context

mertisreader currently reads MERTIS PDS4 data products using low-level libraries:
- **FITS files**: Read directly with `astropy.io.fits`
- **CSV/HK files**: Read with `pandas.read_csv` or `polars` (lazy loading via ADR-006)
- **PDS4 labels**: Parsed minimally with `xmltodict` for HK column extraction

The [pds4_tools](https://pdssbn.astro.umd.edu/tools/pds4_tools_docs/current/) library (developed by NASA PDS Small Bodies Node) provides a comprehensive wrapper for PDS4 data products, offering:

1. **Unified label parsing**: Full PDS4 XML label interpretation with `Label` class (XPath-based access, `to_dict()` conversion)
2. **Data structure validation**: Automatic verification that declared label structure matches actual data
3. **Table metadata access**: Field-level metadata (units, descriptions, data types) via `.meta_data` attribute
4. **Lazy loading support**: `lazy_load=True` for memory-efficient large file handling
5. **Array sectioning**: Read portions of large arrays without loading entire dataset

The roadmap (`.ai/02_ROADMAP.md`) explicitly identifies this as an upcoming phase:
> "Use official PDS4 Python Tools - Currently data read is handled directly with low level files (astropy FITS, Pandas CSV), we need to read the PDS4 xml label too"

## Decision

Integrate pds4tools as a **complementary validation and metadata layer**, not as a complete replacement for existing readers. mertisreader remains specialized for MERTIS-specific workflows, while leveraging pds4tools for:

### 1. Label Validation (Primary Use Case)

Before reading data, validate that the PDS4 label correctly describes the data structure:

```python
import pds4_tools

structures = pds4_tools.read(label_path, lazy_load=True)
# structures[0].meta_data contains declared dimensions, axes, types
# structures[0].data.shape can be compared against declaration
```

### 2. CSV/Table Header Metadata Extraction

Use pds4tools to extract CSV column metadata (units, descriptions) for HK files:

```python
table_structure = structures['Integration']  # or appropriate table name
field_meta = table_structure.field('Wavelength').meta_data
# field_meta['unit'], field_meta['description'], etc.
```

### 3. Label Data Access via `to_dict()`

Convert entire label to dictionary for structured metadata queries:

```python
label_dict = structures.label.to_dict(cast_values=True)
# Access nested elements without XPath
```

### 4. Optional: Replace FITS Reading (Secondary)

For FITS data described by PDS4 labels, pds4tools can read the data directly:

```python
array_structure = structures['MERTIS_TIS_RAW_SCIENCE_DATA']
data = array_structure.data  # Returns numpy array with .meta_data
```

## Implementation Approach

### Dependency Addition

Add pds4tools to `settings.ini` (and `pyproject.toml`):

```ini
[requirements]
...
pds4_tools>=1.10.0
```

### New Module: `mertisreader/pds4_validation.py`

Create a new notebook source `nbs/03_pds4_validation.ipynb` exporting:

1. **`validate_pds4_label(label_path: Union[str, Path]) -> dict`**
   - Returns validation results: `{'valid': bool, 'warnings': list, 'structure': dict}`
   - Compares declared vs. actual data dimensions
   - Checks for required MERTIS-specific elements

2. **`extract_label_metadata(label_path: Union[str, Path]) -> dict`**
   - Returns structured metadata from label using pds4tools
   - Includes processing level, binning mode, acquisition parameters
   - Uses `structures.label.to_dict()` with selective extraction

3. **`get_csv_field_metadata(hk_path: Union[str, Path]) -> pd.DataFrame`**
   - Returns DataFrame of CSV column metadata (name, unit, description, type)
   - Extracted from PDS4 label's `Table_Delimited` section

4. **`PDS4LabelReader` class** (optional, if label-only reading is valuable)
   - Lightweight wrapper around pds4tools for label-focused operations
   - Methods: `get_structure_info()`, `get_field_metadata()`, `validate()`

### Integration Points

1. **In `MERTISDataPackReader.__init__()`**:
   - Optional validation step: `validate_pds4_label()` for each FITS file
   - Can be enabled via `validate=True` parameter

2. **In `extract_mertis_hk_columns()`**:
   - Replace `xmltodict` parsing with pds4tools `Label.find()` or `to_dict()`
   - Gain access to field metadata (units, descriptions)

3. **New convenience method `get_label_summary()`**:
   - Returns human-readable summary of all labels in input directory
   - Uses pds4tools for consistent parsing

## Alternatives Considered

### Alternative A: Complete Replacement of FITS/CSV Reading with pds4tools
**Rejected** because:
- mertisreader has MERTIS-specific logic (axis normalization ADR-007, frame assembly) that pds4tools doesn't provide
- Current astropy/pandas approach is working and well-understood
- pds4tools is general-purpose; mertisreader needs MERTIS specialization
- Performance: direct astropy access may be faster for known FITS structures

### Alternative B: No Integration, Continue with xmltodict
**Rejected** because:
- xmltodict only provides raw XML parsing; no PDS4 semantic understanding
- No built-in validation of label vs. data consistency
- CSV field metadata requires manual XPath parsing
- Roadmap explicitly identifies this as technical debt

### Alternative C: pds4tools as Optional Dependency
**Considered** but decided against for initial implementation:
- Most MERTIS data users will benefit from label validation
- pds4tools is stable (PyPI package, conda-forge, actively maintained by PDS)
- Can add `optional=True` later if needed for minimal install

## Consequences

### Positive
- **Validation before processing**: Catch label/data mismatches early
- **Richer metadata**: Access field-level units, descriptions from labels
- **Standards compliance**: Use official PDS4 tooling for PDS4 products
- **Reduced custom XML parsing**: Less code to maintain in `extract_mertis_hk_columns()`

### Negative
- **New dependency**: Adds pds4tools to requirements (though it's well-maintained)
- **Learning curve**: Team needs to understand pds4tools API (documentation exists)
- **Potential conflicts**: If pds4tools behavior changes, validation layer may need updates

## Implementation Notes

1. **Version pinning**: Use `pds4_tools>=1.10.0` (current stable on PyPI)
2. **Lazy loading**: Default to `lazy_load=True` to match ADR-006 memory efficiency goals
3. **Error handling**: Wrap pds4tools calls in try/except; fallback to existing xmltodict if pds4tools fails
4. **Testing**: Validate against known MERTIS products in `data/` directory

## Files to Modify

- `.ai/decisions/index.md` — Add ADR-007 entry
- `settings.ini` — Add pds4tools dependency
- `pyproject.toml` — Add pds4tools to dependencies
- `nbs/00_core.ipynb` — Update `extract_mertis_hk_columns()` to use pds4tools
- `nbs/03_pds4_validation.ipynb` — New notebook with validation utilities
- `mertisreader/__init__.py` — Export new validation functions

## Waiver

None — this integration complements existing constraints rather than overriding them.
