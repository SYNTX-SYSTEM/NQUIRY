"""Read-only canonical listings for the F02 surfaces (WU-02.9).

Plain reads of canonical rows. These are not projections and not authority,
and no "latest" heuristic is applied: every listing is complete and
ordered by creation, and the one "which event established the current
state" lookup matches the Session's own current state and record version
exactly.

Callers (`application.inquiry_queries`) must prove Workspace membership
before calling (BND-001/002/003 via `resolve_workspace_context`). Every
function here takes the Workspace id and filters by it, so a caller can
never read across Workspaces through this module.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

import sqlalchemy as sa

from persistence.tables import (
    audit_events_table,
    burst_question_memberships_table,
    challenges_table,
    human_authority_bindings_table,
    questions_table,
    role_assignments_table,
    sessions_table,
    users_table,
    workspace_memberships_table,
)


@dataclass(frozen=True, slots=True)
class MemberRow:
    user_id: uuid.UUID
    name: str
    email: str
    role: str | None
    joined_at: datetime


@dataclass(frozen=True, slots=True)
class ChallengeRow:
    challenge_id: uuid.UUID
    title: str
    description: str | None
    created_at: datetime


@dataclass(frozen=True, slots=True)
class SessionRow:
    session_id: uuid.UUID
    state: str
    record_version: int
    created_at: datetime


@dataclass(frozen=True, slots=True)
class BindingRow:
    binding_id: uuid.UUID
    human_user_id: uuid.UUID
    human_name: str
    authority_class: str
    scope_type: str
    scope_id: uuid.UUID
    granted_by_user_id: uuid.UUID
    granted_by_name: str
    granted_at: datetime


@dataclass(frozen=True, slots=True)
class TransitionEvidenceRow:
    command_type: str
    actor_id: str
    actor_name: str | None
    occurred_at: datetime
    commit_id: uuid.UUID
    authority_source_type: str | None
    authority_source_ref: uuid.UUID
    authority_scope_ref: str | None


@dataclass(frozen=True, slots=True)
class CapturedQuestionRow:
    """One Question of a Burst's raw set with its capture facts (F03)."""

    membership_id: uuid.UUID
    question_id: uuid.UUID
    original_text: str
    origin: str
    capture_origin: str
    author_user_id: uuid.UUID | None
    author_name: str | None
    captured_order: int
    captured_at: datetime


def list_captured_questions(
    connection: sa.Connection,
    workspace_id: uuid.UUID,
    burst_id: uuid.UUID,
    *,
    only_author: uuid.UUID | None = None,
) -> tuple[CapturedQuestionRow, ...]:
    """The Burst's raw set in capture order. `only_author` filters IN SQL, so
    a caller entitled to only their own Questions (HD-13) never loads anyone
    else's text. The caller decides entitlement; this module only filters."""
    m, q, u = burst_question_memberships_table, questions_table, users_table
    stmt = (
        sa.select(
            m.c.id,
            q.c.id,
            q.c.original_text,
            q.c.origin,
            m.c.capture_origin,
            m.c.capture_actor_user_id,
            u.c.name,
            m.c.captured_order,
            m.c.captured_at,
        )
        .select_from(m)
        .join(q, sa.and_(q.c.id == m.c.question_id, q.c.workspace_id == m.c.workspace_id))
        .outerjoin(u, u.c.id == m.c.capture_actor_user_id)
        .where(m.c.workspace_id == workspace_id, m.c.question_burst_id == burst_id)
        .order_by(m.c.captured_order.asc(), m.c.id.asc())
    )
    if only_author is not None:
        stmt = stmt.where(m.c.capture_actor_user_id == only_author)
    return tuple(CapturedQuestionRow(*row) for row in connection.execute(stmt).all())


def count_captured_questions(
    connection: sa.Connection, workspace_id: uuid.UUID, burst_id: uuid.UUID
) -> int:
    m = burst_question_memberships_table
    return int(
        connection.execute(
            sa.select(sa.func.count()).where(
                m.c.workspace_id == workspace_id, m.c.question_burst_id == burst_id
            )
        ).scalar_one()
    )


def has_governed_founding(connection: sa.Connection, workspace_id: uuid.UUID) -> bool:
    """True iff this Workspace was founded by a committed CMD_CREATE_WORKSPACE
    (HARD-DEP-001 Option A). Workspaces seeded by the NON_PROOF fixture have no
    such audit row; this is the reconstructable fact the UI labels by."""
    a = audit_events_table
    return (
        connection.execute(
            sa.select(sa.func.count())
            .select_from(a)
            .where(a.c.workspace_id == workspace_id, a.c.command_type == "CMD_CREATE_WORKSPACE")
        ).scalar_one()
        > 0
    )


def list_members(connection: sa.Connection, workspace_id: uuid.UUID) -> tuple[MemberRow, ...]:
    m, r, u = workspace_memberships_table, role_assignments_table, users_table
    rows = connection.execute(
        sa.select(u.c.id, u.c.name, u.c.email, r.c.role, m.c.created_at)
        .select_from(m)
        .join(u, u.c.id == m.c.user_id)
        .outerjoin(r, sa.and_(r.c.membership_id == m.c.id, r.c.revoked_at.is_(None)))
        .where(m.c.workspace_id == workspace_id, m.c.status == "ACTIVE")
        .order_by(m.c.created_at.asc(), u.c.id.asc())
    ).all()
    return tuple(MemberRow(row[0], row[1], row[2], row[3], row[4]) for row in rows)


def list_challenges(connection: sa.Connection, workspace_id: uuid.UUID) -> tuple[ChallengeRow, ...]:
    c = challenges_table
    rows = connection.execute(
        sa.select(c.c.id, c.c.title, c.c.description, c.c.created_at)
        .where(c.c.workspace_id == workspace_id)
        .order_by(c.c.created_at.asc(), c.c.id.asc())
    ).all()
    return tuple(ChallengeRow(*row) for row in rows)


def list_sessions(
    connection: sa.Connection, workspace_id: uuid.UUID, challenge_id: uuid.UUID
) -> tuple[SessionRow, ...]:
    s = sessions_table
    rows = connection.execute(
        sa.select(s.c.id, s.c.state, s.c.record_version, s.c.created_at)
        .where(s.c.workspace_id == workspace_id, s.c.challenge_id == challenge_id)
        .order_by(s.c.created_at.asc(), s.c.id.asc())
    ).all()
    return tuple(SessionRow(*row) for row in rows)


def list_active_bindings_at_scope(
    connection: sa.Connection,
    workspace_id: uuid.UUID,
    *,
    authority_class: str,
    scope_type: str,
    scope_id: uuid.UUID,
) -> tuple[BindingRow, ...]:
    """Raw ACTIVE rows at an exact scope (effectiveness is still decided
    by `AuthorityResolver`; this is display provenance only)."""
    b = human_authority_bindings_table
    holder = users_table.alias("holder")
    grantor = users_table.alias("grantor")
    rows = connection.execute(
        sa.select(
            b.c.id,
            b.c.human_user_id,
            holder.c.name,
            b.c.authority_class,
            b.c.scope_type,
            b.c.scope_id,
            b.c.granted_by_user_id,
            grantor.c.name,
            b.c.granted_at,
        )
        .join(holder, holder.c.id == b.c.human_user_id)
        .join(grantor, grantor.c.id == b.c.granted_by_user_id)
        .where(
            b.c.workspace_id == workspace_id,
            b.c.authority_class == authority_class,
            b.c.scope_type == scope_type,
            b.c.scope_id == scope_id,
            b.c.state == "ACTIVE",
        )
        .order_by(b.c.granted_at.asc(), b.c.id.asc())
    ).all()
    return tuple(BindingRow(*row) for row in rows)


def session_state_established_by(
    connection: sa.Connection,
    workspace_id: uuid.UUID,
    session_id: uuid.UUID,
    current_state: str,
) -> TransitionEvidenceRow | None:
    """The committed audit event whose recorded after-state is the
    Session's CURRENT state, for this Session. Exact match on
    `state_after_ref` (`session:<STATE>` or the TRN-SESS-004 bundle form).
    No ORDER BY/LIMIT: a state is reached at most once in the 03 topology
    (no cycles before CLOSED), so more than one row is an invariant
    violation, and `one_or_none` surfaces it instead of picking one."""
    a, u = audit_events_table, users_table
    target = f"session:{session_id}"
    row = connection.execute(
        sa.select(
            a.c.command_type,
            a.c.actor_id,
            u.c.name,
            a.c.occurred_at,
            a.c.commit_id,
            a.c.authority_source_type,
            a.c.authority_source_ref,
            a.c.authority_scope_ref,
        )
        .outerjoin(u, sa.cast(u.c.id, sa.Text) == a.c.actor_id)
        .where(
            a.c.workspace_id == workspace_id,
            a.c.target_refs.any(target),
            sa.or_(
                a.c.state_after_ref == f"session:{current_state}",
                a.c.state_after_ref.like(f"session:{current_state}|%"),
            ),
        )
    ).one_or_none()
    return None if row is None else TransitionEvidenceRow(*row)


__all__ = [
    "BindingRow",
    "CapturedQuestionRow",
    "ChallengeRow",
    "MemberRow",
    "SessionRow",
    "TransitionEvidenceRow",
    "count_captured_questions",
    "has_governed_founding",
    "list_active_bindings_at_scope",
    "list_captured_questions",
    "list_challenges",
    "list_members",
    "list_sessions",
    "session_state_established_by",
]
