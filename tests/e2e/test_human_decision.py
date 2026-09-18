"""T10 END-TO-END TEST: `application.human_decision_handler` --
OpenDecisionConsideration + RecordHumanDecision, against real
PostgreSQL.

CRITICAL PACKAGE (14 PKG-15's own prompt: ">=10 total novel/adapted
attacks required"). The second fully governed, end-to-end production
Command path in this codebase (after PKG-14's `SelectQuestion`): every
test here exercises the REAL predecessor chain -- NonProofWorkspaceBootstrap
(PKG-04) -> Challenge (PKG-05, direct SQL) -> real `AuthorityResolver`
(PKG-03) -> the real BND-001..007 evaluators (PKG-09) chained via
`boundaries.evaluate_chain` (PKG-08) -> `Bnd014CommitEvaluator`/
`CommitCoordinator` (PKG-13) -> `DecisionRepository`/`ChallengeRepository`
(this package) -> `CommandRepository`/`IdempotencyPort`/`AuditRepository`/
`OutboxRepository`/`CommitRepository` (PKG-10/11/12/13).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from application.human_decision_handler import (
    HumanDecisionDenied,
    SelectedOptionNotCandidate,
    open_decision_consideration,
    record_human_decision,
)
from authority.actor import ActorClass, ActorIdentity
from authority.resolver import AuthorityResolver
from commit.idempotency import IdempotencyAlreadyCommitted, SqlAlchemyIdempotencyRepository
from governance.authority_binding import AuthorityBindingState, AuthorityClass
from governance.membership import WorkspaceRole
from persistence.audit_repository import SqlAlchemyAuditRepository
from persistence.authority_binding_repository import SqlAlchemyAuthorityBindingRepository
from persistence.challenge_repository import (
    SqlAlchemyChallengeRepository,
    SqlAlchemyChallengeVersionReader,
)
from persistence.command_repository import SqlAlchemyCommandRepository
from persistence.commit_repository import SqlAlchemyCommitRepository
from persistence.decision_repository import (
    DecisionConflict,
    SqlAlchemyDecisionRepository,
    SqlAlchemyDecisionVersionReader,
)
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.outbox_repository import SqlAlchemyOutboxRepository
from persistence.tables import (
    challenges_table,
    decisions_table,
    human_authority_bindings_table,
    role_assignments_table,
)
from persistence.workspace_repository import SqlAlchemyWorkspaceRepository
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import (
    AttemptId,
    ChallengeId,
    CommandId,
    CommitId,
    CorrelationId,
    DecisionId,
    UserId,
    WorkspaceId,
)
from semantic_types.versions import RecordVersion
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()


def _bootstrap_challenge(
    db_connection: sa.Connection, *, email: str
) -> tuple[WorkspaceId, UserId, uuid.UUID, ChallengeId]:
    """Bootstraps a Workspace/owner, grants the owner an `OWNER` role
    assignment (the bootstrap fixture itself creates none -- BND-004
    would otherwise deny every test with `NO_CURRENT_ROLE`, mirroring
    PKG-14's own test-fixture precedent), then adds a Challenge.
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
            title="Which onboarding fix to ship first",
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
    return result.workspace_id, result.owner_user_id, result.membership_id, challenge_id


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
            id=_ID_GEN.new_uuid(),
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


def _open(
    db_connection: sa.Connection,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    challenge_id: ChallengeId,
    decision_id: DecisionId | None = None,
    options: tuple[str, ...] = ("fix_a", "fix_b"),
    idempotency_key: str | None = None,
    command_id: CommandId | None = None,
):
    return open_decision_consideration(
        db_connection,
        actor=actor,
        workspace_id=workspace_id,
        challenge_id=challenge_id,
        decision_id=decision_id or DecisionId(_ID_GEN.new_uuid()),
        decision_question_ref=None,
        decision_question_text="Which fix ships first?",
        options=options,
        criteria=("impact", "effort"),
        command_id=command_id or CommandId(uuid.uuid4()),
        attempt_id=AttemptId(uuid.uuid4()),
        correlation_id=CorrelationId(uuid.uuid4()),
        occurred_at=_NOW,
        commit_id=CommitId(uuid.uuid4()),
        idempotency_key=idempotency_key,
        workspace_repository=SqlAlchemyWorkspaceRepository(db_connection),
        membership_repository=SqlAlchemyMembershipRepository(db_connection),
        challenge_repository=SqlAlchemyChallengeRepository(db_connection),
        decision_repository=SqlAlchemyDecisionRepository(db_connection),
        authority_resolver=_resolver(db_connection),
        command_repository=SqlAlchemyCommandRepository(db_connection),
        audit_repository=SqlAlchemyAuditRepository(db_connection),
        outbox_repository=SqlAlchemyOutboxRepository(db_connection),
        commit_repository=SqlAlchemyCommitRepository(db_connection),
        idempotency_port=SqlAlchemyIdempotencyRepository(db_connection),
        current_version_reader=SqlAlchemyChallengeVersionReader(
            db_connection, challenge_id=challenge_id
        ),
    )


def _record(
    db_connection: sa.Connection,
    *,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    decision_id: DecisionId,
    selected_option: str = "fix_a",
    idempotency_key: str | None = None,
    command_id: CommandId | None = None,
):
    return record_human_decision(
        db_connection,
        actor=actor,
        workspace_id=workspace_id,
        decision_id=decision_id,
        selected_option=selected_option,
        rationale="Higher impact, lower effort",
        confidence="high",
        command_id=command_id or CommandId(uuid.uuid4()),
        attempt_id=AttemptId(uuid.uuid4()),
        correlation_id=CorrelationId(uuid.uuid4()),
        occurred_at=_NOW,
        commit_id=CommitId(uuid.uuid4()),
        idempotency_key=idempotency_key,
        evidence_set_ref=None,
        workspace_repository=SqlAlchemyWorkspaceRepository(db_connection),
        membership_repository=SqlAlchemyMembershipRepository(db_connection),
        decision_repository=SqlAlchemyDecisionRepository(db_connection),
        authority_resolver=_resolver(db_connection),
        command_repository=SqlAlchemyCommandRepository(db_connection),
        audit_repository=SqlAlchemyAuditRepository(db_connection),
        outbox_repository=SqlAlchemyOutboxRepository(db_connection),
        commit_repository=SqlAlchemyCommitRepository(db_connection),
        idempotency_port=SqlAlchemyIdempotencyRepository(db_connection),
        current_version_reader=SqlAlchemyDecisionVersionReader(
            db_connection, decision_id=decision_id
        ),
    )


def test_full_success_open_then_record_commits_atomically(db_connection: sa.Connection) -> None:
    workspace_id, owner_id, _membership_id, challenge_id = _bootstrap_challenge(
        db_connection, email="decision-success@nonproof.test"
    )
    _grant_decision_right(
        db_connection,
        workspace_id=workspace_id,
        user_id=owner_id,
        scope_type="CHALLENGE",
        scope_id=challenge_id.value,
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, owner_id)
    decision_id = DecisionId(_ID_GEN.new_uuid())

    open_commit = _open(
        db_connection,
        actor=actor,
        workspace_id=workspace_id,
        challenge_id=challenge_id,
        decision_id=decision_id,
    )
    assert open_commit.outcome.value == "COMMITTED"
    assert len(open_commit.relation_refs) == 1

    _grant_decision_right(
        db_connection,
        workspace_id=workspace_id,
        user_id=owner_id,
        scope_type="DECISION",
        scope_id=decision_id.value,
    )
    record_commit = _record(
        db_connection, actor=actor, workspace_id=workspace_id, decision_id=decision_id
    )
    assert record_commit.outcome.value == "COMMITTED"

    row = (
        db_connection.execute(
            sa.select(decisions_table).where(decisions_table.c.id == decision_id.value)
        )
        .mappings()
        .one()
    )
    assert row["state"] == "DECIDED"
    assert row["selected_option"] == "fix_a"
    assert row["decided_by_user_id"] == owner_id.value


def test_denies_ai_actor_opening_consideration(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: persist AI proposal then only
    view it -- an AI-class actor cannot even open a Decision process.
    """
    workspace_id, owner_id, _membership_id, challenge_id = _bootstrap_challenge(
        db_connection, email="decision-ai@nonproof.test"
    )
    _grant_decision_right(
        db_connection,
        workspace_id=workspace_id,
        user_id=owner_id,
        scope_type="CHALLENGE",
        scope_id=challenge_id.value,
    )
    ai_actor = ActorIdentity(ActorClass.AI_PROCESSOR, owner_id)

    with pytest.raises(HumanDecisionDenied) as excinfo:
        _open(db_connection, actor=ai_actor, workspace_id=workspace_id, challenge_id=challenge_id)

    assert excinfo.value.chain_result.result.value == "DENY"
    assert str(excinfo.value.chain_result.terminal_boundary_id) == "BoundaryId.BND_001"


def test_denies_role_only_actor_without_binding(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: role-only actor."""
    workspace_id, owner_id, _membership_id, challenge_id = _bootstrap_challenge(
        db_connection, email="decision-role-only@nonproof.test"
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, owner_id)

    with pytest.raises(HumanDecisionDenied) as excinfo:
        _open(db_connection, actor=actor, workspace_id=workspace_id, challenge_id=challenge_id)

    assert excinfo.value.chain_result.result.value == "DENY"
    assert str(excinfo.value.chain_result.terminal_boundary_id) == "BoundaryId.BND_005"


def test_denies_technical_admin_without_decision_right(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: technical admin update -- an Owner
    role holder still cannot RecordHumanDecision without an explicit
    DECISION_RIGHT binding (04: "Role alone does not grant authority").
    """
    workspace_id, owner_id, _membership_id, challenge_id = _bootstrap_challenge(
        db_connection, email="decision-admin@nonproof.test"
    )
    _grant_decision_right(
        db_connection,
        workspace_id=workspace_id,
        user_id=owner_id,
        scope_type="CHALLENGE",
        scope_id=challenge_id.value,
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, owner_id)
    decision_id = DecisionId(_ID_GEN.new_uuid())
    _open(
        db_connection,
        actor=actor,
        workspace_id=workspace_id,
        challenge_id=challenge_id,
        decision_id=decision_id,
    )
    # No DECISION_RIGHT granted at DECISION scope -- OWNER role alone
    # is not enough for RecordHumanDecision.

    with pytest.raises(HumanDecisionDenied) as excinfo:
        _record(db_connection, actor=actor, workspace_id=workspace_id, decision_id=decision_id)

    assert excinfo.value.chain_result.result.value == "DENY"
    assert str(excinfo.value.chain_result.terminal_boundary_id) == "BoundaryId.BND_005"


def test_denies_revoked_decision_right_before_record(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: revoked actor."""
    workspace_id, owner_id, _membership_id, challenge_id = _bootstrap_challenge(
        db_connection, email="decision-revoked@nonproof.test"
    )
    _grant_decision_right(
        db_connection,
        workspace_id=workspace_id,
        user_id=owner_id,
        scope_type="CHALLENGE",
        scope_id=challenge_id.value,
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, owner_id)
    decision_id = DecisionId(_ID_GEN.new_uuid())
    _open(
        db_connection,
        actor=actor,
        workspace_id=workspace_id,
        challenge_id=challenge_id,
        decision_id=decision_id,
    )
    _grant_decision_right(
        db_connection,
        workspace_id=workspace_id,
        user_id=owner_id,
        scope_type="DECISION",
        scope_id=decision_id.value,
        state=AuthorityBindingState.REVOKED,
    )

    with pytest.raises(HumanDecisionDenied) as excinfo:
        _record(db_connection, actor=actor, workspace_id=workspace_id, decision_id=decision_id)

    assert excinfo.value.chain_result.result.value == "DENY"
    assert str(excinfo.value.chain_result.terminal_boundary_id) == "BoundaryId.BND_005"


def test_denies_a_challenge_from_another_workspace(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: cross-Workspace Decision."""
    workspace_a, owner_a, _mem_a, _challenge_a = _bootstrap_challenge(
        db_connection, email="decision-cross-a@nonproof.test"
    )
    _workspace_b, _owner_b, _mem_b, challenge_b = _bootstrap_challenge(
        db_connection, email="decision-cross-b@nonproof.test"
    )
    _grant_decision_right(
        db_connection,
        workspace_id=workspace_a,
        user_id=owner_a,
        scope_type="CHALLENGE",
        scope_id=challenge_b.value,
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, owner_a)

    with pytest.raises(HumanDecisionDenied) as excinfo:
        _open(db_connection, actor=actor, workspace_id=workspace_a, challenge_id=challenge_b)

    assert excinfo.value.chain_result.result.value == "DENY"
    assert str(excinfo.value.chain_result.terminal_boundary_id) == "BoundaryId.BND_002"


def test_denies_record_when_decision_absent(db_connection: sa.Connection) -> None:
    """Novel/adapted attack: state skip -- RecordHumanDecision with no
    prior OpenDecisionConsideration at all.
    """
    workspace_id, owner_id, _membership_id, _challenge_id = _bootstrap_challenge(
        db_connection, email="decision-absent@nonproof.test"
    )
    forged_decision_id = DecisionId(uuid.uuid4())
    _grant_decision_right(
        db_connection,
        workspace_id=workspace_id,
        user_id=owner_id,
        scope_type="DECISION",
        scope_id=forged_decision_id.value,
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, owner_id)

    with pytest.raises(HumanDecisionDenied) as excinfo:
        _record(
            db_connection, actor=actor, workspace_id=workspace_id, decision_id=forged_decision_id
        )

    assert excinfo.value.chain_result.result.value == "DENY"
    assert str(excinfo.value.chain_result.terminal_boundary_id) == "BoundaryId.BND_002"


def test_denies_a_second_open_against_the_same_decision_id(db_connection: sa.Connection) -> None:
    """Novel/adapted attack: a second OpenDecisionConsideration against
    an already-`UNDER_CONSIDERATION` decision_id.
    """
    workspace_id, owner_id, _membership_id, challenge_id = _bootstrap_challenge(
        db_connection, email="decision-reopen@nonproof.test"
    )
    _grant_decision_right(
        db_connection,
        workspace_id=workspace_id,
        user_id=owner_id,
        scope_type="CHALLENGE",
        scope_id=challenge_id.value,
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, owner_id)
    decision_id = DecisionId(_ID_GEN.new_uuid())
    _open(
        db_connection,
        actor=actor,
        workspace_id=workspace_id,
        challenge_id=challenge_id,
        decision_id=decision_id,
    )

    with pytest.raises(HumanDecisionDenied) as excinfo:
        _open(
            db_connection,
            actor=actor,
            workspace_id=workspace_id,
            challenge_id=challenge_id,
            decision_id=decision_id,
        )

    assert excinfo.value.chain_result.result.value == "DENY"
    assert str(excinfo.value.chain_result.terminal_boundary_id) == "BoundaryId.BND_007"


def test_denies_a_second_record_against_an_already_decided_decision(
    db_connection: sa.Connection,
) -> None:
    """Novel/adapted attack: 03 section 38 -- DECIDED is terminal, a
    second RecordHumanDecision must not succeed.
    """
    workspace_id, owner_id, _membership_id, challenge_id = _bootstrap_challenge(
        db_connection, email="decision-re-record@nonproof.test"
    )
    _grant_decision_right(
        db_connection,
        workspace_id=workspace_id,
        user_id=owner_id,
        scope_type="CHALLENGE",
        scope_id=challenge_id.value,
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, owner_id)
    decision_id = DecisionId(_ID_GEN.new_uuid())
    _open(
        db_connection,
        actor=actor,
        workspace_id=workspace_id,
        challenge_id=challenge_id,
        decision_id=decision_id,
    )
    _grant_decision_right(
        db_connection,
        workspace_id=workspace_id,
        user_id=owner_id,
        scope_type="DECISION",
        scope_id=decision_id.value,
    )
    _record(db_connection, actor=actor, workspace_id=workspace_id, decision_id=decision_id)

    with pytest.raises(HumanDecisionDenied) as excinfo:
        _record(
            db_connection,
            actor=actor,
            workspace_id=workspace_id,
            decision_id=decision_id,
            selected_option="fix_b",
        )

    assert excinfo.value.chain_result.result.value == "DENY"
    assert str(excinfo.value.chain_result.terminal_boundary_id) == "BoundaryId.BND_007"


def test_denies_selected_option_not_among_candidates(db_connection: sa.Connection) -> None:
    """Novel/adapted attack: 04 section 50 DENY CONDITION -- "Selected
    option not explicitly human-adopted", in its "not even a candidate
    option" shape.
    """
    workspace_id, owner_id, _membership_id, challenge_id = _bootstrap_challenge(
        db_connection, email="decision-bad-option@nonproof.test"
    )
    _grant_decision_right(
        db_connection,
        workspace_id=workspace_id,
        user_id=owner_id,
        scope_type="CHALLENGE",
        scope_id=challenge_id.value,
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, owner_id)
    decision_id = DecisionId(_ID_GEN.new_uuid())
    _open(
        db_connection,
        actor=actor,
        workspace_id=workspace_id,
        challenge_id=challenge_id,
        decision_id=decision_id,
    )
    _grant_decision_right(
        db_connection,
        workspace_id=workspace_id,
        user_id=owner_id,
        scope_type="DECISION",
        scope_id=decision_id.value,
    )

    with pytest.raises(SelectedOptionNotCandidate):
        _record(
            db_connection,
            actor=actor,
            workspace_id=workspace_id,
            decision_id=decision_id,
            selected_option="not_an_option",
        )


def test_duplicate_idempotent_record_after_commit_is_denied(db_connection: sa.Connection) -> None:
    """Not a separate code path here -- PKG-11's own
    `IdempotencyAlreadyCommitted` mechanism, exercised through this
    package's real handler.
    """
    workspace_id, owner_id, _membership_id, challenge_id = _bootstrap_challenge(
        db_connection, email="decision-idempotent@nonproof.test"
    )
    _grant_decision_right(
        db_connection,
        workspace_id=workspace_id,
        user_id=owner_id,
        scope_type="CHALLENGE",
        scope_id=challenge_id.value,
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, owner_id)
    decision_id = DecisionId(_ID_GEN.new_uuid())
    _open(
        db_connection,
        actor=actor,
        workspace_id=workspace_id,
        challenge_id=challenge_id,
        decision_id=decision_id,
    )
    _grant_decision_right(
        db_connection,
        workspace_id=workspace_id,
        user_id=owner_id,
        scope_type="DECISION",
        scope_id=decision_id.value,
    )
    command_id = CommandId(uuid.uuid4())
    _record(
        db_connection,
        actor=actor,
        workspace_id=workspace_id,
        decision_id=decision_id,
        idempotency_key="dup-record-1",
        command_id=command_id,
    )

    with pytest.raises(IdempotencyAlreadyCommitted):
        _record(
            db_connection,
            actor=actor,
            workspace_id=workspace_id,
            decision_id=decision_id,
            idempotency_key="dup-record-1",
            command_id=command_id,
        )


def test_denies_an_observer_role_even_with_the_right_bound(db_connection: sa.Connection) -> None:
    """Novel/adapted attack: 06 section 10's own named DENY example
    ("Observer/Viewer mutation").
    """
    workspace_id, owner_id, membership_id, challenge_id = _bootstrap_challenge(
        db_connection, email="decision-observer@nonproof.test"
    )
    _grant_decision_right(
        db_connection,
        workspace_id=workspace_id,
        user_id=owner_id,
        scope_type="CHALLENGE",
        scope_id=challenge_id.value,
    )
    _set_role(db_connection, membership_id=membership_id, role=WorkspaceRole.VIEWER)
    actor = ActorIdentity(ActorClass.HUMAN_USER, owner_id)

    with pytest.raises(HumanDecisionDenied) as excinfo:
        _open(db_connection, actor=actor, workspace_id=workspace_id, challenge_id=challenge_id)

    assert excinfo.value.chain_result.result.value == "DENY"
    assert str(excinfo.value.chain_result.terminal_boundary_id) == "BoundaryId.BND_004"


def test_concurrent_record_only_one_commits(db_connection: sa.Connection) -> None:
    """Mandatory-category persistence/concurrency attack: two
    DECISION_RIGHT holders racing to record the same Decision.
    Simulated deterministically via a stale `expected_record_version`
    passed to the second attempt's own mutation, mirroring PKG-13's own
    "concurrent Commands" proof technique.
    """
    workspace_id, owner_id, _membership_id, challenge_id = _bootstrap_challenge(
        db_connection, email="decision-concurrent@nonproof.test"
    )
    _grant_decision_right(
        db_connection,
        workspace_id=workspace_id,
        user_id=owner_id,
        scope_type="CHALLENGE",
        scope_id=challenge_id.value,
    )
    actor = ActorIdentity(ActorClass.HUMAN_USER, owner_id)
    decision_id = DecisionId(_ID_GEN.new_uuid())
    _open(
        db_connection,
        actor=actor,
        workspace_id=workspace_id,
        challenge_id=challenge_id,
        decision_id=decision_id,
    )
    _grant_decision_right(
        db_connection,
        workspace_id=workspace_id,
        user_id=owner_id,
        scope_type="DECISION",
        scope_id=decision_id.value,
    )
    _record(db_connection, actor=actor, workspace_id=workspace_id, decision_id=decision_id)

    with pytest.raises(DecisionConflict):
        SqlAlchemyDecisionRepository(db_connection).record_decision(
            decision_id=decision_id,
            workspace_id=workspace_id,
            expected_record_version=RecordVersion(1),
            decided_by_user_id=owner_id,
            selected_option="fix_b",
            rationale=None,
            confidence=None,
            decided_at=_NOW,
        )
