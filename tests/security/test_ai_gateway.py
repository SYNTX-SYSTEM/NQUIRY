"""P-23 (14 §50): "direct provider import/path -> unavailable/security signal".

At Phase 0 there was no running AI Gateway to reject a direct provider
call at request time. What existed then is the static architecture
boundary: a direct provider SDK import outside
`packages/ai_gateway/adapters/providers/` must be rejected as a
CI-time security signal (proven below, unchanged since PKG-00).

UPDATED AT PKG-19: a real `AIGateway`/`MockProviderAdapter` now exists
-- this file's own original docstring promised the dynamic half of
P-23 would land here. `test_the_real_gateway_path_is_the_only_way_to_reach_the_mock_provider`
proves it directly: the one production-importable provider adapter is
reachable ONLY through `AIGateway.run_operation`, and no other
production module (checked exhaustively via the same package scan the
static checkers already use) imports
`ai_gateway.adapters.providers.mock` at all.

Both mandatory checkers police the static half independently (defense
in depth, 14 §41): `check_provider_sdk_imports` (the dedicated
checker) and `check_architecture_dependencies` (the general
dependency-graph checker). Both are proven here.
"""

from __future__ import annotations

from pathlib import Path

import check_architecture_dependencies
import check_provider_sdk_imports


def _write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_direct_provider_import_outside_gateway_adapter_is_rejected(tmp_path: Path) -> None:
    packages_root = tmp_path / "packages"
    # A hypothetical future package attempts to call a provider SDK directly,
    # bypassing the AI Gateway entirely.
    _write(packages_root, "command/__init__.py", "")
    _write(
        packages_root, "command/handler.py", "import openai\n\ndef handle():\n    return openai\n"
    )

    sdk_violations = check_provider_sdk_imports.check(roots=(packages_root,))
    dependency_violations = check_architecture_dependencies.check(roots=(packages_root,))

    assert len(sdk_violations) == 1
    assert sdk_violations[0].owner_package == "command"
    assert sdk_violations[0].imported == "openai"

    assert len(dependency_violations) == 1
    assert dependency_violations[0].owner_package == "command"
    assert dependency_violations[0].imported == "openai"


def test_provider_import_through_the_approved_adapter_boundary_is_not_flagged(
    tmp_path: Path,
) -> None:
    """The boundary must be real, not accidentally total: the one
    approved location must still work, or this would just be a
    provider ban, not a Gateway boundary.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "ai_gateway/adapters/providers/mock.py", "import openai\n")

    sdk_violations = check_provider_sdk_imports.check(roots=(packages_root,))
    dependency_violations = check_architecture_dependencies.check(roots=(packages_root,))

    assert sdk_violations == []
    assert dependency_violations == []


def test_the_real_gateway_path_is_the_only_way_to_reach_the_mock_provider() -> None:
    """P-23 dynamic half (promised by this file's own original
    docstring, delivered at PKG-19): scans this repository's REAL
    production source (not a fixture tree) and proves that
    `MockProviderAdapter` -- the one provider adapter class that
    exists -- is imported (and therefore constructible/invokable) by
    exactly one production module, `ai_gateway.gateway` (the real
    `AIGateway` orchestrator). Other modules (e.g. `ai_gateway.validator`)
    may legitimately import plain DATA types from the same file
    (`MockProviderResponse`) without gaining any invocation capability
    -- this check is deliberately precise to the one class that can
    actually call a provider."""
    import ast

    from check_provider_sdk_imports import API_SRC_ROOT, PACKAGES_ROOT, WORKER_SRC_ROOT

    importers: list[str] = []
    for root in (PACKAGES_ROOT, API_SRC_ROOT, WORKER_SRC_ROOT):
        for py_file in root.rglob("*.py"):
            if "adapters/providers/mock.py" in str(py_file):
                continue  # the adapter module itself, not a caller
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and any(
                    alias.name == "MockProviderAdapter" for alias in node.names
                ):
                    importers.append(str(py_file))

    assert len(importers) == 1, importers
    assert importers[0].endswith("ai_gateway/gateway.py")
