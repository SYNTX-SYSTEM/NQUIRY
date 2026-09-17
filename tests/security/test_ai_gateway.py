"""P-23 (14 §50): "direct provider import/path -> unavailable/security signal".

At Phase 0 there is no running AI Gateway to reject a direct provider
call at request time — that lands with PKG-19. What *does* exist now
is the static architecture boundary: a direct provider SDK import
outside `packages/ai_gateway/adapters/providers/` must be rejected as
a CI-time security signal. This test exercises that boundary directly,
which is the legitimate partial proof of P-23 available at this build
phase (PKG-00 manifest: "PROOF_CLAIMS: P-18,P-23,P-24" — tracked as
"introduced" here, full end-to-end exercise deferred to Phase 10).

Both mandatory checkers police this boundary independently (defense in
depth, 14 §41): `check_provider_sdk_imports` (the dedicated checker)
and `check_architecture_dependencies` (the general dependency-graph
checker). Both are proven here.
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
