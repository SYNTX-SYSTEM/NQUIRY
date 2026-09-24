"""Shared real-PostgreSQL helpers for F03 tests (built on `f02_support`).

Every helper drives the REAL governed F02 handlers. Nothing here inserts a
governed row directly, except `insert_user`/membership plumbing inherited from
`f02_support` (identity only, HD-3 semantics).
"""

from __future__ import annotations

import uuid
from typing import Any

import f02_support as f02
import sqlalchemy as sa
from application.session_control_handler import (
    CommandIdentity,
    admit_participant,
    begin_challenge_capture,
    begin_setup,
    open_question_generation,
    prepare_burst,
)
from semantic_types.ids import BurstId, SessionId, UserId, WorkspaceId


def ident(key: str | None = None) -> CommandIdentity:
    return CommandIdentity.fresh(f02.NOW, key)


def keyed_ident() -> CommandIdentity:
    """An identity whose idempotency key IS its command id (HTTP contract)."""
    fresh = CommandIdentity.fresh(f02.NOW)
    return CommandIdentity(
        command_id=fresh.command_id,
        attempt_id=fresh.attempt_id,
        correlation_id=fresh.correlation_id,
        commit_id=fresh.commit_id,
        occurred_at=fresh.occurred_at,
        idempotency_key=str(fresh.command_id.value),
    )


def retry(previous: CommandIdentity) -> CommandIdentity:
    """A retry of the same logical Command: same command id / key, NEW attempt
    (09 §12.1), exactly as a second HTTP request carries it."""
    fresh = CommandIdentity.fresh(f02.NOW)
    return CommandIdentity(
        command_id=previous.command_id,
        attempt_id=fresh.attempt_id,
        correlation_id=fresh.correlation_id,
        commit_id=fresh.commit_id,
        occurred_at=f02.NOW,
        idempotency_key=previous.idempotency_key,
    )


def session_of(db: sa.Connection, session_id: SessionId) -> Any:
    return f02.ports(db).sessions.get(session_id)


def _step(db: sa.Connection, fn: Any, ctx: dict[str, Any], actor: UserId, **kw: Any) -> Any:
    session = session_of(db, ctx["session"])
    return fn(
        f02.ports(db),
        actor=f02.human(actor),
        workspace_id=ctx["ws"],
        session_id=ctx["session"],
        expected_session_version=session.record_version.value,
        ident=ident(),
        **kw,
    )


def grant_session_control(db: sa.Connection, ctx: dict[str, Any], member: UserId) -> None:
    f02.grant(
        db,
        owner=ctx["owner"],
        workspace_id=ctx["ws"],
        member=member,
        authority_class="SESSION_CONTROL_RIGHT",
        scope_type="SESSION",
        scope_id=ctx["session"].value,
    )


def add_workspace_member(db: sa.Connection, ctx: dict[str, Any], label: str) -> UserId:
    from governance.membership import WorkspaceRole

    user = f02.insert_user(db, label)
    f02.add_member(
        db, owner=ctx["owner"], workspace_id=ctx["ws"], member=user, role=WorkspaceRole.CONTRIBUTOR
    )
    return user


def prepared_context(db: sa.Connection, *, admit: tuple[UserId, ...] = ()) -> dict[str, Any]:
    """Session at CHALLENGE_CAPTURE with a PREPARED Burst; the Facilitator holds
    SESSION-scoped control; `admit` are admitted as participants."""
    ctx: dict[str, Any] = f02.inquiry_context(db)
    grant_session_control(db, ctx, ctx["fac"])
    _step(db, begin_setup, ctx, ctx["fac"])
    _step(db, begin_challenge_capture, ctx, ctx["fac"])
    _, burst_id = _step(db, prepare_burst, ctx, ctx["fac"])
    ctx["burst"] = burst_id
    for user in admit:
        _step(db, admit_participant, ctx, ctx["fac"], participant_user_id=user)
    return ctx


def generating_context(
    db: sa.Connection, *, participants: int = 2, controller_participates: bool = False
) -> dict[str, Any]:
    """Session at QUESTION_GENERATION with an ACTIVE HUMAN_ONLY Burst.
    `ctx["participants"]` are Workspace members admitted by the controller;
    `ctx["outsider"]` is a Workspace member who is NOT a participant."""
    ctx: dict[str, Any] = f02.inquiry_context(db)
    grant_session_control(db, ctx, ctx["fac"])
    people = [add_workspace_member(db, ctx, f"p{i}") for i in range(participants)]
    ctx["participants"] = people
    ctx["outsider"] = add_workspace_member(db, ctx, "outsider")
    _step(db, begin_setup, ctx, ctx["fac"])
    _step(db, begin_challenge_capture, ctx, ctx["fac"])
    _, burst_id = _step(db, prepare_burst, ctx, ctx["fac"])
    ctx["burst"] = burst_id
    admitted = list(people)
    if controller_participates or not admitted:
        admitted.append(ctx["fac"])
    for user in admitted:
        _step(db, admit_participant, ctx, ctx["fac"], participant_user_id=user)
    _step(db, open_question_generation, ctx, ctx["fac"])
    return ctx


def new_workspace_with_member(db: sa.Connection, label: str) -> tuple[WorkspaceId, UserId]:
    """A second, unrelated Workspace (for cross-Workspace attacks)."""
    owner = f02.insert_user(db, f"{label}-owner")
    ws = f02.found_workspace(db, owner=owner, name=f"Other {label}").workspace_id
    return ws, owner


def burst_of(db: sa.Connection, ctx: dict[str, Any]) -> Any:
    burst_id: BurstId = ctx["burst"]
    return f02.ports(db).bursts.get(burst_id)


def uid() -> uuid.UUID:
    return uuid.uuid4()


def capture(
    db: sa.Connection,
    ctx: dict[str, Any],
    actor: UserId,
    text: str,
    *,
    expected_burst_version: int | None = None,
    ident_: CommandIdentity | None = None,
    workspace_id: WorkspaceId | None = None,
    session_id: SessionId | None = None,
    **kw: Any,
) -> Any:
    """Drive the REAL CMD_CAPTURE_BURST_QUESTION handler."""
    from application.burst_capture_handler import capture_burst_question

    burst = burst_of(db, ctx)
    return capture_burst_question(
        f02.ports(db),
        actor=f02.human(actor),
        workspace_id=workspace_id or ctx["ws"],
        session_id=session_id or ctx["session"],
        original_text=text,
        expected_burst_version=(
            burst.record_version.value if expected_burst_version is None else expected_burst_version
        ),
        ident=ident_ or keyed_ident(),
        **kw,
    )


def question_rows(db: sa.Connection, ctx: dict[str, Any]) -> list[Any]:
    from persistence.tables import questions_table

    return list(
        db.execute(
            sa.select(questions_table).where(questions_table.c.workspace_id == ctx["ws"].value)
        ).mappings()
    )


def membership_rows(db: sa.Connection, ctx: dict[str, Any]) -> list[Any]:
    from persistence.tables import burst_question_memberships_table as m

    return list(
        db.execute(
            sa.select(m)
            .where(m.c.question_burst_id == ctx["burst"].value)
            .order_by(m.c.captured_order.asc())
        ).mappings()
    )


def audit_rows(db: sa.Connection, ctx: dict[str, Any], command_type: str) -> list[Any]:
    from persistence.tables import audit_events_table as a

    return list(
        db.execute(
            sa.select(a).where(
                a.c.workspace_id == ctx["ws"].value, a.c.command_type == command_type
            )
        ).mappings()
    )


def complete(
    db: sa.Connection,
    ctx: dict[str, Any],
    actor: UserId,
    *,
    expected_session_version: int | None = None,
    expected_burst_version: int | None = None,
    ident_: CommandIdentity | None = None,
    **kw: Any,
) -> Any:
    """Drive the REAL CMD_COMPLETE_BURST handler."""
    from application.burst_completion_handler import complete_burst

    session = session_of(db, ctx["session"])
    burst = burst_of(db, ctx)
    return complete_burst(
        f02.ports(db),
        actor=f02.human(actor),
        workspace_id=ctx["ws"],
        session_id=ctx["session"],
        expected_session_version=(
            session.record_version.value
            if expected_session_version is None
            else expected_session_version
        ),
        expected_burst_version=(
            burst.record_version.value if expected_burst_version is None else expected_burst_version
        ),
        ident=ident_ or keyed_ident(),
        **kw,
    )


def principal(user_id: UserId) -> Any:
    from security.identity import AuthenticatedPrincipal

    return AuthenticatedPrincipal(
        user_id=user_id,
        authentication_session_ref="f03-session",
        authentication_time=f02.NOW,
        issuer_ref="https://issuer.example.test",
    )


def position(db: sa.Connection, ctx: dict[str, Any], user: UserId) -> dict[str, Any]:
    from application import inquiry_queries as queries

    return queries.session_position(f02.ports(db), principal(user), ctx["ws"], ctx["session"])
