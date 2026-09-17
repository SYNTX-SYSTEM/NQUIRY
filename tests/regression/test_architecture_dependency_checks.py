"""T12 regression: `scripts/check_architecture_dependencies.py` correctness.

Covers 14 §41 (DEPENDENCY ENFORCEMENT) and the PKG-00 mandatory attack
"controlled forbidden import fixture" (PKG-00 COPY-PASTE prompt,
PRE_IMPLEMENTATION_ATTACK_MODEL). Fixtures are built in `tmp_path`, not
committed as real violations in production code — the fixture *is* the
proof, not a note that one should exist.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from check_architecture_dependencies import check


def _write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_real_repository_has_no_dependency_violations() -> None:
    """Regression run: the actual current repository must stay clean."""
    violations = check()
    assert violations == [], "\n".join(str(v) for v in violations)


def test_detects_import_not_on_the_allow_list(tmp_path: Path) -> None:
    """`authority` may depend on {governance, domain, semantic_types}
    (14 §3.1) but must never treat a projection as an authoritative
    source (14 §3.1 forbidden: "projection as authoritative source").
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "authority/__init__.py", "")
    _write(packages_root, "authority/resolver.py", "import projection\n")
    _write(packages_root, "projection/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert len(violations) == 1
    assert violations[0].owner_package == "authority"
    assert violations[0].imported == "projection"


def test_detects_forbidden_external_framework_dependency(tmp_path: Path) -> None:
    """14 §4 forbidden-dependency matrix: `domain` must never import FastAPI."""
    packages_root = tmp_path / "packages"
    _write(packages_root, "domain/__init__.py", "")
    _write(packages_root, "domain/session.py", "import fastapi\n")

    violations = check(roots=(packages_root,))

    assert len(violations) == 1
    assert violations[0].owner_package == "domain"
    assert violations[0].imported == "fastapi"


def test_allows_a_legitimate_dependency(tmp_path: Path) -> None:
    """Negative control: the checker must not flag a dependency that IS
    on the 14 §3.1 allow list — otherwise it would be useless noise,
    not a proof.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "domain/__init__.py", "")
    _write(packages_root, "domain/session.py", "import semantic_types\n")
    _write(packages_root, "semantic_types/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert violations == []


def test_allows_application_to_depend_on_persistence_for_reads(tmp_path: Path) -> None:
    """PKG-01: `application` may depend on `persistence` for read-only
    `CanonicalReadPort` use (14 §11) -- e.g.
    `application.workspace_context` calling
    `persistence.workspace_repository.WorkspaceRepository.get`. This is
    a deliberate, disclosed extension of the 14 §3.1 checkable subset
    (see `check_architecture_dependencies.INTERNAL_ALLOWED["application"]`
    for the citation), not a forbidden-dependency violation.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "application/__init__.py", "")
    _write(packages_root, "application/workspace_context.py", "import persistence\n")
    _write(packages_root, "persistence/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert violations == []


def test_allows_persistence_to_depend_on_governance_for_typed_records(tmp_path: Path) -> None:
    """PKG-02: `persistence` may depend on `governance` (type-only use:
    `WorkspaceRole`, `MembershipStatus`, `AuthorityClass`,
    `AuthorityBindingState`) -- see
    `check_architecture_dependencies.INTERNAL_ALLOWED["persistence"]`
    for the citation. Not a forbidden-dependency violation.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "persistence/__init__.py", "")
    _write(packages_root, "persistence/membership_repository.py", "import governance\n")
    _write(packages_root, "governance/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert violations == []


def test_governance_still_cannot_depend_on_persistence(tmp_path: Path) -> None:
    """Negative control for the extension above: the new
    `persistence -> governance` edge must not have quietly become
    bidirectional. `governance` owns "governance state" (14 §3.1) and
    must not reach back into the storage adapter that implements it --
    that would be a real circular dependency, not a read-only type use.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "governance/__init__.py", "")
    _write(packages_root, "governance/oops.py", "import persistence\n")
    _write(packages_root, "persistence/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert len(violations) == 1
    assert violations[0].owner_package == "governance"
    assert violations[0].imported == "persistence"


def test_allows_authority_to_depend_on_persistence_for_reads(tmp_path: Path) -> None:
    """PKG-03: `authority` may depend on `persistence` so
    `AuthorityResolver` can be constructed against
    `MembershipRepository`/`AuthorityBindingRepository` -- see
    `check_architecture_dependencies.INTERNAL_ALLOWED["authority"]` for
    the citation. Not a forbidden-dependency violation.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "authority/__init__.py", "")
    _write(packages_root, "authority/resolver.py", "import persistence\n")
    _write(packages_root, "persistence/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert violations == []


def test_persistence_still_cannot_depend_on_authority(tmp_path: Path) -> None:
    """Negative control for the extension above: `persistence -> authority`
    must remain forbidden. `persistence` implements storage adapters
    (14 §3.1) and must not reach up into the resolution layer built on
    top of it -- that would be a real circular dependency.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "persistence/__init__.py", "")
    _write(packages_root, "persistence/oops.py", "import authority\n")
    _write(packages_root, "authority/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert len(violations) == 1
    assert violations[0].owner_package == "persistence"
    assert violations[0].imported == "authority"


def test_application_still_cannot_depend_on_commit(tmp_path: Path) -> None:
    """Negative control for the extension above: allowing `application ->
    persistence` for reads must not have quietly opened `application ->
    commit` (the exclusive governed writer, 14 §3.1). Writes stay
    `commit`-only; `application` reaching `commit` directly would be
    exactly the "no direct write" collapse 14 §3.1 forbids for this
    layer.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "application/__init__.py", "")
    _write(packages_root, "application/oops.py", "import commit\n")
    _write(packages_root, "commit/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert len(violations) == 1
    assert violations[0].owner_package == "application"
    assert violations[0].imported == "commit"


def test_allows_persistence_to_depend_on_domain_for_row_mapping(tmp_path: Path) -> None:
    """PKG-05: `persistence` may depend on `domain` so
    `challenge_session_mapping` can map an already-fetched row into
    the frozen `Challenge`/`Session` canonical types -- see
    `check_architecture_dependencies.INTERNAL_ALLOWED["persistence"]`
    for the citation. Not a forbidden-dependency violation.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "persistence/__init__.py", "")
    _write(packages_root, "persistence/challenge_session_mapping.py", "import domain\n")
    _write(packages_root, "domain/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert violations == []


def test_domain_still_cannot_depend_on_persistence(tmp_path: Path) -> None:
    """Negative control for the extension above: the new
    `persistence -> domain` edge must not have quietly become
    bidirectional. `domain`'s only permitted dependency remains
    `semantic_types` (14 §3.1) -- it must never reach into the storage
    adapter built on top of it.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "domain/__init__.py", "")
    _write(packages_root, "domain/oops.py", "import persistence\n")
    _write(packages_root, "persistence/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert len(violations) == 1
    assert violations[0].owner_package == "domain"
    assert violations[0].imported == "persistence"


def test_allows_provider_sdk_only_inside_the_adapter_boundary(tmp_path: Path) -> None:
    packages_root = tmp_path / "packages"
    _write(packages_root, "ai_gateway/__init__.py", "")
    _write(packages_root, "ai_gateway/adapters/__init__.py", "")
    _write(packages_root, "ai_gateway/adapters/providers/__init__.py", "")
    _write(packages_root, "ai_gateway/adapters/providers/mock.py", "import openai\n")

    violations = check(roots=(packages_root,))

    assert violations == []


@pytest.mark.parametrize("relative_path", ["ai_gateway/context.py", "ai_gateway/prompt.py"])
def test_rejects_provider_sdk_outside_the_adapter_boundary(
    tmp_path: Path, relative_path: str
) -> None:
    packages_root = tmp_path / "packages"
    _write(packages_root, "ai_gateway/__init__.py", "")
    _write(packages_root, relative_path, "import openai\n")

    violations = check(roots=(packages_root,))

    assert len(violations) == 1
    assert violations[0].imported == "openai"
