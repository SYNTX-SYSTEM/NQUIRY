"""The F04 AI runtime lane (WU-04.6; HD-19, HD-20; pre-implementation binding PI-5).

HD-19: MockProvider is enabled in the DEV runtime only. 19 §40: "Do not silently
substitute MockProvider". Settings (environment variables, read once at
startup):

- `NQUIRY_ENVIRONMENT`: the `security.events.Environment` vocabulary
  (DEVELOPMENT / TEST / STAGING / PRODUCTION).
- `NQUIRY_AI_PROVIDER`: `mock` enables the MockProvider; unset means no
  provider (analysis is honestly UNAVAILABLE; nothing is substituted).
- `NQUIRY_AI_MOCK_OUTCOME_AIOP_001` / `..._AIOP_002` (dev only): a scripted
  `MockProviderOutcome`, so the real stack can show failure and retry (H4).

FAIL-CLOSED: `NQUIRY_AI_PROVIDER=mock` outside DEVELOPMENT / TEST (including an
unset or unknown environment) raises `MockProviderForbidden` at startup (F1).
There is no real provider adapter: HARD-DEP-002 is external, and any other
provider value is refused rather than guessed.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field

from ai_contracts.aiop import AIOperationId
from ai_gateway.adapters.providers.mock import MockProviderOutcome
from ai_gateway.gateway import AIGateway, mock_gateway
from security.events import Environment

_DEV_ENVIRONMENTS = frozenset({Environment.DEVELOPMENT, Environment.TEST})


class MockProviderForbidden(RuntimeError):
    """The mock was requested outside the dev runtime (HD-19; 19 §40)."""


class UnknownAIProvider(RuntimeError):
    """A provider other than the mock was named; none exists (HARD-DEP-002)."""


@dataclass(frozen=True)
class AnalysisRuntime:
    gateway: AIGateway | None
    environment: Environment | None
    scripted: Mapping[AIOperationId, MockProviderOutcome] = field(default_factory=dict)

    @property
    def available(self) -> bool:
        return self.gateway is not None

    @property
    def provider(self) -> str | None:
        return None if self.gateway is None else self.gateway.provider

    def outcome_for(self, ai_operation_id: AIOperationId) -> MockProviderOutcome:
        return self.scripted.get(ai_operation_id, MockProviderOutcome.SUCCESS)


def mock_runtime(
    scripted: Mapping[AIOperationId, MockProviderOutcome] | None = None,
) -> AnalysisRuntime:
    """The dev/test runtime: MockProvider, optionally scripted."""
    return AnalysisRuntime(
        gateway=mock_gateway(),
        environment=Environment.TEST,
        scripted=dict(scripted or {}),
    )


UNAVAILABLE = AnalysisRuntime(gateway=None, environment=None)


def runtime_from_environment(env: Mapping[str, str] | None = None) -> AnalysisRuntime:
    source = os.environ if env is None else env
    raw_environment = source.get("NQUIRY_ENVIRONMENT")
    try:
        environment = None if raw_environment is None else Environment(raw_environment)
    except ValueError:
        environment = None
    provider = source.get("NQUIRY_AI_PROVIDER")
    if not provider:
        return AnalysisRuntime(gateway=None, environment=environment)
    if provider != "mock":
        raise UnknownAIProvider(
            f"NQUIRY_AI_PROVIDER={provider!r}: no such provider (only 'mock' exists; the real "
            "provider lane is HARD-DEP-002)"
        )
    if environment not in _DEV_ENVIRONMENTS:
        raise MockProviderForbidden(
            f"MockProvider is dev-runtime only (HD-19); refused for NQUIRY_ENVIRONMENT="
            f"{raw_environment!r}"
        )
    scripted: dict[AIOperationId, MockProviderOutcome] = {}
    for op in (AIOperationId.AIOP_001, AIOperationId.AIOP_002):
        value = source.get(f"NQUIRY_AI_MOCK_OUTCOME_{op.name}")
        if value:
            scripted[op] = MockProviderOutcome(value)
    return AnalysisRuntime(
        gateway=mock_gateway(),
        environment=environment,
        scripted=scripted,
    )


__all__ = [
    "AnalysisRuntime",
    "MockProviderForbidden",
    "UNAVAILABLE",
    "UnknownAIProvider",
    "mock_runtime",
    "runtime_from_environment",
]
