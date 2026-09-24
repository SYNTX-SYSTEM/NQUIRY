"""F03 WU-03.1 (FBR-F03-5, HD-15 / NQ-DEC-043): PARTICIPATION is the fourth
typed authority source at the effect gate.

MUST BECOME TRUE: BND-014 ALLOWs a `ParticipationAuthority` for an actor with a
CURRENT SessionParticipation in the named Session (ACTIVE membership, same
Workspace), and the ALLOW carries a proof whose source is PARTICIPATION, whose
ref is that participation's id, and whose scope is `SESSION:<id>`. The audit
vocabulary (model + DB CHECK) admits PARTICIPATION.

MUST REMAIN IMPOSSIBLE: an ALLOW for a non-participant; for the controller
without a participation; for a Workspace Owner; for a participation that has
been left; for a participant whose membership is no longer ACTIVE; for a
participation in another Session or another Workspace; for a non-human actor;
a PARTICIPATION ALLOW with no participation reader; encoding the right as ROLE
or BINDING provenance.

FALSIFIER: each MUST-REMAIN case is a test below.
"""

from __future__ import annotations

import uuid

import f02_support as f02
import f03_support as f03
import pytest
import sqlalchemy as sa
from audit.models import AuditEvent
from authority.actor import ActorClass, ActorIdentity
from boundaries.authority_source import AuthoritySourceType, ParticipationAuthority
from boundaries.bnd_014_commit import Bnd014CommitEvaluator, Bnd014Input
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from persistence.session_participation_repository import SqlAlchemySessionParticipationRepository
from persistence.tables import session_participations_table, workspace_memberships_table
from semantic_types.ids import (
    AuditEventId,
    CommandId,
    CommitId,
    CorrelationId,
    SessionId,
    UserId,
    WorkspaceId,
)
from semantic_types.versions import ContractVersion, RecordVersion


def _evaluator(db: sa.Connection, *, with_reader: bool = True) -> Bnd014CommitEvaluator:
    p = f02.ports(db)
    return Bnd014CommitEvaluator(
        p.resolver,
        membership_repository=p.memberships,
        participation_repository=SqlAlchemySessionParticipationRepository(db)
        if with_reader
        else None,
    )


def _evaluate(
    db: sa.Connection,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    session_id: SessionId,
    with_reader: bool = True,
):  # noqa: ANN202
    context = BoundaryContext(
        workspace_id=workspace_id,
        operation="CMD_CAPTURE_BURST_QUESTION",
        actor=actor,
        correlation_id=CorrelationId(uuid.uuid4()),
        evaluated_at=f02.NOW,
    )
    return _evaluator(db, with_reader=with_reader).evaluate(
        Bnd014Input(
            boundary_id=BoundaryId.BND_014,
            context=context,
            authority=ParticipationAuthority(session_id=session_id.value),
            expected_versions={"t": RecordVersion(1)},
            current_versions={"t": RecordVersion(1)},
            upstream_chain_result=BoundaryResult.ALLOW,
        ),
        context,
    )


def test_participant_is_allowed_with_participation_provenance(
    db_connection: sa.Connection,
) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    participant: UserId = ctx["participants"][0]
    participation = SqlAlchemySessionParticipationRepository(db_connection).get_current(
        ctx["session"], participant
    )
    assert participation is not None

    proof = _evaluate(
        db_connection,
        actor=f02.human(participant),
        workspace_id=ctx["ws"],
        session_id=ctx["session"],
    )

    assert proof.result is BoundaryResult.ALLOW
    source = proof.authority_source
    assert source is not None
    assert source.source_type is AuthoritySourceType.PARTICIPATION
    assert source.source_ref == participation.participation_id
    assert source.scope_ref == f"SESSION:{ctx['session'].value}"
    assert "AUTH-DEP-Q-001" in source.detail


def test_non_participant_member_is_denied(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    proof = _evaluate(
        db_connection,
        actor=f02.human(ctx["outsider"]),
        workspace_id=ctx["ws"],
        session_id=ctx["session"],
    )
    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "PARTICIPATION_NOT_CURRENT"
    assert proof.authority_source is None


def test_controller_without_participation_is_denied(db_connection: sa.Connection) -> None:
    # `participants=1` admits only the one participant: the controller is not admitted.
    ctx = f03.generating_context(db_connection, participants=1)
    proof = _evaluate(
        db_connection,
        actor=f02.human(ctx["fac"]),
        workspace_id=ctx["ws"],
        session_id=ctx["session"],
    )
    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "PARTICIPATION_NOT_CURRENT"


def test_workspace_owner_without_participation_is_denied(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    proof = _evaluate(
        db_connection,
        actor=f02.human(ctx["owner"]),
        workspace_id=ctx["ws"],
        session_id=ctx["session"],
    )
    assert proof.result is BoundaryResult.DENY


def test_left_participation_is_denied(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    participant: UserId = ctx["participants"][0]
    # Fixture-level plumbing: leave semantics are NQ-GAP-079 (open); the
    # relation's `left_at` column exists (09 §28) and BND-014 must honour it.
    db_connection.execute(
        sa.update(session_participations_table)
        .where(session_participations_table.c.user_id == participant.value)
        .values(left_at=f02.NOW)
    )
    proof = _evaluate(
        db_connection,
        actor=f02.human(participant),
        workspace_id=ctx["ws"],
        session_id=ctx["session"],
    )
    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "PARTICIPATION_NOT_CURRENT"


def test_participant_whose_membership_is_revoked_is_denied(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    participant: UserId = ctx["participants"][0]
    db_connection.execute(
        sa.update(workspace_memberships_table)
        .where(workspace_memberships_table.c.user_id == participant.value)
        .values(status="REVOKED", revoked_at=f02.NOW)
    )
    proof = _evaluate(
        db_connection,
        actor=f02.human(participant),
        workspace_id=ctx["ws"],
        session_id=ctx["session"],
    )
    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "PARTICIPATION_NO_ACTIVE_MEMBERSHIP"


def test_participation_in_another_session_does_not_authorize(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    participant: UserId = ctx["participants"][0]
    other_session = SessionId(uuid.uuid4())  # a Session the actor never joined
    proof = _evaluate(
        db_connection,
        actor=f02.human(participant),
        workspace_id=ctx["ws"],
        session_id=other_session,
    )
    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "PARTICIPATION_NOT_CURRENT"


def test_participation_does_not_cross_workspaces(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    participant: UserId = ctx["participants"][0]
    other_ws, _ = f03.new_workspace_with_member(db_connection, "x")
    proof = _evaluate(
        db_connection,
        actor=f02.human(participant),
        workspace_id=other_ws,
        session_id=ctx["session"],
    )
    assert proof.result is BoundaryResult.DENY


def test_non_human_actor_is_denied(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    participant: UserId = ctx["participants"][0]
    proof = _evaluate(
        db_connection,
        actor=ActorIdentity(actor_class=ActorClass.AI_PROCESSOR, user_id=participant),
        workspace_id=ctx["ws"],
        session_id=ctx["session"],
    )
    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "PARTICIPATION_ACTOR_NOT_HUMAN"


def test_missing_participation_reader_fails_closed(db_connection: sa.Connection) -> None:
    ctx = f03.generating_context(db_connection, participants=1)
    proof = _evaluate(
        db_connection,
        actor=f02.human(ctx["participants"][0]),
        workspace_id=ctx["ws"],
        session_id=ctx["session"],
        with_reader=False,
    )
    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "PARTICIPATION_READER_NOT_CONFIGURED"


def _audit_event(source_type: str) -> AuditEvent:
    return AuditEvent(
        audit_event_id=AuditEventId(uuid.uuid4()),
        event_type="CMD_CAPTURE_BURST_QUESTION_COMMITTED",
        event_schema_version=ContractVersion("1.0"),
        workspace_id=WorkspaceId(uuid.uuid4()),
        occurred_at=f02.NOW,
        actor_type="HUMAN_USER",
        actor_id=str(uuid.uuid4()),
        command_type="CMD_CAPTURE_BURST_QUESTION",
        command_id=CommandId(uuid.uuid4()),
        commit_id=CommitId(uuid.uuid4()),
        correlation_id=CorrelationId(uuid.uuid4()),
        target_refs=("burst:x",),
        authority_source_ref=uuid.uuid4(),
        result="COMMITTED",
        authority_source_type=source_type,
        authority_scope_ref=f"SESSION:{uuid.uuid4()}",
    )


def test_audit_model_admits_participation_and_still_refuses_unknown() -> None:
    assert _audit_event("PARTICIPATION").authority_source_type == "PARTICIPATION"
    with pytest.raises(ValueError):
        _audit_event("SELF_DECLARED")


def test_audit_db_check_admits_participation(db_connection: sa.Connection) -> None:
    definition = db_connection.execute(
        sa.text(
            "SELECT pg_get_constraintdef(oid) FROM pg_constraint "
            "WHERE conname = 'ck_audit_events_authority_source_type'"
        )
    ).scalar_one()
    for source in ("BINDING", "ROLE", "FOUNDING", "PARTICIPATION"):
        assert source in definition
    assert "SELF_DECLARED" not in definition
