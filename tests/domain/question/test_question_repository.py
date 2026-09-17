"""T1 DOMAIN INVARIANT TEST: `QuestionRepository` + migration
`33e1d1feed5b`'s live PostgreSQL constraint proof.

13 §6 T1 scope: "Object identity, immutability, relation semantics."
Proves the repository's create/get contract works against a real
database (P-01: "Question persists independently") and that
`original_text`/lineage immutability holds *independently* of
`domain.question`'s own Python-level checks -- the database enforces
it a second time, exactly as PKG-05 proved for Session state
transitions.

Uses `NonProofWorkspaceBootstrap` only to obtain a real Workspace/owner
(13 §5's permitted downstream use); the invariants under test here
(Question identity, immutability, lineage) do not depend on how the
Workspace came to exist.

Expect-failure assertions use `connection.begin_nested()` (SAVEPOINT),
with `pytest.raises` as the OUTER context manager -- see
`tests/transitions/test_session_transition_constraints.py`'s module
docstring for why the order matters (a `begin_nested()` exiting after
`pytest.raises` has already swallowed the exception issues `RELEASE
SAVEPOINT` against an already-aborted connection instead of `ROLLBACK
TO SAVEPOINT`).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from domain.question import Question, QuestionOrigin
from domain.question_lineage import LineageTransformationType, QuestionLineage
from persistence.question_repository import SqlAlchemyQuestionRepository
from persistence.tables import (
    challenges_table,
    question_lineage_table,
    questions_table,
    users_table,
)
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import ChallengeId, QuestionId, RelationId, UserId, WorkspaceId
from semantic_types.versions import RecordVersion
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()


def _bootstrap_challenge(
    connection: sa.Connection, *, owner_email: str
) -> tuple[WorkspaceId, ChallengeId, UserId]:
    """Seed a Workspace + owner (`NonProofWorkspaceBootstrap`) plus one
    Challenge under it, returning the owner's `UserId` too -- callers
    use the *real* seeded owner as `author_user_id` rather than a
    disconnected freshly generated one, since a `questions.author_user_id`
    FK requires a genuinely persisted `users` row.
    """
    bootstrap = NonProofWorkspaceBootstrap(connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email=owner_email)
    challenge_id = ChallengeId(_ID_GEN.new_uuid())
    connection.execute(
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
    return result.workspace_id, challenge_id, result.owner_user_id


def _root_question(
    *, workspace_id: WorkspaceId, challenge_id: ChallengeId, author_user_id: UserId
) -> Question:
    return Question(
        question_id=QuestionId(_ID_GEN.new_uuid()),
        challenge_id=challenge_id,
        workspace_id=workspace_id,
        original_text="Why do onboarding users drop off after step 2?",
        normalized_text=None,
        origin=QuestionOrigin.HUMAN,
        author_user_id=author_user_id,
        created_at=_NOW,
        record_version=RecordVersion.initial(),
    )


def test_create_root_and_get_round_trip(db_connection: sa.Connection) -> None:
    """P-01: "Question persists independently" -- create/retrieve a
    real canonical Question row.
    """
    workspace_id, challenge_id, author_id = _bootstrap_challenge(
        db_connection, owner_email="root@nonproof.test"
    )
    question = _root_question(
        workspace_id=workspace_id, challenge_id=challenge_id, author_user_id=author_id
    )
    repo = SqlAlchemyQuestionRepository(db_connection)

    repo.create_root(question)
    fetched = repo.get(question.question_id)

    assert fetched == question


def test_get_returns_none_for_an_unknown_id(db_connection: sa.Connection) -> None:
    repo = SqlAlchemyQuestionRepository(db_connection)
    assert repo.get(QuestionId(uuid.uuid4())) is None


def test_repository_original_text_update_does_not_exist(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: repository update of original_text.

    Structural proof: no such method exists to call in the first
    place.
    """
    repo = SqlAlchemyQuestionRepository(db_connection)

    assert not hasattr(repo, "update_original_text")
    assert not hasattr(repo, "update")
    assert not hasattr(repo, "set_original_text")


def test_direct_sql_update_of_original_text_is_rejected(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: SQL update of original_text,
    bypassing the repository entirely -- `trg_questions_enforce_immutable_fields`
    rejects it at the database, independent of any Python code.
    """
    workspace_id, challenge_id, author_id = _bootstrap_challenge(
        db_connection, owner_email="sql-update@nonproof.test"
    )
    question = _root_question(
        workspace_id=workspace_id, challenge_id=challenge_id, author_user_id=author_id
    )
    repo = SqlAlchemyQuestionRepository(db_connection)
    repo.create_root(question)

    with (
        pytest.raises(sa.exc.DBAPIError, match="original_text is immutable"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.update(questions_table)
            .where(questions_table.c.id == question.question_id.value)
            .values(original_text="a completely different question")
        )


def test_direct_sql_update_of_origin_is_rejected(db_connection: sa.Connection) -> None:
    """Novel attack: bypassing the author/origin pairing rule by
    changing `origin` in place after creation (rather than at
    construction) -- also rejected by the immutability trigger.
    """
    workspace_id, challenge_id, author_id = _bootstrap_challenge(
        db_connection, owner_email="origin-update@nonproof.test"
    )
    question = _root_question(
        workspace_id=workspace_id, challenge_id=challenge_id, author_user_id=author_id
    )
    repo = SqlAlchemyQuestionRepository(db_connection)
    repo.create_root(question)

    with (
        pytest.raises(sa.exc.DBAPIError, match="origin is an immutable birth fact"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.update(questions_table)
            .where(questions_table.c.id == question.question_id.value)
            .values(origin="AI")
        )


def test_direct_enum_coercion_is_rejected_by_the_check_constraint(
    db_connection: sa.Connection,
) -> None:
    """Mandatory-category adversarial attack: direct enum coercion, at
    the schema level -- a raw SQL client bypassing `QuestionOrigin`
    entirely still cannot write an out-of-vocabulary origin.
    """
    workspace_id, challenge_id, _author_id = _bootstrap_challenge(
        db_connection, owner_email="coerce@nonproof.test"
    )

    with pytest.raises(sa.exc.DBAPIError), db_connection.begin_nested():
        db_connection.execute(
            sa.insert(questions_table).values(
                id=_ID_GEN.new_uuid(),
                challenge_id=challenge_id.value,
                workspace_id=workspace_id.value,
                original_text="does this even parse",
                normalized_text=None,
                origin="TOTALLY_MADE_UP",
                author_user_id=None,
                created_at=_NOW,
                record_version=1,
            )
        )


def test_human_origin_without_author_is_rejected_by_the_check_constraint(
    db_connection: sa.Connection,
) -> None:
    """Structural proof of the author/origin pairing rule at the
    schema level, independent of `Question.__post_init__`.
    """
    workspace_id, challenge_id, _author_id = _bootstrap_challenge(
        db_connection, owner_email="pairing-a@nonproof.test"
    )

    with pytest.raises(sa.exc.DBAPIError), db_connection.begin_nested():
        db_connection.execute(
            sa.insert(questions_table).values(
                id=_ID_GEN.new_uuid(),
                challenge_id=challenge_id.value,
                workspace_id=workspace_id.value,
                original_text="a human question with no author",
                normalized_text=None,
                origin="HUMAN",
                author_user_id=None,
                created_at=_NOW,
                record_version=1,
            )
        )


def test_ai_origin_with_an_author_is_rejected_by_the_check_constraint(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: AI reframe/import claiming human
    authorship, at the schema level.
    """
    workspace_id, challenge_id, _author_id = _bootstrap_challenge(
        db_connection, owner_email="pairing-b@nonproof.test"
    )
    bootstrap_result_author = UserId(_ID_GEN.new_uuid())

    db_connection.execute(
        sa.insert(users_table).values(
            id=bootstrap_result_author.value,
            email="claimed-author@nonproof.test",
            name="Claimed Author",
            record_version=1,
            created_at=_NOW,
            updated_at=_NOW,
        )
    )

    with pytest.raises(sa.exc.DBAPIError), db_connection.begin_nested():
        db_connection.execute(
            sa.insert(questions_table).values(
                id=_ID_GEN.new_uuid(),
                challenge_id=challenge_id.value,
                workspace_id=workspace_id.value,
                original_text="an AI question claiming a human author",
                normalized_text=None,
                origin="AI",
                author_user_id=bootstrap_result_author.value,
                created_at=_NOW,
                record_version=1,
            )
        )


def test_cross_workspace_question_target_is_not_representable(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: cross-Workspace target (Question
    variant, mirroring PKG-05's Session/Challenge proof). A Question
    naming a Challenge from Workspace A but a `workspace_id` belonging
    to Workspace B has no row to match the composite FK.
    """
    _workspace_a, challenge_in_a, _author_a = _bootstrap_challenge(
        db_connection, owner_email="cross-a@nonproof.test"
    )
    workspace_b, _challenge_in_b, _author_b = _bootstrap_challenge(
        db_connection, owner_email="cross-b@nonproof.test"
    )

    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        db_connection.execute(
            sa.insert(questions_table).values(
                id=_ID_GEN.new_uuid(),
                challenge_id=challenge_in_a.value,
                workspace_id=workspace_b.value,
                original_text="a question claiming the wrong workspace",
                normalized_text=None,
                origin="HUMAN",
                author_user_id=None,
                created_at=_NOW,
                record_version=1,
            )
        )


def test_create_derived_persists_child_and_lineage_together(db_connection: sa.Connection) -> None:
    """P-02 positive half: "create reframe as new identity" -- the
    source Question is untouched, a new Question exists, and a
    QuestionLineage relation proves the derivation.
    """
    workspace_id, challenge_id, author_id = _bootstrap_challenge(
        db_connection, owner_email="derive@nonproof.test"
    )
    parent = _root_question(
        workspace_id=workspace_id, challenge_id=challenge_id, author_user_id=author_id
    )
    repo = SqlAlchemyQuestionRepository(db_connection)
    repo.create_root(parent)

    child = Question(
        question_id=QuestionId(_ID_GEN.new_uuid()),
        challenge_id=challenge_id,
        workspace_id=workspace_id,
        original_text="What specifically happens at step 2 that causes drop-off?",
        normalized_text=None,
        origin=QuestionOrigin.HUMAN,
        author_user_id=author_id,
        created_at=_NOW,
        record_version=RecordVersion.initial(),
    )
    lineage = QuestionLineage(
        question_lineage_id=RelationId(_ID_GEN.new_uuid()),
        parent_question_id=parent.question_id,
        child_question_id=child.question_id,
        workspace_id=workspace_id,
        transformation_type=LineageTransformationType.FOLLOW_UP,
        producer_origin=QuestionOrigin.HUMAN,
        ai_generation_id=None,
        created_at=_NOW,
    )

    repo.create_derived(child, lineage)

    # Source Question is byte-for-byte untouched (AC-02-003).
    assert repo.get(parent.question_id) == parent
    assert repo.get(child.question_id) == child
    assert repo.get_lineage_for_child(child.question_id) == lineage


def test_ai_reframe_creates_new_identity_and_never_touches_the_human_original(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: AI reframe replacing human
    original. An AI-produced reframe of a human Question must (a)
    leave the human original completely unchanged, (b) create a
    distinct AI-origin Question with no author, and (c) record the
    derivation via lineage -- never overwrite, never claim the human's
    identity.
    """
    workspace_id, challenge_id, human_author = _bootstrap_challenge(
        db_connection, owner_email="ai-reframe@nonproof.test"
    )
    human_question = _root_question(
        workspace_id=workspace_id, challenge_id=challenge_id, author_user_id=human_author
    )
    repo = SqlAlchemyQuestionRepository(db_connection)
    repo.create_root(human_question)

    ai_reframe = Question(
        question_id=QuestionId(_ID_GEN.new_uuid()),
        challenge_id=challenge_id,
        workspace_id=workspace_id,
        original_text="Reframed: is step 2's friction the actual drop-off cause?",
        normalized_text=None,
        origin=QuestionOrigin.AI,
        author_user_id=None,
        created_at=_NOW,
        record_version=RecordVersion.initial(),
    )
    lineage = QuestionLineage(
        question_lineage_id=RelationId(_ID_GEN.new_uuid()),
        parent_question_id=human_question.question_id,
        child_question_id=ai_reframe.question_id,
        workspace_id=workspace_id,
        transformation_type=LineageTransformationType.REFRAME,
        producer_origin=QuestionOrigin.AI,
        ai_generation_id=None,
        created_at=_NOW,
    )

    repo.create_derived(ai_reframe, lineage)

    reloaded_human = repo.get(human_question.question_id)
    reloaded_ai = repo.get(ai_reframe.question_id)
    assert reloaded_human == human_question  # byte-for-byte unchanged
    assert reloaded_ai is not None
    assert reloaded_ai.origin is QuestionOrigin.AI
    assert reloaded_ai.author_user_id is None
    assert reloaded_ai.question_id != human_question.question_id  # distinct identity


def test_create_derived_rejects_a_mismatched_child_id(db_connection: sa.Connection) -> None:
    """Repository-level precondition: `lineage.child_question_id` must
    equal `question.question_id`.
    """
    workspace_id, challenge_id, author_id = _bootstrap_challenge(
        db_connection, owner_email="mismatch-a@nonproof.test"
    )
    parent = _root_question(
        workspace_id=workspace_id, challenge_id=challenge_id, author_user_id=author_id
    )
    repo = SqlAlchemyQuestionRepository(db_connection)
    repo.create_root(parent)

    child = _root_question(
        workspace_id=workspace_id, challenge_id=challenge_id, author_user_id=author_id
    )
    mismatched_lineage = QuestionLineage(
        question_lineage_id=RelationId(_ID_GEN.new_uuid()),
        parent_question_id=parent.question_id,
        child_question_id=QuestionId(_ID_GEN.new_uuid()),  # not child.question_id
        workspace_id=workspace_id,
        transformation_type=LineageTransformationType.REFRAME,
        producer_origin=QuestionOrigin.HUMAN,
        ai_generation_id=None,
        created_at=_NOW,
    )

    with pytest.raises(ValueError, match="child_question_id"):
        repo.create_derived(child, mismatched_lineage)


def test_invalid_self_lineage_is_rejected_by_the_check_constraint(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: invalid self-lineage, at the
    schema level (bypassing `QuestionLineage.__post_init__` entirely).
    """
    workspace_id, challenge_id, author_id = _bootstrap_challenge(
        db_connection, owner_email="self-lineage@nonproof.test"
    )
    question = _root_question(
        workspace_id=workspace_id, challenge_id=challenge_id, author_user_id=author_id
    )
    repo = SqlAlchemyQuestionRepository(db_connection)
    repo.create_root(question)

    with pytest.raises(sa.exc.DBAPIError), db_connection.begin_nested():
        db_connection.execute(
            sa.insert(question_lineage_table).values(
                id=_ID_GEN.new_uuid(),
                parent_question_id=question.question_id.value,
                child_question_id=question.question_id.value,
                workspace_id=workspace_id.value,
                transformation_type="REFRAME",
                producer_origin="HUMAN",
                ai_generation_id=None,
                created_at=_NOW,
            )
        )


def test_cross_workspace_lineage_is_not_representable(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: cross-Workspace lineage. A parent
    Question in Workspace A and a child Question in Workspace B cannot
    be linked -- the two composite foreign keys against `questions(id,
    workspace_id)` both target the *same* stored `workspace_id` value
    on the lineage row, so no single value can satisfy both when the
    parent and child genuinely live in different Workspaces.
    """
    workspace_a, challenge_a, author_a = _bootstrap_challenge(
        db_connection, owner_email="lineage-a@nonproof.test"
    )
    workspace_b, challenge_b, author_b = _bootstrap_challenge(
        db_connection, owner_email="lineage-b@nonproof.test"
    )
    repo = SqlAlchemyQuestionRepository(db_connection)

    parent = _root_question(
        workspace_id=workspace_a, challenge_id=challenge_a, author_user_id=author_a
    )
    repo.create_root(parent)

    child = _root_question(
        workspace_id=workspace_b, challenge_id=challenge_b, author_user_id=author_b
    )
    repo.create_root(child)

    # Try workspace_a on the lineage row: fails the child's FK (child
    # actually lives in workspace_b).
    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        db_connection.execute(
            sa.insert(question_lineage_table).values(
                id=_ID_GEN.new_uuid(),
                parent_question_id=parent.question_id.value,
                child_question_id=child.question_id.value,
                workspace_id=workspace_a.value,
                transformation_type="FOLLOW_UP",
                producer_origin="HUMAN",
                ai_generation_id=None,
                created_at=_NOW,
            )
        )

    # Try workspace_b: fails the parent's FK (parent actually lives in
    # workspace_a). Neither choice of workspace_id can satisfy both.
    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        db_connection.execute(
            sa.insert(question_lineage_table).values(
                id=_ID_GEN.new_uuid(),
                parent_question_id=parent.question_id.value,
                child_question_id=child.question_id.value,
                workspace_id=workspace_b.value,
                transformation_type="FOLLOW_UP",
                producer_origin="HUMAN",
                ai_generation_id=None,
                created_at=_NOW,
            )
        )


def test_lineage_reassignment_via_update_is_rejected(db_connection: sa.Connection) -> None:
    """Novel attack: lineage reassignment. 09 §32.1: "may not be
    silently reassigned to a different parent." A direct UPDATE attempt
    on an established lineage row -- even changing an unrelated-looking
    field -- is rejected unconditionally.
    """
    workspace_id, challenge_id, author_id = _bootstrap_challenge(
        db_connection, owner_email="reassign@nonproof.test"
    )
    parent = _root_question(
        workspace_id=workspace_id, challenge_id=challenge_id, author_user_id=author_id
    )
    repo = SqlAlchemyQuestionRepository(db_connection)
    repo.create_root(parent)

    child = _root_question(
        workspace_id=workspace_id, challenge_id=challenge_id, author_user_id=author_id
    )
    lineage = QuestionLineage(
        question_lineage_id=RelationId(_ID_GEN.new_uuid()),
        parent_question_id=parent.question_id,
        child_question_id=child.question_id,
        workspace_id=workspace_id,
        transformation_type=LineageTransformationType.FOLLOW_UP,
        producer_origin=QuestionOrigin.HUMAN,
        ai_generation_id=None,
        created_at=_NOW,
    )
    repo.create_derived(child, lineage)

    another_parent = _root_question(
        workspace_id=workspace_id, challenge_id=challenge_id, author_user_id=author_id
    )
    repo.create_root(another_parent)

    with (
        pytest.raises(sa.exc.DBAPIError, match="question_lineage rows are immutable"),
        db_connection.begin_nested(),
    ):
        db_connection.execute(
            sa.update(question_lineage_table)
            .where(question_lineage_table.c.id == lineage.question_lineage_id.value)
            .values(parent_question_id=another_parent.question_id.value)
        )


def test_lineage_repository_exposes_no_mutator(db_connection: sa.Connection) -> None:
    """Structural proof, matching `test_repository_original_text_update_does_not_exist`:
    no reassignment method exists on the repository for lineage
    either.
    """
    repo = SqlAlchemyQuestionRepository(db_connection)

    assert not hasattr(repo, "update_lineage")
    assert not hasattr(repo, "reassign_parent")
