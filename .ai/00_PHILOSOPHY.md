# Design Philosophy

Guidance, not rules. These evolve as the project matures.

## Core Principles

- **Plain Python Source** — The maintained code lives in `mertisreader/*.py`; Quarto pages and tutorials live separately in `docs_src/`.
- **Explicit over Implicit** — Processing levels (RAW/CAL/PAR) are explicitly detected and validated; no magic assumptions about data availability.
- **Lazy Evaluation with Caching** — Heavy computations (frame assembly, geometry assembly) are cached after first computation to avoid redundant work.
- **Fail Fast on Invalid State** — Mixed processing levels raise errors; geometry access on RAW data raises errors; dimension mismatches require explicit interpolation mode.

## Architectural Style

- **Class-Centric API** — `MERTISDataPackReader` encapsulates all state and operations; the surrounding modules expose focused helpers.
- **Separation of Concerns** — Collection, assembly, interpolation, validation, and docs are distinct stages with clear boundaries.
- **Quarto for Narrative Docs** — Tutorials and examples should be written as Quarto pages, while the API is generated from docstrings with quartodoc.

## What We Optimise For

- **Scientific Correctness** — Processing level guards prevent invalid operations; geometry data only available when scientifically valid.
- **Developer Ergonomics** — Rich console output, intuitive method names, sensible defaults for common cases.
- **Reproducibility** — Deterministic ordering in exports; sorted by TIME_UTC; no random behavior in core workflows.

## What We Accept as Trade-offs

- **Some Duplication** — Acceptable to avoid the wrong abstraction; e.g., separate methods for raw vs. assembled frames rather than complex conditional logic.
- **Tutorial Drift Risk** — Quarto examples are executed during render, so they need to be kept in sync with the current data layout.
- **Interpolation Loss** — Upsampling/downsampling inherently loses or invents data; users must choose mode consciously based on their analysis needs.

## Interpolation Philosophy

- **`match` is Default** — No interpolation unless explicitly requested; users should be aware when resampling occurs.
- **`up` vs `down` are Explicit Choices** — Upsampling increases memory; downsampling loses resolution; neither is universally better.
- **Linear (`order=1`) is Default** — Fast and sufficient for most scientific data; cubic (`order=3`) available for smoother results when needed.

## Documentation Style

- **Executable Examples** — `README.md`, `docs_src/tutorials/`, and `examples/read_merstis_test.ipynb` should demonstrate real usage.
- **Quick References** — `ASSEMBLY_QUICK_REFERENCE.md` provides pattern lookup for common operations.
- **Metadata Transparency** — Assembly operations return metadata dicts explaining what was done (mode, order, target dimensions).

_Last updated: 2026-06-05_
