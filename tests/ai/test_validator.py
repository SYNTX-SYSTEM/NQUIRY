"""T6 AI TEST: `ai_gateway.validator` -- contract validation -> AI_VALIDATION_PROOF.
Pure Python, no database required.

F04 WU-04.4 (FBR-F04-8) supersedes the PKG-19 validator, which accepted one
hard-coded mock shape (`{"operation", "classification_proposals"}`) for any
contract. The PKG-19 intents are kept: a well-formed output validates, a wrong
operation and a missing field are rejected, the fingerprint is deterministic,
and the proof is never Evidence-shaped. One reading changes, per the reviewed
F04 architecture (§15 D4): an unparseable / partial output is REJECTED (the
output itself is invalid); INDETERMINATE is reserved for a failure of the
validator itself (08:731-740).
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import ai_gateway.validator as validator_module
import pytest
from ai_contracts.f04_operations import QUESTION_ANALYSIS, QUESTION_CLUSTERING
from ai_contracts.generation import AIValidationProof, AIValidationResult
from ai_gateway.validator import validate_output
from semantic_types.ids import GenerationId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_REFS = [f"question:{uuid.uuid4()}" for _ in range(3)]


def _analysis() -> dict[str, object]:
    return {
        "operation": "AIOP-001",
        "contract_version": "1.0",
        "classification_proposals": [{"question_ref": _REFS[0], "proposed_class": "c"}],
        "question_families": [],
        "unusual_question_flags": [],
        "pattern_descriptions": [],
        "contradiction_proposals": [],
    }


def _validate(raw: object, contract=QUESTION_ANALYSIS):  # type: ignore[no-untyped-def]
    return validate_output(
        raw_content=raw if isinstance(raw, str) else json.dumps(raw),
        contract=contract,
        allowed_question_refs=frozenset(_REFS),
        ai_generation_id=GenerationId(uuid.uuid4()),
        validated_at=_NOW,
    )


def test_well_formed_response_is_validated() -> None:
    outcome = _validate(_analysis())
    assert outcome.proof.validation_result is AIValidationResult.VALIDATED
    assert outcome.payload is not None


def test_wrong_declared_operation_is_rejected() -> None:
    assert _validate({**_analysis(), "operation": "AIOP-014"}).proof.validation_result is (
        AIValidationResult.REJECTED
    )


def test_missing_required_field_is_rejected() -> None:
    outcome = _validate({"operation": "AIOP-001", "contract_version": "1.0"})
    assert outcome.proof.validation_result is AIValidationResult.REJECTED
    assert outcome.payload is None


def test_unparseable_or_partial_response_is_rejected() -> None:
    proof = _validate(json.dumps(_analysis())[:30]).proof
    assert proof.validation_result is AIValidationResult.REJECTED
    assert proof.validation_details_ref == "UNPARSEABLE_OR_PARTIAL_OUTPUT"


def test_validator_failure_is_indeterminate(monkeypatch: pytest.MonkeyPatch) -> None:
    def _boom(*_a: object, **_k: object) -> None:
        raise RuntimeError("validator broke")

    monkeypatch.setattr(validator_module, "_check_analysis", _boom)
    proof = _validate(_analysis()).proof
    assert proof.validation_result is AIValidationResult.INDETERMINATE
    assert proof.validation_details_ref == "VALIDATOR_FAILURE:RuntimeError"


def test_clustering_schema_rejects_priority_and_double_membership() -> None:
    good = {
        "operation": "AIOP-002",
        "contract_version": "1.0",
        "clusters": [{"label": "a", "description": None, "question_refs": _REFS[:2]}],
    }
    assert (
        _validate(good, QUESTION_CLUSTERING).proof.validation_result is AIValidationResult.VALIDATED
    )
    priority = {**good, "clusters": [{**good["clusters"][0], "priority": 1}]}  # type: ignore[dict-item]
    twice = {**good, "clusters": [good["clusters"][0], good["clusters"][0]]}  # type: ignore[index]
    for attack in (priority, twice, {**good, "clusters": []}):
        assert _validate(attack, QUESTION_CLUSTERING).proof.validation_result is (
            AIValidationResult.REJECTED
        )


def test_output_fingerprint_is_deterministic() -> None:
    a, b = _validate(_analysis()).proof, _validate(_analysis()).proof
    assert a.output_fingerprint == b.output_fingerprint
    assert len(a.output_fingerprint) == 64


def test_validator_never_returns_anything_evidence_shaped() -> None:
    field_names = set(AIValidationProof.__dataclass_fields__)
    assert "validation_state" not in field_names
    assert "content" not in field_names
    assert "type" not in field_names
