"""F03 WU-03.3 (FBR-F03-4): the frozen-set fingerprint is computed over
IMMUTABLE birth facts only, so a frozen raw set stays reconstructable after
legitimate post-Burst work on the Questions (03 §25.5, F04).

MUST BECOME TRUE: the fingerprint is a pure function of, per member, the
membership id, question id, the SHA-256 digest of the exact `original_text`,
`captured_order`, capture actor and `captured_at`. Input order does not matter;
the same set always yields the same fingerprint.

MUST REMAIN IMPOSSIBLE: a fingerprint that depends on a mutable column
(`normalized_text`, `record_version`); a fingerprint that survives a changed
`original_text`, a changed order, a changed actor, a changed capture time, an
added or removed member; a fingerprint over an empty set; an incomplete
fingerprint (a member without its text).
"""

from __future__ import annotations

import inspect
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from domain.burst_membership import QuestionBurstMembership, compute_frozen_membership_fingerprint
from domain.question import QuestionOrigin
from semantic_types.ids import BurstId, QuestionId, RelationId, UserId, WorkspaceId
from semantic_types.versions import RecordVersion

_T0 = datetime(2026, 9, 24, 9, 0, tzinfo=timezone.utc)
_BURST = BurstId(uuid.uuid4())
_WS = WorkspaceId(uuid.uuid4())
_ACTOR = UserId(uuid.uuid4())


def _member(order: int, *, actor: UserId = _ACTOR, at: datetime = _T0) -> QuestionBurstMembership:
    return QuestionBurstMembership(
        burst_question_membership_id=RelationId(uuid.uuid4()),
        question_burst_id=_BURST,
        question_id=QuestionId(uuid.uuid4()),
        workspace_id=_WS,
        captured_order=order,
        captured_at=at,
        capture_actor_user_id=actor,
        capture_origin=QuestionOrigin.HUMAN,
        record_version=RecordVersion.initial(),
    )


def _set() -> tuple[list[QuestionBurstMembership], dict[QuestionId, str]]:
    ms = [_member(0), _member(1), _member(2)]
    texts = {m.question_id: f"Question {i}?" for i, m in enumerate(ms)}
    return ms, texts


def test_signature_takes_original_texts_not_record_versions() -> None:
    params = inspect.signature(compute_frozen_membership_fingerprint).parameters
    assert "question_original_texts" in params
    assert "question_record_versions" not in params


def test_deterministic_and_input_order_independent() -> None:
    ms, texts = _set()
    a = compute_frozen_membership_fingerprint(ms, texts)
    b = compute_frozen_membership_fingerprint(list(reversed(ms)), texts)
    assert a == b and len(a) == 64


def test_original_text_change_changes_fingerprint() -> None:
    ms, texts = _set()
    base = compute_frozen_membership_fingerprint(ms, texts)
    changed = dict(texts)
    changed[ms[1].question_id] = "Question 1? "  # one trailing space
    assert compute_frozen_membership_fingerprint(ms, changed) != base


def test_capture_facts_change_fingerprint() -> None:
    ms, texts = _set()
    base = compute_frozen_membership_fingerprint(ms, texts)
    reordered = [ms[0], _rebuilt(ms[1], order=5), ms[2]]
    other_actor = [ms[0], _rebuilt(ms[1], actor=UserId(uuid.uuid4())), ms[2]]
    later = [ms[0], _rebuilt(ms[1], at=_T0 + timedelta(seconds=1)), ms[2]]
    for variant in (reordered, other_actor, later):
        assert compute_frozen_membership_fingerprint(variant, texts) != base


def _rebuilt(m: QuestionBurstMembership, **kw: object) -> QuestionBurstMembership:
    return QuestionBurstMembership(
        burst_question_membership_id=m.burst_question_membership_id,
        question_burst_id=m.question_burst_id,
        question_id=m.question_id,
        workspace_id=m.workspace_id,
        captured_order=kw.get("order", m.captured_order),  # type: ignore[arg-type]
        captured_at=kw.get("at", m.captured_at),  # type: ignore[arg-type]
        capture_actor_user_id=kw.get("actor", m.capture_actor_user_id),  # type: ignore[arg-type]
        capture_origin=m.capture_origin,
        record_version=m.record_version,
    )


def test_membership_record_version_is_not_an_input() -> None:
    ms, texts = _set()
    base = compute_frozen_membership_fingerprint(ms, texts)
    bumped = [
        QuestionBurstMembership(
            burst_question_membership_id=m.burst_question_membership_id,
            question_burst_id=m.question_burst_id,
            question_id=m.question_id,
            workspace_id=m.workspace_id,
            captured_order=m.captured_order,
            captured_at=m.captured_at,
            capture_actor_user_id=m.capture_actor_user_id,
            capture_origin=m.capture_origin,
            record_version=RecordVersion(9),
        )
        for m in ms
    ]
    assert compute_frozen_membership_fingerprint(bumped, texts) == base


def test_added_or_removed_member_changes_fingerprint() -> None:
    ms, texts = _set()
    base = compute_frozen_membership_fingerprint(ms, texts)
    assert compute_frozen_membership_fingerprint(ms[:2], texts) != base
    extra = _member(3)
    assert (
        compute_frozen_membership_fingerprint([*ms, extra], {**texts, extra.question_id: "x?"})
        != base
    )


def test_empty_set_is_refused() -> None:
    with pytest.raises(ValueError, match="zero"):
        compute_frozen_membership_fingerprint([], {})


def test_missing_text_is_refused_not_omitted() -> None:
    ms, texts = _set()
    del texts[ms[2].question_id]
    with pytest.raises(ValueError, match="original_text"):
        compute_frozen_membership_fingerprint(ms, texts)


def test_text_is_hashed_exactly_no_normalization() -> None:
    ms, texts = _set()
    nfc = {**texts, ms[0].question_id: "café?"}
    nfd = {**texts, ms[0].question_id: "café?"}
    assert compute_frozen_membership_fingerprint(ms, nfc) != compute_frozen_membership_fingerprint(
        ms, nfd
    )
