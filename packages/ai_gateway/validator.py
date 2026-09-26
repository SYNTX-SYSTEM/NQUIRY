"""AI_VALIDATION_PROOF: deterministic contract validation (08 §7; 09 §56).

F04 WU-04.4 (FBR-F04-8): validation is against the REGISTERED contract's closed
schema (`ai_contracts.f04_operations`), and every question reference must be in
the context manifest. The former validator accepted one hard-coded mock shape.

Results (09 §56):
- VALIDATED: the output is exactly the closed schema, every ref is in the
  manifest.
- REJECTED: anything else the output itself causes: unparseable or partial
  output, the wrong operation or contract version, a missing or extra key at any
  level (including any new-question field, HD-18), an out-of-manifest ref, a
  limit violation.
- INDETERMINATE: the validator itself could not reach a verdict (an internal
  failure, 08:731-740). The caller records the generation FAILED.

The proof proves only contract validation. It is never DOMAIN_EVIDENCE, and a
VALIDATED proof is a candidate, not an effect (acceptance is 09 §68).
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from ai_contracts.aiop import AIOperationContract, AIOperationId
from ai_contracts.f04_operations import (
    AIOP_001_SECTIONS,
    AIOP_001_TOP_LEVEL,
    AIOP_002_CLUSTER,
    AIOP_002_TOP_LEVEL,
    MAX_ITEMS,
    MAX_LABEL,
    MAX_TEXT,
)
from ai_contracts.generation import AIValidationProof, AIValidationResult
from semantic_types.ids import GenerationId
from semantic_types.versions import ContractVersion

VALIDATOR_VERSION = ContractVersion("4.1")
"""F04 contract validator, version 4.1 (dotted integers are the version form)."""


class _Reject(Exception):
    pass


@dataclass(frozen=True, slots=True)
class ValidationOutcome:
    proof: AIValidationProof
    payload: dict[str, Any] | None
    """The parsed output, only when VALIDATED."""


def output_fingerprint(raw_content: str) -> str:
    return hashlib.sha256(raw_content.encode("utf-8")).hexdigest()


def validate_output(
    *,
    raw_content: str,
    contract: AIOperationContract,
    allowed_question_refs: frozenset[str],
    ai_generation_id: GenerationId,
    validated_at: datetime,
    validator_version: ContractVersion = VALIDATOR_VERSION,
) -> ValidationOutcome:
    def proof(result: AIValidationResult, details: str | None) -> AIValidationProof:
        return AIValidationProof(
            ai_validation_proof_id=uuid.uuid4(),
            ai_generation_id=ai_generation_id,
            ai_operation_id=contract.ai_operation_id,
            contract_version=contract.contract_version,
            validator_version=validator_version,
            validation_result=result,
            validated_at=validated_at,
            output_fingerprint=output_fingerprint(raw_content),
            validation_details_ref=details,
        )

    try:
        payload = _parse(raw_content)
        _check_header(payload, contract)
        if contract.ai_operation_id is AIOperationId.AIOP_001:
            _check_analysis(payload, allowed_question_refs)
        elif contract.ai_operation_id is AIOperationId.AIOP_002:
            _check_clustering(payload, allowed_question_refs)
        else:
            raise _Reject(f"NO_SCHEMA_FOR:{contract.ai_operation_id.value}")
    except _Reject as reject:
        return ValidationOutcome(proof(AIValidationResult.REJECTED, str(reject)[:500]), None)
    except Exception as exc:  # noqa: BLE001 -- validator infrastructure failure
        return ValidationOutcome(
            proof(AIValidationResult.INDETERMINATE, f"VALIDATOR_FAILURE:{type(exc).__name__}"),
            None,
        )
    return ValidationOutcome(proof(AIValidationResult.VALIDATED, None), payload)


def _parse(raw_content: str) -> dict[str, Any]:
    try:
        payload = json.loads(raw_content)
    except (json.JSONDecodeError, TypeError) as exc:
        raise _Reject("UNPARSEABLE_OR_PARTIAL_OUTPUT") from exc
    if not isinstance(payload, dict):
        raise _Reject("OUTPUT_NOT_AN_OBJECT")
    return payload


def _check_header(payload: dict[str, Any], contract: AIOperationContract) -> None:
    if payload.get("operation") != contract.ai_operation_id.value:
        raise _Reject(f"WRONG_OPERATION:{payload.get('operation')!r}")
    if payload.get("contract_version") != str(contract.contract_version):
        raise _Reject(f"WRONG_CONTRACT_VERSION:{payload.get('contract_version')!r}")


def _exact_keys(obj: object, expected: frozenset[str] | set[str], where: str) -> dict[str, Any]:
    if not isinstance(obj, dict):
        raise _Reject(f"NOT_AN_OBJECT:{where}")
    keys = set(obj)
    extra, missing = keys - set(expected), set(expected) - keys
    if extra:
        # HD-18: an additional-question (or any other) field is outside the contract.
        raise _Reject(f"UNKNOWN_FIELD:{where}.{sorted(extra)[0]}")
    if missing:
        raise _Reject(f"MISSING_FIELD:{where}.{sorted(missing)[0]}")
    return obj


def _list(value: object, where: str) -> list[Any]:
    if not isinstance(value, list):
        raise _Reject(f"NOT_A_LIST:{where}")
    if len(value) > MAX_ITEMS:
        raise _Reject(f"TOO_MANY_ITEMS:{where}")
    return value


def _string(value: object, limit: int, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise _Reject(f"EMPTY_OR_NOT_TEXT:{where}")
    if len(value) > limit:
        raise _Reject(f"TOO_LONG:{where}")
    return value


def _ref(value: object, allowed: frozenset[str], where: str) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise _Reject(f"QUESTION_REF_NOT_IN_MANIFEST:{where}")
    return value


def _refs(value: object, allowed: frozenset[str], where: str, minimum: int) -> list[str]:
    items = [_ref(v, allowed, f"{where}[{i}]") for i, v in enumerate(_list(value, where))]
    if len(items) < minimum:
        raise _Reject(f"TOO_FEW_REFS:{where}")
    if len(set(items)) != len(items):
        raise _Reject(f"DUPLICATE_REF:{where}")
    return items


def _check_field(kind: str, value: object, allowed: frozenset[str], where: str) -> None:
    if kind == "ref":
        _ref(value, allowed, where)
    elif kind == "refs":
        _refs(value, allowed, where, 1)
    elif kind == "refs2":
        _refs(value, allowed, where, 2)
    elif kind == "label":
        _string(value, MAX_LABEL, where)
    elif kind == "text":
        _string(value, MAX_TEXT, where)
    elif kind == "optional_label":
        if value is not None:
            _string(value, MAX_LABEL, where)
    elif kind == "optional_text":
        if value is not None:
            _string(value, MAX_TEXT, where)
    else:  # pragma: no cover -- schema constants are closed
        raise ValueError(kind)


def _check_analysis(payload: dict[str, Any], allowed: frozenset[str]) -> None:
    _exact_keys(payload, AIOP_001_TOP_LEVEL, "$")
    for section, fields in AIOP_001_SECTIONS.items():
        for i, item in enumerate(_list(payload[section], section)):
            where = f"{section}[{i}]"
            obj = _exact_keys(item, set(fields), where)
            for name, kind in fields.items():
                _check_field(kind, obj[name], allowed, f"{where}.{name}")


def _check_clustering(payload: dict[str, Any], allowed: frozenset[str]) -> None:
    _exact_keys(payload, AIOP_002_TOP_LEVEL, "$")
    clusters = _list(payload["clusters"], "clusters")
    if not clusters:
        raise _Reject("NO_CLUSTERS")
    seen: set[str] = set()
    for i, item in enumerate(clusters):
        where = f"clusters[{i}]"
        obj = _exact_keys(item, set(AIOP_002_CLUSTER), where)
        for name, kind in AIOP_002_CLUSTER.items():
            _check_field(kind, obj[name], allowed, f"{where}.{name}")
        refs = set(obj["question_refs"])
        if refs & seen:
            raise _Reject(f"QUESTION_IN_TWO_CLUSTERS:{where}")
        seen |= refs


__all__ = ["VALIDATOR_VERSION", "ValidationOutcome", "output_fingerprint", "validate_output"]
