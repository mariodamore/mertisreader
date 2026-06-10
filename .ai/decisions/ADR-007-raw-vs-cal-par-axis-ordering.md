# ADR-007: RAW vs CAL/PAR Science Data Axis Ordering

- **Status**: Active
- **Date**: 2026-06-05
- **Author**: Session 2026-06-05

## Context

MERTIS pipeline product v0.2.6 has inconsistent axis ordering between processing levels:

### RAW Level
```
MERTIS_TIS_RAW_SCIENCE_DATA shape = (62415, 100, 40)
  = (n_frames, n_pixels, n_spectrals)
```

### CAL/PAR Level
```
MERTIS_TIS_CAL_SCIENCE_DATA shape = (40, 100, 62235)
  = (n_spectrals, n_pixels, n_frames)

MERTIS_TIS_PAR_SCIENCE_DATA shape = (40, 100, 62415)
  = (n_spectrals, n_pixels, n_frames)
```

Both levels share:
- `MERTIS_TIS_METADATA` with `rows = n_frames` (62415 for RAW, 62235 for CAL)
- Same spatial/spectral dimensions (100 × 40 for 1×2 binning)

### Binning Modes (from `PAR_TIS_BIN_MODE`)
| Value | Mode | Resulting Shape |
|-------|------|-----------------|
| 0 | 1×1 | (100, 80) |
| 1 | 1×2 | (100, 40) ← default |
| 2 | 2×2 | (50, 40) |
| 3 | 2×4 | (50, 20) |

Full frames (rare): 160 × 120 spectral

## Decision

### 1. Normalize Axis Ordering in Code

All frame assembly functions must accept explicit axis parameters and handle RAW-level transposition:

```python
def data_collector(self):
    # For RAW level, transpose from (frames, pixels, spectrals) to (spectrals, pixels, frames)
    if level == "RAW":
        frames[tis_data_path_stem] = tis_data["fits_data"]['MERTIS_TIS_RAW_SCIENCE_DATA'].data.astype(np.float64)
        # Transpose to match CAL/PAR convention
        frames[tis_data_path_stem] = np.transpose(frames[tis_data_path_stem], (2, 1, 0))
```

### 2. Source n_total_frames from Metadata

Instead of inferring `n_total_frames` from array shape, read it from `MERTIS_TIS_METADATA.rows`:

```python
# Get actual frame count from metadata
n_frames = len(tis_data["fits_data"]['MERTIS_TIS_METADATA'].data)
```

### 3. Compute n_pixels and n_spectrals from Binning Mode

When metadata is available, derive dimensions from binning mode:

```python
# Full frame dimensions
FULL_FRAME_PIXELS = 100  # or 160 for rare cases
FULL_FRAME_SPECTRALS = 80  # or 120 for rare cases

# Binning mode divisors
BIN_DIVISORS = {0: (1, 1), 1: (1, 2), 2: (2, 2), 3: (2, 4)}

bin_mode = metadata['PAR_TIS_BIN_MODE']
spatial_div, spectral_div = BIN_DIVISORS[bin_mode]
n_pixels = FULL_FRAME_PIXELS // spatial_div
n_spectrals = FULL_FRAME_SPECTRALS // spectral_div
```

### 4. Updated Metadata Structure

The `get_frames_by_shape_groups()` function must report dimensions correctly:

```python
metadata = {
    'n_files': len(file_list),
    'n_total_frames': n_frames_from_metadata,  # From MERTIS_TIS_METADATA.rows
    'n_pixels': n_pix,  # From shape or bin mode
    'n_spectrals': n_spec,  # From shape or bin mode
    'shape_key': shape_key,
}
```

## Alternatives Considered

### Alternative A: Keep RAW as-is, Document the Difference
**Rejected** because:
- Forces all downstream code to handle two conventions
- Error-prone: users may assume consistent axis ordering
- The error "Spectrals mismatch: 40 != 22" indicates confusion already

### Alternative B: Transpose in `get_assembled_frames()` Instead
**Rejected** because:
- Transposition should happen at data ingestion (earlier is better)
- `data_collector()` is the natural place for normalization
- Keeps RAW data accessible via `get_original_frames()` in normalized form

## Consequences

### Positive
- Consistent axis ordering across all processing levels
- `n_total_frames` always accurate (from metadata, not shape inference)
- Easier to reason about: `(n_spectrals, n_pixels, n_frames)` everywhere

### Negative
- RAW data is transposed on load (minor memory overhead)
- Old code accessing RAW frames directly must be updated
- `get_original_frames()` returns normalized shapes, not raw FITS shapes

## Implementation Notes

1. **Normalization happens in `data_collector()`** when loading RAW data
2. **`get_original_frames()` returns normalized shapes** - document this clearly
3. **Users needing raw FITS shapes** must access FITS files directly via astropy

## Waiver

None - this is a compatibility fix, not a constraint override.
