"""Response Validator: turns raw provider output into AI_VALIDATION_PROOF.

Source: 08_AI_ARCHITECTURE_AND_CONTRACTS.md section 19 (Response
Validation), section 19.1 (Validator Does Not Determine Truth --
"[VALIDATED] proves only contract validation. It is never
DOMAIN_EVIDENCE."), section 23 (AIOP-001 OUTPUT CONTRACT -- "Structured
derived analysis such as: classification proposals, ..."), section 14.4
(VALIDATED "does not mean domain truth or authority");
09_DATA_EVENT_API_CONTRACTS.md section 56 (DATA CONTRACT:
AI_VALIDATION_PROOF -- exact field list, 3-value validation_result).

WHY VALIDATION IS SCHEMA/CONTRACT SHAPE ONLY, NEVER CONTENT TRUTH
--------------------------------------------------------------------
14 section 48's own file-level map row for this file names "Evidence
promotion" as the one forbidden pattern: this module has no method
that returns anything resembling `evidence.models.Evidence`, and
`AIValidationProof` itself (09 section 56) carries no
`validation_state`/`type`/`content` field of the kind Evidence has --
it is structurally a different class of record. "Validated" here means
exactly what 08 section 19.1 says it means: the response parses as the
declared operation's own expected shape, nothing more.

WHY A PARSE FAILURE IS `INDETERMINATE`, NOT `REJECTED`
--------------------------------------------------------------------
09 section 56's own 3-value vocabulary distinguishes a confirmed
mismatch (REJECTED -- the response parsed fine but named the wrong
operation, or is missing a required field) from a response this
validator genuinely cannot classify either way (INDETERMINATE -- e.g.
`MockProviderOutcome.PARTIAL_RESPONSE`'s own truncated, unparseable
text). Collapsing the two would erase a real distinction 09 already
draws.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime

from ai_contracts.aiop import AIOperationId
from ai_contracts.generation import AIValidationProof, AIValidationResult
from semantic_types.ids import GenerationId
from semantic_types.versions import ContractVersion

from ai_gateway.adapters.providers.mock import MockProviderResponse


def validate_response(
    *,
    response: MockProviderResponse,
    ai_generation_id: GenerationId,
    ai_operation_id: AIOperationId,
    contract_version: ContractVersion,
    validator_version: ContractVersion,
    validated_at: datetime,
) -> AIValidationProof:
    output_fingerprint = hashlib.sha256(response.raw_content.encode("utf-8")).hexdigest()

    try:
        payload = json.loads(response.raw_content)
    except json.JSONDecodeError:
        return _proof(
            AIValidationResult.INDETERMINATE,
            "response could not be parsed as the expected structured shape",
            ai_generation_id=ai_generation_id,
            ai_operation_id=ai_operation_id,
            contract_version=contract_version,
            validator_version=validator_version,
            validated_at=validated_at,
            output_fingerprint=output_fingerprint,
        )

    declared_operation = payload.get("operation") if isinstance(payload, dict) else None
    if declared_operation != ai_operation_id.value:
        return _proof(
            AIValidationResult.REJECTED,
            f"response declared operation {declared_operation!r}, expected "
            f"{ai_operation_id.value!r}",
            ai_generation_id=ai_generation_id,
            ai_operation_id=ai_operation_id,
            contract_version=contract_version,
            validator_version=validator_version,
            validated_at=validated_at,
            output_fingerprint=output_fingerprint,
        )

    if not payload.get("classification_proposals"):
        return _proof(
            AIValidationResult.REJECTED,
            "response missing required classification_proposals (08 section 23 OUTPUT CONTRACT)",
            ai_generation_id=ai_generation_id,
            ai_operation_id=ai_operation_id,
            contract_version=contract_version,
            validator_version=validator_version,
            validated_at=validated_at,
            output_fingerprint=output_fingerprint,
        )

    return _proof(
        AIValidationResult.VALIDATED,
        None,
        ai_generation_id=ai_generation_id,
        ai_operation_id=ai_operation_id,
        contract_version=contract_version,
        validator_version=validator_version,
        validated_at=validated_at,
        output_fingerprint=output_fingerprint,
    )


def _proof(
    result: AIValidationResult,
    details: str | None,
    *,
    ai_generation_id: GenerationId,
    ai_operation_id: AIOperationId,
    contract_version: ContractVersion,
    validator_version: ContractVersion,
    validated_at: datetime,
    output_fingerprint: str,
) -> AIValidationProof:
    return AIValidationProof(
        ai_validation_proof_id=uuid.uuid4(),
        ai_generation_id=ai_generation_id,
        ai_operation_id=ai_operation_id,
        contract_version=contract_version,
        validator_version=validator_version,
        validation_result=result,
        validated_at=validated_at,
        output_fingerprint=output_fingerprint,
        validation_details_ref=details,
    )


__all__ = ["validate_response"]
