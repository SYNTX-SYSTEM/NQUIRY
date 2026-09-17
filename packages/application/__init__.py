"""application: use-case orchestration and Query/Command dispatch.

Architectural ownership (14_IMPLEMENTATION_SEQUENCE.md §3.1):
    Responsibility     : use-case orchestration and Query/Command dispatch.
    May depend on      : public ports above.
    Must not depend on : ORM mutation, provider SDK.
    Canonical write    : no direct write.

PKG-01 SCOPE NOTE: `workspace_context.py` materializes "request
Workspace context" (14 PKG-01 OBJECTIVE) by pairing an
`AuthenticatedPrincipal` with a proven `WorkspaceRecord` read through
`persistence.WorkspaceRepository` (a `CanonicalReadPort` use, 14 §11 —
see `scripts/check_architecture_dependencies.py`'s `INTERNAL_ALLOWED`
extension for `application -> persistence`, read-only). No Command/
Query dispatch is implemented yet.

PKG-07 added `burst_operations.py` (`check_burst_operation_readiness` —
composes `domain.burst_transitions`' topology check with a genuine,
current `authority.resolver.AuthorityResolver.resolve()` call; the
first real, non-test authority resolution outside PKG-03/04's own
proofs) and `burst_contamination.py` (`evaluate_burst_contamination_guard`
— 06 §14 BND-008's one testable invariant, computed as a pure function;
lives here rather than in `domain` because it needs `authority.actor.ActorClass`).
Both remain strictly read-only per this package's own topology row
("Canonical write: no direct write") — neither calls any
`persistence.burst_repository.BurstRepository` mutating method; those
are exercised only by tests, mirroring PKG-06's disclosed-unwired
`QuestionRepository` pattern.
"""
