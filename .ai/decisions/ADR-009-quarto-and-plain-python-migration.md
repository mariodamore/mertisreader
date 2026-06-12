# ADR-009: Migrate from nbdev to Quarto + plain Python

- **Status:** Active
- **Date:** 2026-06-10
- **Author:** Session 2026-06-10

## Context

The repository currently uses nbdev as the source-of-truth workflow: Python modules are generated from notebooks, packaging metadata is split between `settings.ini` and `pyproject.toml`, and documentation/build automation is tied to nbdev commands and generated artifacts.

That workflow has been useful for rapid literate development, but it now creates avoidable friction:

- the code path depends on notebook export state,
- packaging metadata is split across multiple files,
- generated Python modules are treated as derived artifacts instead of maintained source,
- and the current docs/build stack mixes nbdev, Quarto, and historical scaffolding.

The project is moving toward a workflow where LLM assistants operate natively on source files. That favors a standard Python package layout with Quarto-owned documentation and explicit example material rather than nbdev-managed code generation.

## Decision

Migrate the project from an nbdev-based literate programming workflow to a plain Python package with Quarto documentation.

The new architecture is:

- **Package source of truth:** regular Python modules under `mertisreader/`.
- **Documentation source of truth:** Quarto pages and posts, rendered from `.qmd` files.
- **API documentation:** generated from Python docstrings with `quartodoc`.
- **Example/tutorial material:** kept in `examples/` as notebook-friendly content, preferably paired with `.py:percent` scripts via jupytext when a text companion is useful.
- **Packaging metadata:** centralized in a PEP 621 `pyproject.toml`.
- **Build backend:** use **Hatchling** for the package build system.

This decision also means:

- `settings.ini` is no longer the packaging source of truth.
- nbdev export tags such as `#| export` are not part of the package build path.
- nbdev hooks and nbdev-specific CI commands are removed from the main workflow.
- any notebooks that remain are tutorials, examples, or rendered documentation inputs, not the authoritative package source.

## Consequences

Positive:

- The package becomes easier to edit, review, and automate against with standard Python tooling.
- Source files are directly readable without notebook export indirection.
- Documentation becomes cleaner: narrative content lives in Quarto, API pages are generated from docstrings, and examples are separated from implementation.
- CI can validate package, tests, and docs with conventional commands instead of nbdev-specific steps.
- Example notebooks can be kept LLM-friendly by pairing them with `.py:percent` scripts.

Negative:

- The notebook-as-source workflow is retired, so some current literate-programming convenience is lost.
- The migration requires a coordinated update across packaging, docs, CI, and contributor instructions.
- Existing notebook-derived artifacts will become stale or disposable during the transition and must be cleaned up carefully.

## Alternatives Considered

- **Keep nbdev as the source-of-truth workflow** — rejected because it preserves the current coupling between code generation and notebook state, which is the primary source of friction.
- **Docs-only Quarto migration while keeping nbdev for code generation** — rejected because it still leaves package source tied to notebooks and does not simplify the core workflow enough.
- **Manual export from notebooks to Python modules** — rejected because it reintroduces an error-prone sync step and does not give a clear source-of-truth model.
- **Flit as the build backend** — considered, but Hatchling was chosen because it is a better fit for a repo that will combine standard package code, generated API docs, and separate tutorial material.

## Migration Shape

The migration should be treated as a full repository transition rather than a partial refactor.

Target structure:

- `mertisreader/` for maintained Python source
- `examples/` for tutorial notebooks and optional `.py:percent` companions
- `_quarto.yml` and related Quarto configuration for the docs site
- `docs/` as Quarto output, not nbdev-generated documentation

Operationally, the following repo areas must move together:

- `settings.ini` and nbdev-specific metadata
- `pyproject.toml` packaging and dependency declarations
- `Makefile` targets
- pre-commit hooks
- CI pipelines
- GitHub Pages or equivalent documentation deployment
- contributor instructions in `CLAUDE.md` and Copilot instructions

## Notes

This ADR supersedes ADR-001. ADR-001 remains useful as a historical record of why nbdev was adopted, but it no longer describes the desired end state for the repository.

## Implementation Guidance

The migration should be executed in this order:

1. Convert the generated Python modules into maintained source files.
2. Replace packaging metadata with a single `pyproject.toml`.
3. Introduce or refine Quarto + quartodoc docs configuration : we can use existing nbs/*ipynb as starting point for quarto doc.
4. Rework example notebooks into LLM-friendly tutorial assets.
5. Update automation and CI.
6. Remove stale nbdev scaffolding once the new workflow is verified, check git nbdev filters.
