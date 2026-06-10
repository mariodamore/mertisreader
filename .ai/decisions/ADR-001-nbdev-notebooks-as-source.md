# ADR-001: nbdev-based development with notebooks as source

- **Status**: Superseded by ADR-009
- **Date**: 2026-06-05
- **Author**: Session 2026-06-05

## Context

The project needs a development workflow that combines executable code with narrative documentation. Traditional Python development separates code (`*.py`) from documentation (docstrings, separate markdown), leading to drift between examples and implementation.

## Decision

Adopt **nbdev** as the primary development methodology:
- All library code lives in Jupyter notebooks under `nbs/`
- Code cells marked with `#| export` are included in the generated Python module
- `nbs/00_core.ipynb` is the single source notebook for all library logic
- `mertisreader/core.py` is auto-generated via `nbdev_export`
- Manual edits to `mertisreader/*.py` are forbidden; they are read-only artifacts

## Alternatives Considered

- **Traditional Python with Sphinx** — Rejected: Documentation and code are separate; examples can become stale
- **Jupyter + manual export** — Rejected: Error-prone; no automated testing integration
- **quarto-only documentation** — Rejected: Would not solve the code-as-documentation problem

## Consequences

**Positive:**
- Examples in documentation are always executable and up-to-date
- Development workflow encourages literate programming
- Tests can be embedded as notebook cells
- Single file contains both implementation and explanation

**Negative:**
- Git diffs are less readable for notebook JSON format
- Requires nbdev tooling familiarity
- Monolithic notebook can become large (`00_core.ipynb` is ~580 lines)

## Waiver

None.
