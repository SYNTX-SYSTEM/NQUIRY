"""Differential test: `boundaries.bnd_008_question_burst` and
`application.burst_contamination` are two independently written
expressions of the same 06 §14 testable invariant (see
`packages/boundaries/bnd_008_question_burst.py`'s module docstring for
why they cannot import one another). This test exhaustively proves
they never disagree -- turning what would otherwise be a silent
duplication risk into a cross-checked invariant.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from application.burst_contamination import (
    BurstContaminationVerdict,
    evaluate_burst_contamination_guard,
)
from application.burst_contamination import BurstOperationCategory as AppOperationCategory
from authority.actor import ActorClass, ActorIdentity
from boundaries.bnd_008_question_burst import (
    Bnd008Input,
    Bnd008OperationCategory,
    Bnd008QuestionBurstEvaluator,
)
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from domain.burst import BurstState
from domain.burst_input import check_burst_input
from semantic_types.ids import CorrelationId, UserId, WorkspaceId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)

# Both enums are independently derived from the same 06 §14 categories
# and must have identical member names for this differential test to
# make sense pairing them up.
_CATEGORY_PAIRS = [(c.name, c) for c in Bnd008OperationCategory]


@pytest.mark.parametrize("actor_class", list(ActorClass))
@pytest.mark.parametrize("burst_state", list(BurstState))
@pytest.mark.parametrize("category_name,bnd_category", _CATEGORY_PAIRS)
def test_both_implementations_agree(
    actor_class: ActorClass,
    burst_state: BurstState,
    category_name: str,
    bnd_category: Bnd008OperationCategory,
) -> None:
    app_category = AppOperationCategory[category_name]

    context = BoundaryContext(
        workspace_id=WorkspaceId(uuid.uuid4()),
        operation="TEST_OPERATION",
        actor=ActorIdentity(actor_class, UserId(uuid.uuid4())),
        correlation_id=CorrelationId(uuid.uuid4()),
        evaluated_at=_NOW,
    )
    boundary_input = Bnd008Input(
        boundary_id=BoundaryId.BND_008,
        context=context,
        burst_state=burst_state,
        operation_category=bnd_category,
        # F03 WU-03.5: a capture also needs an established BURST_INPUT_VALID;
        # the differential compares the contamination facts, so it is supplied valid.
        input_check=(
            check_burst_input("Why did it drop?")
            if bnd_category is Bnd008OperationCategory.CAPTURE_BURST_QUESTION
            else None
        ),
    )
    boundary_proof = Bnd008QuestionBurstEvaluator().evaluate(boundary_input, context)

    app_result = evaluate_burst_contamination_guard(
        burst_state=burst_state, operation=app_category, actor_class=actor_class
    )

    boundary_allowed = boundary_proof.result is BoundaryResult.ALLOW
    app_allowed = app_result.verdict is BurstContaminationVerdict.ALLOW

    assert boundary_allowed == app_allowed, (
        f"disagreement for actor={actor_class}, state={burst_state}, "
        f"category={category_name}: boundary={boundary_proof.result}, "
        f"application={app_result.verdict}"
    )


def test_category_vocabularies_have_identical_member_names() -> None:
    """Both enums must name exactly the same categories -- if one gains
    a member the other lacks, this test fails loudly instead of the
    parametrization above silently skipping the new case.
    """
    assert {c.name for c in Bnd008OperationCategory} == {c.name for c in AppOperationCategory}
