"""boundaries: BND-001 through BND-018 evaluators.

Architectural ownership (14_IMPLEMENTATION_SEQUENCE.md §3.1):
    Responsibility     : BND-001 through BND-018 evaluators.
    May depend on      : domain, authority, governance, evidence contracts.
    Must not depend on : controllers, provider SDK.
    Canonical write    : no.

PKG-08 (Build Phase 3) materialized the generic boundary ENGINE only:

- `types.BoundaryId`        — 06's 18 named boundaries, closed vocabulary
- `types.BoundaryResult`    — 06 §2's exact ALLOW/DENY/REQUIRE/ESCALATE
- `types.BoundaryContext`/`BoundaryInput`/`BoundaryProof`/`BoundaryEvaluator`
                            — the typed contract a concrete evaluator
                              implements against
- `registry.BoundaryRegistry`/`evaluate_chain`
                            — registration + monotonic-restriction
                              chain composition (06 §3): the first
                              non-ALLOW result is final; nothing later
                              in the chain is even invoked

No concrete BND-001..018 evaluator lives here. 14's own package DAG
assigns those explicitly to PKG-09 ("Prototype boundaries 001-008",
`PUBLIC INTERFACES: BND-001..008`) and later packages — implementing
one here would be exactly the "successor behavior" the package
boundary forbids. This package proves the engine's composition
semantics against real predecessor logic (PKG-03's `AuthorityResolver`,
PKG-05's `session_transitions`) only through test-only evaluator
fixtures that are never registered by production code.
"""
