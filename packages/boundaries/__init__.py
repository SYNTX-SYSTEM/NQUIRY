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

PKG-09 (Build Phase 3) added the first 8 concrete evaluators, each its
own file/class (14 PKG-09: "Do not compress to one authorization
function"):

- `bnd_001_identity.Bnd001IdentityEvaluator`         — actor-class check
- `bnd_002_workspace.Bnd002WorkspaceEvaluator`        — real `WorkspaceRepository`
- `bnd_003_membership.Bnd003MembershipEvaluator`      — real `MembershipRepository`
- `bnd_004_role_context.Bnd004RoleContextEvaluator`   — real current-role read
- `bnd_005_human_authority.Bnd005HumanAuthorityEvaluator` — real `AuthorityResolver`
- `bnd_006_human_decision.Bnd006HumanDecisionEvaluator` — decision-origin check
- `bnd_007_state_transition.Bnd007StateTransitionEvaluator` — consumes real
                            `session_transitions`/`burst_transitions` resolutions
- `bnd_008_question_burst.Bnd008QuestionBurstEvaluator` — AI-exclusion during
                            protected Burst states

None of these is wired into any production caller (no Command/Query
dispatch exists yet, Phase 4+) — each is proven directly, and in real
cross-layer chains, by `tests/boundaries/`/`tests/security/`. BND-009
through BND-018 remain unbuilt; later packages own those explicitly.

Extension: `INTERNAL_ALLOWED["boundaries"]` now also includes
`persistence` (read-only use by BND-002/003/004 only — BND-005 takes an
already-constructed `AuthorityResolver` via injection and never imports
`persistence` itself).
"""
