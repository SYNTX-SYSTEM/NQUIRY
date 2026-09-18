"""T3 AUTHORITY TEST: DECISION_RIGHT resolved at `scope_type="CHALLENGE"`
(OpenDecisionConsideration) and `scope_type="DECISION"`
(RecordHumanDecision), against real PostgreSQL.

04 section 49/50 (AUTH-DEP-DEC-001/002) state "AUTHORITY SCOPE: Specific
Decision/Challenge" / "Specific Decision" -- this is the third distinct
scope convention this codebase resolves DECISION_RIGHT against
(after WORKSPACE for Burst/Session-control, SESSION for
QuestionSelection). `AuthorityResolver` itself is generic over
`scope_type`, so this file proves the *existing* resolver behaves
correctly under these two new scope shapes, not a new resolver code
path.
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
from semantic_types.ids import ChallengeId, DecisionId, UserId, WorkspaceId
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


def _grant_decision_right(
    db_connection: sa.Connection,
    *,
    workspace_id: WorkspaceId,
    user_id: UserId,
    scope_type: str,
    scope_id: uuid.UUID,
    state: AuthorityBindingState = AuthorityBindingState.ACTIVE,
) -> None:
    db_connection.execute(
        sa.insert(human_authority_bindings_table).values(
            id=uuid.uuid4(),
            workspace_id=workspace_id.value,
            human_user_id=user_id.value,
            authority_class=AuthorityClass.DECISION_RIGHT.value,
            scope_type=scope_type,
            scope_id=scope_id,
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
    *, workspace_id: WorkspaceId, actor: ActorIdentity, scope_type: str, scope_id: uuid.UUID
) -> AuthorityRequest:
    return AuthorityRequest(
        actor=actor,
        workspace_id=workspace_id,
        operation="RECORD_HUMAN_DECISION",
        required_authority_class=AuthorityClass.DECISION_RIGHT,
        scope_type=scope_type,
        scope_id=scope_id,
    )


def test_grants_when_a_current_challenge_scoped_binding_exists_for_open(
    db_connection: sa.Connection,
) -> None:
    workspace_id, user_id = _bootstrap(db_connection, email="dec-open-grant@nonproof.test")
    challenge_id = ChallengeId(uuid.uuid4())
    _grant_decision_right(
        db_connection,
        workspace_id=workspace_id,
        user_id=user_id,
        scope_type="CHALLENGE",
        scope_id=challenge_id.value,
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, user_id)

    resolution = _resolver(db_connection).resolve(
        _request(
            workspace_id=workspace_id,
            actor=actor,
            scope_type="CHALLENGE",
            scope_id=challenge_id.value,
        )
    )

    assert resolution.verdict is AuthorityVerdict.GRANTED


def test_grants_when_a_current_decision_scoped_binding_exists_for_record(
    db_connection: sa.Connection,
) -> None:
    workspace_id, user_id = _bootstrap(db_connection, email="dec-record-grant@nonproof.test")
    decision_id = DecisionId(uuid.uuid4())
    _grant_decision_right(
        db_connection,
        workspace_id=workspace_id,
        user_id=user_id,
        scope_type="DECISION",
        scope_id=decision_id.value,
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, user_id)

    resolution = _resolver(db_connection).resolve(
        _request(
            workspace_id=workspace_id,
            actor=actor,
            scope_type="DECISION",
            scope_id=decision_id.value,
        )
    )

    assert resolution.verdict is AuthorityVerdict.GRANTED


def test_denies_a_binding_scoped_to_a_different_decision(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: wrong scope."""
    workspace_id, user_id = _bootstrap(db_connection, email="dec-wrong-decision@nonproof.test")
    granted_decision_id = DecisionId(uuid.uuid4())
    requested_decision_id = DecisionId(uuid.uuid4())
    _grant_decision_right(
        db_connection,
        workspace_id=workspace_id,
        user_id=user_id,
        scope_type="DECISION",
        scope_id=granted_decision_id.value,
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, user_id)

    resolution = _resolver(db_connection).resolve(
        _request(
            workspace_id=workspace_id,
            actor=actor,
            scope_type="DECISION",
            scope_id=requested_decision_id.value,
        )
    )

    assert resolution.verdict is not AuthorityVerdict.GRANTED


def test_denies_a_revoked_binding(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: revoked actor (P-10)."""
    workspace_id, user_id = _bootstrap(db_connection, email="dec-revoked@nonproof.test")
    decision_id = DecisionId(uuid.uuid4())
    _grant_decision_right(
        db_connection,
        workspace_id=workspace_id,
        user_id=user_id,
        scope_type="DECISION",
        scope_id=decision_id.value,
        state=AuthorityBindingState.REVOKED,
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, user_id)

    resolution = _resolver(db_connection).resolve(
        _request(
            workspace_id=workspace_id,
            actor=actor,
            scope_type="DECISION",
            scope_id=decision_id.value,
        )
    )

    assert resolution.verdict is not AuthorityVerdict.GRANTED


def test_denies_a_never_granted_right(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: role-only actor (no explicit
    DECISION_RIGHT binding at all).
    """
    workspace_id, user_id = _bootstrap(db_connection, email="dec-never-granted@nonproof.test")
    decision_id = DecisionId(uuid.uuid4())
    actor = ActorIdentity(ActorClass.HUMAN_USER, user_id)

    resolution = _resolver(db_connection).resolve(
        _request(
            workspace_id=workspace_id,
            actor=actor,
            scope_type="DECISION",
            scope_id=decision_id.value,
        )
    )

    assert resolution.verdict is not AuthorityVerdict.GRANTED


def test_denies_a_binding_scoped_to_workspace_instead_of_decision(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: wrong scope -- a binding recorded
    with the identical `scope_id` value but the wrong `scope_type`
    string must not satisfy the request.
    """
    workspace_id, user_id = _bootstrap(db_connection, email="dec-wrong-scope-type@nonproof.test")
    decision_id = DecisionId(uuid.uuid4())
    _grant_decision_right(
        db_connection,
        workspace_id=workspace_id,
        user_id=user_id,
        scope_type="WORKSPACE",
        scope_id=workspace_id.value,
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, user_id)

    resolution = _resolver(db_connection).resolve(
        _request(
            workspace_id=workspace_id,
            actor=actor,
            scope_type="DECISION",
            scope_id=decision_id.value,
        )
    )

    assert resolution.verdict is not AuthorityVerdict.GRANTED
