"""BurstTransitionSpec registry base for the QuestionBurst state machine.

Source: 03_STATE_AND_TRANSITION_ARCHITECTURE.md §19 (state vocabulary),
§20 (TRN-BURST-001..005); 04_AUTHORITY_AND_DECISION_RIGHTS.md §35-39
(AUTH-DEP-BURST-001..005); 12_MINIMUM_PROTOTYPE_ARCHITECTURE.md §7
(Authority Profile).

Mirrors `domain.session_transitions`'s design exactly (same module
docstring reasoning applies throughout: `STATE_ELIGIBLE` is necessary,
never sufficient; authority is a reference, not a `governance.AuthorityClass`;
boundary dependencies are 03's own names, not BND-001..018 identifiers).
`BoundaryDependency`, `TransitionProofType`, `ProofObligation` and
`ProofRequirement` are *imported*, not redefined -- every value 03 §20
uses for Burst transitions (`Workspace`, `Authority`, `Question Burst`,
`Methodology`, `State Transition`, `Audit`, `Human / AI`, `Persistence`,
`Failure`, `Recovery`) already exists in `session_transitions`, and
duplicating a generic vocabulary for a second object class would be
exactly the kind of "second source of truth for a closed list"
`session_transitions`'s own docstring warns against.

SUPERSESSION (F02, recorded in WU-02.12): the WORKSPACE-scope reading in
the next section is the PKG-07 historical record. HD-1 (16 §41 REC-002)
fixed Session control at `SESSION:<session_id>`, and HD-9 (16 §41
REC-009 / NQ-DEC-037) closed Burst control for the current prototype as
Session-scoped `SESSION_CONTROL_RIGHT`: an explicit prototype narrowing of
04 §35-39 / 05 §20, whose Facilitator + FacilitatorScopeBinding model stays
OPEN for production (NQ-GAP-080). 12 §8.1 already lists
FacilitatorScopeBinding as conditional ("IF BURST CONTROL PATH REQUIRES
IT"), and HD-9 decides it is not required in the prototype.

WHY BURST AUTHORITY RESOLVES TO `SESSION_CONTROL_RIGHT` AT `WORKSPACE`
SCOPE (NOT `SESSION` OR `QuestionBurst` SCOPE)  [PKG-07, HISTORICAL]
------------------------------------------------------------------------
04 §35-39 each state an "AUTHORITY SCOPE" of "Specific Session" or a
similarly narrow object boundary, and 04 §2.7 describes scope as an
exact, non-hierarchical boundary ("Authority outside its scope is
invalid"). But 12 §8.1's bootstrap sequence grants `SESSION_CONTROL_RIGHT`
exactly once, *before* any Challenge/Session/Burst exists -- the only
scope obtainable at that point is `WORKSPACE`. 12 §7's own authority
profile table resolves the tension explicitly: "SESSION_CONTROL_RIGHT
... Create/control legal Session and Burst progression *where upstream
assigns it*." This package reads that hedge as authorizing exactly one
non-inventive choice: every Burst authority check in this prototype
uses `scope_type="WORKSPACE"`, matching the only binding shape the
prototype's own bootstrap path can produce and requiring **no
extension** to `authority.resolver.AuthorityResolver` (its exact-match
design is honored, not widened with a scope-hierarchy rule 04/05 never
state). `FacilitatorScopeBinding` (09 §51) remains correctly deferred:
12 §8.1 lists it as conditional ("IF BURST CONTROL PATH REQUIRES IT"),
and the prototype's minimum profile does not require it.

04's resolution, reproduced as documentation only (04 §35-39 / summary
table lines 3784-3788):

    AUTH-DEP-BURST-001  Prepare Burst   SESSION_CONTROL_RIGHT (ARCHITECTURAL_CLOSURE)
    AUTH-DEP-BURST-002  Start Burst     Facilitator source right (LEVEL_1_EXPLICIT)
    AUTH-DEP-BURST-003  Pause Burst     Facilitator source right (LEVEL_1_EXPLICIT)
    AUTH-DEP-BURST-004  Resume Burst    Facilitator resume right (ARCHITECTURAL_CLOSURE)
    AUTH-DEP-BURST-005  Complete Burst  Facilitator end right (LEVEL_1_EXPLICIT)
                                        + SYSTEM_DERIVED timer path (not implemented --
                                        this package materializes manual completion only)

All five resolve, in this prototype's own Authority Profile (12 §7),
through the same `SESSION_CONTROL_RIGHT` binding a Facilitator holds --
"Facilitator eligible" language throughout 04 §35-39 describes *who*
typically holds that binding, not a second, role-based authority path
(04 §2.3: "Role alone does not grant authority").

TRN-BURST-005's SYSTEM_DERIVED timer path is deliberately not
represented at all, even as inert reference data: 03 §21 (CONFLICT-007)
and §22 (GAP-03-002) leave timer semantics unresolved, and this
package's own coding prompt requires "Manual authorized completion
only. No automatic timer." Inventing an `AuthorityDependency` value for
an unresolved timer authority would itself be semantic invention.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum

from domain.burst import TERMINAL_BURST_STATES, BurstState
from domain.session_transitions import (
    BoundaryDependency,
    ProofObligation,
    ProofRequirement,
    TransitionProofType,
)


class BurstTransitionId(Enum):
    """The 5 transition identifiers 03 §20 defines. Closed."""

    TRN_BURST_001 = "TRN-BURST-001"
    TRN_BURST_002 = "TRN-BURST-002"
    TRN_BURST_003 = "TRN-BURST-003"
    TRN_BURST_004 = "TRN-BURST-004"
    TRN_BURST_005 = "TRN-BURST-005"


class BurstOperation(Enum):
    """The `REQUESTED TRANSITION` name each 03 §20 contract carries."""

    PREPARE_BURST = "PREPARE_BURST"
    START_BURST = "START_BURST"
    PAUSE_BURST = "PAUSE_BURST"
    RESUME_BURST = "RESUME_BURST"
    COMPLETE_BURST = "COMPLETE_BURST"


class BurstAuthorityDependency(Enum):
    """04's authority-requirement identifiers for the Burst machine.
    Closed to the identifiers 04 §35-39 actually define. See the
    module docstring for why every one resolves to
    `AuthorityClass.SESSION_CONTROL_RIGHT` (at `SESSION:<session_id>` since
    HD-1/HD-9; PKG-07 read `WORKSPACE`) in this prototype, without this
    package importing `governance.AuthorityClass` itself (14 §3.1: `domain`
    depends on `semantic_types` only).
    """

    AUTH_DEP_BURST_001 = "AUTH-DEP-BURST-001"
    AUTH_DEP_BURST_002 = "AUTH-DEP-BURST-002"
    AUTH_DEP_BURST_003 = "AUTH-DEP-BURST-003"
    AUTH_DEP_BURST_004 = "AUTH-DEP-BURST-004"
    AUTH_DEP_BURST_005 = "AUTH-DEP-BURST-005"


@dataclass(frozen=True, slots=True)
class BurstTransitionSpec:
    """One 03 §20 QuestionBurst transition contract, as data. Same
    inert-reference design as `session_transitions.TransitionSpec`.

    `from_state is None` means the Burst does not yet exist
    (TRN-BURST-001 CURRENT STATE: "QuestionBurst absent").
    """

    transition_id: BurstTransitionId
    operation: BurstOperation
    from_state: BurstState | tuple[BurstState, ...] | None
    to_state: BurstState
    authority_dependency: BurstAuthorityDependency
    required_boundary_dependencies: tuple[BoundaryDependency, ...]
    required_proofs: tuple[ProofRequirement, ...]


_SYSTEM_PROOF_ALWAYS = ProofRequirement(TransitionProofType.SYSTEM_PROOF, ProofObligation.ALWAYS)

_SPECS: tuple[BurstTransitionSpec, ...] = (
    BurstTransitionSpec(
        transition_id=BurstTransitionId.TRN_BURST_001,
        operation=BurstOperation.PREPARE_BURST,
        from_state=None,
        to_state=BurstState.PREPARED,
        authority_dependency=BurstAuthorityDependency.AUTH_DEP_BURST_001,
        required_boundary_dependencies=(
            BoundaryDependency.WORKSPACE,
            BoundaryDependency.AUTHORITY,
            BoundaryDependency.QUESTION_BURST,
            BoundaryDependency.METHODOLOGY,
            BoundaryDependency.AUDIT,
        ),
        required_proofs=(_SYSTEM_PROOF_ALWAYS,),
    ),
    BurstTransitionSpec(
        transition_id=BurstTransitionId.TRN_BURST_002,
        operation=BurstOperation.START_BURST,
        from_state=BurstState.PREPARED,
        to_state=BurstState.ACTIVE,
        authority_dependency=BurstAuthorityDependency.AUTH_DEP_BURST_002,
        required_boundary_dependencies=(
            BoundaryDependency.AUTHORITY,
            BoundaryDependency.QUESTION_BURST,
            BoundaryDependency.METHODOLOGY,
            BoundaryDependency.STATE_TRANSITION,
            BoundaryDependency.AUDIT,
        ),
        required_proofs=(_SYSTEM_PROOF_ALWAYS,),
    ),
    BurstTransitionSpec(
        transition_id=BurstTransitionId.TRN_BURST_003,
        operation=BurstOperation.PAUSE_BURST,
        from_state=BurstState.ACTIVE,
        to_state=BurstState.PAUSED,
        authority_dependency=BurstAuthorityDependency.AUTH_DEP_BURST_003,
        required_boundary_dependencies=(
            BoundaryDependency.AUTHORITY,
            BoundaryDependency.QUESTION_BURST,
            BoundaryDependency.AUDIT,
        ),
        required_proofs=(_SYSTEM_PROOF_ALWAYS,),
    ),
    BurstTransitionSpec(
        transition_id=BurstTransitionId.TRN_BURST_004,
        operation=BurstOperation.RESUME_BURST,
        from_state=BurstState.PAUSED,
        to_state=BurstState.ACTIVE,
        authority_dependency=BurstAuthorityDependency.AUTH_DEP_BURST_004,
        required_boundary_dependencies=(
            BoundaryDependency.AUTHORITY,
            BoundaryDependency.QUESTION_BURST,
            BoundaryDependency.STATE_TRANSITION,
            BoundaryDependency.AUDIT,
        ),
        required_proofs=(_SYSTEM_PROOF_ALWAYS,),
    ),
    BurstTransitionSpec(
        transition_id=BurstTransitionId.TRN_BURST_005,
        operation=BurstOperation.COMPLETE_BURST,
        # 03 TRN-BURST-005 CURRENT STATE: "ACTIVE or PAUSED" -- the one
        # spec with more than one legal source state.
        from_state=(BurstState.ACTIVE, BurstState.PAUSED),
        to_state=BurstState.COMPLETED,
        authority_dependency=BurstAuthorityDependency.AUTH_DEP_BURST_005,
        required_boundary_dependencies=(
            BoundaryDependency.QUESTION_BURST,
            BoundaryDependency.HUMAN_AI,
            BoundaryDependency.AUTHORITY,
            BoundaryDependency.PERSISTENCE,
            BoundaryDependency.AUDIT,
            BoundaryDependency.FAILURE,
            BoundaryDependency.RECOVERY,
        ),
        required_proofs=(_SYSTEM_PROOF_ALWAYS,),
    ),
)

BURST_TRANSITION_SPECS: Mapping[BurstTransitionId, BurstTransitionSpec] = {
    spec.transition_id: spec for spec in _SPECS
}

_BY_OPERATION_NAME: Mapping[str, BurstTransitionSpec] = {
    spec.operation.value: spec for spec in _SPECS
}


def _source_states(spec: BurstTransitionSpec) -> tuple[BurstState, ...]:
    if spec.from_state is None:
        return ()
    if isinstance(spec.from_state, tuple):
        return spec.from_state
    return (spec.from_state,)


_BY_STATE_PAIR: dict[tuple[BurstState | None, BurstState], BurstTransitionSpec] = {}
for _spec in _SPECS:
    if _spec.from_state is None:
        _BY_STATE_PAIR[(None, _spec.to_state)] = _spec
    else:
        for _source in _source_states(_spec):
            _BY_STATE_PAIR[(_source, _spec.to_state)] = _spec


class BurstTransitionVerdict(Enum):
    """Outcome of the topology evaluation. Default-DENY, identical
    vocabulary and meaning to `session_transitions.SessionTransitionVerdict`.
    """

    STATE_ELIGIBLE = "STATE_ELIGIBLE"
    DENIED_UNKNOWN_TRANSITION = "DENIED_UNKNOWN_TRANSITION"
    DENIED_ILLEGAL_TRANSITION = "DENIED_ILLEGAL_TRANSITION"
    DENIED_TERMINAL_STATE = "DENIED_TERMINAL_STATE"
    DENIED_BURST_ALREADY_EXISTS = "DENIED_BURST_ALREADY_EXISTS"


@dataclass(frozen=True, slots=True)
class BurstTransitionResolution:
    verdict: BurstTransitionVerdict
    spec: BurstTransitionSpec | None
    current_state: BurstState | None
    requested: str

    @property
    def is_state_eligible(self) -> bool:
        return self.verdict is BurstTransitionVerdict.STATE_ELIGIBLE


def _refuse(
    verdict: BurstTransitionVerdict, *, current_state: BurstState | None, requested: str
) -> BurstTransitionResolution:
    return BurstTransitionResolution(
        verdict=verdict, spec=None, current_state=current_state, requested=requested
    )


def _evaluate_by_identifier(
    *,
    current_state: BurstState | None,
    spec: BurstTransitionSpec | None,
    requested: str,
) -> BurstTransitionResolution:
    """Shared evaluation for lookups keyed by a transition identifier
    (03 §20 ID or operation name) -- see
    `session_transitions._evaluate_by_identifier` for why this must
    not be reused for target-state-addressed requests.
    """
    if spec is None:
        return _refuse(
            BurstTransitionVerdict.DENIED_UNKNOWN_TRANSITION,
            current_state=current_state,
            requested=requested,
        )
    if current_state is not None and current_state in TERMINAL_BURST_STATES:
        return _refuse(
            BurstTransitionVerdict.DENIED_TERMINAL_STATE,
            current_state=current_state,
            requested=requested,
        )
    valid_sources = _source_states(spec)
    if not valid_sources and current_state is not None:
        return _refuse(
            BurstTransitionVerdict.DENIED_BURST_ALREADY_EXISTS,
            current_state=current_state,
            requested=requested,
        )
    if valid_sources and current_state not in valid_sources:
        return _refuse(
            BurstTransitionVerdict.DENIED_ILLEGAL_TRANSITION,
            current_state=current_state,
            requested=requested,
        )
    return BurstTransitionResolution(
        verdict=BurstTransitionVerdict.STATE_ELIGIBLE,
        spec=spec,
        current_state=current_state,
        requested=requested,
    )


def resolve_burst_transition(
    *, current_state: BurstState | None, transition_id: BurstTransitionId
) -> BurstTransitionResolution:
    """Evaluate a transition addressed by its 03 §20 identifier."""
    return _evaluate_by_identifier(
        current_state=current_state,
        spec=BURST_TRANSITION_SPECS.get(transition_id),
        requested=transition_id.value,
    )


def resolve_burst_transition_by_operation_name(
    *, current_state: BurstState | None, operation_name: str
) -> BurstTransitionResolution:
    """Evaluate a transition requested by name, as an untyped caller
    supplies it. An unrecognised name yields `DENIED_UNKNOWN_TRANSITION`
    (14 PKG-07 FAILURE_RECOVERY: fails closed precommit)."""
    return _evaluate_by_identifier(
        current_state=current_state,
        spec=_BY_OPERATION_NAME.get(operation_name),
        requested=operation_name,
    )


def resolve_burst_transition_to_state(
    *, current_state: BurstState | None, target_state: BurstState
) -> BurstTransitionResolution:
    """Evaluate a request expressed as a desired *target state* -- the
    generic-setter collapse shape. See
    `session_transitions.resolve_session_transition_to_state` for why
    an unmatched pair means illegal/terminal, never "unknown": a
    target *state* is always a real `BurstState`.
    """
    requested = target_state.value
    if current_state is not None and current_state in TERMINAL_BURST_STATES:
        return _refuse(
            BurstTransitionVerdict.DENIED_TERMINAL_STATE,
            current_state=current_state,
            requested=requested,
        )
    spec = _BY_STATE_PAIR.get((current_state, target_state))
    if spec is None:
        return _refuse(
            BurstTransitionVerdict.DENIED_ILLEGAL_TRANSITION,
            current_state=current_state,
            requested=requested,
        )
    return BurstTransitionResolution(
        verdict=BurstTransitionVerdict.STATE_ELIGIBLE,
        spec=spec,
        current_state=current_state,
        requested=requested,
    )


def legal_state_pairs() -> frozenset[tuple[BurstState | None, BurstState]]:
    """Every `(from, to)` pair 03 §20 registers, expanded so
    TRN-BURST-005's two-source spec appears as two pairs. Used by the
    migration proof to confirm the database trigger and this registry
    agree.
    """
    return frozenset(_BY_STATE_PAIR)


__all__ = [
    "BurstTransitionId",
    "BurstOperation",
    "BurstAuthorityDependency",
    "BurstTransitionSpec",
    "BURST_TRANSITION_SPECS",
    "BurstTransitionVerdict",
    "BurstTransitionResolution",
    "resolve_burst_transition",
    "resolve_burst_transition_by_operation_name",
    "resolve_burst_transition_to_state",
    "legal_state_pairs",
]
