# ADR-002: MERTISDataPackReader class-centric API design

- **Status**: Active
- **Date**: 2026-06-05
- **Author**: Session 2026-06-05

## Context

The API needs to manage complex state: input/output directories, processing level, collected data, assembled frames, geometry, and metadata. A functional API would require passing many arguments between calls and make state management cumbersome.

## Decision

Design the API around a single **`MERTISDataPackReader`** class that:
- Encapsulates all state as instance attributes
- Provides methods for each stage: `data_collector()`, `data_assembler()`, `get_assembled_frames()`, `get_assembled_geometry()`
- Uses lazy evaluation with caching for expensive operations
- Exposes read-only properties for processed data (`frames`, `geom_ls`, `mertis_tis_metadata`)

## Alternatives Considered

- **Functional API with explicit state passing** — Rejected: Would require passing data dicts through many functions; harder to track state
- **Multiple specialized classes** — Rejected: Over-engineering for this codebase size; adds import complexity
- **Dataclass-based state container** — Rejected: Would not encapsulate behavior; methods would still be scattered

## Consequences

**Positive:**
- Intuitive workflow: instantiate → collect → assemble → access
- State is implicit in the instance; no global state
- Easy to work with multiple data packs simultaneously
- IDE autocomplete works naturally

**Negative:**
- Class can become large (God Object anti-pattern risk)
- Stateful design makes pure testing harder
- Users must understand initialization order

## Waiver

None.
