"""Shared real-PostgreSQL helpers for F02 tests.

Every helper drives the REAL governed handler through
`application.composition.GovernedPorts`. None of them insert governed
rows directly, except `insert_user`, which creates an identity only
(HD-3 semantics: identity carries no authority).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from application.challenge_creation_handler import CreateChallengeResult
from application.challenge_creation_handler import create_challenge as _create_challenge
from application.composition import GovernedPorts
from application.membership_operations_handler import add_member as _add_member
from application.workspace_creation_handler import (
    AllowAllWorkspaceCreationEligibilityChecker,
    CreateWorkspaceResult,
    create_workspace,
)
from authority.actor import ActorClass, ActorIdentity
from governance.membership import WorkspaceRole
from persistence.tables import users_table
from persistence.workspace_repository import SqlAlchemyWorkspaceVersionReader
from semantic_types.ids import AttemptId, CommandId, CommitId, CorrelationId, UserId, WorkspaceId
from test_support.clock import FixedClock

NOW = datetime(2026, 9, 24, 9, 0, tzinfo=timezone.utc)


def ports(db: sa.Connection) -> GovernedPorts:
    return GovernedPorts(db, clock=FixedClock(NOW))


def human(user_id: UserId) -> ActorIdentity:
    return ActorIdentity(actor_class=ActorClass.HUMAN_USER, user_id=user_id)


def ids() -> dict[str, object]:
    return {
        "command_id": CommandId(uuid.uuid4()),
        "attempt_id": AttemptId(uuid.uuid4()),
        "correlation_id": CorrelationId(uuid.uuid4()),
        "occurred_at": NOW,
        "commit_id": CommitId(uuid.uuid4()),
    }


def insert_user(db: sa.Connection, label: str) -> UserId:
    user_id = uuid.uuid4()
    db.execute(
        sa.insert(users_table).values(
            id=user_id,
            email=f"{label}-{user_id.hex[:8]}@f02.test",
            name=f"{label.title()} {user_id.hex[:4]}",
            record_version=1,
            created_at=NOW,
            updated_at=NOW,
        )
    )
    return UserId(user_id)


def found_workspace(db: sa.Connection, *, owner: UserId, name: str) -> CreateWorkspaceResult:
    p = ports(db)
    return create_workspace(
        db,
        actor=human(owner),
        workspace_name=name,
        eligibility_checker=AllowAllWorkspaceCreationEligibilityChecker(),
        command_repository=p.commands,
        audit_repository=p.audit,
        outbox_repository=p.outbox,
        commit_repository=p.commits,
        workspace_repository=p.workspaces,
        membership_repository=p.memberships,
        authority_binding_repository=p.bindings,
        **ids(),  # type: ignore[arg-type]
    )


def add_member(
    db: sa.Connection,
    *,
    owner: UserId,
    workspace_id: WorkspaceId,
    member: UserId,
    role: WorkspaceRole = WorkspaceRole.FACILITATOR,
) -> None:
    p = ports(db)
    _add_member(
        db,
        actor=human(owner),
        workspace_id=workspace_id,
        new_member_user_id=member,
        role=role,
        idempotency_key=None,
        workspace_repository=p.workspaces,
        membership_repository=p.memberships,
        authority_resolver=p.resolver,
        command_repository=p.commands,
        audit_repository=p.audit,
        outbox_repository=p.outbox,
        commit_repository=p.commits,
        idempotency_port=p.idempotency,
        current_version_reader=SqlAlchemyWorkspaceVersionReader(db, workspace_id=workspace_id),
        **ids(),  # type: ignore[arg-type]
    )


def create_challenge(
    db: sa.Connection, *, actor: UserId, workspace_id: WorkspaceId, title: str
) -> CreateChallengeResult:
    p = ports(db)
    return _create_challenge(
        db,
        actor=human(actor),
        workspace_id=workspace_id,
        title=title,
        description=None,
        context=None,
        desired_outcome=None,
        constraints=None,
        stakeholders=None,
        idempotency_key=None,
        workspace_repository=p.workspaces,
        membership_repository=p.memberships,
        challenge_repository=p.challenges,
        command_repository=p.commands,
        audit_repository=p.audit,
        outbox_repository=p.outbox,
        commit_repository=p.commits,
        idempotency_port=p.idempotency,
        **ids(),  # type: ignore[arg-type]
    )


def grant(
    db: sa.Connection,
    *,
    owner: UserId,
    workspace_id: WorkspaceId,
    member: UserId,
    authority_class: str,
    scope_type: str,
    scope_id: uuid.UUID,
) -> None:
    from application.authority_binding_handler import grant_human_authority_binding
    from governance.authority_binding import AuthorityClass

    p = ports(db)
    grant_human_authority_binding(
        db,
        actor=human(owner),
        workspace_id=workspace_id,
        human_user_id=member,
        authority_class=AuthorityClass(authority_class),
        scope_type=scope_type,
        scope_id=scope_id,
        idempotency_key=None,
        workspace_repository=p.workspaces,
        membership_repository=p.memberships,
        authority_binding_repository=p.bindings,
        authority_resolver=p.resolver,
        command_repository=p.commands,
        audit_repository=p.audit,
        outbox_repository=p.outbox,
        commit_repository=p.commits,
        idempotency_port=p.idempotency,
        current_version_reader=SqlAlchemyWorkspaceVersionReader(db, workspace_id=workspace_id),
        **ids(),  # type: ignore[arg-type]
    )


def create_session(
    db: sa.Connection, *, actor: UserId, workspace_id: WorkspaceId, challenge_id: object
) -> object:
    from application.session_creation_handler import create_session as _create_session
    from persistence.challenge_repository import SqlAlchemyChallengeVersionReader
    from semantic_types.ids import ChallengeId, SessionId
    from semantic_types.versions import MethodVersion

    p = ports(db)
    session_id = SessionId(uuid.uuid4())
    cid = challenge_id if isinstance(challenge_id, ChallengeId) else ChallengeId(challenge_id)  # type: ignore[arg-type]
    _create_session(
        db,
        actor=human(actor),
        workspace_id=workspace_id,
        challenge_id=cid,
        session_id=session_id,
        applied_method_key="QUESTION_BURST",
        applied_method_version=MethodVersion("1.0"),
        idempotency_key=None,
        workspace_repository=p.workspaces,
        membership_repository=p.memberships,
        challenge_repository=p.challenges,
        session_repository=p.sessions,
        authority_resolver=p.resolver,
        command_repository=p.commands,
        audit_repository=p.audit,
        outbox_repository=p.outbox,
        commit_repository=p.commits,
        idempotency_port=p.idempotency,
        current_version_reader=SqlAlchemyChallengeVersionReader(db, challenge_id=cid),
        **ids(),  # type: ignore[arg-type]
    )
    return session_id


def inquiry_context(db: sa.Connection) -> dict[str, object]:
    """Owner founds, admits a Facilitator, Facilitator creates a Challenge,
    Owner grants Challenge-scoped session control, Facilitator opens a
    Session. All through real governed Commands."""
    owner = insert_user(db, "owner")
    fac = insert_user(db, "facilitator")
    ws = found_workspace(db, owner=owner, name="Inquiry").workspace_id
    add_member(db, owner=owner, workspace_id=ws, member=fac)
    challenge = create_challenge(db, actor=fac, workspace_id=ws, title="Why did it drop?")
    grant(
        db,
        owner=owner,
        workspace_id=ws,
        member=fac,
        authority_class="SESSION_CONTROL_RIGHT",
        scope_type="CHALLENGE",
        scope_id=challenge.challenge_id.value,
    )
    session_id = create_session(db, actor=fac, workspace_id=ws, challenge_id=challenge.challenge_id)
    return {"owner": owner, "fac": fac, "ws": ws, "challenge": challenge, "session": session_id}
