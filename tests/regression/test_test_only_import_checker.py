"""T12 regression: `scripts/check_test_only_imports.py` correctness.

Covers the PKG-00 mandatory attack "production import of
packages/test_support" (14 §41, §45).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from check_test_only_imports import check


def _write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_real_repository_has_no_test_only_import_violations() -> None:
    violations = check()
    assert violations == [], "\n".join(str(v) for v in violations)


@pytest.mark.parametrize("owner", ["command", "boundaries", "domain", "nquiry_api"])
def test_rejects_production_import_of_test_support(tmp_path: Path, owner: str) -> None:
    packages_root = tmp_path / "packages"
    _write(packages_root, f"{owner}/__init__.py", "")
    _write(packages_root, f"{owner}/bad.py", "from test_support.clock import FixedClock\n")

    violations = check(roots=(packages_root,))

    assert len(violations) == 1
    assert violations[0].owner_package == owner
    assert violations[0].imported == "test_support"


def test_test_support_importing_its_own_sibling_module_is_not_a_violation(tmp_path: Path) -> None:
    packages_root = tmp_path / "packages"
    _write(packages_root, "test_support/__init__.py", "")
    _write(packages_root, "test_support/clock.py", "import semantic_types\n")

    violations = check(roots=(packages_root,))

    assert violations == []
