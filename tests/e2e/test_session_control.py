"""F02 WU-02.7/02.8: Session transitions, Burst preparation, participation and
the TRN-SESS-004 bundle, against real PostgreSQL, through real handlers.

MUST BECOME TRUE: an explicitly Session-scoped controller lawfully walks
DRAFT → SETUP → CHALLENGE_CAPTURE, prepares a HUMAN_ONLY Burst, admits a
participant, and opens QUESTION_GENERATION with the Burst ACTIVE in the
same commit. Audit provenance names the SESSION-scoped binding.

MUST REMAIN IMPOSSIBLE (HD-1/HD-7/HD-8): Challenge- or Workspace-scoped
control moving a Session; an Owner without a Session binding moving it; a
stale version committing; a cross-Workspace actor acting; opening Question
Generation without a participant, without a PREPARED Burst, or so that the
Session commits without the Burst (or vice versa); admitting a non-member;
admitting the same participant twice; a second Burst for one Session.
"""

from __future__ import annotations

import uuid

import f02_support as f02
import pytest
import sqlalchemy as sa
from application.session_control_handler import (
    CommandIdentity,
    SessionCommandDenied,
    SessionPreconditionUnmet,
    SessionVersionStale,
    admit_participant,
    begin_challenge_capture,
    begin_setup,
    open_question_generation,
    prepare_burst,
)
from commit.coordinator import CommitFailedPrecommit
from domain.burst import BurstState
from domain.session import SessionState
from persistence.tables import (
    audit_events_table,
    human_authority_bindings_table,
    session_participations_table,
)
from semantic_types.ids import SessionId, UserId, WorkspaceId


def _ident() -> CommandIdentity:
    return CommandIdentity.fresh(f02.NOW)


def _session(db: sa.Connection, sid: SessionId):  # noqa: ANN202
    return f02.ports(db).sessions.get(sid)


def _grant_session_control(db: sa.Connection, ctx: dict, member: UserId) -> None:  # type: ignore[type-arg]
    f02.grant(
        db,
        owner=ctx["owner"],
        workspace_id=ctx["ws"],
        member=member,
        authority_class="SESSION_CONTROL_RIGHT",
        scope_type="SESSION",
        scope_id=ctx["session"].value,
    )


def _step(db: sa.Connection, fn, ctx: dict, actor: UserId, **kw):  # type: ignore[no-untyped-def,type-arg]
    session = _session(db, ctx["session"])
    return fn(
        f02.ports(db),
        actor=f02.human(actor),
        workspace_id=ctx["ws"],
        session_id=ctx["session"],
        expected_session_version=session.record_version.value,
        ident=_ident(),
        **kw,
    )


def test_lawful_path_reaches_question_generation_with_active_burst(
    db_connection: sa.Connection,
) -> None:
    ctx = f02.inquiry_context(db_connection)
    _grant_session_control(db_connection, ctx, ctx["fac"])

    _step(db_connection, begin_setup, ctx, ctx["fac"])
    assert _session(db_connection, ctx["session"]).state is SessionState.SETUP
    _step(db_connection, begin_challenge_capture, ctx, ctx["fac"])
    assert _session(db_connection, ctx["session"]).state is SessionState.CHALLENGE_CAPTURE
    _, burst_id = _step(db_connection, prepare_burst, ctx, ctx["fac"])
    burst = f02.ports(db_connection).bursts.get(burst_id)
    assert burst is not None and burst.state is BurstState.PREPARED
    _step(db_connection, admit_participant, ctx, ctx["fac"], participant_user_id=ctx["owner"])
    unit = _step(db_connection, open_question_generation, ctx, ctx["fac"])

    session = _session(db_connection, ctx["session"])
    assert session.state is SessionState.QUESTION_GENERATION
    burst = f02.ports(db_connection).bursts.get(burst_id)
    assert burst is not None and burst.state is BurstState.ACTIVE and burst.started_at == f02.NOW

    # Provenance: BINDING at SESSION:<id>, ref = the real Session-scoped binding.
    row = (
        db_connection.execute(
            sa.select(audit_events_table).where(
                audit_events_table.c.commit_id == unit.commit_id.value
            )
        )
        .mappings()
        .one()
    )
    assert row["command_type"] == "CMD_OPEN_QUESTION_GENERATION"
    assert row["authority_source_type"] == "BINDING"
    assert row["authority_scope_ref"] == f"SESSION:{ctx['session'].value}"
    binding = (
        db_connection.execute(
            sa.select(human_authority_bindings_table).where(
                human_authority_bindings_table.c.id == row["authority_source_ref"]
            )
        )
        .mappings()
        .one()
    )
    assert binding["scope_type"] == "SESSION" and binding["human_user_id"] == ctx["fac"].value
    # The bundle is reconstructable together: both targets on one audit row.
    assert f"session:{ctx['session'].value}" in row["target_refs"]
    assert f"burst:{burst_id.value}" in row["target_refs"]


def test_challenge_scoped_control_does_not_move_the_session(db_connection: sa.Connection) -> None:
    """HD-1: no Challenge→Session inheritance (the facilitator holds CHALLENGE scope only)."""
    ctx = f02.inquiry_context(db_connection)
    with pytest.raises(SessionCommandDenied):
        _step(db_connection, begin_setup, ctx, ctx["fac"])
    assert _session(db_connection, ctx["session"]).state is SessionState.DRAFT


def test_workspace_scoped_control_does_not_move_the_session(db_connection: sa.Connection) -> None:
    ctx = f02.inquiry_context(db_connection)
    f02.grant(
        db_connection,
        owner=ctx["owner"],
        workspace_id=ctx["ws"],
        member=ctx["fac"],
        authority_class="SESSION_CONTROL_RIGHT",
        scope_type="WORKSPACE",
        scope_id=ctx["ws"].value,
    )
    with pytest.raises(SessionCommandDenied):
        _step(db_connection, begin_setup, ctx, ctx["fac"])


def test_owner_without_session_binding_is_denied(db_connection: sa.Connection) -> None:
    ctx = f02.inquiry_context(db_connection)
    _grant_session_control(db_connection, ctx, ctx["fac"])
    with pytest.raises(SessionCommandDenied):
        _step(db_connection, begin_setup, ctx, ctx["owner"])


def test_binding_for_another_session_is_denied(db_connection: sa.Connection) -> None:
    ctx = f02.inquiry_context(db_connection)
    other = f02.create_session(
        db_connection,
        actor=ctx["fac"],
        workspace_id=ctx["ws"],
        challenge_id=ctx["challenge"].challenge_id,
    )
    f02.grant(
        db_connection,
        owner=ctx["owner"],
        workspace_id=ctx["ws"],
        member=ctx["fac"],
        authority_class="SESSION_CONTROL_RIGHT",
        scope_type="SESSION",
        scope_id=other.value,  # type: ignore[attr-defined]
    )
    with pytest.raises(SessionCommandDenied):
        _step(db_connection, begin_setup, ctx, ctx["fac"])


def test_stale_version_is_stale_not_denied(db_connection: sa.Connection) -> None:
    ctx = f02.inquiry_context(db_connection)
    _grant_session_control(db_connection, ctx, ctx["fac"])
    _step(db_connection, begin_setup, ctx, ctx["fac"])
    with pytest.raises(SessionVersionStale) as info:
        begin_setup(
            f02.ports(db_connection),
            actor=f02.human(ctx["fac"]),
            workspace_id=ctx["ws"],
            session_id=ctx["session"],
            expected_session_version=1,
            ident=_ident(),
        )
    assert info.value.current == 2 and info.value.current_state == "SETUP"


def test_cross_workspace_actor_is_denied(db_connection: sa.Connection) -> None:
    ctx = f02.inquiry_context(db_connection)
    outsider = f02.insert_user(db_connection, "outsider")
    other_ws = f02.found_workspace(db_connection, owner=outsider, name="Elsewhere").workspace_id
    # Claims its own Workspace for a foreign Session: BND-002 denies.
    with pytest.raises(SessionCommandDenied):
        begin_setup(
            f02.ports(db_connection),
            actor=f02.human(outsider),
            workspace_id=other_ws,
            session_id=ctx["session"],
            expected_session_version=1,
            ident=_ident(),
        )
    # Claims the Session's real Workspace: not a member, denied.
    with pytest.raises(SessionCommandDenied):
        begin_setup(
            f02.ports(db_connection),
            actor=f02.human(outsider),
            workspace_id=ctx["ws"],
            session_id=ctx["session"],
            expected_session_version=1,
            ident=_ident(),
        )
    # Unknown Workspace id: denied without a commands row.
    with pytest.raises(SessionCommandDenied):
        begin_setup(
            f02.ports(db_connection),
            actor=f02.human(outsider),
            workspace_id=WorkspaceId(uuid.uuid4()),
            session_id=ctx["session"],
            expected_session_version=1,
            ident=_ident(),
        )
    assert _session(db_connection, ctx["session"]).state is SessionState.DRAFT


def test_illegal_transition_is_denied_by_topology(db_connection: sa.Connection) -> None:
    ctx = f02.inquiry_context(db_connection)
    _grant_session_control(db_connection, ctx, ctx["fac"])
    with pytest.raises(SessionCommandDenied) as info:
        _step(
            db_connection, begin_challenge_capture, ctx, ctx["fac"]
        )  # DRAFT → CHALLENGE_CAPTURE skips SETUP
    from boundaries.types import BoundaryId

    assert info.value.chain_result.terminal_boundary_id is BoundaryId.BND_007


def _to_challenge_capture(db: sa.Connection) -> dict:  # type: ignore[type-arg]
    ctx = f02.inquiry_context(db)
    _grant_session_control(db, ctx, ctx["fac"])
    _step(db, begin_setup, ctx, ctx["fac"])
    _step(db, begin_challenge_capture, ctx, ctx["fac"])
    return ctx


def test_question_generation_is_blocked_without_burst_and_without_participant(
    db_connection: sa.Connection,
) -> None:
    ctx = _to_challenge_capture(db_connection)
    with pytest.raises(SessionPreconditionUnmet, match="BURST_ABSENT"):
        _step(db_connection, open_question_generation, ctx, ctx["fac"])
    _step(db_connection, prepare_burst, ctx, ctx["fac"])
    with pytest.raises(SessionPreconditionUnmet, match="NO_SESSION_PARTICIPANT"):
        _step(db_connection, open_question_generation, ctx, ctx["fac"])
    assert _session(db_connection, ctx["session"]).state is SessionState.CHALLENGE_CAPTURE


def test_second_burst_is_blocked(db_connection: sa.Connection) -> None:
    ctx = _to_challenge_capture(db_connection)
    _step(db_connection, prepare_burst, ctx, ctx["fac"])
    with pytest.raises(SessionPreconditionUnmet, match="BURST_ALREADY_EXISTS"):
        _step(db_connection, prepare_burst, ctx, ctx["fac"])


def test_admission_requires_active_member_and_is_not_repeatable(
    db_connection: sa.Connection,
) -> None:
    ctx = _to_challenge_capture(db_connection)
    stranger = f02.insert_user(db_connection, "stranger")
    with pytest.raises(SessionPreconditionUnmet, match="PARTICIPANT_NOT_ACTIVE_MEMBER"):
        _step(db_connection, admit_participant, ctx, ctx["fac"], participant_user_id=stranger)
    _step(db_connection, admit_participant, ctx, ctx["fac"], participant_user_id=ctx["owner"])
    with pytest.raises(SessionPreconditionUnmet, match="ALREADY_PARTICIPANT"):
        _step(db_connection, admit_participant, ctx, ctx["fac"], participant_user_id=ctx["owner"])


def test_owner_cannot_admit_without_session_control(db_connection: sa.Connection) -> None:
    ctx = _to_challenge_capture(db_connection)
    with pytest.raises(SessionCommandDenied):
        _step(db_connection, admit_participant, ctx, ctx["owner"], participant_user_id=ctx["owner"])


def test_db_rejects_participation_for_non_member(db_connection: sa.Connection) -> None:
    ctx = f02.inquiry_context(db_connection)
    stranger = f02.insert_user(db_connection, "raw")
    with (
        pytest.raises(sa.exc.DBAPIError, match="ACTIVE workspace_membership"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.insert(session_participations_table).values(
                id=uuid.uuid4(),
                session_id=ctx["session"].value,
                workspace_id=ctx["ws"].value,
                user_id=stranger.value,
                joined_at=f02.NOW,
                left_at=None,
                admitted_by_user_id=ctx["owner"].value,
                record_version=1,
            )
        )


def test_bundle_is_atomic_when_the_burst_moved_underneath(db_connection: sa.Connection) -> None:
    """TRN-SESS-004: 'A partial pair is invalid architecture state.' The Burst
    advancing between read and commit must leave the Session untouched."""
    ctx = _to_challenge_capture(db_connection)
    _, burst_id = _step(db_connection, prepare_burst, ctx, ctx["fac"])
    _step(db_connection, admit_participant, ctx, ctx["fac"], participant_user_id=ctx["owner"])
    session = _session(db_connection, ctx["session"])
    ports = f02.ports(db_connection)
    burst = ports.bursts.get(burst_id)
    assert burst is not None

    class _RacingBursts:
        """Delegates to the real repository, but a concurrent writer
        advances the Burst right before this bundle's own start()."""

        def __init__(self, real):  # type: ignore[no-untyped-def]
            self._real = real

        def __getattr__(self, name):  # type: ignore[no-untyped-def]
            return getattr(self._real, name)

        def start(self, **kw):  # type: ignore[no-untyped-def]
            db_connection.execute(
                sa.text(
                    "UPDATE question_bursts SET record_version = record_version + 1 WHERE id = :id"
                ),
                {"id": burst_id.value},
            )
            return self._real.start(**kw)

    ports.bursts = _RacingBursts(ports.bursts)  # type: ignore[assignment]
    with pytest.raises(CommitFailedPrecommit):
        open_question_generation(
            ports,
            actor=f02.human(ctx["fac"]),
            workspace_id=ctx["ws"],
            session_id=ctx["session"],
            expected_session_version=session.record_version.value,
            ident=_ident(),
        )
    assert _session(db_connection, ctx["session"]).state is SessionState.CHALLENGE_CAPTURE
    fresh = f02.ports(db_connection).bursts.get(burst_id)
    assert fresh is not None and fresh.state is BurstState.PREPARED
