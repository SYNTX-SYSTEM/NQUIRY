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


def test_allows_boundaries_to_depend_on_persistence_for_reads(tmp_path: Path) -> None:
    """PKG-09: `boundaries` may depend on `persistence` so BND-002/003/004
    evaluators can read live WorkspaceRecord/MembershipRecord/
    RoleAssignmentRecord state through the PKG-01/02 read-only Protocol
    repositories -- see
    `check_architecture_dependencies.INTERNAL_ALLOWED["boundaries"]` for
    the citation. Not a forbidden-dependency violation.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "boundaries/__init__.py", "")
    _write(packages_root, "boundaries/bnd_002_workspace.py", "import persistence\n")
    _write(packages_root, "persistence/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert violations == []


def test_persistence_still_cannot_depend_on_boundaries(tmp_path: Path) -> None:
    """Negative control for the extension above: `persistence ->
    boundaries` must remain forbidden. `persistence` implements storage
    adapters (14 §3.1) and must not reach up into the boundary
    evaluation layer built on top of it.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "persistence/__init__.py", "")
    _write(packages_root, "persistence/oops.py", "import boundaries\n")
    _write(packages_root, "boundaries/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert len(violations) == 1
    assert violations[0].owner_package == "persistence"
    assert violations[0].imported == "boundaries"


def test_allows_commit_to_depend_on_authority_for_actor_identity(tmp_path: Path) -> None:
    """PKG-13: `commit` may depend on `authority` so `coordinator.py`
    can construct a real `authority.actor.ActorIdentity` for
    `boundaries.types.BoundaryContext.actor` when invoking BND-014 --
    see `check_architecture_dependencies.INTERNAL_ALLOWED["commit"]`
    for the citation. Type-only use: `commit` never constructs an
    `AuthorityResolver` itself. Not a forbidden-dependency violation.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "commit/__init__.py", "")
    _write(packages_root, "commit/coordinator.py", "import authority\n")
    _write(packages_root, "authority/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert violations == []


def test_authority_still_cannot_depend_on_commit(tmp_path: Path) -> None:
    """Negative control for the extension above: the new
    `commit -> authority` edge must not have quietly become
    bidirectional. `authority`'s permitted dependencies remain
    `governance`, `domain`, `semantic_types`, `persistence` (14 §3.1)
    -- it must never reach into the write-coordination layer built on
    top of it.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "authority/__init__.py", "")
    _write(packages_root, "authority/oops.py", "import commit\n")
    _write(packages_root, "commit/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert len(violations) == 1
    assert violations[0].owner_package == "authority"
    assert violations[0].imported == "commit"


def test_allows_commit_to_depend_on_governance_for_authority_class(tmp_path: Path) -> None:
    """PKG-13: `commit` may depend on `governance` so
    `coordinator.py`'s own `commit()` method can type its
    `required_authority_class` parameter as the real
    `governance.authority_binding.AuthorityClass` -- see
    `check_architecture_dependencies.INTERNAL_ALLOWED["commit"]` for
    the citation. Type-only use. Not a forbidden-dependency violation.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "commit/__init__.py", "")
    _write(packages_root, "commit/coordinator.py", "import governance\n")
    _write(packages_root, "governance/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert violations == []


def test_governance_still_cannot_depend_on_commit(tmp_path: Path) -> None:
    """Negative control for the extension above: the new
    `commit -> governance` edge must not have quietly become
    bidirectional. `governance`'s permitted dependencies remain
    `domain`, `semantic_types` (14 §3.1) -- it must never reach into
    the write-coordination layer built on top of it.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "governance/__init__.py", "")
    _write(packages_root, "governance/oops.py", "import commit\n")
    _write(packages_root, "commit/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert len(violations) == 1
    assert violations[0].owner_package == "governance"
    assert violations[0].imported == "commit"


def test_allows_persistence_to_depend_on_commit_for_typed_records(tmp_path: Path) -> None:
    """PKG-13: `persistence` may depend on `commit` so
    `commit_repository.py` can store/reconstruct real
    `CommitUnit`/`CommitOutcome` instances -- see
    `check_architecture_dependencies.INTERNAL_ALLOWED["persistence"]`
    for the citation. This is the reverse direction of the
    already-existing `commit -> persistence` edge (`commit/idempotency.py`
    reads/writes through persistence's repositories); it does not
    create an actual Python-level circular import because the two
    directions are exercised by disjoint submodules
    (`commit/idempotency.py` vs. `commit/coordinator.py` +
    `persistence/commit_repository.py`), and `commit/__init__.py`
    itself has no imports. Not a forbidden-dependency violation.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "persistence/__init__.py", "")
    _write(packages_root, "persistence/commit_repository.py", "import commit\n")
    _write(packages_root, "commit/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert violations == []


def test_allows_application_to_depend_on_commit_for_the_command_processor(
    tmp_path: Path,
) -> None:
    """PKG-14: `application` may depend on `commit` so
    `question_selection_handler.py` can construct and invoke a real
    `CommitCoordinator` -- see
    `check_architecture_dependencies.INTERNAL_ALLOWED["application"]`
    for the citation (14 §3.1's own "may depend on: public ports
    above"). Not a forbidden-dependency violation.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "application/__init__.py", "")
    _write(packages_root, "application/question_selection_handler.py", "import commit\n")
    _write(packages_root, "commit/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert violations == []


def test_commit_still_cannot_depend_on_application(tmp_path: Path) -> None:
    """Negative control for the extension above: the new
    `application -> commit` edge must not have quietly become
    bidirectional. `commit`'s permitted dependencies remain `command`,
    `boundaries`, `persistence`, `audit`, `events`, `authority`,
    `governance`, `semantic_types` (14 §3.1) -- it must never reach up
    into the use-case orchestration layer built on top of it.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "commit/__init__.py", "")
    _write(packages_root, "commit/oops.py", "import application\n")
    _write(packages_root, "application/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert len(violations) == 1
    assert violations[0].owner_package == "commit"
    assert violations[0].imported == "application"


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


def test_allows_persistence_to_depend_on_command_for_typed_records(tmp_path: Path) -> None:
    """PKG-10: `persistence` may depend on `command` so
    `command_repository.py` can store/reconstruct real
    `CommandEnvelope`/`CommandOutcome` instances -- see
    `check_architecture_dependencies.INTERNAL_ALLOWED["persistence"]`
    for the citation. Not a forbidden-dependency violation.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "persistence/__init__.py", "")
    _write(packages_root, "persistence/command_repository.py", "import command\n")
    _write(packages_root, "command/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert violations == []


def test_command_still_cannot_depend_on_persistence(tmp_path: Path) -> None:
    """Negative control for the extension above: the new
    `persistence -> command` edge must not have quietly become
    bidirectional. `command`'s only permitted dependencies remain
    `domain` and `semantic_types` (14 §3.1: "no direct write") -- it
    must never reach into the storage adapter built on top of it.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "command/__init__.py", "")
    _write(packages_root, "command/oops.py", "import persistence\n")
    _write(packages_root, "persistence/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert len(violations) == 1
    assert violations[0].owner_package == "command"
    assert violations[0].imported == "persistence"


def test_allows_persistence_to_depend_on_audit_for_typed_records(tmp_path: Path) -> None:
    """PKG-12: `persistence` may depend on `audit` so
    `audit_repository.py` can store/reconstruct real `AuditEvent`
    instances -- see
    `check_architecture_dependencies.INTERNAL_ALLOWED["persistence"]`
    for the citation. Not a forbidden-dependency violation.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "persistence/__init__.py", "")
    _write(packages_root, "persistence/audit_repository.py", "import audit\n")
    _write(packages_root, "audit/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert violations == []


def test_audit_still_cannot_depend_on_persistence(tmp_path: Path) -> None:
    """Negative control for the extension above: the new
    `persistence -> audit` edge must not have quietly become
    bidirectional. `audit`'s only permitted dependency remains
    `semantic_types` (14 §3.1) -- it must never reach into the storage
    adapter built on top of it.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "audit/__init__.py", "")
    _write(packages_root, "audit/oops.py", "import persistence\n")
    _write(packages_root, "persistence/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert len(violations) == 1
    assert violations[0].owner_package == "audit"
    assert violations[0].imported == "persistence"


def test_allows_persistence_to_depend_on_events_for_typed_records(tmp_path: Path) -> None:
    """PKG-12: `persistence` may depend on `events` so
    `outbox_repository.py` can store/reconstruct real
    `OutboxRecord`/`DeliveryStatus` instances -- see
    `check_architecture_dependencies.INTERNAL_ALLOWED["persistence"]`
    for the citation. Not a forbidden-dependency violation.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "persistence/__init__.py", "")
    _write(packages_root, "persistence/outbox_repository.py", "import events\n")
    _write(packages_root, "events/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert violations == []


def test_events_still_cannot_depend_on_persistence(tmp_path: Path) -> None:
    """Negative control for the extension above: the new
    `persistence -> events` edge must not have quietly become
    bidirectional. `events`'s only permitted dependency remains
    `semantic_types` (14 §3.1) -- it must never reach into the storage
    adapter built on top of it.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "events/__init__.py", "")
    _write(packages_root, "events/oops.py", "import persistence\n")
    _write(packages_root, "persistence/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert len(violations) == 1
    assert violations[0].owner_package == "events"
    assert violations[0].imported == "persistence"


def test_rejects_a_db_driver_import_from_audit(tmp_path: Path) -> None:
    """PKG-12 hardening: `audit`'s own directory-ownership row (14
    §3.1: "semantic_types" only) already implies no ORM code belongs
    here; this is the independently checkable half.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "audit/__init__.py", "")
    _write(packages_root, "audit/oops.py", "import sqlalchemy\n")

    violations = check(roots=(packages_root,))

    assert len(violations) == 1
    assert violations[0].owner_package == "audit"
    assert violations[0].imported == "sqlalchemy"


def test_rejects_a_db_driver_import_from_events(tmp_path: Path) -> None:
    packages_root = tmp_path / "packages"
    _write(packages_root, "events/__init__.py", "")
    _write(packages_root, "events/oops.py", "import sqlalchemy\n")

    violations = check(roots=(packages_root,))

    assert len(violations) == 1
    assert violations[0].owner_package == "events"
    assert violations[0].imported == "sqlalchemy"


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


def test_allows_persistence_to_depend_on_evidence_for_typed_records(tmp_path: Path) -> None:
    """PKG-16: `persistence` may depend on `evidence` so
    `evidence_repository.py` can store/reconstruct real `Evidence`/
    `SourceReference`/`ClaimAnchor`/`EvidenceRelation`/
    `EvidenceSetReference` instances -- see
    `check_architecture_dependencies.INTERNAL_ALLOWED["persistence"]`
    for the citation. Not a forbidden-dependency violation.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "persistence/__init__.py", "")
    _write(packages_root, "persistence/evidence_repository.py", "import evidence\n")
    _write(packages_root, "evidence/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert violations == []


def test_evidence_still_cannot_depend_on_persistence(tmp_path: Path) -> None:
    """Negative control for the extension above: the new
    `persistence -> evidence` edge must not have quietly become
    bidirectional. `evidence`'s permitted dependencies remain `domain`,
    `semantic_types` (14 §3.1) -- it must never reach into the storage
    adapter built on top of it.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "evidence/__init__.py", "")
    _write(packages_root, "evidence/oops.py", "import persistence\n")
    _write(packages_root, "persistence/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert len(violations) == 1
    assert violations[0].owner_package == "evidence"
    assert violations[0].imported == "persistence"


def test_allows_commit_to_depend_on_evidence_for_freshness_linkage(tmp_path: Path) -> None:
    """PKG-17: `commit` may depend on `evidence` so `coordinator.py`
    can resolve `evidence.freshness.EvidenceSetFreshnessResult`
    immediately before invoking BND-014 (09 section 114: "BND-014
    compares member versions/current states") -- see
    `check_architecture_dependencies.INTERNAL_ALLOWED["commit"]` for
    the citation. Not a forbidden-dependency violation.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "commit/__init__.py", "")
    _write(packages_root, "commit/coordinator.py", "import evidence\n")
    _write(packages_root, "evidence/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert violations == []


def test_evidence_still_cannot_depend_on_commit(tmp_path: Path) -> None:
    """Negative control for the extension above: the new
    `commit -> evidence` edge must not have quietly become
    bidirectional. `evidence`'s permitted dependencies remain `domain`,
    `semantic_types` (14 section 3.1) -- it must never reach into the
    commit orchestration layer built on top of it.
    """
    packages_root = tmp_path / "packages"
    _write(packages_root, "evidence/__init__.py", "")
    _write(packages_root, "evidence/oops.py", "import commit\n")
    _write(packages_root, "commit/__init__.py", "")

    violations = check(roots=(packages_root,))

    assert len(violations) == 1
    assert violations[0].owner_package == "evidence"
    assert violations[0].imported == "commit"
