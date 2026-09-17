"""test_support: deterministic fixtures, clocks, and hooks for tests only.

Architectural ownership (14_IMPLEMENTATION_SEQUENCE.md §3.1):
    Responsibility : deterministic fixtures, clocks, hooks.
    May depend on  : public contracts (ports) of other packages.
    Must not depend on: nothing production-side depends on this package.
    Canonical write: no.

This package must never be imported from `apps/` or from any other
`packages/*` package. `scripts/check_test_only_imports.py` enforces
this at CI time (14 §41, §45). Import it only from `tests/` or from
another test-only fixture.
"""
