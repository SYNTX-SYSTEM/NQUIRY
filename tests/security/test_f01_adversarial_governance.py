"""F01 WU-01.10 — adversarial governance proof (19 §21's own TESTS
FIRST list), against real PostgreSQL, no mocks.

This file's own job is NOT to re-prove every one of 19 §21's 13
mandatory attack scenarios from scratch -- most already have real,
independently-verified coverage elsewhere in this codebase, cited
below rather than duplicated (this Field's own established
Proof-Proportionality discipline: prove what is not yet proven, do
not re-derive what already is). This file adds tests ONLY for the
scenarios that audit found genuinely uncovered by any earlier F01 Work
Unit's own test file, using F01's OWN real Commands specifically
(`add_member`, `revoke_human_authority_binding`, `create_workspace`),
not a generic unit-level substitute.

19 §21 TESTS FIRST — coverage audit (file:test, or "NEW below"):
  valid login                          -> tests/e2e/test_http_auth.py
  invalid login                        -> tests/e2e/test_http_auth.py
  expired/revoked session              -> tests/e2e/test_auth_handler.py
  accessible Workspace list            -> tests/e2e/test_accessible_workspaces_query.py
  revoked membership                   -> covered for the LIST query
                                           (test_accessible_workspaces_query.py::
                                           test_revoked_membership_is_excluded);
                                           NOT YET covered for F01's own
                                           governance-WRITE Commands -> NEW below
  cross-Workspace isolation            -> tests/e2e/test_membership_operations.py,
                                           tests/e2e/test_revoke_authority_binding.py
                                           (both have their own "stranger"/
                                           "non-member" adversarial cases)
  grant authority                      -> tests/e2e/test_create_workspace.py
  revoke authority                     -> tests/e2e/test_revoke_authority_binding.py
  role without right                   -> tests/authority/test_resolver.py::
                                           test_role_only_is_denied (generic,
                                           reused by every F01 Command via the
                                           one shared AuthorityResolver)
  wrong operation                      -> tests/authority/test_resolver.py::
                                           test_binding_for_different_authority_class_does_not_satisfy_request
  wrong scope                          -> tests/authority/test_resolver.py::
                                           test_wrong_scope_is_denied,
                                           test_wrong_workspace_is_denied;
                                           tests/e2e/test_revoke_authority_binding.py::
                                           test_binding_from_a_different_workspace_is_denied_not_revoked
  authority revoked between view/commit -> tests/authority/test_resolver.py::
                                           test_stale_binding_denied_after_revoke_between_two_resolutions;
                                           tests/command_commit_event/test_commit.py::
                                           test_commit_denies_when_authority_was_revoked_after_preparation
                                           (both generic, reused by every F01
                                           Command via the shared
                                           CommitCoordinator/AuthorityResolver --
                                           NOT independently re-exercisable via
                                           `add_member`/`revoke_human_authority_binding`
                                           specifically: the one binding class
                                           those Commands gate on,
                                           WORKSPACE_GOVERNANCE_RIGHT, cannot be
                                           revoked out from under an in-flight
                                           caller without first tripping
                                           GovernanceRootOrphaningRefused, since
                                           at most one such binding exists per
                                           Workspace by construction -- disclosed,
                                           not silently skipped)
  bootstrap self-grant attacks          -> partially covered (test_create_workspace.py's
                                           own `test_founder_owner_role_assignment_is_self_granted`
                                           proves the POSITIVE shape); the
                                           cross-Workspace NON-LEAKAGE property
                                           -- founding a second Workspace grants
                                           no authority whatsoever in an
                                           unrelated first one -- was NOT yet
                                           proven anywhere -> NEW below
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from application.authority_binding_handler import (
    RevokeAuthorityBindingDenied,
    revoke_human_authority_binding,
)
from application.capability_projection import project_capabilities
from application.membership_operations_handler import AddMemberDenied, add_member
from application.workspace_context import resolve_workspace_context
from application.workspace_creation_handler import (
    AllowAllWorkspaceCreationEligibilityChecker,
    create_workspace,
)
from authority.actor import ActorClass, ActorIdentity
from authority.resolver import AuthorityResolver
from commit.idempotency import SqlAlchemyIdempotencyRepository
from governance.authority_binding import AuthorityClass
from governance.membership import MembershipStatus, WorkspaceRole
from persistence.audit_repository import SqlAlchemyAuditRepository
from persistence.authority_binding_repository import (
    SqlAlchemyAuthorityBindingRepository,
    SqlAlchemyAuthorityBindingVersionReader,
)
from persistence.command_repository import SqlAlchemyCommandRepository
from persistence.commit_repository import SqlAlchemyCommitRepository
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.outbox_repository import SqlAlchemyOutboxRepository
from persistence.tables import (
    human_authority_bindings_table,
    users_table,
    workspace_memberships_table,
)
from persistence.workspace_repository import (
    SqlAlchemyWorkspaceRepository,
    SqlAlchemyWorkspaceVersionReader,
)
from security.identity import AuthenticatedPrincipal
from semantic_types.ids import (
    AttemptId,
    AuthorityBindingId,
    CommandId,
    CommitId,
    CorrelationId,
    UserId,
    WorkspaceId,
)
from test_support.clock import FixedClock

_NOW = datetime(2026, 9, 21, tzinfo=timezone.utc)


def _insert_user(connection: sa.Connection, *, email: str) -> UserId:
    user_id = uuid.uuid4()
    connection.execute(
        sa.insert(users_table).values(
            id=user_id,
            email=email,
            name="Real Human",
            record_version=1,
            created_at=_NOW,
            updated_at=_NOW,
        )
    )
    return UserId(user_id)


def _human_actor(user_id: UserId) -> ActorIdentity:
    return ActorIdentity(actor_class=ActorClass.HUMAN_USER, user_id=user_id)


def _principal(user_id: UserId) -> AuthenticatedPrincipal:
    return AuthenticatedPrincipal(
        user_id=user_id,
        authentication_session_ref="s",
        authentication_time=_NOW,
        issuer_ref="issuer",
    )


def _resolver(db_connection: sa.Connection) -> AuthorityResolver:
    return AuthorityResolver(
        SqlAlchemyMembershipRepository(db_connection),
        SqlAlchemyAuthorityBindingRepository(db_connection),
        FixedClock(_NOW),
    )


def _found_workspace(db_connection: sa.Connection, *, owner: UserId, name: str) -> WorkspaceId:
    result = create_workspace(
        db_connection,
        actor=_human_actor(owner),
        workspace_name=name,
        command_id=CommandId(uuid.uuid4()),
        attempt_id=AttemptId(uuid.uuid4()),
        correlation_id=CorrelationId(uuid.uuid4()),
        occurred_at=_NOW,
        commit_id=CommitId(uuid.uuid4()),
        eligibility_checker=AllowAllWorkspaceCreationEligibilityChecker(),
        command_repository=SqlAlchemyCommandRepository(db_connection),
        audit_repository=SqlAlchemyAuditRepository(db_connection),
        outbox_repository=SqlAlchemyOutboxRepository(db_connection),
        commit_repository=SqlAlchemyCommitRepository(db_connection),
        workspace_repository=SqlAlchemyWorkspaceRepository(db_connection),
        membership_repository=SqlAlchemyMembershipRepository(db_connection),
        authority_binding_repository=SqlAlchemyAuthorityBindingRepository(db_connection),
    )
    return result.workspace_id


def _add(
    db_connection: sa.Connection,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    new_member_user_id: UserId,
    role: WorkspaceRole = WorkspaceRole.CONTRIBUTOR,
):
    return add_member(
        db_connection,
        actor=actor,
        workspace_id=workspace_id,
        new_member_user_id=new_member_user_id,
        role=role,
        command_id=CommandId(uuid.uuid4()),
        attempt_id=AttemptId(uuid.uuid4()),
        correlation_id=CorrelationId(uuid.uuid4()),
        occurred_at=_NOW,
        commit_id=CommitId(uuid.uuid4()),
        idempotency_key=None,
        workspace_repository=SqlAlchemyWorkspaceRepository(db_connection),
        membership_repository=SqlAlchemyMembershipRepository(db_connection),
        authority_resolver=_resolver(db_connection),
        command_repository=SqlAlchemyCommandRepository(db_connection),
        audit_repository=SqlAlchemyAuditRepository(db_connection),
        outbox_repository=SqlAlchemyOutboxRepository(db_connection),
        commit_repository=SqlAlchemyCommitRepository(db_connection),
        idempotency_port=SqlAlchemyIdempotencyRepository(db_connection),
        current_version_reader=SqlAlchemyWorkspaceVersionReader(
            db_connection, workspace_id=workspace_id
        ),
    )


def _revoke_own_governance_membership(
    db_connection: sa.Connection, *, workspace_id: WorkspaceId
) -> None:
    """Revokes the founder's own `workspace_memberships` row directly --
    no real Command does this yet (`remove member`/`leave Workspace` is
    `SUCCESSOR_NOT_BUILT`, disclosed since WU-01.5/01.6). This is
    deliberately NOT the same as revoking the founder's own
    `WORKSPACE_GOVERNANCE_RIGHT` binding (which `GovernanceRootOrphaningRefused`
    would correctly refuse) -- membership and authority binding are two
    independently-stored facts (05 §18), and this fixture exercises
    membership loss specifically, simulating a future "account
    deactivated"/"left the org" mechanism this codebase does not build
    yet."""
    db_connection.execute(
        sa.update(workspace_memberships_table)
        .where(workspace_memberships_table.c.workspace_id == workspace_id.value)
        .values(status=MembershipStatus.REVOKED.value, revoked_at=_NOW)
    )


# ---------------------------------------------------------------------------
# NEW: "revoked membership" for F01's own governance-write Commands
# ---------------------------------------------------------------------------


def test_a_founder_whose_own_membership_is_revoked_can_no_longer_add_members(
    db_connection: sa.Connection,
) -> None:
    founder = _insert_user(db_connection, email="revoked-founder-add@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=founder, name="Revoked Founder Add")
    target = _insert_user(db_connection, email="target-revoked-founder-add@real-human.test")

    _revoke_own_governance_membership(db_connection, workspace_id=workspace_id)

    with pytest.raises(AddMemberDenied):
        _add(
            db_connection,
            actor=_human_actor(founder),
            workspace_id=workspace_id,
            new_member_user_id=target,
        )

    count = db_connection.execute(
        sa.select(sa.func.count())
        .select_from(workspace_memberships_table)
        .where(
            workspace_memberships_table.c.workspace_id == workspace_id.value,
            workspace_memberships_table.c.user_id == target.value,
        )
    ).scalar_one()
    assert count == 0


def test_a_founder_whose_own_membership_is_revoked_can_no_longer_revoke_bindings(
    db_connection: sa.Connection,
) -> None:
    founder = _insert_user(db_connection, email="revoked-founder-revoke@real-human.test")
    workspace_id = _found_workspace(db_connection, owner=founder, name="Revoked Founder Revoke")
    holder = _insert_user(db_connection, email="holder-revoked-founder-revoke@real-human.test")
    _add(
        db_connection,
        actor=_human_actor(founder),
        workspace_id=workspace_id,
        new_member_user_id=holder,
    )
    binding_id = AuthorityBindingId(uuid.uuid4())
    db_connection.execute(
        sa.insert(human_authority_bindings_table).values(
            id=binding_id.value,
            workspace_id=workspace_id.value,
            human_user_id=holder.value,
            authority_class=AuthorityClass.DECISION_RIGHT.value,
            scope_type="WORKSPACE",
            scope_id=workspace_id.value,
            authority_source="LEVEL_1_EXPLICIT",
            granted_by_user_id=founder.value,
            granted_at=_NOW,
            revoked_by_user_id=None,
            revoked_at=None,
            state="ACTIVE",
            record_version=1,
        )
    )

    _revoke_own_governance_membership(db_connection, workspace_id=workspace_id)

    with pytest.raises(RevokeAuthorityBindingDenied):
        revoke_human_authority_binding(
            db_connection,
            actor=_human_actor(founder),
            workspace_id=workspace_id,
            binding_id=binding_id,
            command_id=CommandId(uuid.uuid4()),
            attempt_id=AttemptId(uuid.uuid4()),
            correlation_id=CorrelationId(uuid.uuid4()),
            occurred_at=_NOW,
            commit_id=CommitId(uuid.uuid4()),
            idempotency_key=None,
            workspace_repository=SqlAlchemyWorkspaceRepository(db_connection),
            membership_repository=SqlAlchemyMembershipRepository(db_connection),
            authority_binding_repository=SqlAlchemyAuthorityBindingRepository(db_connection),
            authority_resolver=_resolver(db_connection),
            command_repository=SqlAlchemyCommandRepository(db_connection),
            audit_repository=SqlAlchemyAuditRepository(db_connection),
            outbox_repository=SqlAlchemyOutboxRepository(db_connection),
            commit_repository=SqlAlchemyCommitRepository(db_connection),
            idempotency_port=SqlAlchemyIdempotencyRepository(db_connection),
            current_version_reader=SqlAlchemyAuthorityBindingVersionReader(db_connection),
        )

    row = db_connection.execute(
        sa.select(human_authority_bindings_table.c.state).where(
            human_authority_bindings_table.c.id == binding_id.value
        )
    ).scalar_one()
    assert row == "ACTIVE"


# ---------------------------------------------------------------------------
# NEW: "bootstrap self-grant attacks" -- cross-Workspace non-leakage
# ---------------------------------------------------------------------------


def test_founding_a_second_workspace_grants_no_authority_whatsoever_in_an_unrelated_first_one(
    db_connection: sa.Connection,
) -> None:
    founder_a = _insert_user(db_connection, email="founder-a-no-leak@real-human.test")
    workspace_a = _found_workspace(db_connection, owner=founder_a, name="Workspace A No Leak")
    contributor = _insert_user(db_connection, email="contributor-no-leak@real-human.test")
    _add(
        db_connection,
        actor=_human_actor(founder_a),
        workspace_id=workspace_a,
        new_member_user_id=contributor,
    )

    def _capabilities_in_a() -> tuple[bool, bool]:
        context = resolve_workspace_context(
            _principal(contributor),
            workspace_a,
            SqlAlchemyWorkspaceRepository(db_connection),
            SqlAlchemyMembershipRepository(db_connection),
        )
        projection = project_capabilities(
            context,
            membership_repository=SqlAlchemyMembershipRepository(db_connection),
            authority_binding_repository=SqlAlchemyAuthorityBindingRepository(db_connection),
        )
        return projection.authorized, projection.governance_capable

    before = _capabilities_in_a()
    assert before == (False, False)

    # The Contributor of Workspace A founds their own, entirely separate
    # Workspace B -- a real, legitimate self-grant (WU-01.4b), but for a
    # DIFFERENT Workspace.
    workspace_b = _found_workspace(
        db_connection, owner=contributor, name="Workspace B Self-Founded"
    )

    # Their real, new WORKSPACE_GOVERNANCE_RIGHT binding is scoped to B
    # alone -- proven by their own capability projection in B...
    context_b = resolve_workspace_context(
        _principal(contributor),
        workspace_b,
        SqlAlchemyWorkspaceRepository(db_connection),
        SqlAlchemyMembershipRepository(db_connection),
    )
    projection_b = project_capabilities(
        context_b,
        membership_repository=SqlAlchemyMembershipRepository(db_connection),
        authority_binding_repository=SqlAlchemyAuthorityBindingRepository(db_connection),
    )
    assert projection_b.governance_capable is True

    # ...and it grants NOTHING new back in Workspace A: identical to the
    # "before" snapshot, byte-for-byte.
    after = _capabilities_in_a()
    assert after == before == (False, False)

    # The real, structural proof: they still cannot administer Workspace
    # A's own membership.
    outsider = _insert_user(db_connection, email="outsider-no-leak@real-human.test")
    with pytest.raises(AddMemberDenied):
        _add(
            db_connection,
            actor=_human_actor(contributor),
            workspace_id=workspace_a,
            new_member_user_id=outsider,
        )


def test_founding_a_workspace_does_not_grant_authority_over_an_unrelated_preexisting_binding(
    db_connection: sa.Connection,
) -> None:
    """The inverse direction of the same non-leakage property: an
    ALREADY-EXISTING HumanAuthorityBinding for a stranger in a
    different Workspace is untouched by a brand-new founder's own
    self-grant -- founding never reads, iterates, or mutates any row
    outside the one Workspace it creates."""
    other_founder = _insert_user(db_connection, email="other-founder-no-leak@real-human.test")
    other_workspace = _found_workspace(
        db_connection, owner=other_founder, name="Pre-Existing Workspace"
    )
    other_binding_row = db_connection.execute(
        sa.select(
            human_authority_bindings_table.c.id, human_authority_bindings_table.c.record_version
        ).where(human_authority_bindings_table.c.workspace_id == other_workspace.value)
    ).one()

    new_founder = _insert_user(db_connection, email="new-founder-no-leak@real-human.test")
    _found_workspace(db_connection, owner=new_founder, name="Brand New, Unrelated")

    unchanged_row = db_connection.execute(
        sa.select(
            human_authority_bindings_table.c.id, human_authority_bindings_table.c.record_version
        ).where(human_authority_bindings_table.c.id == other_binding_row.id)
    ).one()
    assert unchanged_row.record_version == other_binding_row.record_version
