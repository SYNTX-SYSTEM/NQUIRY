"""T1 DOMAIN INVARIANT TEST: `domain.question.Question` / `QuestionOrigin`.

13 §6 T1 scope: "Object identity, immutability, relation semantics."
Pure Python -- no database. The live PostgreSQL trigger/constraint
proof is `tests/domain/question/test_question_repository.py`.
"""

from __future__ import annotations

import dataclasses
import uuid
from datetime import datetime, timezone

import pytest
from domain.question import Question, QuestionOrigin
from semantic_types.ids import ChallengeId, QuestionId, UserId, WorkspaceId
from semantic_types.versions import RecordVersion

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)


def _question(**overrides: object) -> Question:
    defaults: dict[str, object] = {
        "question_id": QuestionId(uuid.uuid4()),
        "challenge_id": ChallengeId(uuid.uuid4()),
        "workspace_id": WorkspaceId(uuid.uuid4()),
        "original_text": "Why do onboarding users drop off after step 2?",
        "normalized_text": None,
        "origin": QuestionOrigin.HUMAN,
        "author_user_id": UserId(uuid.uuid4()),
        "created_at": _NOW,
        "record_version": RecordVersion.initial(),
    }
    defaults.update(overrides)
    return Question(**defaults)  # type: ignore[arg-type]


def test_question_carries_independent_identity() -> None:
    """02 §14.2: "Question.id establishes independent identity." """
    question_id = QuestionId(uuid.uuid4())
    assert _question(question_id=question_id).question_id == question_id


def test_question_is_immutable() -> None:
    """14 §3.1 gives `domain` no canonical write capability; this
    package additionally makes immutability the *point* of the object
    (AC-02-001).
    """
    question = _question()

    with pytest.raises(dataclasses.FrozenInstanceError):
        question.original_text = "a different question entirely"  # type: ignore[misc]


def test_question_exposes_no_mutator_of_any_kind() -> None:
    """14 PKG-06 FAILURE_RECOVERY: "Immutable-field mutation rejected."
    Strongest form of the guarantee: no setter/updater exists at all,
    matching the `Session` precedent from PKG-05.
    """
    setter_shaped = [
        name
        for name in dir(Question)
        if name.startswith(("set_", "update_", "edit_", "mutate", "overwrite"))
    ]
    assert setter_shaped == []


def test_question_has_no_status_field() -> None:
    """03 §25.1 (GAP-02-013): Question status vocabulary remains
    UNDERDEFINED, and 03 §25.2 forbids every use this prototype would
    have for one. Same fail-closed omission as `Challenge.status`
    (PKG-05).
    """
    field_names = {f.name for f in dataclasses.fields(Question)}

    assert "status" not in field_names
    assert not hasattr(_question(), "status")


def test_question_has_no_text_field_distinct_from_original_text() -> None:
    """GAP-02-002: `text`'s semantics remain UNDERDEFINED and 09 §31.2
    forbids it becoming "a mechanism for silently replacing
    original_text." No application contract in this package
    distinguishes the two, so no `text` field exists to become that
    mechanism.
    """
    field_names = {f.name for f in dataclasses.fields(Question)}

    assert "text" not in field_names


def test_question_has_no_classification_or_scoring_fields() -> None:
    """02 §14.9-§14.11: question_type/priority/emotional_signal/
    novelty_score/catalytic_score are classification metadata or
    derived assessments outside this package's stated objective.
    """
    field_names = {f.name for f in dataclasses.fields(Question)}

    assert field_names.isdisjoint(
        {"question_type", "priority", "emotional_signal", "novelty_score", "catalytic_score"}
    )


def test_question_requires_non_empty_original_text() -> None:
    with pytest.raises(ValueError, match="original_text must be non-empty"):
        _question(original_text="")


def test_direct_enum_coercion_of_an_unknown_origin_is_rejected() -> None:
    """Mandatory-category adversarial attack: direct enum coercion.
    `QuestionOrigin(...)` with a value from outside 02 §15's list gets
    a `ValueError`, not a new member.
    """
    with pytest.raises(ValueError):
        QuestionOrigin("REFRAMED")  # explicitly excluded -- belongs to derivation, not origin
    with pytest.raises(ValueError):
        QuestionOrigin("human")  # casing is part of the vocabulary


def test_origin_vocabulary_excludes_reframed() -> None:
    """02 §15.2 AC-02-002: `reframed` belongs to the derivation axis
    (`LineageTransformationType`), not the origin axis.
    """
    names = {origin.name for origin in QuestionOrigin}

    assert "REFRAMED" not in names
    assert names == {"HUMAN", "AI", "IMPORTED", "INFERRED"}


def test_human_origin_requires_an_author() -> None:
    """09 §31: "author_user_id nullable where non-human" -- read as a
    biconditional. A HUMAN-origin Question with no author is refused.
    """
    with pytest.raises(ValueError, match="author_user_id must be set if and only if"):
        _question(origin=QuestionOrigin.HUMAN, author_user_id=None)


def test_non_human_origin_forbids_an_author() -> None:
    """Mandatory adversarial attack: AI reframe (or import/inference)
    replacing human original -- the structural half. An AI-origin
    Question cannot claim a human author.
    """
    for origin in (QuestionOrigin.AI, QuestionOrigin.IMPORTED, QuestionOrigin.INFERRED):
        with pytest.raises(ValueError, match="author_user_id must be set if and only if"):
            _question(origin=origin, author_user_id=UserId(uuid.uuid4()))


def test_non_human_origin_with_no_author_is_valid() -> None:
    """Negative control for the pairing rule above: the *correct*
    shape for non-human origin must still construct successfully.
    """
    for origin in (QuestionOrigin.AI, QuestionOrigin.IMPORTED, QuestionOrigin.INFERRED):
        question = _question(origin=origin, author_user_id=None)
        assert question.origin is origin
        assert question.author_user_id is None


def test_question_rejects_a_bare_uuid_identity() -> None:
    with pytest.raises(TypeError, match="question_id must be a QuestionId"):
        _question(question_id=uuid.uuid4())


def test_question_belongs_to_exactly_one_challenge() -> None:
    """02 §14.3: "Question belongs to a Challenge through
    `challenge_id`." """
    challenge_id = ChallengeId(uuid.uuid4())
    assert _question(challenge_id=challenge_id).challenge_id == challenge_id

    with pytest.raises(TypeError, match="challenge_id must be a ChallengeId"):
        _question(challenge_id=uuid.uuid4())


def test_normalized_text_is_independent_of_original_text() -> None:
    """02 §14.7: `normalized_text` is a derived representation, not a
    second identity-bearing field. Setting it must not affect
    `original_text` and must not require lineage (02 §16.6:
    "Normalization is not lineage").
    """
    question = _question(original_text="original phrasing", normalized_text="normalized phrasing")

    assert question.original_text == "original phrasing"
    assert question.normalized_text == "normalized phrasing"
