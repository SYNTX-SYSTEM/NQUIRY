"""observability: correlation and diagnostic telemetry.

Architectural ownership (14_IMPLEMENTATION_SEQUENCE.md §3.1):
    Responsibility     : correlation and diagnostic telemetry.
    May depend on      : semantic_types.
    Must not depend on : canonical mutation.
    Canonical write    : no.

PKG-27 SCOPE NOTE (Phase 10, "Observability correlation"): materializes
`ObservationContext`/`ObservationSink`/`LocalOtelObservationSink`
(`context.py`) -- structured diagnostic correlation only, never
authority or domain truth (14 §46). No domain, authority, or
persistence behavior is implemented here; this package still cannot
depend on anything but `semantic_types` (see
`scripts/check_architecture_dependencies.py`).
"""
