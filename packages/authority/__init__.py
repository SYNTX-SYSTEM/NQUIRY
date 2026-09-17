"""authority: current authority resolution.

Architectural ownership (14_IMPLEMENTATION_SEQUENCE.md §3.1):
    Responsibility     : current authority resolution.
    May depend on      : governance, domain.
    Must not depend on : UI roles, AI, projection.
    Canonical write    : no.

PKG-03 SCOPE NOTE: `actor.py` (Actor Identity Model, 04 §3) and
`resolver.py` (`AuthorityResolver`, 14 §16) materialize current,
operation-specific authority resolution over PKG-02's read
repositories. No boundary evaluator consumes this yet (BND-005/BND-006
land with PKG-09); this package only produces the
`GRANTED`/`DENIED`/`UNRESOLVED` resolution with proof refs that a
future boundary will call.
"""
