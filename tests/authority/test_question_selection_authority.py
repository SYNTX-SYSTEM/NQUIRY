"""T3 AUTHORITY TEST: QUESTION_SELECTION_RIGHT resolved at
`scope_type="SESSION"`, against real PostgreSQL.

04 section 41/42 (AUTH-DEP-SEL-001/002) state, unhedged: "AUTHORITY
SCOPE: Specific Session." This is the first package to resolve any
authority class at Session scope (every predecessor package's own
right -- `SESSION_CONTROL_RIGHT` -- resolves at `WORKSPACE` scope, a
disclosed workaround for a bootstrap-ordering tension that does not
apply here; see `application.question_selection_handler`'s own module
docstring). `AuthorityResolver` itself is generic over `scope_type`
(a plain `str`, `authority/resolver.py`), so this file proves the
*existing* resolver behaves correctly under this *new* scope shape,
not a new resolver code path.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from authority.actor import ActorClass, ActorIdentity
from authority.resolver import AuthorityRequest, AuthorityResolver, AuthorityVerdict
from governance.authority_binding import AuthorityBindingState, AuthorityClass
from persistence.authority_binding_repository import SqlAlchemyAuthorityBindingRepository
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.tables import human_authority_bindings_table
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import SessionId, UserId, WorkspaceId
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()


def _resolver(connection: sa.Connection) -> AuthorityResolver:
    return AuthorityResolver(
        SqlAlchemyMembershipRepository(connection),
        SqlAlchemyAuthorityBindingRepository(connection),
        FixedClock(_NOW),
    )


def _bootstrap(db_connection: sa.Connection, *, email: str) -> tuple[WorkspaceId, UserId]:
    result = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN).seed(
        owner_email=email
    )
    return result.workspace_id, result.owner_user_id


def _grant_question_selection_right(
    db_connection: sa.Connection,
    *,
    workspace_id: WorkspaceId,
    user_id: UserId,
    session_id: SessionId,
    state: AuthorityBindingState = AuthorityBindingState.ACTIVE,
) -> None:
    db_connection.execute(
        sa.insert(human_authority_bindings_table).values(
            id=uuid.uuid4(),
            workspace_id=workspace_id.value,
            human_user_id=user_id.value,
            authority_class=AuthorityClass.QUESTION_SELECTION_RIGHT.value,
            scope_type="SESSION",
            scope_id=session_id.value,
            authority_source="LEVEL_1_EXPLICIT",
            granted_by_user_id=user_id.value,
            granted_at=_NOW,
            state=state.value,
            revoked_at=_NOW if state is AuthorityBindingState.REVOKED else None,
            revoked_by_user_id=user_id.value if state is AuthorityBindingState.REVOKED else None,
            record_version=1,
        )
    )


def _request(
    *, workspace_id: WorkspaceId, actor: ActorIdentity, session_id: SessionId
) -> AuthorityRequest:
    return AuthorityRequest(
        actor=actor,
        workspace_id=workspace_id,
        operation="SELECT_COMPELLING_QUESTION",
        required_authority_class=AuthorityClass.QUESTION_SELECTION_RIGHT,
        scope_type="SESSION",
        scope_id=session_id.value,
    )


def test_grants_when_a_current_session_scoped_binding_exists(db_connection: sa.Connection) -> None:
    workspace_id, user_id = _bootstrap(db_connection, email="sel-grant@nonproof.test")
    session_id = SessionId(uuid.uuid4())
    _grant_question_selection_right(
        db_connection, workspace_id=workspace_id, user_id=user_id, session_id=session_id
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, user_id)

    resolution = _resolver(db_connection).resolve(
        _request(workspace_id=workspace_id, actor=actor, session_id=session_id)
    )

    assert resolution.verdict is AuthorityVerdict.GRANTED


def test_denies_a_binding_scoped_to_a_different_session(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: wrong scope -- here in its
    "different Session" shape, the new scope dimension this package
    introduces.
    """
    workspace_id, user_id = _bootstrap(db_connection, email="sel-wrong-session@nonproof.test")
    granted_session_id = SessionId(uuid.uuid4())
    requested_session_id = SessionId(uuid.uuid4())
    _grant_question_selection_right(
        db_connection, workspace_id=workspace_id, user_id=user_id, session_id=granted_session_id
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, user_id)

    resolution = _resolver(db_connection).resolve(
        _request(workspace_id=workspace_id, actor=actor, session_id=requested_session_id)
    )

    assert resolution.verdict is not AuthorityVerdict.GRANTED


def test_denies_a_revoked_binding(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: revoked authority (P-11)."""
    workspace_id, user_id = _bootstrap(db_connection, email="sel-revoked@nonproof.test")
    session_id = SessionId(uuid.uuid4())
    _grant_question_selection_right(
        db_connection,
        workspace_id=workspace_id,
        user_id=user_id,
        session_id=session_id,
        state=AuthorityBindingState.REVOKED,
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, user_id)

    resolution = _resolver(db_connection).resolve(
        _request(workspace_id=workspace_id, actor=actor, session_id=session_id)
    )

    assert resolution.verdict is not AuthorityVerdict.GRANTED


def test_denies_a_never_granted_right(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: human without right (P-10)."""
    workspace_id, user_id = _bootstrap(db_connection, email="sel-never-granted@nonproof.test")
    session_id = SessionId(uuid.uuid4())
    actor = ActorIdentity(ActorClass.HUMAN_USER, user_id)

    resolution = _resolver(db_connection).resolve(
        _request(workspace_id=workspace_id, actor=actor, session_id=session_id)
    )

    assert resolution.verdict is not AuthorityVerdict.GRANTED


def test_denies_a_binding_scoped_to_workspace_instead_of_session(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: wrong scope -- a binding recorded
    with the identical `scope_id` value but the wrong `scope_type`
    string ("WORKSPACE" instead of "SESSION") must not satisfy the
    request. Proves `AuthorityResolver`'s exact-match design (04 SESSION
    scope, not a scope-hierarchy fallback) is honored for this right too.
    """
    workspace_id, user_id = _bootstrap(db_connection, email="sel-wrong-scope-type@nonproof.test")
    session_id = SessionId(uuid.uuid4())
    db_connection.execute(
        sa.insert(human_authority_bindings_table).values(
            id=uuid.uuid4(),
            workspace_id=workspace_id.value,
            human_user_id=user_id.value,
            authority_class=AuthorityClass.QUESTION_SELECTION_RIGHT.value,
            scope_type="WORKSPACE",
            scope_id=workspace_id.value,
            authority_source="LEVEL_1_EXPLICIT",
            granted_by_user_id=user_id.value,
            granted_at=_NOW,
            state=AuthorityBindingState.ACTIVE.value,
            record_version=1,
        )
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, user_id)

    resolution = _resolver(db_connection).resolve(
        _request(workspace_id=workspace_id, actor=actor, session_id=session_id)
    )

    assert resolution.verdict is not AuthorityVerdict.GRANTED
