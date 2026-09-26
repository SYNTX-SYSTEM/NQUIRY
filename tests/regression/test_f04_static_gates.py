"""F04 static and runtime gates (WU-04.6 mock lane; PI-3; PI-5).

MUST BECOME TRUE: the MockProvider is dev-runtime only and refused at startup
elsewhere (F1); only the mock adapter exists and it has no network egress (F4,
F6); only the F04 system module constructs the SYSTEM_SERVICE identity (PI-3)
or calls the Gateway; BEGIN_ANALYSIS and the F03 handlers import no AI.

MUST REMAIN IMPOSSIBLE: the mock in a production / staging / unknown
environment; a provider SDK or network library in the AI lane; a
SYSTEM_SERVICE actor fabricated by any other module; a worker calling a
provider.

FALSIFIERS: F1, F4, F6, PI-3, PI-5.
"""

from __future__ import annotations

import ast
import socket
from pathlib import Path

import pytest
from ai_contracts.aiop import AIOperationId
from ai_contracts.f04_operations import F04_CONTRACT_VERSION
from ai_gateway.adapters.providers.mock import MockProviderAdapter
from ai_gateway.prompt import DataBlock, build_invocation_prompt
from application.analysis_runtime import (
    MockProviderForbidden,
    UnknownAIProvider,
    runtime_from_environment,
)
from semantic_types.versions import PromptVersion

ROOT = Path(__file__).resolve().parents[2]
SOURCES = [
    *(ROOT / "packages").rglob("*.py"),
    *(ROOT / "apps").rglob("*.py"),
]


def _tree(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"))


def _imports(path: Path) -> set[str]:
    tree = _tree(path)
    found = {n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    found |= {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    return found


@pytest.mark.parametrize("environment", ["PRODUCTION", "STAGING", None, "prod"])
def test_f1_mock_refused_outside_the_dev_runtime(environment: str | None) -> None:
    env = {"NQUIRY_AI_PROVIDER": "mock"}
    if environment is not None:
        env["NQUIRY_ENVIRONMENT"] = environment
    with pytest.raises(MockProviderForbidden):
        runtime_from_environment(env)


@pytest.mark.parametrize("environment", ["DEVELOPMENT", "TEST"])
def test_f1_mock_allowed_in_the_dev_runtime(environment: str) -> None:
    runtime = runtime_from_environment(
        {"NQUIRY_AI_PROVIDER": "mock", "NQUIRY_ENVIRONMENT": environment}
    )
    assert runtime.available and runtime.provider == "mock"


def test_f1_no_provider_means_unavailable_never_a_substitute() -> None:
    runtime = runtime_from_environment({"NQUIRY_ENVIRONMENT": "PRODUCTION"})
    assert runtime.available is False and runtime.gateway is None
    with pytest.raises(UnknownAIProvider):
        runtime_from_environment(
            {"NQUIRY_AI_PROVIDER": "openai", "NQUIRY_ENVIRONMENT": "DEVELOPMENT"}
        )


def test_f1_api_startup_applies_the_check() -> None:
    main = (ROOT / "apps/api/src/nquiry_api/main.py").read_text()
    assert "configure_runtime(runtime_from_environment())" in main


def test_f4_only_the_mock_adapter_exists() -> None:
    providers = ROOT / "packages/ai_gateway/adapters/providers"
    assert sorted(p.name for p in providers.glob("*.py") if p.name != "__init__.py") == ["mock.py"]


_NETWORK = {
    "socket",
    "http",
    "urllib",
    "requests",
    "httpx",
    "aiohttp",
    "ssl",
    "openai",
    "anthropic",
}


def test_f6_the_ai_lane_imports_no_network_or_sdk() -> None:
    for path in (ROOT / "packages/ai_gateway").rglob("*.py"):
        roots = {m.split(".")[0] for m in _imports(path)}
        assert not roots & _NETWORK, (path, roots & _NETWORK)


def test_f6_mock_invoke_performs_no_egress(monkeypatch: pytest.MonkeyPatch) -> None:
    def _refuse(*_a: object, **_k: object) -> None:
        raise AssertionError("network egress attempted")

    monkeypatch.setattr(socket, "socket", _refuse)
    monkeypatch.setattr(socket, "create_connection", _refuse)
    prompt = build_invocation_prompt(
        ai_operation_id=AIOperationId.AIOP_001,
        ai_operation_contract_version=F04_CONTRACT_VERSION,
        prompt_version=PromptVersion("4.1"),
        mode_template_ref="POST_BURST_ANALYSIS",
        system_instructions="x",
        data_blocks=(DataBlock(source_ref="question:1", content="Why?"),),
    )
    assert MockProviderAdapter().invoke(prompt).provider == "mock"


def test_pi3_only_the_f04_system_module_constructs_the_service_actor() -> None:
    users = sorted(
        str(p.relative_to(ROOT))
        for p in SOURCES
        if "F04_ANALYSIS_SERVICE_ID" in p.read_text(encoding="utf-8")
    )
    assert users == [
        "packages/application/analysis_system.py",
        "packages/authority/system_service.py",
        "packages/boundaries/system_operation.py",
    ]
    constructors = []
    for path in SOURCES:
        for node in ast.walk(_tree(path)):
            if (
                isinstance(node, ast.Call)
                and getattr(node.func, "id", getattr(node.func, "attr", "")) == "ActorIdentity"
                and any(
                    isinstance(a, ast.Attribute) and a.attr == "SYSTEM_SERVICE"
                    for a in [*node.args, *(k.value for k in node.keywords)]
                )
            ):
                constructors.append(str(path.relative_to(ROOT)))
    assert constructors == ["packages/application/analysis_system.py"]


def test_no_worker_and_no_f03_handler_reaches_the_ai_lane() -> None:
    guarded = [
        *(ROOT / "apps/worker").rglob("*.py"),
        ROOT / "packages/application/burst_capture_handler.py",
        ROOT / "packages/application/burst_completion_handler.py",
        ROOT / "packages/application/analysis_begin_handler.py",
        ROOT / "packages/application/analysis_request_handler.py",
    ]
    for path in guarded:
        assert not any(m.startswith("ai_gateway") for m in _imports(path)), path
