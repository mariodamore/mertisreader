# ADR-004: Lazy evaluation with caching for heavy computations

- **Status**: Active
- **Date**: 2026-06-05
- **Author**: Session 2026-06-05

## Context

Assembling frames from FITS files, performing interpolation, and building geometry arrays are computationally expensive operations. Users may call `get_assembled_frames()` multiple times with the same parameters during analysis; recomputing each time would waste resources.

## Decision

- Use **lazy evaluation**: expensive computations occur only on first access
- Cache results in private attributes (`_raw_frames`, `_assembled_cube`, `_assembled_geometry`)
- First call computes and caches; subsequent calls return the cached object (identity check: `cube2 is cube1`)
- **No parameter tracking**: users must not re-call with different parameters—caching is single-result-per-method

## Alternatives Considered

- **Eager evaluation on initialization** — Rejected: Wastes time if user only inspects metadata
- **No caching** — Rejected: Users would experience unnecessary delays during iterative analysis
- **Parameter-keyed cache** — Rejected: Complexity not justified for typical usage (call once, reuse result)

## Consequences

**Positive:**
- Fast repeated access to computed data
- Users control when computation happens
- Simple implementation (no parameter tracking overhead)

**Negative:**
- First access may be slow; users need to understand this pattern
- Cache consumes memory for large datasets
- Calling with different parameters returns stale (first-call) result
- Users must be aware that modifying returned objects affects the cache

## Waiver

None.
