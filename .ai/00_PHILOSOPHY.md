# Design Philosophy

Guidance, not rules. These evolve as the project matures.

## Core Principles

- **Notebooks as Source** — All code lives in `nbs/*.ipynb`; Python modules are derived artifacts. This enables literate programming with executable documentation.
- **Token saving** - to save token, agent can export the nbdev library and analyze python code in mertisreader/ directory. optionally, each notebook can be converted to python percent format in place with jupytext --to py:percent your_notebook.ipynb, produces your_notebook.py and back to a notebook with jupytext --to notebook your_script.py, produces your_notebook.ipynb.
- **environment** - the project runs in the conda environment mertis for develop, activate is before running any command `conda activate mertis`
- **Explicit over Implicit** — Processing levels (RAW/CAL/PAR) are explicitly detected and validated; no magic assumptions about data availability.
- **Lazy Evaluation with Caching** — Heavy computations (frame assembly, geometry assembly) are cached after first computation to avoid redundant work.
- **Fail Fast on Invalid State** — Mixed processing levels raise errors; geometry access on RAW data raises errors; dimension mismatches require explicit interpolation mode.

## Architectural Style

- **Single Large Notebook** — `nbs/00_core.ipynb` contains all library logic; no fragmentation across multiple core notebooks.
- **Export-Marked Cells** — Code cells intended for the public API are marked with `#| export`; unmarked cells remain internal.
- **Class-Centric API** — `MERTISDataPackReader` encapsulates all state and operations; no standalone functions for primary workflow.
- **Separation of Concerns** — Collection, assembly, and interpolation are distinct stages with clear boundaries.

## What We Optimise For

- **Scientific Correctness** — Processing level guards prevent invalid operations; geometry data only available when scientifically valid.
- **Developer Ergonomics** — Rich console output, intuitive method names, sensible defaults for common cases.
- **Reproducibility** — Deterministic ordering in exports; sorted by TIME_UTC; no random behavior in core workflows.

## What We Accept as Trade-offs

- **Some Duplication** — Acceptable to avoid the wrong abstraction; e.g., separate methods for raw vs. assembled frames rather than complex conditional logic.
- **Monolithic Notebook** — While `00_core.ipynb` is large (~580 lines), splitting it would add complexity without clear benefit for this codebase size.
- **Interpolation Loss** — Upsampling/downsampling inherently loses or invents data; users must choose mode consciously based on their analysis needs.

## Interpolation Philosophy

- **'match' is Default** — No interpolation unless explicitly requested; users should be aware when resampling occurs.
- **'up' vs 'down' are Explicit Choices** — Upsampling increases memory; downsampling loses resolution; neither is universally better.
- **Linear (order=1) is Default** — Fast and sufficient for most scientific data; cubic (order=3) available for smoother results when needed.

## Documentation Style

- **Executable Examples** — README.md and `nbs/index.ipynb` contain copy-pasteable examples that demonstrate real usage.
- **Quick References** — `ASSEMBLY_QUICK_REFERENCE.md` provides pattern lookup for common operations.
- **Metadata Transparency** — Assembly operations return metadata dicts explaining what was done (mode, order, target dimensions).

_Last updated: 2026-06-05_
