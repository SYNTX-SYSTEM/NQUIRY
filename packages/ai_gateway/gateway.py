"""AIGateway: the exclusive path from an authorized invocation to a validated
CANDIDATE (08 §3 "All LLM traffic through Gateway"; 06 BND-009 / BND-010).

F04 WU-04.5 root repair of FBR-F04-1 / FBR-F04-2 / FBR-F04-7. The PKG-19
Gateway was a parallel canonical writer: it persisted the derived artifact
itself, before the generation was VALIDATED, gated only by a caller boolean.
Now:

- The Gateway ENDS AT A CANDIDATE: the provider response plus its
  AI_VALIDATION_PROOF. It writes nothing at all: no generation, no proof, no
  artifact. CANDIDATE ≠ EFFECT.
- Operational records (manifest, generation lifecycle, proof) are written by
  the F04 system handlers (`application.analysis_system`); the accepted
  artifact only by the acceptance Command through BND-010 → BND-014
  SYSTEM_OPERATION (09 §68), atomically with VALIDATED and the proof (PI-1).
- Invocation authority is not a parameter here. Only the F04 system handlers
  import this module (static gate), and they call it only after the
  SYSTEM_OPERATION EXECUTE commit that consumed the operation authorization
  (§0.1). The call happens outside any lock or transaction (PI-2).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from ai_contracts.aiop import AIOperationContract
from ai_contracts.generation import AIValidationProof
from semantic_types.ids import GenerationId

from ai_gateway.adapters.providers.mock import (
    MockProviderAdapter,
    MockProviderOutcome,
    MockProviderResponse,
    ProviderError,
    ProviderTimeout,
)
from ai_gateway.prompt import InvocationPrompt
from ai_gateway.validator import ValidationOutcome, validate_output


class InvocationFailure(Enum):
    PROVIDER_TIMEOUT = "PROVIDER_TIMEOUT"
    PROVIDER_ERROR = "PROVIDER_ERROR"


@dataclass(frozen=True, slots=True)
class GatewayCandidate:
    """What the Gateway hands back. Never an effect."""

    response: MockProviderResponse | None
    failure: InvocationFailure | None
    failure_detail: str | None
    validation: ValidationOutcome | None

    @property
    def proof(self) -> AIValidationProof | None:
        return None if self.validation is None else self.validation.proof


class AIGateway:
    def __init__(self, *, provider_adapter: MockProviderAdapter) -> None:
        self._provider = provider_adapter

    @property
    def provider(self) -> str:
        return self._provider.provider

    @property
    def model(self) -> str:
        return self._provider.model

    def invoke(
        self,
        *,
        contract: AIOperationContract,
        prompt: InvocationPrompt,
        allowed_question_refs: frozenset[str],
        ai_generation_id: GenerationId,
        validated_at: datetime,
        scripted_outcome: MockProviderOutcome = MockProviderOutcome.SUCCESS,
    ) -> GatewayCandidate:
        if prompt.ai_operation_id is not contract.ai_operation_id:
            raise ValueError("prompt and contract name different operations")
        try:
            response = self._provider.invoke(prompt, scripted_outcome=scripted_outcome)
        except ProviderTimeout as exc:
            return GatewayCandidate(None, InvocationFailure.PROVIDER_TIMEOUT, str(exc)[:200], None)
        except ProviderError as exc:
            return GatewayCandidate(None, InvocationFailure.PROVIDER_ERROR, str(exc)[:200], None)
        validation = validate_output(
            raw_content=response.raw_content,
            contract=contract,
            allowed_question_refs=allowed_question_refs,
            ai_generation_id=ai_generation_id,
            validated_at=validated_at,
        )
        return GatewayCandidate(response, None, None, validation)


def mock_gateway() -> AIGateway:
    """The dev-runtime Gateway over the MockProvider (HD-19). The only place the
    mock adapter is constructed (P-23); whether it may be used at all is decided
    by `application.analysis_runtime` (dev-only, refused elsewhere)."""
    return AIGateway(provider_adapter=MockProviderAdapter())


__all__ = ["AIGateway", "GatewayCandidate", "InvocationFailure", "mock_gateway"]
