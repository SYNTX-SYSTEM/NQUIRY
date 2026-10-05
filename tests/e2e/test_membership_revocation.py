"""WU-AUTHZ-01: 05 GOV-003 REVOKE_MEMBERSHIP and GOV-004 ASSIGN_ROLE (change
of the current role) — the two governance successors the add-member Command
left as SUCCESSOR_NOT_BUILT. Real PostgreSQL, real boundary chain, real
CommitCoordinator; no mocks.

MUST BECOME TRUE: the governance root ends a membership — the membership is
REVOKED, its current role ended, every Workspace binding of the member
revoked in the SAME commit (09 §102.1), one audit event naming them; the
member loses every authority on the next resolution and can be re-added as a
new membership (old bindings not restored). The root changes a member's role
— the prior assignment ends, a new one is current, before/after audited.

MUST REMAIN IMPOSSIBLE: removing or re-labelling the governance root
(GAP-05-001; 05 §12 / §14 / L752); any of this by a non-root member, a
non-member or a non-human; an unknown or already-revoked target (one class);
assigning Owner; a no-op role change; a stale membership version committing.
"""

from __future__ import annotations

import uuid

import pytest
import sqlalchemy as sa
from application.membership_operations_handler import (
    AddMemberDenied,
    GovernanceRootNotRemovable,
    MembershipNotFound,
    OwnerRoleNotAssignable,
    RoleUnchanged,
    change_member_role,
    revoke_membership,
)
from authority.actor import ActorClass, ActorIdentity
from authority.resolver import AuthorityRequest, AuthorityVerdict
from commit.coordinator import CommitDenied
from commit.idempotency import SqlAlchemyIdempotencyRepository
from f02_support import grant
from governance.authority_binding import AuthorityBindingState, AuthorityClass
from governance.membership import MembershipStatus, WorkspaceRole
from persistence.audit_repository import SqlAlchemyAuditRepository
from persistence.authority_binding_repository import SqlAlchemyAuthorityBindingRepository
from persistence.command_repository import SqlAlchemyCommandRepository
from persistence.commit_repository import SqlAlchemyCommitRepository
from persistence.membership_repository import (
    SqlAlchemyMembershipRepository,
    SqlAlchemyMembershipVersionReader,
)
from persistence.outbox_repository import SqlAlchemyOutboxRepository
from persistence.tables import (
    audit_events_table,
    commit_units_table,
    committed_events_table,
    human_authority_bindings_table,
    role_assignments_table,
    workspace_memberships_table,
)
from persistence.workspace_repository import (
    SqlAlchemyWorkspaceRepository,
    SqlAlchemyWorkspaceVersionReader,
)
from semantic_types.ids import AttemptId, CommandId, CommitId, CorrelationId, UserId, WorkspaceId
from semantic_types.versions import RecordVersion
from test_membership_operations import (
    _NOW,
    _add,
    _found_workspace,
    _human_actor,
    _insert_user,
    _resolver,
)


def _ports(db: sa.Connection) -> dict[str, object]:
    return {
        "workspace_repository": SqlAlchemyWorkspaceRepository(db),
        "membership_repository": SqlAlchemyMembershipRepository(db),
        "binding_repository": SqlAlchemyAuthorityBindingRepository(db),
        "authority_resolver": _resolver(db),
        "command_repository": SqlAlchemyCommandRepository(db),
        "audit_repository": SqlAlchemyAuditRepository(db),
        "outbox_repository": SqlAlchemyOutboxRepository(db),
        "commit_repository": SqlAlchemyCommitRepository(db),
        "idempotency_port": SqlAlchemyIdempotencyRepository(db),
    }


def _reader(db: sa.Connection, workspace_id: WorkspaceId, member: UserId):  # type: ignore[no-untyped-def]
    membership = SqlAlchemyMembershipRepository(db).get_current_membership(workspace_id, member)
    if membership is None:
        return SqlAlchemyWorkspaceVersionReader(db, workspace_id=workspace_id)
    return SqlAlchemyMembershipVersionReader(db, membership_id=membership.id)


def _revoke(db: sa.Connection, *, actor: ActorIdentity, workspace_id: WorkspaceId, member: UserId):  # type: ignore[no-untyped-def]
    return revoke_membership(
        db,
        actor=actor,
        workspace_id=workspace_id,
        member_user_id=member,
        command_id=CommandId(uuid.uuid4()),
        attempt_id=AttemptId(uuid.uuid4()),
        correlation_id=CorrelationId(uuid.uuid4()),
        occurred_at=_NOW,
        commit_id=CommitId(uuid.uuid4()),
        idempotency_key=None,
        current_version_reader=_reader(db, workspace_id, member),
        **_ports(db),  # type: ignore[arg-type]
    )


def _change(
    db: sa.Connection,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    member: UserId,
    role: WorkspaceRole,
):  # type: ignore[no-untyped-def]
    return change_member_role(
        db,
        actor=actor,
        workspace_id=workspace_id,
        member_user_id=member,
        role=role,
        command_id=CommandId(uuid.uuid4()),
        attempt_id=AttemptId(uuid.uuid4()),
        correlation_id=CorrelationId(uuid.uuid4()),
        occurred_at=_NOW,
        commit_id=CommitId(uuid.uuid4()),
        idempotency_key=None,
        current_version_reader=_reader(db, workspace_id, member),
        **_ports(db),  # type: ignore[arg-type]
    )


def _world(db: sa.Connection) -> tuple[UserId, UserId, WorkspaceId, uuid.UUID]:
    owner = _insert_user(db, email=f"owner-{uuid.uuid4()}@example.test")
    member = _insert_user(db, email=f"member-{uuid.uuid4()}@example.test")
    workspace_id = _found_workspace(db, owner=owner, name="Revocation Field")
    _add(db, actor=_human_actor(owner), workspace_id=workspace_id, new_member_user_id=member)
    membership_id = (
        SqlAlchemyMembershipRepository(db).get_current_membership(workspace_id, member).id
    )  # type: ignore[union-attr]
    return owner, member, workspace_id, membership_id


def _holds(
    db: sa.Connection,
    workspace_id: WorkspaceId,
    member: UserId,
    cls: AuthorityClass,
    scope_type: str,
    scope_id: uuid.UUID,
) -> bool:
    verdict = (
        _resolver(db)
        .resolve(
            AuthorityRequest(
                actor=_human_actor(member),
                workspace_id=workspace_id,
                operation="PROBE",
                required_authority_class=cls,
                scope_type=scope_type,
                scope_id=scope_id,
            )
        )
        .verdict
    )
    return verdict is AuthorityVerdict.GRANTED


# ---------------------------------------------------------------- GOV-003


def test_the_root_revokes_a_membership_with_its_role_and_bindings_in_one_commit(
    db_connection: sa.Connection,
) -> None:
    owner, member, ws, membership_id = _world(db_connection)
    grant(
        db_connection,
        owner=owner,
        workspace_id=ws,
        member=member,
        authority_class="QUESTION_SELECTION_RIGHT",
        scope_type="WORKSPACE",
        scope_id=ws.value,
    )
    assert _holds(
        db_connection, ws, member, AuthorityClass.QUESTION_SELECTION_RIGHT, "WORKSPACE", ws.value
    )
    unit = _revoke(db_connection, actor=_human_actor(owner), workspace_id=ws, member=member)

    membership = (
        db_connection.execute(
            sa.select(workspace_memberships_table).where(
                workspace_memberships_table.c.id == membership_id
            )
        )
        .mappings()
        .one()
    )
    assert membership["status"] == MembershipStatus.REVOKED.value
    assert membership["revoked_at"] is not None and membership["record_version"] == 2
    roles = (
        db_connection.execute(
            sa.select(role_assignments_table).where(
                role_assignments_table.c.membership_id == membership_id
            )
        )
        .mappings()
        .all()
    )
    assert len(roles) == 1 and roles[0]["revoked_at"] is not None
    bindings = (
        db_connection.execute(
            sa.select(human_authority_bindings_table).where(
                human_authority_bindings_table.c.workspace_id == ws.value,
                human_authority_bindings_table.c.human_user_id == member.value,
            )
        )
        .mappings()
        .all()
    )
    assert len(bindings) == 1
    assert bindings[0]["state"] == AuthorityBindingState.REVOKED.value
    assert bindings[0]["revoked_by_user_id"] == owner.value
    # every authority is gone on the next resolution; the member is no member
    assert not _holds(
        db_connection, ws, member, AuthorityClass.QUESTION_SELECTION_RIGHT, "WORKSPACE", ws.value
    )
    assert SqlAlchemyMembershipRepository(db_connection).get_current_membership(ws, member) is None
    assert (
        SqlAlchemyMembershipRepository(db_connection).list_active_memberships_for_user(member) == ()
    )
    # one audit event naming the membership; the role and binding refs on the CommitUnit; one event
    audit = (
        db_connection.execute(
            sa.select(audit_events_table).where(
                audit_events_table.c.commit_id == unit.commit_id.value
            )
        )
        .mappings()
        .one()
    )
    assert audit["event_type"] == "CMD_REVOKE_MEMBERSHIP_COMMITTED"
    assert f"workspace_membership:{membership_id}" in " ".join(audit["target_refs"])
    # the dependent relations invalidated in the same bundle are recorded on the CommitUnit (09 §13)
    commit = (
        db_connection.execute(
            sa.select(commit_units_table).where(
                commit_units_table.c.id == unit.commit_id.value
            )
        )
        .mappings()
        .one()
    )
    refs = " ".join(commit["relation_refs"])
    assert f"workspace_membership:{membership_id}" in refs
    assert f"role_assignment:{roles[0]['id']}" in refs
    assert f"authority_binding:{bindings[0]['id']}" in refs
    assert audit["state_before_ref"] == "ACTIVE" and audit["state_after_ref"] == "REVOKED"
    committed = (
        db_connection.execute(
            sa.select(committed_events_table).where(
                committed_events_table.c.commit_id == unit.commit_id.value
            )
        )
        .mappings()
        .all()
    )
    assert len(committed) == 1 and committed[0]["event_type"] == "CMD_REVOKE_MEMBERSHIP_COMMITTED"
    # the owner's own governance root is untouched
    assert _holds(
        db_connection, ws, owner, AuthorityClass.WORKSPACE_GOVERNANCE_RIGHT, "WORKSPACE", ws.value
    )


def test_a_revoked_member_can_be_added_again_as_a_new_membership_without_old_bindings(
    db_connection: sa.Connection,
) -> None:
    owner, member, ws, old_membership = _world(db_connection)
    grant(
        db_connection,
        owner=owner,
        workspace_id=ws,
        member=member,
        authority_class="QUESTION_SELECTION_RIGHT",
        scope_type="WORKSPACE",
        scope_id=ws.value,
    )
    _revoke(db_connection, actor=_human_actor(owner), workspace_id=ws, member=member)
    _add(
        db_connection,
        actor=_human_actor(owner),
        workspace_id=ws,
        new_member_user_id=member,
        role=WorkspaceRole.FACILITATOR,
    )
    current = SqlAlchemyMembershipRepository(db_connection).get_current_membership(ws, member)
    assert current is not None and current.id != old_membership
    assert (
        SqlAlchemyMembershipRepository(db_connection).get_current_role(current.id).role
        is WorkspaceRole.FACILITATOR
    )  # type: ignore[union-attr]
    assert not _holds(
        db_connection, ws, member, AuthorityClass.QUESTION_SELECTION_RIGHT, "WORKSPACE", ws.value
    )
    history = SqlAlchemyMembershipRepository(db_connection).list_membership_history(ws, member)
    assert {m.status for m in history} == {MembershipStatus.ACTIVE, MembershipStatus.REVOKED}


def test_the_governance_root_is_not_removable_and_its_role_not_changeable(
    db_connection: sa.Connection,
) -> None:
    owner, member, ws, _ = _world(db_connection)
    with pytest.raises(GovernanceRootNotRemovable):
        _revoke(db_connection, actor=_human_actor(owner), workspace_id=ws, member=owner)
    with pytest.raises(GovernanceRootNotRemovable):
        _change(
            db_connection,
            actor=_human_actor(owner),
            workspace_id=ws,
            member=owner,
            role=WorkspaceRole.CONTRIBUTOR,
        )
    assert (
        SqlAlchemyMembershipRepository(db_connection).get_current_membership(ws, owner) is not None
    )
    assert _holds(
        db_connection, ws, owner, AuthorityClass.WORKSPACE_GOVERNANCE_RIGHT, "WORKSPACE", ws.value
    )


def test_only_the_root_may_revoke_or_relabel_non_member_and_non_human_denied_without_disclosure(
    db_connection: sa.Connection,
) -> None:
    owner, member, ws, _ = _world(db_connection)
    other = _insert_user(db_connection, email=f"other-{uuid.uuid4()}@example.test")
    _add(
        db_connection,
        actor=_human_actor(owner),
        workspace_id=ws,
        new_member_user_id=other,
        role=WorkspaceRole.FACILITATOR,
    )
    outsider = _insert_user(db_connection, email=f"outsider-{uuid.uuid4()}@example.test")
    for actor in (
        _human_actor(other),
        _human_actor(outsider),
        ActorIdentity(actor_class=ActorClass.AI_PROCESSOR, user_id=owner),
    ):
        with pytest.raises(AddMemberDenied):
            _revoke(db_connection, actor=actor, workspace_id=ws, member=member)
        with pytest.raises(AddMemberDenied):
            _change(
                db_connection,
                actor=actor,
                workspace_id=ws,
                member=member,
                role=WorkspaceRole.FACILITATOR,
            )
    # a non-root asking about a non-member gets the same denial, never "not found"
    with pytest.raises(AddMemberDenied):
        _revoke(db_connection, actor=_human_actor(outsider), workspace_id=ws, member=outsider)
    assert (
        SqlAlchemyMembershipRepository(db_connection).get_current_membership(ws, member) is not None
    )
    # a Workspace that does not exist: denied by the precheck, no commands row
    with pytest.raises(AddMemberDenied):
        _revoke(
            db_connection,
            actor=_human_actor(owner),
            workspace_id=WorkspaceId(uuid.uuid4()),
            member=member,
        )


def test_an_unknown_or_already_revoked_target_is_one_not_found_class(
    db_connection: sa.Connection,
) -> None:
    owner, member, ws, _ = _world(db_connection)
    stranger = _insert_user(db_connection, email=f"stranger-{uuid.uuid4()}@example.test")
    with pytest.raises(MembershipNotFound):
        _revoke(db_connection, actor=_human_actor(owner), workspace_id=ws, member=stranger)
    _revoke(db_connection, actor=_human_actor(owner), workspace_id=ws, member=member)
    with pytest.raises(MembershipNotFound):
        _revoke(db_connection, actor=_human_actor(owner), workspace_id=ws, member=member)
    with pytest.raises(MembershipNotFound):
        _change(
            db_connection,
            actor=_human_actor(owner),
            workspace_id=ws,
            member=member,
            role=WorkspaceRole.FACILITATOR,
        )


# ---------------------------------------------------------------- GOV-004


def test_the_root_changes_a_members_role_prior_assignment_ends_new_one_current(
    db_connection: sa.Connection,
) -> None:
    owner, member, ws, membership_id = _world(db_connection)
    unit = _change(
        db_connection,
        actor=_human_actor(owner),
        workspace_id=ws,
        member=member,
        role=WorkspaceRole.FACILITATOR,
    )
    roles = (
        db_connection.execute(
            sa.select(role_assignments_table)
            .where(role_assignments_table.c.membership_id == membership_id)
            .order_by(
                role_assignments_table.c.granted_at,
                role_assignments_table.c.revoked_at.nulls_last(),
            )
        )
        .mappings()
        .all()
    )
    assert len(roles) == 2
    ended = [r for r in roles if r["revoked_at"] is not None]
    current = [r for r in roles if r["revoked_at"] is None]
    assert len(ended) == 1 and ended[0]["role"] == "Contributor"
    assert (
        len(current) == 1
        and current[0]["role"] == "Facilitator"
        and current[0]["granted_by_user_id"] == owner.value
    )
    assert (
        SqlAlchemyMembershipRepository(db_connection).get_current_role(membership_id).role
        is WorkspaceRole.FACILITATOR
    )  # type: ignore[union-attr]
    membership = SqlAlchemyMembershipRepository(db_connection).get_current_membership(ws, member)
    assert membership is not None and membership.record_version == RecordVersion(2)
    audit = (
        db_connection.execute(
            sa.select(audit_events_table).where(
                audit_events_table.c.commit_id == unit.commit_id.value
            )
        )
        .mappings()
        .one()
    )
    assert audit["event_type"] == "CMD_CHANGE_MEMBER_ROLE_COMMITTED"
    assert audit["state_before_ref"] == "Contributor" and audit["state_after_ref"] == "Facilitator"
    # a second change back works on the advanced version
    _change(
        db_connection,
        actor=_human_actor(owner),
        workspace_id=ws,
        member=member,
        role=WorkspaceRole.CONTRIBUTOR,
    )
    assert (
        SqlAlchemyMembershipRepository(db_connection).get_current_role(membership_id).role
        is WorkspaceRole.CONTRIBUTOR
    )  # type: ignore[union-attr]


def test_owner_role_unknown_role_and_unchanged_role_are_refused(
    db_connection: sa.Connection,
) -> None:
    owner, member, ws, membership_id = _world(db_connection)
    with pytest.raises(OwnerRoleNotAssignable):
        _change(
            db_connection,
            actor=_human_actor(owner),
            workspace_id=ws,
            member=member,
            role=WorkspaceRole.OWNER,
        )
    with pytest.raises(OwnerRoleNotAssignable):
        _change(
            db_connection,
            actor=_human_actor(owner),
            workspace_id=ws,
            member=member,
            role=WorkspaceRole.VIEWER,
        )
    with pytest.raises(RoleUnchanged):
        _change(
            db_connection,
            actor=_human_actor(owner),
            workspace_id=ws,
            member=member,
            role=WorkspaceRole.CONTRIBUTOR,
        )
    roles = (
        db_connection.execute(
            sa.select(role_assignments_table).where(
                role_assignments_table.c.membership_id == membership_id
            )
        )
        .mappings()
        .all()
    )
    assert len(roles) == 1 and roles[0]["revoked_at"] is None


def test_a_stale_membership_version_cannot_commit(db_connection: sa.Connection) -> None:
    owner, member, ws, membership_id = _world(db_connection)
    # someone else advanced the aggregate between the read and the commit
    db_connection.execute(
        sa.update(workspace_memberships_table)
        .where(workspace_memberships_table.c.id == membership_id)
        .values(record_version=5)
    )
    stale_reader = SqlAlchemyMembershipVersionReader(db_connection, membership_id=membership_id)
    with pytest.raises(CommitDenied):
        revoke_membership(
            db_connection,
            actor=_human_actor(owner),
            workspace_id=ws,
            member_user_id=member,
            command_id=CommandId(uuid.uuid4()),
            attempt_id=AttemptId(uuid.uuid4()),
            correlation_id=CorrelationId(uuid.uuid4()),
            occurred_at=_NOW,
            commit_id=CommitId(uuid.uuid4()),
            idempotency_key=None,
            current_version_reader=_StaleReader(stale_reader),
            **_ports(db_connection),  # type: ignore[arg-type]
        )
    assert (
        SqlAlchemyMembershipRepository(db_connection).get_current_membership(ws, member) is not None
    )


class _StaleReader:
    """Reports a version that differs from the envelope's expectation."""

    def __init__(self, inner: SqlAlchemyMembershipVersionReader) -> None:
        self._inner = inner

    def read(self, target_ref: str) -> RecordVersion | None:
        real = self._inner.read(target_ref)
        return None if real is None else RecordVersion(real.value + 1)
