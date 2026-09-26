"""MockProviderAdapter: the deterministic, dev-runtime-only provider (HD-19).

F04 WU-04.4/04.6 (FBR-F04-9):
- The output conforms to the registered closed schema of the invoked AIOP
  (AIOP-001, HD-18; AIOP-002, 09 §34/§35). Its question references are the
  prompt's data-block `source_ref`s, i.e. exactly the manifest's Questions.
- Its MEANING is input-independent: it never reads a data block's `content`
  (a Question's text), so what it "says" is not analysis of the real Questions.
  That is why every result is marked MOCK / NON_PROOF (`provider = "mock"`,
  proof class MOCK_NON_PROOF) and never counts toward BEGIN_REFLECTION for a
  non-fixture Session (HD-20).
- It has no network egress and no credential of any kind (R4; 11 AC-11-011 is
  not engaged). This module imports no network library (static gate F6).
- Scripted outcomes exist so failure, retry and recovery paths can be proven
  deterministically. They are selected by the caller (tests; the dev runtime
  setting `NQUIRY_AI_MOCK_OUTCOME`, refused in production).

MOCK RESULT ≠ REAL PROVIDER PROOF. The real-provider lane is HARD-DEP-002
(external); nothing here stands in for it.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Any

from ai_contracts.aiop import AIOperationId

from ai_gateway.prompt import InvocationPrompt

MOCK_PROVIDER = "mock"
MOCK_MODEL = "mock-model-v1"


class MockProviderOutcome(Enum):
    SUCCESS = "SUCCESS"
    TIMEOUT = "TIMEOUT"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    PARTIAL_RESPONSE = "PARTIAL_RESPONSE"
    NEW_QUESTION_FIELD = "NEW_QUESTION_FIELD"
    """Schema attack (HD-18 / D5): an additional-questions field."""
    FOREIGN_REF = "FOREIGN_REF"
    """Schema attack (D5 / K6): a question reference outside the manifest."""
    WRONG_OPERATION = "WRONG_OPERATION"


class ProviderTimeout(Exception):
    """Raised by `MockProviderAdapter.invoke` when scripted to time out."""


class ProviderError(Exception):
    """Raised by `MockProviderAdapter.invoke` when scripted to fail."""


@dataclass(frozen=True, slots=True)
class MockProviderResponse:
    raw_content: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    latency_ms: int


class MockProviderAdapter:
    """No credential field, no egress (14 PKG-19; R4)."""

    is_mock = True

    def __init__(self, *, model: str = MOCK_MODEL) -> None:
        self._model = model

    @property
    def model(self) -> str:
        return self._model

    @property
    def provider(self) -> str:
        return MOCK_PROVIDER

    def invoke(
        self,
        prompt: InvocationPrompt,
        *,
        scripted_outcome: MockProviderOutcome = MockProviderOutcome.SUCCESS,
    ) -> MockProviderResponse:
        op = prompt.ai_operation_id
        if scripted_outcome is MockProviderOutcome.TIMEOUT:
            raise ProviderTimeout(f"mock provider timed out for {op.value}")
        if scripted_outcome is MockProviderOutcome.PROVIDER_ERROR:
            raise ProviderError(f"mock provider error for {op.value}")

        refs = [b.source_ref for b in prompt.data_blocks if b.source_ref.startswith("question:")]
        payload = self._deterministic_payload(prompt, refs)
        if scripted_outcome is MockProviderOutcome.NEW_QUESTION_FIELD:
            payload["additional_questions"] = ["What else should we ask?"]
        elif scripted_outcome is MockProviderOutcome.FOREIGN_REF:
            foreign = "question:00000000-0000-4000-8000-00000000f0f0"
            if op is AIOperationId.AIOP_002:
                payload["clusters"][0]["question_refs"].append(foreign)
            else:
                payload["classification_proposals"].append(
                    {"question_ref": foreign, "proposed_class": "foreign"}
                )
        elif scripted_outcome is MockProviderOutcome.WRONG_OPERATION:
            payload["operation"] = "AIOP-014"
        content = json.dumps(payload, sort_keys=True)
        if scripted_outcome is MockProviderOutcome.PARTIAL_RESPONSE:
            content = content[: max(1, len(content) // 4)]

        return MockProviderResponse(
            raw_content=content,
            model=self._model,
            provider=MOCK_PROVIDER,
            input_tokens=len(prompt.data_blocks) * 10,
            output_tokens=len(content.split()),
            latency_ms=1,
        )

    def _deterministic_payload(self, prompt: InvocationPrompt, refs: list[str]) -> dict[str, Any]:
        # Derived from the OPERATION identity and the ORDER of the refs only;
        # never from any `DataBlock.content`.
        op = prompt.ai_operation_id
        tag = hashlib.sha256(f"{op.value}:{len(refs)}".encode()).hexdigest()[:8]
        version = str(prompt.ai_operation_contract_version)
        if op is AIOperationId.AIOP_002:
            half = max(1, (len(refs) + 1) // 2)
            groups = [g for g in (refs[:half], refs[half:]) if g]
            return {
                "operation": op.value,
                "contract_version": version,
                "clusters": [
                    {
                        "label": f"Mock cluster {i + 1}",
                        "description": (
                            f"Deterministic mock grouping {tag}-{i + 1} (MOCK / NON_PROOF)."
                        ),
                        "question_refs": group,
                    }
                    for i, group in enumerate(groups)
                ],
            }
        return {
            "operation": op.value,
            "contract_version": version,
            "classification_proposals": [
                {"question_ref": r, "proposed_class": f"mock-class-{i % 3 + 1}"}
                for i, r in enumerate(refs)
            ],
            "question_families": [
                {"label": f"Mock family {tag}", "question_refs": refs[:2] or refs}
            ]
            if refs
            else [],
            "unusual_question_flags": [
                {
                    "question_ref": refs[-1],
                    "reason": "Mock flag: position-based, not content-based.",
                }
            ]
            if refs
            else [],
            "pattern_descriptions": [
                {
                    "text": "Mock pattern description (MOCK / NON_PROOF; not an analysis).",
                    "supporting_question_refs": refs[:1],
                }
            ]
            if refs
            else [],
            "contradiction_proposals": [
                {"question_refs": refs[:2], "description": "Mock contradiction proposal."}
            ]
            if len(refs) >= 2
            else [],
        }


__all__ = [
    "MOCK_MODEL",
    "MOCK_PROVIDER",
    "MockProviderAdapter",
    "MockProviderOutcome",
    "MockProviderResponse",
    "ProviderError",
    "ProviderTimeout",
]
