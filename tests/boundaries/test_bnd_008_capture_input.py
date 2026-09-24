"""F03 WU-03.5 (HD-12): BND-008 establishes BURST_INPUT_VALID for capture.

MUST BECOME TRUE: a HUMAN capture with a valid input check is ALLOWed.
MUST REMAIN IMPOSSIBLE: a capture ALLOWed with no established input validity
(06 BND-008 REQUIRE: "If BURST_INPUT_VALID cannot be established by a
source-compatible mechanism: REQUIRE"); an invalid input ALLOWed; a capture by
an AI_PROCESSOR or SYSTEM_SERVICE ("Human submission requires authenticated
Session Participant. AI must remain AI_PROCESSOR."); the application guard and
the boundary disagreeing on the capture actor rule.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from application.burst_contamination import (
    BurstContaminationVerdict,
    BurstOperationCategory,
    ContaminationDenyReason,
    evaluate_burst_contamination_guard,
)
from authority.actor import ActorClass, ActorIdentity
from boundaries.bnd_008_question_burst import (
    Bnd008Input,
    Bnd008OperationCategory,
    Bnd008QuestionBurstEvaluator,
)
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from domain.burst import BurstState
from domain.burst_input import BurstInputCheck, check_burst_input
from semantic_types.ids import CorrelationId, UserId, WorkspaceId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)


def _evaluate(actor_class: ActorClass, input_check: BurstInputCheck | None):  # noqa: ANN202
    context = BoundaryContext(
        workspace_id=WorkspaceId(uuid.uuid4()),
        operation="CMD_CAPTURE_BURST_QUESTION",
        actor=ActorIdentity(actor_class, UserId(uuid.uuid4())),
        correlation_id=CorrelationId(uuid.uuid4()),
        evaluated_at=_NOW,
    )
    return Bnd008QuestionBurstEvaluator().evaluate(
        Bnd008Input(
            boundary_id=BoundaryId.BND_008,
            context=context,
            burst_state=BurstState.ACTIVE,
            operation_category=Bnd008OperationCategory.CAPTURE_BURST_QUESTION,
            input_check=input_check,
        ),
        context,
    )


def test_valid_human_capture_is_allowed() -> None:
    proof = _evaluate(ActorClass.HUMAN_USER, check_burst_input("Why did it drop?"))
    assert proof.result is BoundaryResult.ALLOW
    assert proof.reason_code == "BURST_INPUT_VALID"


def test_capture_without_established_input_validity_requires() -> None:
    proof = _evaluate(ActorClass.HUMAN_USER, None)
    assert proof.result is BoundaryResult.REQUIRE
    assert proof.reason_code == "BURST_INPUT_VALID_NOT_ESTABLISHED"


@pytest.mark.parametrize(
    ("text", "code"),
    [("It dropped.", "INPUT_NOT_A_QUESTION"), ("   ", "INPUT_EMPTY")],
)
def test_invalid_input_is_denied(text: str, code: str) -> None:
    proof = _evaluate(ActorClass.HUMAN_USER, check_burst_input(text))
    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == f"BURST_INPUT_INVALID:{code}"


@pytest.mark.parametrize("actor_class", [ActorClass.AI_PROCESSOR, ActorClass.SYSTEM_SERVICE])
def test_non_human_capture_is_denied_even_with_valid_input(actor_class: ActorClass) -> None:
    proof = _evaluate(actor_class, check_burst_input("Why did it drop?"))
    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "CAPTURE_REQUIRES_HUMAN_ACTOR"


@pytest.mark.parametrize("actor_class", [ActorClass.AI_PROCESSOR, ActorClass.SYSTEM_SERVICE])
def test_application_guard_agrees_on_the_capture_actor_rule(actor_class: ActorClass) -> None:
    result = evaluate_burst_contamination_guard(
        burst_state=BurstState.ACTIVE,
        operation=BurstOperationCategory.CAPTURE_BURST_QUESTION,
        actor_class=actor_class,
    )
    assert result.verdict is BurstContaminationVerdict.DENY
    assert result.reason is ContaminationDenyReason.CAPTURE_REQUIRES_HUMAN_ACTOR
