"""T12 regression: `scripts/check_provider_sdk_imports.py` correctness.

Covers the PKG-00 mandatory attack "provider SDK import outside
packages/ai_gateway approved adapter boundary".
"""

from __future__ import annotations

from pathlib import Path

import pytest
from check_provider_sdk_imports import check


def _write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_real_repository_has_no_provider_sdk_violations() -> None:
    violations = check()
    assert violations == [], "\n".join(str(v) for v in violations)


@pytest.mark.parametrize("owner", ["command", "boundaries", "domain", "authority"])
def test_rejects_provider_sdk_import_from_any_other_package(tmp_path: Path, owner: str) -> None:
    packages_root = tmp_path / "packages"
    _write(packages_root, f"{owner}/__init__.py", "")
    _write(packages_root, f"{owner}/bad.py", "import anthropic\n")

    violations = check(roots=(packages_root,))

    assert len(violations) == 1
    assert violations[0].owner_package == owner
    assert violations[0].imported == "anthropic"


def test_allows_provider_sdk_import_inside_the_adapter_boundary(tmp_path: Path) -> None:
    packages_root = tmp_path / "packages"
    _write(packages_root, "ai_gateway/adapters/providers/mock.py", "import openai\n")

    violations = check(roots=(packages_root,))

    assert violations == []


def test_ignores_unrelated_imports(tmp_path: Path) -> None:
    packages_root = tmp_path / "packages"
    _write(packages_root, "domain/session.py", "import dataclasses\nimport semantic_types\n")

    violations = check(roots=(packages_root,))

    assert violations == []
