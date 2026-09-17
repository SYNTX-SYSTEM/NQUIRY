"""Authentication adapter boundary — extension point only.

14_IMPLEMENTATION_SEQUENCE.md §2.1: "pluggable OIDC adapter plus
deterministic test adapter... Establish identity without embedding
domain authority in tokens." Concrete adapter selection is
`GAP-14-001` (Reference Authentication Provider Selection, 15 §0) and
lands with PKG-01 (Identity and Workspace types).

Empty in this build phase (Phase 0). Authenticating a request must
never itself grant a Decision Right, Authority, or Workspace
membership — identity mapping only (14 §16 non-collapse:
`Authentication != Authority`).
"""
