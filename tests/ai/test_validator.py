"""T6 AI TEST: `ai_gateway.validator` -- Response Validator ->
AI_VALIDATION_PROOF. Pure Python, no database required.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from ai_contracts.aiop import AIOperationId
from ai_contracts.generation import AIValidationProof, AIValidationResult
from ai_gateway.adapters.providers.mock import MockProviderResponse
from ai_gateway.validator import validate_response
from semantic_types.ids import GenerationId
from semantic_types.versions import ContractVersion

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)


def _validate(raw_content: str, ai_operation_id: AIOperationId = AIOperationId.AIOP_001):
    response = MockProviderResponse(
        raw_content=raw_content,
        model="mock-model-v1",
        provider="mock",
        input_tokens=1,
        output_tokens=1,
        latency_ms=1,
    )
    return validate_response(
        response=response,
        ai_generation_id=GenerationId(uuid.uuid4()),
        ai_operation_id=ai_operation_id,
        contract_version=ContractVersion("1.0"),
        validator_version=ContractVersion("1.0"),
        validated_at=_NOW,
    )


def test_well_formed_response_is_validated() -> None:
    proof = _validate('{"operation": "AIOP-001", "classification_proposals": ["pattern-1"]}')

    assert isinstance(proof, AIValidationProof)
    assert proof.validation_result is AIValidationResult.VALIDATED
    assert proof.validation_details_ref is None


def test_wrong_declared_operation_is_rejected() -> None:
    """Mandatory package-specific attack: invalid schema (wrong
    operation)."""
    proof = _validate(
        '{"operation": "AIOP-002", "classification_proposals": ["pattern-1"]}',
        ai_operation_id=AIOperationId.AIOP_001,
    )

    assert proof.validation_result is AIValidationResult.REJECTED
    assert proof.validation_details_ref is not None
    assert "AIOP-002" in proof.validation_details_ref


def test_missing_required_field_is_rejected() -> None:
    """Mandatory package-specific attack: invalid schema (missing
    field)."""
    proof = _validate('{"operation": "AIOP-001"}')

    assert proof.validation_result is AIValidationResult.REJECTED


def test_unparseable_response_is_indeterminate() -> None:
    """Mandatory package-specific attack: partial response. A truncated,
    unparseable response cannot be confirmed invalid OR valid."""
    proof = _validate('{"operation": "AIOP-001", "classif')

    assert proof.validation_result is AIValidationResult.INDETERMINATE
    assert proof.validation_details_ref is not None


def test_output_fingerprint_is_deterministic() -> None:
    content = '{"operation": "AIOP-001", "classification_proposals": ["pattern-1"]}'
    proof_a = _validate(content)
    proof_b = _validate(content)

    assert proof_a.output_fingerprint == proof_b.output_fingerprint
    assert len(proof_a.output_fingerprint) == 64


def test_validator_never_returns_anything_evidence_shaped() -> None:
    """Structural proof (14 section 48's own forbidden pattern for this
    file: "Evidence promotion"): `AIValidationProof`'s own field list
    has no `validation_state`/`type`/`content` field -- it cannot be
    mistaken for `evidence.models.Evidence`."""
    field_names = set(AIValidationProof.__dataclass_fields__)
    assert "validation_state" not in field_names
    assert "content" not in field_names
    assert "type" not in field_names
