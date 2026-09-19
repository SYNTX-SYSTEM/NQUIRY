"""MockProviderAdapter: the one and only production-eligible provider
adapter at this build phase.

Source: 12_MINIMUM_PROTOTYPE_ARCHITECTURE.md section 12.3 (Provider
rule -- AC-12-008: "One eligible provider is sufficient; gateway
exclusivity and provider independence remain."); 08_AI_ARCHITECTURE_AND_CONTRACTS.md
section 17 (Model and Provider Boundary -- 17.1 Provider Independence,
17.2 Provider Substitution); 14_IMPLEMENTATION_SEQUENCE.md section 41
("provider SDK import only under provider adapter",
`packages/ai_gateway/adapters/providers/`), section 48's own file-level
map row ("deterministic mock | 12,13 | provider port | canonical
writer [forbidden]").

WHY THIS FILE IMPORTS NO PROVIDER SDK AT ALL
--------------------------------------------------------------------
This file is the one APPROVED location a real provider SDK import
could legitimately live (14 section 41; enforced by
`scripts/check_provider_sdk_imports.py`'s own allowlist). It does not
contain one: HARD-DEP-002 (real provider eligibility) remains BLOCKED
(16_DECISION_GAP_REGISTER.md) -- "Real provider execution disabled and
policy-gated beyond an environment variable" (14 PKG-19's own
OBJECTIVE). A real adapter (e.g. `openai.py`/`anthropic.py`) is
therefore `SUCCESSOR_NOT_BUILT`, not merely disabled by a flag with no
adapter behind it -- there is nothing here that COULD reach a real
model even if a flag were flipped, because no such adapter file
exists yet.

WHY `MockProviderAdapter.invoke` NEVER READS `DataBlock.content`
--------------------------------------------------------------------
Mandatory adversarial attack: prompt injection. The mock's own
deterministic output is a pure function of
`(ai_operation_id, scripted_outcome)` -- never of the prompt's own
`data_blocks` text. This is not merely "the mock happens not to be
influenced" -- it is the strongest available proof that DATA content
cannot drive AI output shape at this build phase, since the one
component that produces "model output" in this codebase provably never
parses that content at all.

WHY FAILURE SCENARIOS ARE A CONSTRUCTOR-INJECTED, PRODUCTION-IMPORTABLE
ENUM -- NOT A `test_support` DOUBLE
--------------------------------------------------------------------
Unlike `commit.coordinator.FailureInjectionPort` (a hook production
code never triggers itself), THIS adapter IS the production default
provider (12 section 12.1: "MockProvider default") -- a real caller
(a future package's own Command handler) legitimately needs to select
a scenario for its own adversarial/failure-path tests using the exact
same public constructor every production code path uses, the identical
precedent already established for `boundaries.bnd_014_commit`'s own
"no separate double, the real evaluator IS deterministic" shape.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import Enum

from ai_contracts.aiop import AIOperationId

from ai_gateway.prompt import InvocationPrompt


class MockProviderOutcome(Enum):
    """Deterministic scenarios this adapter can be told to produce.
    Mandatory package-specific attacks: timeout, provider error,
    partial response."""

    SUCCESS = "SUCCESS"
    TIMEOUT = "TIMEOUT"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    PARTIAL_RESPONSE = "PARTIAL_RESPONSE"


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
    """The default, always-eligible provider (AC-12-008). Carries no
    credential field of any kind -- "Provider credentials only Gateway"
    (14 PKG-19 OBJECTIVE) is trivially true here since a mock has
    nothing to authenticate."""

    def __init__(self, *, model: str = "mock-model-v1") -> None:
        self._model = model

    @property
    def model(self) -> str:
        return self._model

    @property
    def provider(self) -> str:
        return "mock"

    def invoke(
        self,
        prompt: InvocationPrompt,
        *,
        scripted_outcome: MockProviderOutcome = MockProviderOutcome.SUCCESS,
    ) -> MockProviderResponse:
        if scripted_outcome is MockProviderOutcome.TIMEOUT:
            raise ProviderTimeout(f"mock provider timed out for {prompt.ai_operation_id.value}")
        if scripted_outcome is MockProviderOutcome.PROVIDER_ERROR:
            raise ProviderError(f"mock provider error for {prompt.ai_operation_id.value}")

        content = self._deterministic_content(prompt.ai_operation_id)
        if scripted_outcome is MockProviderOutcome.PARTIAL_RESPONSE:
            content = content[: max(1, len(content) // 4)]

        return MockProviderResponse(
            raw_content=content,
            model=self._model,
            provider="mock",
            input_tokens=len(prompt.data_blocks) * 10,
            output_tokens=len(content.split()),
            latency_ms=1,
        )

    def _deterministic_content(self, ai_operation_id: AIOperationId) -> str:
        # Deliberately derived from the OPERATION identity only, never
        # from any `DataBlock.content` -- see module docstring.
        digest = hashlib.sha256(ai_operation_id.value.encode("utf-8")).hexdigest()[:12]
        return (
            f'{{"operation": "{ai_operation_id.value}", '
            f'"analysis_id": "{digest}", '
            f'"classification_proposals": ["pattern-{digest}"]}}'
        )


__all__ = [
    "MockProviderOutcome",
    "ProviderTimeout",
    "ProviderError",
    "MockProviderResponse",
    "MockProviderAdapter",
]
