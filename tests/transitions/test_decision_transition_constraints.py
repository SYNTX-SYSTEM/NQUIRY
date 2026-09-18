"""T2 TRANSITION TEST: `domain.decision`'s pure topology plus migration
`e2f94137f8a9`'s live PostgreSQL constraint proof for `decisions`.

Mirrors `test_burst_transition_constraints.py`'s design exactly (same
SAVEPOINT-ordering discipline: `pytest.raises` is always the OUTER
context manager, `db_connection.begin_nested()` the inner one).
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from domain.decision import (
    DecisionState,
    DecisionTransitionId,
    resolve_decision_transition_to_state,
)
from persistence.decision_repository import DecisionConflict, SqlAlchemyDecisionRepository
from persistence.tables import challenges_table, decisions_table
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import ChallengeId, DecisionId, WorkspaceId
from semantic_types.versions import RecordVersion
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()


def _bootstrap_challenge(connection: sa.Connection, *, owner_email: str):
    result = NonProofWorkspaceBootstrap(connection, FixedClock(_NOW), _ID_GEN).seed(
        owner_email=owner_email
    )
    challenge_id = ChallengeId(_ID_GEN.new_uuid())
    connection.execute(
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
    return result.workspace_id, challenge_id, result.owner_user_id


def _decision_row_values(
    *, decision_id: DecisionId, workspace_id: WorkspaceId, challenge_id: ChallengeId, owner
):
    return dict(
        id=decision_id.value,
        workspace_id=workspace_id.value,
        challenge_id=challenge_id.value,
        decision_question_ref=None,
        decision_question_text="Which fix ships first?",
        options=["fix_a", "fix_b"],
        criteria=["impact", "effort"],
        selected_option=None,
        rationale=None,
        confidence=None,
        state="UNDER_CONSIDERATION",
        opened_by_user_id=owner.value,
        decision_authority_binding_id=_ID_GEN.new_uuid(),
        decided_by_user_id=None,
        created_at=_NOW,
        decided_at=None,
        record_version=1,
        provenance_ref=None,
    )


# --- Pure domain topology (no DB) ---------------------------------------


def test_resolves_open_from_absent() -> None:
    resolution = resolve_decision_transition_to_state(
        current_state=None, target_state=DecisionState.UNDER_CONSIDERATION
    )
    assert resolution.is_state_eligible


def test_resolves_record_from_under_consideration() -> None:
    resolution = resolve_decision_transition_to_state(
        current_state=DecisionState.UNDER_CONSIDERATION, target_state=DecisionState.DECIDED
    )
    assert resolution.is_state_eligible


def test_denies_record_when_decision_absent() -> None:
    """Mandatory-category adversarial attack: state skip -- RecordHumanDecision
    with no prior OpenDecisionConsideration.
    """
    resolution = resolve_decision_transition_to_state(
        current_state=None, target_state=DecisionState.DECIDED
    )
    assert not resolution.is_state_eligible
    assert resolution.verdict.value == "DENIED_ILLEGAL_TRANSITION"


def test_denies_a_second_open_against_an_already_open_decision() -> None:
    resolution = resolve_decision_transition_to_state(
        current_state=DecisionState.UNDER_CONSIDERATION,
        target_state=DecisionState.UNDER_CONSIDERATION,
    )
    assert not resolution.is_state_eligible
    assert resolution.verdict.value == "DENIED_DECISION_ALREADY_EXISTS"


def test_denies_decided_to_under_consideration_reversal() -> None:
    """03 section 38 (GAP-03-005): "03 does not permit
    DECIDED -> UNDER_CONSIDERATION as a silent rewrite."
    """
    resolution = resolve_decision_transition_to_state(
        current_state=DecisionState.DECIDED, target_state=DecisionState.UNDER_CONSIDERATION
    )
    assert not resolution.is_state_eligible


def test_decision_transition_id_values_are_closed() -> None:
    assert {t.value for t in DecisionTransitionId} == {"TRN-DEC-001", "TRN-DEC-002"}


# --- Live PostgreSQL constraint proof -----------------------------------


def test_decision_created_in_under_consideration_succeeds(db_connection: sa.Connection) -> None:
    workspace_id, challenge_id, owner = _bootstrap_challenge(
        db_connection, owner_email="decision-open@nonproof.test"
    )
    decision_id = DecisionId(_ID_GEN.new_uuid())
    db_connection.execute(
        sa.insert(decisions_table).values(
            **_decision_row_values(
                decision_id=decision_id,
                workspace_id=workspace_id,
                challenge_id=challenge_id,
                owner=owner,
            )
        )
    )

    repo = SqlAlchemyDecisionRepository(db_connection)
    decision = repo.get(decision_id)
    assert decision is not None
    assert decision.state is DecisionState.UNDER_CONSIDERATION


def test_decision_created_outside_under_consideration_is_rejected(
    db_connection: sa.Connection,
) -> None:
    workspace_id, challenge_id, owner = _bootstrap_challenge(
        db_connection, owner_email="decision-open-bad@nonproof.test"
    )
    values = _decision_row_values(
        decision_id=DecisionId(_ID_GEN.new_uuid()),
        workspace_id=workspace_id,
        challenge_id=challenge_id,
        owner=owner,
    )
    values["state"] = "DECIDED"
    values["decided_by_user_id"] = owner.value
    values["decided_at"] = _NOW
    values["selected_option"] = "fix_a"

    with (
        pytest.raises(sa.exc.DBAPIError, match="must be created in UNDER_CONSIDERATION"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(sa.insert(decisions_table).values(**values))


def test_illegal_decision_transition_is_rejected(db_connection: sa.Connection) -> None:
    """With only 2 legal states, the only way to exercise the
    transition trigger's own illegal-pair branch (as opposed to the
    separate terminal-state or CHECK-vocabulary guards) is a third,
    undefined target value -- the trigger fires BEFORE constraint
    checking in PostgreSQL, so this is caught here, not by
    `ck_decisions_state_vocabulary`.
    """
    workspace_id, challenge_id, owner = _bootstrap_challenge(
        db_connection, owner_email="decision-illegal@nonproof.test"
    )
    decision_id = DecisionId(_ID_GEN.new_uuid())
    db_connection.execute(
        sa.insert(decisions_table).values(
            **_decision_row_values(
                decision_id=decision_id,
                workspace_id=workspace_id,
                challenge_id=challenge_id,
                owner=owner,
            )
        )
    )

    with (
        pytest.raises(sa.exc.DBAPIError, match="illegal decision transition"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.update(decisions_table)
            .where(decisions_table.c.id == decision_id.value)
            .values(
                state="MADE_UP_STATE",
                record_version=2,
            )
        )


def test_decided_decision_is_fully_immutable(db_connection: sa.Connection) -> None:
    """03 section 38: DECIDED is terminal -- not just for `state`, for
    the whole row (mirrors `question_bursts`' own COMPLETED-immutability
    precedent, PKG-07).
    """
    workspace_id, challenge_id, owner = _bootstrap_challenge(
        db_connection, owner_email="decision-immutable@nonproof.test"
    )
    decision_id = DecisionId(_ID_GEN.new_uuid())
    db_connection.execute(
        sa.insert(decisions_table).values(
            **_decision_row_values(
                decision_id=decision_id,
                workspace_id=workspace_id,
                challenge_id=challenge_id,
                owner=owner,
            )
        )
    )
    repo = SqlAlchemyDecisionRepository(db_connection)
    repo.record_decision(
        decision_id=decision_id,
        workspace_id=workspace_id,
        expected_record_version=RecordVersion(1),
        decided_by_user_id=owner,
        selected_option="fix_a",
        rationale="Higher impact, lower effort",
        confidence="high",
        decided_at=_NOW,
    )

    with (
        pytest.raises(sa.exc.DBAPIError, match="is DECIDED, which is terminal"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.update(decisions_table)
            .where(decisions_table.c.id == decision_id.value)
            .values(record_version=3)
        )


def test_decided_without_attribution_is_rejected_at_the_database_layer(
    db_connection: sa.Connection,
) -> None:
    """Mandatory-category adversarial attack: unattributed Decision --
    proven at the DB layer independent of `Decision.__post_init__`.
    `trg_decisions_enforce_initial_state` requires every INSERT to be
    `UNDER_CONSIDERATION` (03 TRN-DEC-001's own single entry point), so
    the only way to reach `DECIDED` at all -- legally or not -- is an
    UPDATE; the CHECK constraint fires on that UPDATE once the
    transition-topology trigger's own check (a legal
    UNDER_CONSIDERATION -> DECIDED pair) has already passed.
    """
    workspace_id, challenge_id, owner = _bootstrap_challenge(
        db_connection, owner_email="decision-unattributed@nonproof.test"
    )
    decision_id = DecisionId(_ID_GEN.new_uuid())
    db_connection.execute(
        sa.insert(decisions_table).values(
            **_decision_row_values(
                decision_id=decision_id,
                workspace_id=workspace_id,
                challenge_id=challenge_id,
                owner=owner,
            )
        )
    )

    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        db_connection.execute(
            sa.update(decisions_table)
            .where(decisions_table.c.id == decision_id.value)
            .values(state="DECIDED", selected_option="fix_a", record_version=2)
            # decided_by_user_id / decided_at deliberately left unset.
        )


def test_cross_workspace_decision_target_is_not_representable(db_connection: sa.Connection) -> None:
    """Mandatory-category Workspace attack, Decision variant."""
    _workspace_a, challenge_a, owner_a = _bootstrap_challenge(
        db_connection, owner_email="decision-cross-a@nonproof.test"
    )
    workspace_b, _challenge_b, _owner_b = _bootstrap_challenge(
        db_connection, owner_email="decision-cross-b@nonproof.test"
    )

    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        db_connection.execute(
            sa.insert(decisions_table).values(
                **_decision_row_values(
                    decision_id=DecisionId(_ID_GEN.new_uuid()),
                    workspace_id=workspace_b,
                    challenge_id=challenge_a,
                    owner=owner_a,
                )
            )
        )


def test_decision_conflict_raised_on_stale_expected_version(db_connection: sa.Connection) -> None:
    workspace_id, challenge_id, owner = _bootstrap_challenge(
        db_connection, owner_email="decision-stale@nonproof.test"
    )
    decision_id = DecisionId(_ID_GEN.new_uuid())
    db_connection.execute(
        sa.insert(decisions_table).values(
            **_decision_row_values(
                decision_id=decision_id,
                workspace_id=workspace_id,
                challenge_id=challenge_id,
                owner=owner,
            )
        )
    )
    repo = SqlAlchemyDecisionRepository(db_connection)

    with pytest.raises(DecisionConflict):
        repo.record_decision(
            decision_id=decision_id,
            workspace_id=workspace_id,
            expected_record_version=RecordVersion(99),  # wrong
            decided_by_user_id=owner,
            selected_option="fix_a",
            rationale=None,
            confidence=None,
            decided_at=_NOW,
        )
