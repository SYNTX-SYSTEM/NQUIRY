"""TransitionSpec registry base for the Session state machine.

Source: 03_STATE_AND_TRANSITION_ARCHITECTURE.md §7 (Transition Proof
Types), §13.2 (source-defined topology), §14 (AC-03-001), §15
(TRN-SESS-001..013 transition contracts) and §16 (Session Illegal
Transitions); 04_AUTHORITY_AND_DECISION_RIGHTS.md §22..§34
(AUTH-DEP-SESS-001..013); 06_BOUNDARY_ARCHITECTURE.md §13 (BND-007
SESSION / STATE TRANSITION BOUNDARY).

WHAT THIS MODULE IS
-------------------
A declarative transcription of 03's 13 Session transition contracts,
plus a topology evaluator that answers exactly one question:

    is (current state -> requested transition) a pair 03 defines?

WHAT THIS MODULE IS NOT
-----------------------
`STATE_ELIGIBLE` is the wording 06 §13 uses for BND-007's ALLOW
("Transition is state-eligible") and it is deliberately not called
"allowed", "authorized" or "permitted". It is:

    NOT authority        -- 04's AUTH-DEP requirement is unevaluated here
    NOT a boundary result -- BND-001..018 are PKG-08, not PKG-05
    NOT a commit          -- BND-014/CommitUnit are Phase 4
    NOT a precondition check -- 03's PRECONDITIONS reference objects
                            (QuestionBurst, QuestionSelection, ImpactChain,
                            Experiment) that do not exist yet

Every one of those must additionally pass before any consequence
occurs. 06 §13 states the same division from the boundary side:
"BND-007 does not invent authority." A `STATE_ELIGIBLE` verdict is a
necessary condition and never a sufficient one.

WHY AUTHORITY IS A REFERENCE, NOT AN `AuthorityClass`
-----------------------------------------------------
14 §3.1 gives `domain` exactly one permitted internal dependency:
`semantic_types`. `AuthorityClass` (04 §9's closed 7-value Decision
Right vocabulary) lives in `governance`, whose own permitted
dependencies are `domain, semantic_types` -- the sanctioned arrow runs
`governance -> domain`. A `TransitionSpec` holding an `AuthorityClass`
would invert it, and duplicating the vocabulary inside `domain` would
create a second source of truth for a closed list. So each spec
carries the 04 identifier instead. Nothing unapproved is referenceable
(`AuthorityDependency` is closed to the identifiers 04 actually
defines for these transitions), and resolving an identifier to a
concrete Decision Right stays where 04 put it -- materialized by the
authority/boundary layer (PKG-08 onward), which may legitimately
import `governance`.

04's resolution, reproduced here as documentation only (04 §21 summary
table, lines 3770-3783), so a reader never has to guess what an
identifier means:

    AUTH-DEP-SESS-001  Create Session              SESSION_CONTROL_RIGHT
    AUTH-DEP-SESS-002  Begin Setup                 SESSION_CONTROL_RIGHT
    AUTH-DEP-SESS-003  Begin Challenge Capture     SESSION_CONTROL_RIGHT
    AUTH-DEP-SESS-004  Open Question Generation    Facilitator source right
                                                   (LEVEL_1_EXPLICIT; materialized
                                                   through FacilitatorScopeBinding,
                                                   09 §51, table not yet created)
    AUTH-DEP-SESS-005  Close Question Generation   Facilitator source right
                                                   + SYSTEM_DERIVED timer path
    AUTH-DEP-SESS-006  Begin Analysis              controller or bounded System
    AUTH-DEP-SESS-007  Begin Reflection            controller or bounded System
    AUTH-DEP-SESS-008  Begin Question Selection    SESSION_CONTROL_RIGHT
    AUTH-DEP-SESS-009  Begin Investigation         SESSION_CONTROL_RIGHT
    AUTH-DEP-SESS-010  Begin Experiment Phase      SESSION_CONTROL_RIGHT
    AUTH-DEP-SESS-011  Begin Action Phase          SESSION_CONTROL_RIGHT
                                                   + ACTION_DECISION_RIGHT
    AUTH-DEP-SESS-012  Begin Review                SESSION_CONTROL_RIGHT
    AUTH-DEP-SESS-013  Close Session               SESSION_CONTROL_RIGHT

12 §10 narrows the prototype path to SESSION_CONTROL_RIGHT for the
Session rows it lists, but 04 is upstream of 12 and governs.

WHY TRN-CH-001 IS NOT IN THIS REGISTRY
--------------------------------------
03 §12.3 models Challenge creation as an existential transition
ABSENT -> PRESENT and says plainly: "This does not define
`Challenge.status`." There is no Challenge state vocabulary to
register (GAP-02-012 / GAP-03-013 remain OPEN -- see
`domain.challenge`), so TRN-CH-001 has no from/to state pair and does
not belong in a state-transition registry. Registering it with
invented placeholder states would be exactly the collapse 03 §12.2
forbids.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum

from domain.session import TERMINAL_SESSION_STATES, SessionState


class SessionTransitionId(Enum):
    """The 13 transition identifiers 03 §15 defines. Closed."""

    TRN_SESS_001 = "TRN-SESS-001"
    TRN_SESS_002 = "TRN-SESS-002"
    TRN_SESS_003 = "TRN-SESS-003"
    TRN_SESS_004 = "TRN-SESS-004"
    TRN_SESS_005 = "TRN-SESS-005"
    TRN_SESS_006 = "TRN-SESS-006"
    TRN_SESS_007 = "TRN-SESS-007"
    TRN_SESS_008 = "TRN-SESS-008"
    TRN_SESS_009 = "TRN-SESS-009"
    TRN_SESS_010 = "TRN-SESS-010"
    TRN_SESS_011 = "TRN-SESS-011"
    TRN_SESS_012 = "TRN-SESS-012"
    TRN_SESS_013 = "TRN-SESS-013"


class SessionOperation(Enum):
    """The `REQUESTED TRANSITION` name each 03 §15 contract carries.

    Kept distinct from `SessionTransitionId` because 03 uses both: the
    identifier addresses the contract, the operation names what a human
    requests. Neither is a Command -- 09 §62's Process Transition
    Command Registry owns Commands, and 14 assigns no Command to PKG-05.
    """

    CREATE_SESSION = "CREATE_SESSION"
    BEGIN_SETUP = "BEGIN_SETUP"
    BEGIN_CHALLENGE_CAPTURE = "BEGIN_CHALLENGE_CAPTURE"
    OPEN_QUESTION_GENERATION = "OPEN_QUESTION_GENERATION"
    CLOSE_QUESTION_GENERATION = "CLOSE_QUESTION_GENERATION"
    BEGIN_ANALYSIS = "BEGIN_ANALYSIS"
    BEGIN_REFLECTION = "BEGIN_REFLECTION"
    BEGIN_QUESTION_SELECTION = "BEGIN_QUESTION_SELECTION"
    BEGIN_INVESTIGATION = "BEGIN_INVESTIGATION"
    BEGIN_EXPERIMENT_PHASE = "BEGIN_EXPERIMENT_PHASE"
    BEGIN_ACTION_PHASE = "BEGIN_ACTION_PHASE"
    BEGIN_REVIEW = "BEGIN_REVIEW"
    CLOSE_SESSION = "CLOSE_SESSION"


class AuthorityDependency(Enum):
    """04's authority-requirement identifiers for the Session machine.

    Closed to the identifiers 04 §22..§34 actually define. See the
    module docstring for why a `TransitionSpec` references these rather
    than holding a `governance.AuthorityClass` directly.
    """

    AUTH_DEP_SESS_001 = "AUTH-DEP-SESS-001"
    AUTH_DEP_SESS_002 = "AUTH-DEP-SESS-002"
    AUTH_DEP_SESS_003 = "AUTH-DEP-SESS-003"
    AUTH_DEP_SESS_004 = "AUTH-DEP-SESS-004"
    AUTH_DEP_SESS_005 = "AUTH-DEP-SESS-005"
    AUTH_DEP_SESS_006 = "AUTH-DEP-SESS-006"
    AUTH_DEP_SESS_007 = "AUTH-DEP-SESS-007"
    AUTH_DEP_SESS_008 = "AUTH-DEP-SESS-008"
    AUTH_DEP_SESS_009 = "AUTH-DEP-SESS-009"
    AUTH_DEP_SESS_010 = "AUTH-DEP-SESS-010"
    AUTH_DEP_SESS_011 = "AUTH-DEP-SESS-011"
    AUTH_DEP_SESS_012 = "AUTH-DEP-SESS-012"
    AUTH_DEP_SESS_013 = "AUTH-DEP-SESS-013"


class BoundaryDependency(Enum):
    """03's own `BOUNDARY DEPENDENCIES` vocabulary, transcribed verbatim.

    These are 03's names, not 06's BND identifiers. Mapping a name to a
    concrete BND-001..BND-018 evaluator is 06's authority and the
    boundary engine's job (PKG-08); doing it here would mean this
    package deciding, for instance, whether 03's "Human / AI" means
    BND-008, BND-010 or both -- a judgement `domain` has no source
    warrant to make. The values below are exactly the distinct strings
    03 §15 uses across TRN-SESS-001..013.
    """

    IDENTITY = "Identity"
    WORKSPACE = "Workspace"
    AUTHORITY = "Authority"
    METHODOLOGY = "Methodology"
    QUESTION_BURST = "Question Burst"
    HUMAN_AI = "Human / AI"
    AI = "AI"
    AI_CONTEXT = "AI Context"
    PROVENANCE = "Provenance"
    DECISION = "Decision"
    EVIDENCE = "Evidence"
    STATE_TRANSITION = "State Transition"
    PERSISTENCE = "Persistence"
    AUDIT = "Audit"
    FAILURE = "Failure"
    RECOVERY = "Recovery"


class TransitionProofType(Enum):
    """03 §7's typed `REQUIRED EVIDENCE` classes.

    03 §7 exists precisely "to avoid collapsing domain Evidence with
    system proof". `HUMAN_DECISION` is intentionally absent: 03 §7.3
    says a human decision "is not evidence. It is an authority-bearing
    prerequisite where required. It belongs under `AUTHORITY
    REQUIREMENT`, not `REQUIRED EVIDENCE`."
    """

    SYSTEM_PROOF = "SYSTEM_PROOF"
    DOMAIN_EVIDENCE = "DOMAIN_EVIDENCE"
    AI_VALIDATION_PROOF = "AI_VALIDATION_PROOF"


class ProofObligation(Enum):
    """Whether 03 requires a proof type unconditionally.

    03 TRN-SESS-010 and TRN-SESS-011 both qualify DOMAIN_EVIDENCE as
    required "only where later method/07 requires it". Recording that
    qualifier is the difference between referencing an approved
    Evidence requirement and inventing a new sufficiency rule -- which
    14 PKG-05 forbids outright ("EVIDENCE: Only approved references, no
    new sufficiency"). A conditional obligation whose condition cannot
    yet be evaluated fails closed; it never silently becomes "not
    required".
    """

    ALWAYS = "ALWAYS"
    ONLY_WHERE_LATER_CONTRACT_REQUIRES = "ONLY_WHERE_LATER_CONTRACT_REQUIRES"


class CoupledProcessObject(Enum):
    """A second state-owning object whose transition is part of the same
    logical bundle.

    03 TRN-SESS-004 ("This transition is logically coupled to
    QuestionBurst start") and TRN-SESS-005 ("...to QuestionBurst
    completion") each change two objects' states as one transition:
    "The Session and Burst state changes form one logical transition
    bundle... A partial pair is invalid architecture state."
    `QuestionBurst` is a 02 §13 canonical process object; naming it
    here is a reference, not a stub. Its own state machine is PKG-07's,
    so any executor that meets a non-empty coupling set before that
    package exists must fail closed rather than commit half a bundle.
    """

    QUESTION_BURST = "QUESTION_BURST"


@dataclass(frozen=True, slots=True)
class ProofRequirement:
    """One typed proof requirement from a 03 `REQUIRED EVIDENCE` field."""

    proof_type: TransitionProofType
    obligation: ProofObligation


@dataclass(frozen=True, slots=True)
class TransitionSpec:
    """One 03 §15 Session transition contract, as data.

    Frozen and inert: a spec describes requirements, it does not check
    them and cannot perform a transition. Everything it holds is a
    reference into an upstream authority (03 for states and proofs, 04
    for authority, 03's own vocabulary for boundaries), so no field can
    carry a meaning this package invented.

    `from_state is None` means the Session does not yet exist
    (TRN-SESS-001 CURRENT STATE: "Session absent"). It is the only spec
    for which that is true.
    """

    transition_id: SessionTransitionId
    operation: SessionOperation
    from_state: SessionState | None
    to_state: SessionState
    authority_dependency: AuthorityDependency
    required_boundary_dependencies: tuple[BoundaryDependency, ...]
    required_proofs: tuple[ProofRequirement, ...]
    coupled_process_objects: frozenset[CoupledProcessObject]


_SYSTEM_PROOF_ALWAYS = ProofRequirement(TransitionProofType.SYSTEM_PROOF, ProofObligation.ALWAYS)
_AI_VALIDATION_PROOF_ALWAYS = ProofRequirement(
    TransitionProofType.AI_VALIDATION_PROOF, ProofObligation.ALWAYS
)
_DOMAIN_EVIDENCE_CONDITIONAL = ProofRequirement(
    TransitionProofType.DOMAIN_EVIDENCE, ProofObligation.ONLY_WHERE_LATER_CONTRACT_REQUIRES
)

_NO_COUPLING: frozenset[CoupledProcessObject] = frozenset()
_BURST_COUPLED = frozenset({CoupledProcessObject.QUESTION_BURST})

_SPECS: tuple[TransitionSpec, ...] = (
    TransitionSpec(
        transition_id=SessionTransitionId.TRN_SESS_001,
        operation=SessionOperation.CREATE_SESSION,
        from_state=None,
        to_state=SessionState.DRAFT,
        authority_dependency=AuthorityDependency.AUTH_DEP_SESS_001,
        required_boundary_dependencies=(
            BoundaryDependency.IDENTITY,
            BoundaryDependency.WORKSPACE,
            BoundaryDependency.AUTHORITY,
            BoundaryDependency.AUDIT,
        ),
        required_proofs=(_SYSTEM_PROOF_ALWAYS,),
        coupled_process_objects=_NO_COUPLING,
    ),
    TransitionSpec(
        transition_id=SessionTransitionId.TRN_SESS_002,
        operation=SessionOperation.BEGIN_SETUP,
        from_state=SessionState.DRAFT,
        to_state=SessionState.SETUP,
        authority_dependency=AuthorityDependency.AUTH_DEP_SESS_002,
        required_boundary_dependencies=(
            BoundaryDependency.IDENTITY,
            BoundaryDependency.WORKSPACE,
            BoundaryDependency.AUTHORITY,
            BoundaryDependency.STATE_TRANSITION,
            BoundaryDependency.AUDIT,
        ),
        required_proofs=(_SYSTEM_PROOF_ALWAYS,),
        coupled_process_objects=_NO_COUPLING,
    ),
    TransitionSpec(
        transition_id=SessionTransitionId.TRN_SESS_003,
        operation=SessionOperation.BEGIN_CHALLENGE_CAPTURE,
        from_state=SessionState.SETUP,
        to_state=SessionState.CHALLENGE_CAPTURE,
        authority_dependency=AuthorityDependency.AUTH_DEP_SESS_003,
        required_boundary_dependencies=(
            BoundaryDependency.WORKSPACE,
            BoundaryDependency.AUTHORITY,
            BoundaryDependency.METHODOLOGY,
            BoundaryDependency.STATE_TRANSITION,
            BoundaryDependency.AUDIT,
        ),
        # 03 TRN-SESS-003 is explicit: "No epistemic DOMAIN_EVIDENCE required."
        required_proofs=(_SYSTEM_PROOF_ALWAYS,),
        coupled_process_objects=_NO_COUPLING,
    ),
    TransitionSpec(
        transition_id=SessionTransitionId.TRN_SESS_004,
        operation=SessionOperation.OPEN_QUESTION_GENERATION,
        from_state=SessionState.CHALLENGE_CAPTURE,
        to_state=SessionState.QUESTION_GENERATION,
        authority_dependency=AuthorityDependency.AUTH_DEP_SESS_004,
        required_boundary_dependencies=(
            BoundaryDependency.IDENTITY,
            BoundaryDependency.WORKSPACE,
            BoundaryDependency.AUTHORITY,
            BoundaryDependency.QUESTION_BURST,
            BoundaryDependency.METHODOLOGY,
            BoundaryDependency.STATE_TRANSITION,
            BoundaryDependency.AUDIT,
        ),
        required_proofs=(_SYSTEM_PROOF_ALWAYS,),
        coupled_process_objects=_BURST_COUPLED,
    ),
    TransitionSpec(
        transition_id=SessionTransitionId.TRN_SESS_005,
        operation=SessionOperation.CLOSE_QUESTION_GENERATION,
        from_state=SessionState.QUESTION_GENERATION,
        to_state=SessionState.QUESTION_CAPTURE,
        authority_dependency=AuthorityDependency.AUTH_DEP_SESS_005,
        required_boundary_dependencies=(
            BoundaryDependency.WORKSPACE,
            BoundaryDependency.AUTHORITY,
            BoundaryDependency.QUESTION_BURST,
            BoundaryDependency.HUMAN_AI,
            BoundaryDependency.STATE_TRANSITION,
            BoundaryDependency.PERSISTENCE,
            BoundaryDependency.AUDIT,
            BoundaryDependency.FAILURE,
        ),
        required_proofs=(_SYSTEM_PROOF_ALWAYS,),
        coupled_process_objects=_BURST_COUPLED,
    ),
    TransitionSpec(
        transition_id=SessionTransitionId.TRN_SESS_006,
        operation=SessionOperation.BEGIN_ANALYSIS,
        from_state=SessionState.QUESTION_CAPTURE,
        to_state=SessionState.ANALYSIS,
        authority_dependency=AuthorityDependency.AUTH_DEP_SESS_006,
        required_boundary_dependencies=(
            BoundaryDependency.AUTHORITY,
            BoundaryDependency.QUESTION_BURST,
            BoundaryDependency.HUMAN_AI,
            BoundaryDependency.AI_CONTEXT,
            BoundaryDependency.STATE_TRANSITION,
            BoundaryDependency.AUDIT,
            BoundaryDependency.FAILURE,
        ),
        required_proofs=(_SYSTEM_PROOF_ALWAYS,),
        # 03 TRN-SESS-006 requires a COMPLETED Burst as a *precondition*
        # but changes only the Session's state -- unlike 004/005 it is
        # not a two-object bundle.
        coupled_process_objects=_NO_COUPLING,
    ),
    TransitionSpec(
        transition_id=SessionTransitionId.TRN_SESS_007,
        operation=SessionOperation.BEGIN_REFLECTION,
        from_state=SessionState.ANALYSIS,
        to_state=SessionState.REFLECTION,
        authority_dependency=AuthorityDependency.AUTH_DEP_SESS_007,
        required_boundary_dependencies=(
            BoundaryDependency.AUTHORITY,
            BoundaryDependency.AI,
            BoundaryDependency.PROVENANCE,
            BoundaryDependency.STATE_TRANSITION,
            BoundaryDependency.AUDIT,
            BoundaryDependency.FAILURE,
        ),
        # The only transition in the machine that requires an
        # AI_VALIDATION_PROOF. 03 §7.4 is explicit that this "proves
        # processing validity. It does not prove truth or authority" --
        # and TRN-SESS-007's own recovery clause adds "AI failure does
        # not advance state."
        required_proofs=(_AI_VALIDATION_PROOF_ALWAYS, _SYSTEM_PROOF_ALWAYS),
        coupled_process_objects=_NO_COUPLING,
    ),
    TransitionSpec(
        transition_id=SessionTransitionId.TRN_SESS_008,
        operation=SessionOperation.BEGIN_QUESTION_SELECTION,
        from_state=SessionState.REFLECTION,
        to_state=SessionState.QUESTION_SELECTION,
        authority_dependency=AuthorityDependency.AUTH_DEP_SESS_008,
        required_boundary_dependencies=(
            BoundaryDependency.AUTHORITY,
            BoundaryDependency.HUMAN_AI,
            BoundaryDependency.STATE_TRANSITION,
            BoundaryDependency.AUDIT,
        ),
        required_proofs=(_SYSTEM_PROOF_ALWAYS,),
        coupled_process_objects=_NO_COUPLING,
    ),
    TransitionSpec(
        transition_id=SessionTransitionId.TRN_SESS_009,
        operation=SessionOperation.BEGIN_INVESTIGATION,
        from_state=SessionState.QUESTION_SELECTION,
        to_state=SessionState.INVESTIGATION,
        authority_dependency=AuthorityDependency.AUTH_DEP_SESS_009,
        required_boundary_dependencies=(
            BoundaryDependency.AUTHORITY,
            BoundaryDependency.HUMAN_AI,
            BoundaryDependency.DECISION,
            BoundaryDependency.STATE_TRANSITION,
            BoundaryDependency.AUDIT,
        ),
        required_proofs=(_SYSTEM_PROOF_ALWAYS,),
        coupled_process_objects=_NO_COUPLING,
    ),
    TransitionSpec(
        transition_id=SessionTransitionId.TRN_SESS_010,
        operation=SessionOperation.BEGIN_EXPERIMENT_PHASE,
        from_state=SessionState.INVESTIGATION,
        to_state=SessionState.EXPERIMENT,
        authority_dependency=AuthorityDependency.AUTH_DEP_SESS_010,
        required_boundary_dependencies=(
            BoundaryDependency.AUTHORITY,
            BoundaryDependency.EVIDENCE,
            BoundaryDependency.HUMAN_AI,
            BoundaryDependency.STATE_TRANSITION,
            BoundaryDependency.AUDIT,
        ),
        required_proofs=(_SYSTEM_PROOF_ALWAYS, _DOMAIN_EVIDENCE_CONDITIONAL),
        coupled_process_objects=_NO_COUPLING,
    ),
    TransitionSpec(
        transition_id=SessionTransitionId.TRN_SESS_011,
        operation=SessionOperation.BEGIN_ACTION_PHASE,
        from_state=SessionState.EXPERIMENT,
        to_state=SessionState.ACTION,
        authority_dependency=AuthorityDependency.AUTH_DEP_SESS_011,
        required_boundary_dependencies=(
            BoundaryDependency.AUTHORITY,
            BoundaryDependency.DECISION,
            BoundaryDependency.EVIDENCE,
            BoundaryDependency.STATE_TRANSITION,
            BoundaryDependency.AUDIT,
        ),
        required_proofs=(_SYSTEM_PROOF_ALWAYS, _DOMAIN_EVIDENCE_CONDITIONAL),
        coupled_process_objects=_NO_COUPLING,
    ),
    TransitionSpec(
        transition_id=SessionTransitionId.TRN_SESS_012,
        operation=SessionOperation.BEGIN_REVIEW,
        from_state=SessionState.ACTION,
        to_state=SessionState.REVIEW,
        authority_dependency=AuthorityDependency.AUTH_DEP_SESS_012,
        required_boundary_dependencies=(
            BoundaryDependency.AUTHORITY,
            BoundaryDependency.STATE_TRANSITION,
            BoundaryDependency.AUDIT,
        ),
        required_proofs=(_SYSTEM_PROOF_ALWAYS,),
        coupled_process_objects=_NO_COUPLING,
    ),
    TransitionSpec(
        transition_id=SessionTransitionId.TRN_SESS_013,
        operation=SessionOperation.CLOSE_SESSION,
        from_state=SessionState.REVIEW,
        to_state=SessionState.CLOSED,
        authority_dependency=AuthorityDependency.AUTH_DEP_SESS_013,
        required_boundary_dependencies=(
            BoundaryDependency.AUTHORITY,
            BoundaryDependency.STATE_TRANSITION,
            BoundaryDependency.AUDIT,
            BoundaryDependency.FAILURE,
            BoundaryDependency.RECOVERY,
        ),
        required_proofs=(_SYSTEM_PROOF_ALWAYS,),
        coupled_process_objects=_NO_COUPLING,
    ),
)

SESSION_TRANSITION_SPECS: Mapping[SessionTransitionId, TransitionSpec] = {
    spec.transition_id: spec for spec in _SPECS
}
"""The registry. 03 §15 defines exactly these 13 contracts and no others."""

_BY_OPERATION_NAME: Mapping[str, TransitionSpec] = {spec.operation.value: spec for spec in _SPECS}

_BY_STATE_PAIR: Mapping[tuple[SessionState | None, SessionState], TransitionSpec] = {
    (spec.from_state, spec.to_state): spec for spec in _SPECS
}


class SessionTransitionVerdict(Enum):
    """Outcome of the topology evaluation. Default-DENY: every value
    except `STATE_ELIGIBLE` refuses.
    """

    STATE_ELIGIBLE = "STATE_ELIGIBLE"
    """06 §13's wording for BND-007 ALLOW: "Transition is
    state-eligible." Necessary, never sufficient -- see module
    docstring.
    """

    DENIED_UNKNOWN_TRANSITION = "DENIED_UNKNOWN_TRANSITION"
    """No 03 §15 contract carries the requested name. 03 §13.2: "No
    skip transition is legal unless later architecture provides
    explicit source-supported method semantics and authority."
    """

    DENIED_ILLEGAL_TRANSITION = "DENIED_ILLEGAL_TRANSITION"
    """A contract exists but the Session's current state is not its
    `CURRENT STATE`. Covers every pair in 03 §16 and 03 §16's general
    rule: "Skipping a named source state is denied by default."
    """

    DENIED_TERMINAL_STATE = "DENIED_TERMINAL_STATE"
    """03 §13.3 CLOSED: "No further transition inside the same Session
    is legal", and AC-03-001 (03 §14). Reported separately from
    ILLEGAL so that a CLOSED-resurrection attempt is distinguishable in
    proof artifacts from an ordinary out-of-order request.
    """

    DENIED_SESSION_ALREADY_EXISTS = "DENIED_SESSION_ALREADY_EXISTS"
    """TRN-SESS-001 requires CURRENT STATE "Session absent". Requesting
    it against an existing Session is refused rather than silently
    re-creating or resetting one.
    """


@dataclass(frozen=True, slots=True)
class SessionTransitionResolution:
    """A topology verdict plus, when eligible, the governing contract.

    `spec` is populated only on `STATE_ELIGIBLE`, so a caller cannot
    read requirements off a refused resolution and proceed.
    """

    verdict: SessionTransitionVerdict
    spec: TransitionSpec | None
    current_state: SessionState | None
    requested: str

    @property
    def is_state_eligible(self) -> bool:
        return self.verdict is SessionTransitionVerdict.STATE_ELIGIBLE


def _refuse(
    verdict: SessionTransitionVerdict, *, current_state: SessionState | None, requested: str
) -> SessionTransitionResolution:
    return SessionTransitionResolution(
        verdict=verdict, spec=None, current_state=current_state, requested=requested
    )


def _evaluate_by_identifier(
    *,
    current_state: SessionState | None,
    spec: TransitionSpec | None,
    requested: str,
) -> SessionTransitionResolution:
    """Shared evaluation for lookups keyed by a transition *identifier*
    (03 §15 ID, or operation name) -- contexts where `spec is None`
    genuinely means the identifier itself is not recognised. Not used
    for target-state-addressed requests: there, every `target_state` is
    by construction a real `SessionState`, so an unmatched lookup means
    the transition is illegal (or the Session terminal), never that the
    identifier is unknown. See `resolve_session_transition_to_state`.
    """
    if spec is None:
        return _refuse(
            SessionTransitionVerdict.DENIED_UNKNOWN_TRANSITION,
            current_state=current_state,
            requested=requested,
        )
    if current_state is not None and current_state in TERMINAL_SESSION_STATES:
        return _refuse(
            SessionTransitionVerdict.DENIED_TERMINAL_STATE,
            current_state=current_state,
            requested=requested,
        )
    if spec.from_state is None and current_state is not None:
        return _refuse(
            SessionTransitionVerdict.DENIED_SESSION_ALREADY_EXISTS,
            current_state=current_state,
            requested=requested,
        )
    if spec.from_state is not current_state:
        return _refuse(
            SessionTransitionVerdict.DENIED_ILLEGAL_TRANSITION,
            current_state=current_state,
            requested=requested,
        )
    return SessionTransitionResolution(
        verdict=SessionTransitionVerdict.STATE_ELIGIBLE,
        spec=spec,
        current_state=current_state,
        requested=requested,
    )


def resolve_session_transition(
    *, current_state: SessionState | None, transition_id: SessionTransitionId
) -> SessionTransitionResolution:
    """Evaluate a transition addressed by its 03 §15 identifier."""
    return _evaluate_by_identifier(
        current_state=current_state,
        spec=SESSION_TRANSITION_SPECS.get(transition_id),
        requested=transition_id.value,
    )


def resolve_session_transition_by_operation_name(
    *, current_state: SessionState | None, operation_name: str
) -> SessionTransitionResolution:
    """Evaluate a transition requested by name, as an untyped caller supplies it.

    This is the entry point an HTTP controller or worker would reach:
    the requested operation arrives as a string from outside the
    system. An unrecognised name yields `DENIED_UNKNOWN_TRANSITION`
    rather than an exception or a permissive default, which is what
    "Illegal/unknown transition fails closed precommit" (14 PKG-05
    FAILURE_RECOVERY) requires.
    """
    return _evaluate_by_identifier(
        current_state=current_state,
        spec=_BY_OPERATION_NAME.get(operation_name),
        requested=operation_name,
    )


def resolve_session_transition_to_state(
    *, current_state: SessionState | None, target_state: SessionState
) -> SessionTransitionResolution:
    """Evaluate a request expressed as a desired *target state*.

    This is the shape the generic-setter collapse takes: a caller says
    "put this Session into state X". Unlike the identifier-addressed
    evaluators above, `target_state` is always a real `SessionState` --
    there is no "unknown state" case here. An unmatched `(current,
    target)` pair therefore means the transition is illegal (03 §16),
    or, if the current state is already terminal, that no transition at
    all is legal (03 §13.3 / AC-03-001) -- checked first so CLOSED's
    refusal is reported as terminal rather than merely illegal.
    """
    requested = target_state.value
    if current_state is not None and current_state in TERMINAL_SESSION_STATES:
        return _refuse(
            SessionTransitionVerdict.DENIED_TERMINAL_STATE,
            current_state=current_state,
            requested=requested,
        )
    spec = _BY_STATE_PAIR.get((current_state, target_state))
    if spec is None:
        return _refuse(
            SessionTransitionVerdict.DENIED_ILLEGAL_TRANSITION,
            current_state=current_state,
            requested=requested,
        )
    return SessionTransitionResolution(
        verdict=SessionTransitionVerdict.STATE_ELIGIBLE,
        spec=spec,
        current_state=current_state,
        requested=requested,
    )


def legal_state_pairs() -> frozenset[tuple[SessionState | None, SessionState]]:
    """Every `(from, to)` pair 03 §15 registers. Used by the migration
    proof to confirm the database trigger and this registry agree.
    """
    return frozenset(_BY_STATE_PAIR)


__all__ = [
    "SessionTransitionId",
    "SessionOperation",
    "AuthorityDependency",
    "BoundaryDependency",
    "TransitionProofType",
    "ProofObligation",
    "CoupledProcessObject",
    "ProofRequirement",
    "TransitionSpec",
    "SESSION_TRANSITION_SPECS",
    "SessionTransitionVerdict",
    "SessionTransitionResolution",
    "resolve_session_transition",
    "resolve_session_transition_by_operation_name",
    "resolve_session_transition_to_state",
    "legal_state_pairs",
]
