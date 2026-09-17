"""T1 DOMAIN INVARIANT TEST: `domain.question_lineage.QuestionLineage`.

13 §6 T1 scope: "Object identity, immutability, relation semantics."
Pure Python -- no database.
"""

from __future__ import annotations

import dataclasses
import uuid
from datetime import datetime, timezone

import pytest
from domain.question import QuestionOrigin
from domain.question_lineage import LineageTransformationType, QuestionLineage
from semantic_types.ids import GenerationId, QuestionId, RelationId, WorkspaceId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)


def _lineage(**overrides: object) -> QuestionLineage:
    defaults: dict[str, object] = {
        "question_lineage_id": RelationId(uuid.uuid4()),
        "parent_question_id": QuestionId(uuid.uuid4()),
        "child_question_id": QuestionId(uuid.uuid4()),
        "workspace_id": WorkspaceId(uuid.uuid4()),
        "transformation_type": LineageTransformationType.REFRAME,
        "producer_origin": QuestionOrigin.HUMAN,
        "ai_generation_id": None,
        "created_at": _NOW,
    }
    defaults.update(overrides)
    return QuestionLineage(**defaults)  # type: ignore[arg-type]


def test_lineage_relates_a_child_to_a_parent_question() -> None:
    """02 §16.3: "Question child -> derived from / follows Question
    parent." """
    parent_id = QuestionId(uuid.uuid4())
    child_id = QuestionId(uuid.uuid4())

    lineage = _lineage(parent_question_id=parent_id, child_question_id=child_id)

    assert lineage.parent_question_id == parent_id
    assert lineage.child_question_id == child_id


def test_lineage_is_immutable() -> None:
    """09 §32.1: lineage "may not be silently reassigned to a
    different parent."
    """
    lineage = _lineage()

    with pytest.raises(dataclasses.FrozenInstanceError):
        lineage.parent_question_id = QuestionId(uuid.uuid4())  # type: ignore[misc]


def test_lineage_exposes_no_mutator_of_any_kind() -> None:
    setter_shaped = [
        name
        for name in dir(QuestionLineage)
        if name.startswith(("set_", "update_", "reassign", "edit_"))
    ]
    assert setter_shaped == []


def test_invalid_self_lineage_is_rejected() -> None:
    """Mandatory adversarial attack: invalid self-lineage. A Question
    cannot be derived from itself.
    """
    question_id = QuestionId(uuid.uuid4())

    with pytest.raises(ValueError, match="parent_question_id and child_question_id must differ"):
        _lineage(parent_question_id=question_id, child_question_id=question_id)


def test_direct_enum_coercion_of_an_unknown_transformation_type_is_rejected() -> None:
    """Mandatory-category adversarial attack: direct enum coercion."""
    with pytest.raises(ValueError):
        LineageTransformationType("NORMALIZE")  # 02 §16.6: normalization is not lineage
    with pytest.raises(ValueError):
        LineageTransformationType("reframe")  # casing is part of the vocabulary


def test_transformation_type_vocabulary_excludes_normalization() -> None:
    """02 §16.6: "Normalization is not lineage." No corresponding
    member exists.
    """
    names = {t.name for t in LineageTransformationType}

    assert "NORMALIZE" not in names
    assert "NORMALIZATION" not in names
    assert names == {"REFRAME", "FOLLOW_UP"}


def test_lineage_rejects_a_bare_uuid_identity() -> None:
    with pytest.raises(TypeError, match="question_lineage_id must be a RelationId"):
        _lineage(question_lineage_id=uuid.uuid4())


def test_lineage_rejects_a_question_id_where_relation_id_belongs() -> None:
    """Negative: the relation's own identity must not be confusable
    with either endpoint's identity.
    """
    with pytest.raises(TypeError, match="question_lineage_id must be a RelationId"):
        _lineage(question_lineage_id=QuestionId(uuid.uuid4()))


def test_ai_generation_id_accepts_none_or_a_generation_id() -> None:
    """09 §32: `ai_generation_id` is nullable. A human-driven reframe
    has none; an AI-driven one references a GenerationId (no FK exists
    at the schema level yet -- see the migration's docstring -- but the
    Python type is still enforced)."""
    lineage_without = _lineage(ai_generation_id=None)
    assert lineage_without.ai_generation_id is None

    generation_id = GenerationId(uuid.uuid4())
    lineage_with = _lineage(ai_generation_id=generation_id)
    assert lineage_with.ai_generation_id == generation_id

    with pytest.raises(TypeError, match="ai_generation_id must be a GenerationId or None"):
        _lineage(ai_generation_id=uuid.uuid4())
