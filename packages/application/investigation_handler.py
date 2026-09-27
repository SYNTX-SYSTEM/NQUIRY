"""CMD_BEGIN_INVESTIGATION (WU-PFC-B5): TRN-SESS-009, QUESTION_SELECTION -> INVESTIGATION.

Source: 03 TRN-SESS-009 (PRECONDITIONS: at least one compelling Question
selected; exactly one primary Question; "For the Question Burst method, the
five-level ImpactChain is complete"; "AI may have recommended Questions but may
not create the authority-bearing selection"; REQUIRED EVIDENCE: SYSTEM_PROOF of
the selection relation(s), of exactly one primary, and of the complete
five-level ImpactChain; DENY "Only AI recommendation exists / No primary
Question exists / ImpactChain incomplete / Authority denied"; FAILURE "Session
remains QUESTION_SELECTION"); 03 §40.3, §47.7; 04 AUTH-DEP-SESS-009 (HUMAN_USER,
SESSION_CONTROL_RIGHT at the specific Session; "Selection was created by valid
Question Selection Authority"; "the required human decision is the prior
Question selection, not this operation authorization"; SYSTEM-DERIVED not
required; AUDIT "Link transition authority to selection authority evidence");
HD-26 / NQ-DEC-054 (completion: exactly levels 1..5 in successive order; no
confirmation after level 5).

AUTHORITY: `_run` with SESSION_CONTROL_RIGHT, BINDING at `SESSION:<id>`, BND-001
HUMAN_USER only. No AI path exists (there is no AI-originated selection or
chain to consume).

PRECONDITIONS (`investigation_readiness`, shared with the projection, re-checked
under the Session row lock): the Session is in QUESTION_SELECTION; at least one
COMPELLING selection; exactly one PRIMARY selection; every selection was
created by a QUESTION_SELECTION_RIGHT binding at this Session held by its
selector; the ImpactChain of the current primary is complete. Each unmet
condition is `blocked` and the Session stays in QUESTION_SELECTION.

EFFECT (one commit): the Session becomes INVESTIGATION. The audit links the
transition to the selection authority evidence (every selection and its
binding, and the chain, are relation refs); the event SESSION_INVESTIGATION
records the primary selection, its binding, the compelling count, the chain
and the Fixture status.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from authority.actor import ActorIdentity
from commit.coordinator import CommitUnit, FailureInjectionPort, MutationOutcome
from domain.question_selection import QuestionSelection, SelectionType, session_target_ref
from domain.session import Session, SessionState
from domain.session_transitions import SessionTransitionId, resolve_session_transition
from events.contracts import EventFacts
from governance.authority_binding import AuthorityClass
from persistence.impact_chain_repository import ImpactChain, impact_chain_target_ref
from persistence.question_selection_repository import SqlAlchemyQuestionSelectionRepository
from persistence.session_repository import SqlAlchemySessionVersionReader
from semantic_types.ids import SessionId, WorkspaceId
from semantic_types.versions import RecordVersion

from application.composition import GovernedPorts
from application.impact_chain_handler import current_chain, is_complete
from application.session_control_handler import (
    CommandIdentity,
    SessionNotFound,
    SessionPreconditionUnmet,
    SessionVersionStale,
    _run,
    deny_unless_member,
    replay_guard,
)

COMMAND_TYPE = "CMD_BEGIN_INVESTIGATION"


@dataclass(frozen=True, slots=True)
class BeginInvestigationPayload:
    session_id: str
    expected_session_version: int


@dataclass(frozen=True, slots=True)
class InvestigationBasis:
    """The SYSTEM_PROOF facts TRN-SESS-009 is based on."""

    selections: tuple[QuestionSelection, ...]
    primary: QuestionSelection
    chain: ImpactChain


@dataclass(frozen=True, slots=True)
class InvestigationReadiness:
    blocker: str | None
    basis: InvestigationBasis | None


@dataclass(frozen=True, slots=True)
class BeginInvestigationResult:
    commit_unit: CommitUnit
    basis: InvestigationBasis


def _selection_authority_valid(ports: GovernedPorts, selection: QuestionSelection) -> bool:
    """04 AUTH-DEP-SESS-009: "Selection was created by valid Question Selection
    Authority" -- the stored binding is a QUESTION_SELECTION_RIGHT at exactly
    this Session, held by the selector. (A later revocation does not undo a
    selection validly made; 09 §33.1.)"""
    binding = ports.bindings.get_by_id(selection.human_authority_binding_id)
    return (
        binding is not None
        and binding.workspace_id == selection.workspace_id
        and binding.authority_class is AuthorityClass.QUESTION_SELECTION_RIGHT
        and binding.scope_type == "SESSION"
        and binding.scope_id == selection.session_id.value
        and binding.human_user_id == selection.selected_by_user_id
    )


def investigation_readiness(ports: GovernedPorts, session: Session) -> InvestigationReadiness:
    """The one definition of TRN-SESS-009's preconditions. The first unmet
    condition is reported."""
    if session.state is not SessionState.QUESTION_SELECTION:
        return InvestigationReadiness("SESSION_NOT_IN_QUESTION_SELECTION", None)
    selections = SqlAlchemyQuestionSelectionRepository(ports.connection).list_for_session(
        session.session_id
    )
    if not any(s.selection_type is SelectionType.COMPELLING for s in selections):
        return InvestigationReadiness("NO_COMPELLING_QUESTION_SELECTED", None)
    primaries = [s for s in selections if s.selection_type is SelectionType.PRIMARY]
    if len(primaries) != 1:
        return InvestigationReadiness("NO_PRIMARY_QUESTION", None)
    if not all(_selection_authority_valid(ports, s) for s in selections):
        return InvestigationReadiness("SELECTION_AUTHORITY_INVALID", None)
    chain = current_chain(ports, session.session_id)
    if chain is None or not is_complete(chain):
        return InvestigationReadiness("IMPACT_CHAIN_INCOMPLETE", None)
    return InvestigationReadiness(
        None, InvestigationBasis(selections=selections, primary=primaries[0], chain=chain)
    )


def begin_investigation(
    ports: GovernedPorts,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    session_id: SessionId,
    expected_session_version: int,
    ident: CommandIdentity,
    failure_injector: FailureInjectionPort | None = None,
) -> BeginInvestigationResult:
    payload = BeginInvestigationPayload(
        session_id=str(session_id.value), expected_session_version=expected_session_version
    )
    replay_guard(ports, workspace_id, COMMAND_TYPE, ident, payload)

    session = ports.sessions.get(session_id)
    deny_unless_member(
        ports,
        actor=actor,
        workspace_id=workspace_id,
        session=session,
        operation=COMMAND_TYPE,
        ident=ident,
    )
    if session is None:
        raise SessionNotFound(str(session_id.value))
    if session.record_version.value != expected_session_version:
        raise SessionVersionStale(
            expected=expected_session_version,
            current=session.record_version.value,
            current_state=session.state.value,
        )

    session_ref = session_target_ref(session_id)
    resolution = (
        resolve_session_transition(
            current_state=session.state, transition_id=SessionTransitionId.TRN_SESS_009
        )
        if session.state is SessionState.QUESTION_SELECTION
        else None
    )
    ready: dict[str, Any] = {}

    def precondition() -> None:
        fresh = ports.sessions.get_for_update(session_id)
        if fresh is None:  # pragma: no cover -- rows are never deleted
            raise SessionNotFound(str(session_id.value))
        readiness = investigation_readiness(ports, fresh)
        if readiness.blocker is not None:
            raise SessionPreconditionUnmet(readiness.blocker)
        assert readiness.basis is not None  # noqa: S101 -- no blocker means a basis
        ready["basis"] = readiness.basis
        ready["session"] = fresh

    def mutate() -> MutationOutcome:
        fresh = ready["session"]
        basis: InvestigationBasis = ready["basis"]
        ports.sessions.transition(
            session_id=session_id,
            from_state=SessionState.QUESTION_SELECTION,
            to_state=SessionState.INVESTIGATION,
            expected_record_version=fresh.record_version,
            updated_at=ident.occurred_at,
        )
        return MutationOutcome(
            state_before_ref="session:QUESTION_SELECTION",
            state_after_ref="session:INVESTIGATION",
            relation_refs=(
                *(f"question_selection:{s.question_selection_id.value}" for s in basis.selections),
                *sorted(
                    {
                        f"authority_binding:{s.human_authority_binding_id.value}"
                        for s in basis.selections
                    }
                ),
                impact_chain_target_ref(basis.chain.impact_chain_id),
            ),
            event_type="SESSION_INVESTIGATION",
            result_ref=str(basis.primary.question_selection_id.value),
            event=EventFacts(
                aggregate_ref=session_ref,
                payload={
                    "session_id": str(session_id.value),
                    "previous_state": SessionState.QUESTION_SELECTION.value,
                    "state": SessionState.INVESTIGATION.value,
                    "fixture": fresh.fixture,
                    "primary_question_id": str(basis.primary.question_id.value),
                    "primary_selection_id": str(basis.primary.question_selection_id.value),
                    "primary_selection_binding_id": str(
                        basis.primary.human_authority_binding_id.value
                    ),
                    "compelling_count": sum(
                        1 for s in basis.selections if s.selection_type is SelectionType.COMPELLING
                    ),
                    "impact_chain_id": str(basis.chain.impact_chain_id),
                },
            ),
        )

    unit = _run(
        ports,
        actor=actor,
        workspace_id=workspace_id,
        session=session,
        session_id=session_id,
        command_type=COMMAND_TYPE,
        payload=payload,
        ident=ident,
        resolution=resolution,
        target_refs=(session_ref,),
        expected_versions={session_ref: RecordVersion(expected_session_version)},
        created_refs=(),
        reader=SqlAlchemySessionVersionReader(ports.connection, session_id=session_id),
        precondition=precondition,
        mutation=mutate,
        failure_injector=failure_injector,
    )
    return BeginInvestigationResult(commit_unit=unit, basis=ready["basis"])


__all__ = [
    "COMMAND_TYPE",
    "BeginInvestigationPayload",
    "BeginInvestigationResult",
    "InvestigationBasis",
    "InvestigationReadiness",
    "begin_investigation",
    "investigation_readiness",
]
