"""Fixture validation: `NonProofWorkspaceBootstrap`, against real PostgreSQL.

Covers PKG-04's 3 mandatory adversarial attacks (production import,
fixture used to claim bootstrap legitimacy, fixture authority escaping
test environment) plus 2 novel/adapted ones (cross-layer proof with
`AuthorityResolver`, and double-seeding non-collision), exceeding the
>=5 total minimum.
"""

from __future__ import annotations

import dataclasses
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest
import sqlalchemy as sa
from authority.actor import ActorClass, ActorIdentity
from authority.resolver import AuthorityRequest, AuthorityResolver, AuthorityVerdict
from check_test_only_imports import check as check_test_only_imports
from governance.authority_binding import AuthorityClass
from persistence.authority_binding_repository import SqlAlchemyAuthorityBindingRepository
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.tables import human_authority_bindings_table, users_table
from semantic_types.id_generator import SystemIdGenerator
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import (
    FIXTURE_LEGITIMACY,
    NonProofWorkspaceBootstrap,
    NonProofWorkspaceBootstrapResult,
)


def _bootstrap(connection: sa.Connection) -> NonProofWorkspaceBootstrap:
    return NonProofWorkspaceBootstrap(
        connection, FixedClock(datetime(2030, 1, 1, tzinfo=timezone.utc)), SystemIdGenerator()
    )


def test_seed_produces_a_working_governance_root(db_connection: sa.Connection) -> None:
    result = _bootstrap(db_connection).seed(owner_email="owner@nonproof.test")

    assert result.fixture_legitimacy == "NON_PROOF_FIXTURE"

    row = (
        db_connection.execute(
            sa.select(users_table).where(users_table.c.id == result.owner_user_id.value)
        )
        .mappings()
        .one()
    )
    assert row["email"] == "owner@nonproof.test"


def test_fixture_legitimacy_cannot_be_any_other_value() -> None:
    """Mandatory adversarial attack: fixture used to claim bootstrap
    legitimacy. There is no constructor path to a
    `NonProofWorkspaceBootstrapResult` claiming anything else.
    """
    with pytest.raises(ValueError, match="NON_PROOF_FIXTURE"):
        NonProofWorkspaceBootstrapResult(
            fixture_legitimacy="LEGITIMATE",  # type: ignore[arg-type]
            workspace_id=None,  # type: ignore[arg-type]
            owner_user_id=None,  # type: ignore[arg-type]
            membership_id=uuid.uuid4(),
            governance_binding_id=None,  # type: ignore[arg-type]
        )


def test_result_fields_do_not_include_a_legitimacy_override_field() -> None:
    """Structural half of the same attack: no field exists that could
    let a caller assert legitimacy some other way."""
    fields = {f.name for f in dataclasses.fields(NonProofWorkspaceBootstrapResult)}
    assert fields == {
        "fixture_legitimacy",
        "workspace_id",
        "owner_user_id",
        "membership_id",
        "governance_binding_id",
    }


def test_seeded_row_is_db_indistinguishable_from_a_legitimate_one(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: fixture authority escaping test
    environment. Stated plainly rather than hidden: the seeded
    `human_authority_bindings` row has no schema-level marker
    distinguishing it from a legitimate grant (14 §38: fixture metadata
    lives "in the test harness, not as production domain semantics").
    The *only* thing standing between this fixture and production
    reachability is the import-graph guard proven below -- not
    anything in the row itself.
    """
    result = _bootstrap(db_connection).seed(owner_email="owner2@nonproof.test")

    row = (
        db_connection.execute(
            sa.select(human_authority_bindings_table).where(
                human_authority_bindings_table.c.id == result.governance_binding_id.value
            )
        )
        .mappings()
        .one()
    )

    # No fixture_legitimacy/is_fixture/etc. column exists at all -- the
    # row's columns are exactly the production schema, nothing added.
    assert set(row.keys()) == {
        "id",
        "workspace_id",
        "human_user_id",
        "authority_class",
        "scope_type",
        "scope_id",
        "authority_source",
        "granted_by_user_id",
        "granted_at",
        "revoked_by_user_id",
        "revoked_at",
        "state",
        "record_version",
    }
    # The one legitimate, pre-existing column that happens to carry a
    # trace of provenance -- not a new mechanism, just an honest use of
    # a field that already varies by grant.
    assert row["authority_source"] == FIXTURE_LEGITIMACY


def test_production_code_cannot_import_this_module(tmp_path: Path) -> None:
    """Mandatory adversarial attack: production import. Reuses the
    real checker (not a reimplementation), targeting this exact
    submodule specifically, not just the generic `test_support` package
    name.
    """
    packages_root = tmp_path / "packages"
    (packages_root / "command").mkdir(parents=True)
    (packages_root / "command" / "__init__.py").write_text("")
    (packages_root / "command" / "bootstrap_workspace.py").write_text(
        "from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap\n"
    )

    violations = check_test_only_imports(roots=(packages_root,))

    assert len(violations) == 1
    assert violations[0].owner_package == "command"
    assert violations[0].imported == "test_support"


def test_cross_layer_authority_resolver_grants_against_the_seeded_root(
    db_connection: sa.Connection,
) -> None:
    """Novel attack 1 (cross-layer proof, not an isolated mock): the
    seeded root is genuinely usable by the real `AuthorityResolver`
    (PKG-03) for `WORKSPACE_GOVERNANCE_RIGHT` -- proving the fixture is
    useful for downstream falsification, which is exactly and only
    what 13 §5 permits ("Tests built on those fixtures may prove
    downstream invariants if the tested invariant does not depend on
    bootstrap legitimacy... They may not prove the bootstrap path
    itself.").
    """
    result = _bootstrap(db_connection).seed(owner_email="owner3@nonproof.test")

    resolver = AuthorityResolver(
        SqlAlchemyMembershipRepository(db_connection),
        SqlAlchemyAuthorityBindingRepository(db_connection),
        FixedClock(datetime(2030, 1, 1, tzinfo=timezone.utc)),
    )
    request = AuthorityRequest(
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
        workspace_id=result.workspace_id,
        operation="GRANT_HUMAN_AUTHORITY_BINDING",
        required_authority_class=AuthorityClass.WORKSPACE_GOVERNANCE_RIGHT,
        scope_type="WORKSPACE",
        scope_id=result.workspace_id.value,
    )
    resolution = resolver.resolve(request)

    assert resolution.verdict == AuthorityVerdict.GRANTED


def test_double_seeding_produces_two_independent_non_colliding_roots(
    db_connection: sa.Connection,
) -> None:
    """Novel attack 2: two `seed()` calls must not collide (shared IDs,
    accidental cross-Workspace membership, etc.) -- a fixture that
    silently reused state between tests would be a correctness hazard
    disguised as convenience.
    """
    bootstrap = _bootstrap(db_connection)
    first = bootstrap.seed(owner_email="first@nonproof.test")
    second = bootstrap.seed(owner_email="second@nonproof.test")

    assert first.workspace_id != second.workspace_id
    assert first.owner_user_id != second.owner_user_id
    assert first.membership_id != second.membership_id
    assert first.governance_binding_id != second.governance_binding_id

    resolver = AuthorityResolver(
        SqlAlchemyMembershipRepository(db_connection),
        SqlAlchemyAuthorityBindingRepository(db_connection),
        FixedClock(datetime(2030, 1, 1, tzinfo=timezone.utc)),
    )
    # Owner of the first Workspace has no authority in the second.
    cross_request = AuthorityRequest(
        actor=ActorIdentity(ActorClass.HUMAN_USER, first.owner_user_id),
        workspace_id=second.workspace_id,
        operation="GRANT_HUMAN_AUTHORITY_BINDING",
        required_authority_class=AuthorityClass.WORKSPACE_GOVERNANCE_RIGHT,
        scope_type="WORKSPACE",
        scope_id=second.workspace_id.value,
    )
    assert resolver.resolve(cross_request).verdict == AuthorityVerdict.DENIED
