"""T7 COMMAND/COMMIT TEST: `application.question_selection_handler.select_question`,
against real PostgreSQL.

The first fully governed, end-to-end production Command path in this
codebase: every test in this file exercises the REAL predecessor chain
-- NonProofWorkspaceBootstrap (PKG-04) -> Challenge/Session (PKG-05,
direct SQL, Session seeded directly in `QUESTION_SELECTION` state) ->
Question (PKG-06, real `QuestionRepository`) -> real `AuthorityResolver`
(PKG-03) -> the real BND-001..007 evaluators (PKG-09) chained via
`boundaries.evaluate_chain` (PKG-08) -> `Bnd014CommitEvaluator`/
`CommitCoordinator` (PKG-13) -> `QuestionSelectionRepository` (this
package) -> `CommandRepository`/`IdempotencyPort`/`AuditRepository`/
`OutboxRepository`/`CommitRepository` (PKG-10/11/12/13).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from application.question_selection_handler import (
    SelectQuestionDenied,
    select_question,
)
from authority.actor import ActorClass, ActorIdentity
from authority.resolver import AuthorityResolver
from commit.coordinator import CommitFailedPrecommit
from commit.idempotency import IdempotencyAlreadyCommitted, SqlAlchemyIdempotencyRepository
from domain.question import Question, QuestionOrigin
from domain.question_selection import SelectionType
from governance.authority_binding import AuthorityBindingState, AuthorityClass
from governance.membership import WorkspaceRole
from persistence.audit_repository import SqlAlchemyAuditRepository
from persistence.authority_binding_repository import SqlAlchemyAuthorityBindingRepository
from persistence.command_repository import SqlAlchemyCommandRepository
from persistence.commit_repository import SqlAlchemyCommitRepository
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.outbox_repository import SqlAlchemyOutboxRepository
from persistence.question_repository import SqlAlchemyQuestionRepository
from persistence.question_selection_repository import SqlAlchemyQuestionSelectionRepository
from persistence.session_repository import (
    SqlAlchemySessionRepository,
    SqlAlchemySessionVersionReader,
)
from persistence.tables import (
    challenges_table,
    human_authority_bindings_table,
    question_selections_table,
    role_assignments_table,
    sessions_table,
)
from persistence.workspace_repository import SqlAlchemyWorkspaceRepository
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import (
    AttemptId,
    ChallengeId,
    CommandId,
    CommitId,
    CorrelationId,
    QuestionId,
    QuestionSelectionId,
    SessionId,
    UserId,
    WorkspaceId,
)
from semantic_types.versions import RecordVersion
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()


def _bootstrap_session(
    db_connection: sa.Connection, *, email: str, final_state: str = "QUESTION_SELECTION"
) -> tuple[WorkspaceId, UserId, uuid.UUID, ChallengeId, SessionId]:
    """Bootstraps a Workspace/owner (NonProofWorkspaceBootstrap, PKG-04),
    grants the owner an `OWNER` role assignment (the bootstrap fixture
    itself creates no role -- BND-004 would otherwise deny every test
    in this file with `NO_CURRENT_ROLE`), then adds a Challenge and a
    Session already seeded in `QUESTION_SELECTION` state.
    """
    result = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN).seed(
        owner_email=email
    )
    db_connection.execute(
        sa.insert(role_assignments_table).values(
            id=_ID_GEN.new_uuid(),
            workspace_id=result.workspace_id.value,
            membership_id=result.membership_id,
            role=WorkspaceRole.OWNER.value,
            granted_by_user_id=result.owner_user_id.value,
            granted_at=_NOW,
            revoked_at=None,
            record_version=1,
        )
    )
    challenge_id = ChallengeId(_ID_GEN.new_uuid())
    db_connection.execute(
        sa.insert(challenges_table).values(
            id=challenge_id.value,
            workspace_id=result.workspace_id.value,
            title="Onboarding drop-off",
            description=None,
            context=None,
            desired_outcome=None,
            constraints=None,
            stakeholders=None,
            created_at=_NOW,
            updated_at=_NOW,
            record_version=1,
        )
    )
    session_id = SessionId(_ID_GEN.new_uuid())
    db_connection.execute(
        sa.insert(sessions_table).values(
            id=session_id.value,
            challenge_id=challenge_id.value,
            workspace_id=result.workspace_id.value,
            applied_method_key="QUESTION_BURST",
            applied_method_version="1.0",
            state="DRAFT",
            created_at=_NOW,
            updated_at=_NOW,
            closed_at=None,
            record_version=1,
        )
    )
    _advance_session_state(db_connection, session_id=session_id, final_state=final_state)
    return result.workspace_id, result.owner_user_id, result.membership_id, challenge_id, session_id


_SESSION_STATE_CHAIN_TO_QUESTION_SELECTION = (
    "SETUP",
    "CHALLENGE_CAPTURE",
    "QUESTION_GENERATION",
    "QUESTION_CAPTURE",
    "ANALYSIS",
    "REFLECTION",
    "QUESTION_SELECTION",
)


def _advance_session_state(
    db_connection: sa.Connection, *, session_id: SessionId, final_state: str
) -> None:
    """`trg_sessions_enforce_transition` (03 section 13.2/16) only
    allows one adjacent, legal state pair per UPDATE, and a new Session
    must be created in `DRAFT` (`trg_sessions_enforce_initial_state`,
    03 TRN-SESS-001) -- there is no shortcut past the real topology,
    even for a test fixture. This walks the exact
    `domain.session_transitions.SESSION_TRANSITION_SPECS` chain
    DRAFT -> ... one legal step at a time, stopping at `final_state`
    (used by the one test needing an earlier, non-`QUESTION_SELECTION`
    Session state).
    """
    for step, state in enumerate(_SESSION_STATE_CHAIN_TO_QUESTION_SELECTION, start=2):
        db_connection.execute(
            sa.update(sessions_table)
            .where(sessions_table.c.id == session_id.value)
            .values(state=state, record_version=step)
        )
        if state == final_state:
            return


def _insert_question(
    db_connection: sa.Connection,
    *,
    workspace_id: WorkspaceId,
    challenge_id: ChallengeId,
    author_user_id: UserId,
) -> QuestionId:
    question = Question(
        question_id=QuestionId(_ID_GEN.new_uuid()),
        challenge_id=challenge_id,
        workspace_id=workspace_id,
        original_text="What stops users from finishing onboarding?",
        normalized_text=None,
        origin=QuestionOrigin.HUMAN,
        author_user_id=author_user_id,
        created_at=_NOW,
        record_version=RecordVersion.initial(),
    )
    SqlAlchemyQuestionRepository(db_connection).create_root(question)
    return question.question_id


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
            id=_ID_GEN.new_uuid(),
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


def _set_role(
    db_connection: sa.Connection, *, membership_id: uuid.UUID, role: WorkspaceRole
) -> None:
    db_connection.execute(
        sa.update(role_assignments_table)
        .where(role_assignments_table.c.membership_id == membership_id)
        .values(role=role.value)
    )


def _resolver(db_connection: sa.Connection) -> AuthorityResolver:
    return AuthorityResolver(
        SqlAlchemyMembershipRepository(db_connection),
        SqlAlchemyAuthorityBindingRepository(db_connection),
        FixedClock(_NOW),
    )


def _call_select_question(
    db_connection: sa.Connection,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    session_id: SessionId,
    question_id: QuestionId,
    selection_type: SelectionType,
    idempotency_key: str | None = None,
    correlation_id: uuid.UUID | None = None,
    command_id: CommandId | None = None,
):
    return select_question(
        db_connection,
        actor=actor,
        workspace_id=workspace_id,
        session_id=session_id,
        question_id=question_id,
        selection_type=selection_type,
        question_selection_id=QuestionSelectionId(_ID_GEN.new_uuid()),
        command_id=command_id or CommandId(uuid.uuid4()),
        attempt_id=AttemptId(uuid.uuid4()),
        correlation_id=CorrelationId(correlation_id or uuid.uuid4()),
        occurred_at=_NOW,
        commit_id=CommitId(uuid.uuid4()),
        idempotency_key=idempotency_key,
        workspace_repository=SqlAlchemyWorkspaceRepository(db_connection),
        membership_repository=SqlAlchemyMembershipRepository(db_connection),
        session_repository=SqlAlchemySessionRepository(db_connection),
        question_repository=SqlAlchemyQuestionRepository(db_connection),
        question_selection_repository=SqlAlchemyQuestionSelectionRepository(db_connection),
        authority_resolver=_resolver(db_connection),
        command_repository=SqlAlchemyCommandRepository(db_connection),
        audit_repository=SqlAlchemyAuditRepository(db_connection),
        outbox_repository=SqlAlchemyOutboxRepository(db_connection),
        commit_repository=SqlAlchemyCommitRepository(db_connection),
        idempotency_port=SqlAlchemyIdempotencyRepository(db_connection),
        current_version_reader=SqlAlchemySessionVersionReader(db_connection, session_id=session_id),
    )


def test_full_success_commits_a_compelling_selection_atomically(
    db_connection: sa.Connection,
) -> None:
    workspace_id, owner_id, membership_id, challenge_id, session_id = _bootstrap_session(
        db_connection, email="select-success@nonproof.test"
    )
    question_id = _insert_question(
        db_connection, workspace_id=workspace_id, challenge_id=challenge_id, author_user_id=owner_id
    )
    _grant_question_selection_right(
        db_connection, workspace_id=workspace_id, user_id=owner_id, session_id=session_id
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, owner_id)

    commit_unit = _call_select_question(
        db_connection,
        actor=actor,
        workspace_id=workspace_id,
        session_id=session_id,
        question_id=question_id,
        selection_type=SelectionType.COMPELLING,
        idempotency_key="select-1",
    )

    assert commit_unit.outcome.value == "COMMITTED"
    assert len(commit_unit.relation_refs) == 1
    row = (
        db_connection.execute(
            sa.select(question_selections_table).where(
                question_selections_table.c.session_id == session_id.value
            )
        )
        .mappings()
        .one()
    )
    assert row["question_id"] == question_id.value
    assert row["selection_type"] == "COMPELLING"


def test_denies_ai_selection(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: AI selection."""
    workspace_id, owner_id, membership_id, challenge_id, session_id = _bootstrap_session(
        db_connection, email="select-ai@nonproof.test"
    )
    question_id = _insert_question(
        db_connection, workspace_id=workspace_id, challenge_id=challenge_id, author_user_id=owner_id
    )
    _grant_question_selection_right(
        db_connection, workspace_id=workspace_id, user_id=owner_id, session_id=session_id
    )
    ai_actor = ActorIdentity(ActorClass.AI_PROCESSOR, owner_id)

    with pytest.raises(SelectQuestionDenied) as excinfo:
        _call_select_question(
            db_connection,
            actor=ai_actor,
            workspace_id=workspace_id,
            session_id=session_id,
            question_id=question_id,
            selection_type=SelectionType.COMPELLING,
        )

    assert excinfo.value.chain_result.result.value == "DENY"
    assert str(excinfo.value.chain_result.terminal_boundary_id) == "BoundaryId.BND_001"


def test_denies_human_without_the_right(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: human without right."""
    workspace_id, owner_id, membership_id, challenge_id, session_id = _bootstrap_session(
        db_connection, email="select-no-right@nonproof.test"
    )
    question_id = _insert_question(
        db_connection, workspace_id=workspace_id, challenge_id=challenge_id, author_user_id=owner_id
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, owner_id)

    with pytest.raises(SelectQuestionDenied) as excinfo:
        _call_select_question(
            db_connection,
            actor=actor,
            workspace_id=workspace_id,
            session_id=session_id,
            question_id=question_id,
            selection_type=SelectionType.COMPELLING,
        )

    assert excinfo.value.chain_result.result.value == "DENY"
    assert str(excinfo.value.chain_result.terminal_boundary_id) == "BoundaryId.BND_005"


def test_denies_stale_selector_authority_revoked_before_submission(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: stale selector authority."""
    workspace_id, owner_id, membership_id, challenge_id, session_id = _bootstrap_session(
        db_connection, email="select-stale@nonproof.test"
    )
    question_id = _insert_question(
        db_connection, workspace_id=workspace_id, challenge_id=challenge_id, author_user_id=owner_id
    )
    _grant_question_selection_right(
        db_connection, workspace_id=workspace_id, user_id=owner_id, session_id=session_id
    )
    db_connection.execute(
        sa.update(human_authority_bindings_table)
        .where(human_authority_bindings_table.c.human_user_id == owner_id.value)
        .values(
            state=AuthorityBindingState.REVOKED.value,
            revoked_at=_NOW,
            revoked_by_user_id=owner_id.value,
        )
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, owner_id)

    with pytest.raises(SelectQuestionDenied) as excinfo:
        _call_select_question(
            db_connection,
            actor=actor,
            workspace_id=workspace_id,
            session_id=session_id,
            question_id=question_id,
            selection_type=SelectionType.COMPELLING,
        )

    assert excinfo.value.chain_result.result.value == "DENY"
    assert str(excinfo.value.chain_result.terminal_boundary_id) == "BoundaryId.BND_005"


def test_denies_a_question_from_another_workspace(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: wrong Workspace."""
    workspace_id, owner_id, membership_id, challenge_id, session_id = _bootstrap_session(
        db_connection, email="select-wrong-ws-a@nonproof.test"
    )
    other_workspace_id, other_owner_id, _, other_challenge_id, _ = _bootstrap_session(
        db_connection, email="select-wrong-ws-b@nonproof.test"
    )
    foreign_question_id = _insert_question(
        db_connection,
        workspace_id=other_workspace_id,
        challenge_id=other_challenge_id,
        author_user_id=other_owner_id,
    )
    _grant_question_selection_right(
        db_connection, workspace_id=workspace_id, user_id=owner_id, session_id=session_id
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, owner_id)

    with pytest.raises(SelectQuestionDenied) as excinfo:
        _call_select_question(
            db_connection,
            actor=actor,
            workspace_id=workspace_id,
            session_id=session_id,
            question_id=foreign_question_id,
            selection_type=SelectionType.COMPELLING,
        )

    assert excinfo.value.chain_result.result.value == "DENY"
    assert str(excinfo.value.chain_result.terminal_boundary_id) == "BoundaryId.BND_002"


def test_denies_a_question_from_a_different_challenge_same_workspace(
    db_connection: sa.Connection,
) -> None:
    """Novel/adapted attack: same Workspace, different Challenge --
    distinct from the mandatory "wrong Workspace" attack, caught by
    BND-007's own cross-object check, not BND-002.
    """
    workspace_id, owner_id, membership_id, challenge_id, session_id = _bootstrap_session(
        db_connection, email="select-wrong-challenge@nonproof.test"
    )
    other_challenge_id = ChallengeId(_ID_GEN.new_uuid())
    db_connection.execute(
        sa.insert(challenges_table).values(
            id=other_challenge_id.value,
            workspace_id=workspace_id.value,
            title="A different Challenge",
            description=None,
            context=None,
            desired_outcome=None,
            constraints=None,
            stakeholders=None,
            created_at=_NOW,
            updated_at=_NOW,
            record_version=1,
        )
    )
    other_challenge_question_id = _insert_question(
        db_connection,
        workspace_id=workspace_id,
        challenge_id=other_challenge_id,
        author_user_id=owner_id,
    )
    _grant_question_selection_right(
        db_connection, workspace_id=workspace_id, user_id=owner_id, session_id=session_id
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, owner_id)

    with pytest.raises(SelectQuestionDenied) as excinfo:
        _call_select_question(
            db_connection,
            actor=actor,
            workspace_id=workspace_id,
            session_id=session_id,
            question_id=other_challenge_question_id,
            selection_type=SelectionType.COMPELLING,
        )

    assert excinfo.value.chain_result.result.value == "DENY"
    assert str(excinfo.value.chain_result.terminal_boundary_id) == "BoundaryId.BND_007"


def test_denies_selection_when_session_is_not_in_question_selection_state(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: selection in invalid Session state."""
    workspace_id, owner_id, membership_id, challenge_id, session_id = _bootstrap_session(
        db_connection, email="select-wrong-state@nonproof.test", final_state="ANALYSIS"
    )
    question_id = _insert_question(
        db_connection, workspace_id=workspace_id, challenge_id=challenge_id, author_user_id=owner_id
    )
    _grant_question_selection_right(
        db_connection, workspace_id=workspace_id, user_id=owner_id, session_id=session_id
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, owner_id)

    with pytest.raises(SelectQuestionDenied) as excinfo:
        _call_select_question(
            db_connection,
            actor=actor,
            workspace_id=workspace_id,
            session_id=session_id,
            question_id=question_id,
            selection_type=SelectionType.COMPELLING,
        )

    assert excinfo.value.chain_result.result.value == "DENY"
    assert str(excinfo.value.chain_result.terminal_boundary_id) == "BoundaryId.BND_007"


def test_denies_a_literal_duplicate_selection(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: duplicate selection where relation
    semantics forbid it -- the same Question, same type, same Session,
    selected twice.
    """
    workspace_id, owner_id, membership_id, challenge_id, session_id = _bootstrap_session(
        db_connection, email="select-duplicate@nonproof.test"
    )
    question_id = _insert_question(
        db_connection, workspace_id=workspace_id, challenge_id=challenge_id, author_user_id=owner_id
    )
    _grant_question_selection_right(
        db_connection, workspace_id=workspace_id, user_id=owner_id, session_id=session_id
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, owner_id)
    _call_select_question(
        db_connection,
        actor=actor,
        workspace_id=workspace_id,
        session_id=session_id,
        question_id=question_id,
        selection_type=SelectionType.COMPELLING,
    )

    with pytest.raises(CommitFailedPrecommit):
        _call_select_question(
            db_connection,
            actor=actor,
            workspace_id=workspace_id,
            session_id=session_id,
            question_id=question_id,
            selection_type=SelectionType.COMPELLING,
        )


def test_denies_a_fourth_compelling_selection(db_connection: sa.Connection) -> None:
    """Novel/adapted attack: 04 section 41's own 1-3 compelling
    cardinality cap.
    """
    workspace_id, owner_id, membership_id, challenge_id, session_id = _bootstrap_session(
        db_connection, email="select-cardinality@nonproof.test"
    )
    _grant_question_selection_right(
        db_connection, workspace_id=workspace_id, user_id=owner_id, session_id=session_id
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, owner_id)
    for _ in range(3):
        question_id = _insert_question(
            db_connection,
            workspace_id=workspace_id,
            challenge_id=challenge_id,
            author_user_id=owner_id,
        )
        _call_select_question(
            db_connection,
            actor=actor,
            workspace_id=workspace_id,
            session_id=session_id,
            question_id=question_id,
            selection_type=SelectionType.COMPELLING,
        )

    fourth_question_id = _insert_question(
        db_connection, workspace_id=workspace_id, challenge_id=challenge_id, author_user_id=owner_id
    )
    with pytest.raises(CommitFailedPrecommit):
        _call_select_question(
            db_connection,
            actor=actor,
            workspace_id=workspace_id,
            session_id=session_id,
            question_id=fourth_question_id,
            selection_type=SelectionType.COMPELLING,
        )


def test_denies_a_second_conflicting_primary_selection(db_connection: sa.Connection) -> None:
    """Novel/adapted attack: 04 section 42's own "no conflicting primary
    selection unless governed replacement is defined" -- no governed
    replacement path exists in this build phase.
    """
    workspace_id, owner_id, membership_id, challenge_id, session_id = _bootstrap_session(
        db_connection, email="select-primary-conflict@nonproof.test"
    )
    _grant_question_selection_right(
        db_connection, workspace_id=workspace_id, user_id=owner_id, session_id=session_id
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, owner_id)
    first_question_id = _insert_question(
        db_connection, workspace_id=workspace_id, challenge_id=challenge_id, author_user_id=owner_id
    )
    _call_select_question(
        db_connection,
        actor=actor,
        workspace_id=workspace_id,
        session_id=session_id,
        question_id=first_question_id,
        selection_type=SelectionType.PRIMARY,
    )

    second_question_id = _insert_question(
        db_connection, workspace_id=workspace_id, challenge_id=challenge_id, author_user_id=owner_id
    )
    with pytest.raises(CommitFailedPrecommit):
        _call_select_question(
            db_connection,
            actor=actor,
            workspace_id=workspace_id,
            session_id=session_id,
            question_id=second_question_id,
            selection_type=SelectionType.PRIMARY,
        )


def test_duplicate_idempotent_request_after_commit_is_denied(db_connection: sa.Connection) -> None:
    """Not a separate code path here -- PKG-11's own
    `IdempotencyAlreadyCommitted` mechanism, exercised through this
    package's real handler for the first time.
    """
    workspace_id, owner_id, membership_id, challenge_id, session_id = _bootstrap_session(
        db_connection, email="select-idempotent@nonproof.test"
    )
    question_id = _insert_question(
        db_connection, workspace_id=workspace_id, challenge_id=challenge_id, author_user_id=owner_id
    )
    _grant_question_selection_right(
        db_connection, workspace_id=workspace_id, user_id=owner_id, session_id=session_id
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, owner_id)
    command_id = CommandId(uuid.uuid4())
    _call_select_question(
        db_connection,
        actor=actor,
        workspace_id=workspace_id,
        session_id=session_id,
        question_id=question_id,
        selection_type=SelectionType.COMPELLING,
        idempotency_key="dup-select-1",
        command_id=command_id,
    )

    with pytest.raises(IdempotencyAlreadyCommitted):
        _call_select_question(
            db_connection,
            actor=actor,
            workspace_id=workspace_id,
            session_id=session_id,
            question_id=question_id,
            selection_type=SelectionType.COMPELLING,
            idempotency_key="dup-select-1",
            command_id=command_id,
        )


def test_denies_an_observer_role_even_with_the_right_bound(db_connection: sa.Connection) -> None:
    """Novel/adapted attack: 06 section 10's own named DENY example
    ("Observer/Viewer mutation") -- proves BND-004's role gate is
    independent of BND-005's rights check, even for a rights-gated
    operation.
    """
    workspace_id, owner_id, membership_id, challenge_id, session_id = _bootstrap_session(
        db_connection, email="select-observer@nonproof.test"
    )
    question_id = _insert_question(
        db_connection, workspace_id=workspace_id, challenge_id=challenge_id, author_user_id=owner_id
    )
    _grant_question_selection_right(
        db_connection, workspace_id=workspace_id, user_id=owner_id, session_id=session_id
    )
    _set_role(db_connection, membership_id=membership_id, role=WorkspaceRole.VIEWER)
    actor = ActorIdentity(ActorClass.HUMAN_USER, owner_id)

    with pytest.raises(SelectQuestionDenied) as excinfo:
        _call_select_question(
            db_connection,
            actor=actor,
            workspace_id=workspace_id,
            session_id=session_id,
            question_id=question_id,
            selection_type=SelectionType.COMPELLING,
        )

    assert excinfo.value.chain_result.result.value == "DENY"
    assert str(excinfo.value.chain_result.terminal_boundary_id) == "BoundaryId.BND_004"


def test_denies_when_session_no_longer_exists(db_connection: sa.Connection) -> None:
    """Novel/adapted attack: a Session referenced by a stale/forged
    session_id that was never actually created -- proves the
    `resolved_object_workspace_ids = ()` generalization (this handler's
    own module docstring) DENYs via BND-002 rather than crashing.
    """
    workspace_id, owner_id, membership_id, challenge_id, session_id = _bootstrap_session(
        db_connection, email="select-no-session@nonproof.test"
    )
    question_id = _insert_question(
        db_connection, workspace_id=workspace_id, challenge_id=challenge_id, author_user_id=owner_id
    )
    forged_session_id = SessionId(uuid.uuid4())
    actor = ActorIdentity(ActorClass.HUMAN_USER, owner_id)

    with pytest.raises(SelectQuestionDenied) as excinfo:
        _call_select_question(
            db_connection,
            actor=actor,
            workspace_id=workspace_id,
            session_id=forged_session_id,
            question_id=question_id,
            selection_type=SelectionType.COMPELLING,
        )

    assert excinfo.value.chain_result.result.value == "DENY"
    assert str(excinfo.value.chain_result.terminal_boundary_id) == "BoundaryId.BND_002"
