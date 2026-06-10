# ADR-005: Explicit interpolation modes over automatic selection

- **Status**: Active
- **Date**: 2026-06-05
- **Author**: Session 2026-06-05

## Context

TIS frames from different acquisition targets may have different spatial/spectral dimensions due to binning modes (1x2, 2x2, etc.) and window sizes. When assembling frames into a cube, the API must decide how to handle dimension mismatches. Automatic selection could hide important trade-offs from users.

## Decision

Provide **explicit interpolation modes** that users must choose:
- `'match'` (default): No interpolation; fails if dimensions differ (safe default)
- `'up'`: Upsample all frames to largest dimensions (preserves detail, increases memory)
- `'down'`: Downsample all frames to smallest dimensions (saves memory, loses resolution)
- `'none'`: Stack without interpolation (fastest, fails with heterogeneous dims)

Users must explicitly specify mode when calling `get_assembled_frames(interp_mode=...)`.

## Alternatives Considered

- **Automatic mode selection** — Rejected: Hides trade-offs; users may not realize resampling occurred
- **Always upsample** — Rejected: Wastes memory when frames already match
- **Always downsample** — Rejected: Loses data without user consent

## Consequences

**Positive:**
- Users are aware of interpolation effects on their data
- Explicit choice makes analysis reproducible
- Metadata includes interpolation mode for documentation

**Negative:**
- Users must understand the options to proceed
- `'match'` mode frequently fails, requiring user to choose another mode

## Waiver

None.
