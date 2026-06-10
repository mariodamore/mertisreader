# ADR-006: Unified Lazy vs Eager Strategy for Large FITS and CSV Ingestion

- **Status:** Proposed
- **Date:** 2026-06-05
- **Author:** Session 2026-06-05

## Context
MERTIS dataset products are highly resource-intensive:
1. Binary FITS collection cubes can reach sizes up to 5.5 GB per file.
2. Accompanying CSV housekeeping tables contain hundreds of thousands of rows.

Eagerly parsing both file types via standard methods during `MERTISDataPackReader` initialization causes severe memory pressure, leading to kernel crashes in local Jupyter notebook environments. However, complete in-memory loading remains highly desirable for fast, repetitive analysis loops when system memory is abundant.

## Decision
We will implement a unified "Lazy by Default, Eager on Demand" architecture across the `MERTISDataPackReader` class:

### Initialization
```python
reader = MERTISDataPackReader(input_dir, lazy=True)  # All files in directory use lazy mode
```
The `lazy=True/False` parameter is set at instantiation and applies uniformly to all files in the input directory, ensuring a homogeneous interface across heterogeneous file sizes.

### FITS Data Handling
- When `lazy=True`: Use `astropy.io.fits.open(..., memmap=True)` with a custom proxy wrapper that defers I/O. Array slicing and iteration work transparently and only read needed data from disk. Metadata access (shape, dtype, header) never triggers I/O.
- When `lazy=False`: Read arrays eagerly via `.copy()` into RAM.
- **Materialization**: `.materialize()` forces full array load into RAM and returns a copy (explicit, repeatable).

### CSV Data Handling
- When `lazy=True`: Use `polars.scan_csv()` to create an unevaluated query plan (LazyFrame).
- When `lazy=False`: Use `pd.read_csv()` to read the entire file into a Pandas DataFrame.
- **Materialization**: `.materialize()` calls `.collect()` (Polars) or returns identity (Pandas) and always returns a materialized DataFrame.

### FITS Proxy Behavior
Operations on lazy FITS arrays:
- **Safe (no full load required):** Slicing (`arr[0, :, :]`), iteration, `.shape`, `.dtype`, `.mean()`, `.sum()`
- **Unsafe (require `.materialize()` first):** Complex indexing, sorting, reshaping, operations requiring contiguous memory
- **Never trigger I/O:** Metadata access (`.header`, `.shape`, `.dtype`)

### Caching Strategy (Interaction with ADR-004)
- **Eager mode (`lazy=False`)**: Results cached in `_assembled_cube`, `_assembly_metadata`, `_assembled_geometry` after first call (per ADR-004). Subsequent calls return cached objects instantly.
- **Lazy mode (`lazy=True`)**: No caching. Each method call returns fresh memmap views. Users must call `.materialize()` explicitly to load into RAM if repeated fast access is needed.
- **Rationale**: Caching eager data avoids recomputation; lazy data already defers I/O via memmap, so caching adds no value and wastes RAM.

Both lazy and eager objects present `.materialize()` for consistency; attempting lazy-incompatible operations (e.g., random indexing) raises `NotImplementedError` with guidance to call `.materialize()` first.

We explicitly reject introducing **Dask DataFrames** due to unneeded parallel processing overhead and graph execution complexity within a local data-pack library. We also reject the `pd.read_csv(..., chunksize=N)` fallback, preferring Polars for clean, efficient lazy CSV evaluation.

## Alternatives Considered
- **Dask DataFrames:** Rejected due to API footprint, parallel task-graph overhead, and complexity unsuited to single-node notebook environments.
- **Chunked Pandas CSV reading:** Rejected in favor of Polars for cleaner lazy semantics and better performance.
- **Separate ADRs for FITS and CSV:** Rejected to preserve a single unified ingestion philosophy for the `MERTISDataPackReader` architecture.
- **Parameter-keyed caching (one cache per parameter set):** Rejected; caching only applies to eager mode for simplicity.

## Consequences
- **Positive:** 
  - Multi-gigabyte data packs can be instantiated instantly inside notebooks without memory risk
  - Unified `.materialize()` API across FITS and CSV types for predictable user experience
  - Lazy mode delegates I/O to memmap; no custom caching overhead
  - Eager mode retains fast caching via ADR-004 for repeated access
  - Clear, upfront choice at init time; no silent mode switches
- **Negative:** 
  - Lazy mode requires Polars (new dependency)
  - Lazy-incompatible operations raise `NotImplementedError`; users must call `.materialize()` first
  - Downstream analysis code must either handle both lazy and eager modes, or require explicit materialization
  - Lazy mode trades repeated-access speed for startup speed; users wanting both must call `.materialize()`