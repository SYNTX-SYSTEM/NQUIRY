"""semantic_types: strong code-level identities and closed semantic primitives.

Architectural ownership (14_IMPLEMENTATION_SEQUENCE.md §3.1):
    Responsibility : IDs, versions, closed semantic primitives.
    May depend on  : stdlib only.
    Must not depend on: HTTP, DB, AI SDK, or any other package in this repository.
    Canonical write: no.

IDs and versions defined here carry no authority and no domain semantics.
They are non-semantic identifiers and structural counters only. See
14_IMPLEMENTATION_SEQUENCE.md §5 (SEMANTIC TYPE SYSTEM) and §42
(CONTRACT VERSIONING, CLOCK, IDS AND FINGERPRINTS).
"""
