"""governance: governance state and mutation plans.

Architectural ownership (14_IMPLEMENTATION_SEQUENCE.md §3.1):
    Responsibility     : governance state and mutation plans.
    May depend on      : domain, semantic_types.
    Must not depend on : UI, provider SDK.
    Canonical write    : only through CommitUnit.

PKG-02 SCOPE NOTE: `membership.py` and `authority_binding.py` materialize
the closed vocabularies for WorkspaceMembership/RoleAssignment (02 §7,
09 §23-24) and HumanAuthorityBinding (04 §6/§9, 05 §8). No governed
mutation (grant/revoke) is executed here — no CommitUnit exists yet
(that lands with PKG-04/PKG-10/PKG-13). "Governed mutation ports" (14
PKG-02 OBJECTIVE) refers to the repository Protocols in
`packages/persistence` (14 §10 is literally titled "REPOSITORY PORTS"),
not a separate plan type.
"""
