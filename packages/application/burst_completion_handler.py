"""CMD_COMPLETE_BURST (F03 WU-03.7): TRN-SESS-005 + TRN-BURST-005, ONE bundle.

The holder of `SESSION_CONTROL_RIGHT` at exactly `SESSION:<id>` (HD-9,
NQ-DEC-037, a prototype narrowing of 04 §39; HD-1 for the coupled Session half)
manually closes question generation. In ONE commit:

- the Burst goes ACTIVE -> COMPLETED and stores the frozen-set fingerprint;
- the Session goes QUESTION_GENERATION -> QUESTION_CAPTURE.

`QUESTION_GENERATION -> ANALYSIS` is illegal in 03 §16, so the Session ends this
Field at QUESTION_CAPTURE; TRN-SESS-006 BEGIN_ANALYSIS is F04.

MANUAL ONLY (HD-11 / NQ-DEC-039, NQ-DEC-017): the timer is presentation. There
is no scheduler, no SYSTEM_SERVICE path and no time-based effect. PAUSE/RESUME
is out of scope (HD-10): only an ACTIVE Burst can be completed.

REFUSALS (distinct outcomes, F02 order): stale expected version (`stale`,
before any boundary); not the Session controller (`denied`); not
QUESTION_GENERATION / Burst not ACTIVE, a capture still unresolved (FBR-F03-3),
zero captured Questions (O-6) (`blocked`); BND-014 re-checks versions and the
binding at commit.

CONCURRENCY (FBR-F03-2): the precondition takes the Burst row lock FIRST
(`FOR NO KEY UPDATE`, the same lock every capture takes), re-reads Session and
Burst under it, and only then reads the membership and computes the
fingerprint. An in-flight capture has committed (and is in the set) or has not
started (and will find COMPLETED); a capture can never commit into a set whose
fingerprint was already computed.

FAILURE: Session, Burst and audit are written inside the coordinator's
SAVEPOINT, so a failure before commit leaves no partial freeze.
"""

from __future__ import annotations

from dataclasses import dataclass

from authority.actor import ActorIdentity
from commit.coordinator import (
    CommitUnit,
    CurrentVersionReader,
    FailureInjectionPort,
    MutationOutcome,
)
from domain.burst import BurstState
from domain.burst_membership import compute_frozen_membership_fingerprint
from domain.burst_transitions import BurstTransitionId, resolve_burst_transition
from domain.question_selection import session_target_ref
from domain.session import SessionState
from domain.session_transitions import SessionTransitionId, resolve_session_transition
from events.contracts import EventFacts
from persistence.burst_repository import SqlAlchemyBurstVersionReader, burst_target_ref
from persistence.session_repository import SqlAlchemySessionVersionReader
from semantic_types.ids import SessionId, WorkspaceId
from semantic_types.versions import RecordVersion

from application.composition import GovernedPorts
from application.frozen_set import load_members
from application.session_control_handler import (
    CommandIdentity,
    SessionNotFound,
    SessionPreconditionUnmet,
    SessionVersionStale,
    _FirstReader,
    _run,
    replay_guard,
)

COMMAND_TYPE = "CMD_COMPLETE_BURST"


@dataclass(frozen=True, slots=True)
class CompleteBurstPayload:
    session_id: str
    expected_session_version: int
    expected_burst_version: int


@dataclass(frozen=True, slots=True)
class CompleteResult:
    commit_unit: CommitUnit
    fingerprint: str
    member_count: int


def complete_burst_blocker(
    session_state: SessionState,
    burst_state: BurstState | None,
    *,
    unresolved_capture: bool = False,
    member_count: int | None = None,
) -> str | None:
    """The completion preconditions that are neither authority nor version, in
    one place, shared with the capability projection so the UI affordance can
    never disagree with the Command: state (TRN-SESS-005 / TRN-BURST-005),
    then an unresolved capture (FBR-F03-3), then an empty set (O-6). Facts the
    caller has not loaded are passed as their neutral default."""
    if session_state is not SessionState.QUESTION_GENERATION:
        return f"SESSION_NOT_QUESTION_GENERATION:{session_state.value}"
    if burst_state is None:
        return "BURST_ABSENT"
    if burst_state is not BurstState.ACTIVE:
        return f"BURST_NOT_ACTIVE:{burst_state.value}"
    if not resolve_burst_transition(
        current_state=burst_state, transition_id=BurstTransitionId.TRN_BURST_005
    ).is_state_eligible:
        return "BURST_COMPLETION_NOT_ELIGIBLE"
    if unresolved_capture:
        return "UNRESOLVED_CAPTURE"
    if member_count is not None and member_count == 0:
        # O-6: an empty raw set cannot seed F04's AIOP-001 input.
        return "NO_CAPTURED_QUESTIONS"
    return None


def complete_burst(
    ports: GovernedPorts,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    session_id: SessionId,
    expected_session_version: int,
    expected_burst_version: int,
    ident: CommandIdentity,
    failure_injector: FailureInjectionPort | None = None,
) -> CompleteResult:
    payload = CompleteBurstPayload(
        session_id=str(session_id.value),
        expected_session_version=expected_session_version,
        expected_burst_version=expected_burst_version,
    )
    replay_guard(ports, workspace_id, COMMAND_TYPE, ident, payload)

    session = ports.sessions.get(session_id)
    if session is None:
        raise SessionNotFound(str(session_id.value))
    if session.record_version.value != expected_session_version:
        raise SessionVersionStale(
            expected=expected_session_version,
            current=session.record_version.value,
            current_state=session.state.value,
        )
    burst = ports.bursts.get_by_session(session_id)
    if burst is not None and burst.record_version.value != expected_burst_version:
        raise SessionVersionStale(
            expected=expected_burst_version,
            current=burst.record_version.value,
            current_state=burst.state.value,
        )

    session_ref = session_target_ref(session_id)
    target_refs: tuple[str, ...] = (session_ref,)
    expected: dict[str, RecordVersion] = {session_ref: RecordVersion(expected_session_version)}
    readers: list[CurrentVersionReader] = [
        SqlAlchemySessionVersionReader(ports.connection, session_id=session_id)
    ]
    if burst is not None:
        bref = burst_target_ref(burst.burst_id)
        target_refs = (session_ref, bref)
        expected[bref] = RecordVersion(expected_burst_version)
        readers.append(SqlAlchemyBurstVersionReader(ports.connection, burst_id=burst.burst_id))

    # BND-007 is consulted only when the topology itself allows the transition;
    # a Session that is not in QUESTION_GENERATION is a PRECONDITION (blocked),
    # the same reading F02 applies to a second Burst.
    resolution = (
        resolve_session_transition(
            current_state=session.state, transition_id=SessionTransitionId.TRN_SESS_005
        )
        if session.state is SessionState.QUESTION_GENERATION
        else None
    )

    frozen: dict[str, object] = {}

    def precondition() -> None:
        # FBR-F03-2: lock FIRST, then re-read everything under the lock.
        locked = ports.bursts.get_by_session_for_update(session_id)
        fresh_session = ports.sessions.get(session_id)
        if fresh_session is None:  # pragma: no cover -- rows are never deleted
            raise SessionNotFound(str(session_id.value))
        state_blocker = complete_burst_blocker(
            fresh_session.state, None if locked is None else locked.state
        )
        if state_blocker is not None:
            raise SessionPreconditionUnmet(state_blocker)
        assert locked is not None  # noqa: S101 -- the blocker guarantees it
        unresolved = bool(
            ports.commands.list_unresolved_for_target(
                workspace_id=workspace_id,
                command_type="CMD_CAPTURE_BURST_QUESTION",
                target_ref=burst_target_ref(locked.burst_id),
            )
        )
        members, texts = load_members(ports, locked.burst_id)
        blocker = complete_burst_blocker(
            fresh_session.state,
            locked.state,
            unresolved_capture=unresolved,
            member_count=len(members),
        )
        if blocker is not None:
            raise SessionPreconditionUnmet(blocker)
        frozen["burst"] = locked
        frozen["session"] = fresh_session
        frozen["count"] = len(members)
        frozen["fingerprint"] = compute_frozen_membership_fingerprint(members, texts)

    def mutate() -> MutationOutcome:
        locked = frozen["burst"]
        fresh_session = frozen["session"]
        ports.bursts.complete(
            burst_id=locked.burst_id,  # type: ignore[attr-defined]
            workspace_id=locked.workspace_id,  # type: ignore[attr-defined]
            expected_record_version=locked.record_version,  # type: ignore[attr-defined]
            completed_at=ident.occurred_at,
            frozen_membership_fingerprint=str(frozen["fingerprint"]),
        )
        ports.sessions.transition(
            session_id=session_id,
            from_state=SessionState.QUESTION_GENERATION,
            to_state=SessionState.QUESTION_CAPTURE,
            expected_record_version=fresh_session.record_version,  # type: ignore[attr-defined]
            updated_at=ident.occurred_at,
        )
        return MutationOutcome(
            state_before_ref="session:QUESTION_GENERATION|burst:ACTIVE",
            state_after_ref="session:QUESTION_CAPTURE|burst:COMPLETED",
            event_type="QUESTION_GENERATION_CLOSED",
            result_ref=str(locked.burst_id.value),  # type: ignore[attr-defined]
            event=EventFacts(
                aggregate_ref=session_target_ref(session_id),
                payload={
                    "session_id": str(session_id.value),
                    "previous_state": SessionState.QUESTION_GENERATION.value,
                    "state": SessionState.QUESTION_CAPTURE.value,
                    "burst_id": str(locked.burst_id.value),  # type: ignore[attr-defined]
                    "burst_state": "COMPLETED",
                    "frozen_membership_fingerprint": str(frozen["fingerprint"]),
                    "frozen_member_count": int(frozen["count"]),  # type: ignore[call-overload]
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
        target_refs=target_refs,
        expected_versions=expected,
        created_refs=(),
        reader=_FirstReader(*readers),
        precondition=precondition,
        mutation=mutate,
        failure_injector=failure_injector,
    )
    return CompleteResult(
        commit_unit=unit,
        fingerprint=str(frozen["fingerprint"]),
        member_count=int(frozen["count"]),  # type: ignore[call-overload]
    )


__all__ = [
    "COMMAND_TYPE",
    "CompleteBurstPayload",
    "CompleteResult",
    "complete_burst",
    "complete_burst_blocker",
]
