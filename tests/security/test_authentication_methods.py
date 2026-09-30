"""T9 SECURITY: the authentication method model (24 WU-AUTH-02; FBR-AUTH-002).

MUST BECOME TRUE: a canonical `UserId` can have typed authentication methods
(24 §9.1, §13.2): each method names its user, its type, its status and its
provenance, and its status is the fact that later controls login.

MUST REMAIN IMPOSSIBLE: email equality relates methods or identities; a
recovery challenge, an OIDC transaction, an initiating user-agent binding or a
local login-CSRF proof appears as an authentication method (24 §9.1, §13.2
"Excluded"); a method without a canonical user; a revoked method becoming
active again; a method carrying or creating Workspace authority; the relation
being treated as Workspace-scoped (24 §38 falsifier 64).
"""

from __future__ import annotations

import dataclasses
import uuid
from datetime import datetime, timedelta, timezone

import pytest
import sqlalchemy as sa
from security.auth_methods import (
    AuthenticationMethod,
    AuthenticationMethodStatus,
    AuthenticationMethodType,
)
from semantic_types.ids import AuthenticationMethodId, UserId

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_PROVENANCE = "test:wu-auth-02"
_NON_METHODS = (
    "RECOVERY_CHALLENGE",
    "OIDC_TRANSACTION",
    "INITIATING_USER_AGENT_BINDING",
    "LOCAL_LOGIN_CSRF_PROOF",
    "PKCE_VERIFIER",
    "CSRF_PROOF",
    "FUTURE_OIDC_PROVIDER",
)
_AUTHORITY_TABLES = (
    "workspace_memberships",
    "role_assignments",
    "human_authority_bindings",
    "session_participations",
    "workspaces",
)


def _method(**overrides: object) -> AuthenticationMethod:
    values: dict[str, object] = {
        "method_id": AuthenticationMethodId(uuid.uuid4()),
        "user_id": UserId(uuid.uuid4()),
        "method_type": AuthenticationMethodType.LOCAL_PASSWORD,
        "status": AuthenticationMethodStatus.ACTIVE,
        "created_at": _NOW,
        "revoked_at": None,
        "last_authenticated_at": None,
        "provenance_ref": _PROVENANCE,
    }
    values.update(overrides)
    return AuthenticationMethod(**values)  # type: ignore[arg-type]


# --- the vocabulary (no database) -------------------------------------------


def test_the_method_types_are_exactly_the_persistent_methods_of_24_section_9_1() -> None:
    assert {member.value for member in AuthenticationMethodType} == {
        "LOCAL_PASSWORD",
        "GOOGLE_OIDC",
        "TEST_PROVIDER",
    }


@pytest.mark.parametrize("name", _NON_METHODS)
def test_proof_and_protocol_relations_are_not_method_types(name: str) -> None:
    assert name not in {member.value for member in AuthenticationMethodType}
    with pytest.raises(ValueError):
        AuthenticationMethodType(name)


def test_the_method_statuses_are_active_and_revoked() -> None:
    assert {member.value for member in AuthenticationMethodStatus} == {"ACTIVE", "REVOKED"}


def test_a_method_carries_no_email_and_no_authority_shaped_field() -> None:
    assert {field.name for field in dataclasses.fields(AuthenticationMethod)} == {
        "method_id",
        "user_id",
        "method_type",
        "status",
        "created_at",
        "revoked_at",
        "last_authenticated_at",
        "provenance_ref",
    }


def test_an_active_method_cannot_carry_a_revocation_time() -> None:
    with pytest.raises(ValueError):
        _method(revoked_at=_NOW)


def test_a_revoked_method_must_carry_its_revocation_time() -> None:
    with pytest.raises(ValueError):
        _method(status=AuthenticationMethodStatus.REVOKED)
    revoked = _method(status=AuthenticationMethodStatus.REVOKED, revoked_at=_NOW)
    assert revoked.status is AuthenticationMethodStatus.REVOKED


def test_a_method_requires_provenance() -> None:
    with pytest.raises(ValueError):
        _method(provenance_ref="")


def test_a_method_rejects_naive_timestamps() -> None:
    with pytest.raises(ValueError):
        _method(created_at=datetime(2030, 1, 1))


def test_a_method_rejects_untyped_type_and_status() -> None:
    with pytest.raises(TypeError):
        _method(method_type="LOCAL_PASSWORD")
    with pytest.raises(TypeError):
        _method(status="ACTIVE")


# --- the persisted relation (real PostgreSQL) -------------------------------


def _repository(connection: sa.Connection):  # type: ignore[no-untyped-def]
    from persistence.authentication_method_repository import (
        SqlAlchemyAuthenticationMethodRepository,
    )

    return SqlAlchemyAuthenticationMethodRepository(connection)


def _insert_user(connection: sa.Connection, *, email: str | None = None) -> UserId:
    from persistence.tables import users_table

    user_id = UserId(uuid.uuid4())
    connection.execute(
        sa.insert(users_table).values(
            id=user_id.value,
            email=email or f"{user_id.value}@example.test",
            name="Method Owner",
            record_version=1,
            created_at=_NOW,
            updated_at=_NOW,
        )
    )
    return user_id


def _raw_insert(connection: sa.Connection, **overrides: object) -> None:
    values: dict[str, object] = {
        "id": uuid.uuid4(),
        "method_type": "LOCAL_PASSWORD",
        "status": "ACTIVE",
        "created_at": _NOW,
        "revoked_at": None,
        "last_authenticated_at": None,
        "provenance_ref": _PROVENANCE,
    }
    values.update(overrides)
    connection.execute(
        sa.text(
            "INSERT INTO authentication_methods "
            "(id, user_id, method_type, status, created_at, revoked_at, "
            "last_authenticated_at, provenance_ref) VALUES "
            "(:id, :user_id, :method_type, :status, :created_at, :revoked_at, "
            ":last_authenticated_at, :provenance_ref)"
        ),
        values,
    )


def _refused(connection: sa.Connection, statement: sa.TextClause, params: dict[str, object]) -> str:
    """Runs `statement` in a savepoint and returns the database's refusal."""
    with pytest.raises(sa.exc.DBAPIError) as refused, connection.begin_nested():
        connection.execute(statement, params)
    return str(refused.value)


def test_a_user_gets_a_typed_active_method_traceable_to_the_user(
    db_connection: sa.Connection,
) -> None:
    user_id = _insert_user(db_connection)
    repository = _repository(db_connection)

    created = repository.create(
        user_id=user_id,
        method_type=AuthenticationMethodType.LOCAL_PASSWORD,
        provenance_ref=_PROVENANCE,
        now=_NOW,
    )

    assert created.user_id == user_id
    assert created.method_type is AuthenticationMethodType.LOCAL_PASSWORD
    assert created.status is AuthenticationMethodStatus.ACTIVE
    assert created.revoked_at is None and created.last_authenticated_at is None
    assert created.provenance_ref == _PROVENANCE
    assert repository.get(created.method_id) == created
    assert repository.list_for_user(user_id) == (created,)


def test_a_user_may_hold_methods_of_several_types(db_connection: sa.Connection) -> None:
    user_id = _insert_user(db_connection)
    repository = _repository(db_connection)
    local = repository.create(
        user_id=user_id,
        method_type=AuthenticationMethodType.LOCAL_PASSWORD,
        provenance_ref=_PROVENANCE,
        now=_NOW,
    )
    google = repository.create(
        user_id=user_id,
        method_type=AuthenticationMethodType.GOOGLE_OIDC,
        provenance_ref=_PROVENANCE,
        now=_NOW + timedelta(seconds=1),
    )
    assert repository.list_for_user(user_id) == (local, google)


def test_an_unknown_method_id_resolves_to_nothing(db_connection: sa.Connection) -> None:
    assert _repository(db_connection).get(AuthenticationMethodId(uuid.uuid4())) is None
    assert _repository(db_connection).list_for_user(UserId(uuid.uuid4())) == ()


def test_a_user_cannot_hold_two_active_local_password_methods(
    db_connection: sa.Connection,
) -> None:
    user_id = _insert_user(db_connection)
    _raw_insert(db_connection, user_id=user_id.value)
    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        _raw_insert(db_connection, user_id=user_id.value)
    assert len(_repository(db_connection).list_for_user(user_id)) == 1


def test_a_revoked_local_password_method_may_be_succeeded_by_a_new_one(
    db_connection: sa.Connection,
) -> None:
    user_id = _insert_user(db_connection)
    repository = _repository(db_connection)
    first = repository.create(
        user_id=user_id,
        method_type=AuthenticationMethodType.LOCAL_PASSWORD,
        provenance_ref=_PROVENANCE,
        now=_NOW,
    )
    assert repository.revoke(first.method_id, revoked_at=_NOW + timedelta(minutes=1)) is True
    second = repository.create(
        user_id=user_id,
        method_type=AuthenticationMethodType.LOCAL_PASSWORD,
        provenance_ref=_PROVENANCE,
        now=_NOW + timedelta(minutes=2),
    )
    statuses = [method.status for method in repository.list_for_user(user_id)]
    assert statuses == [AuthenticationMethodStatus.REVOKED, AuthenticationMethodStatus.ACTIVE]
    assert second.method_id != first.method_id


def test_no_method_exists_without_a_canonical_user(db_connection: sa.Connection) -> None:
    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        _raw_insert(db_connection, user_id=uuid.uuid4())


@pytest.mark.parametrize("name", _NON_METHODS)
def test_the_database_refuses_proof_and_protocol_relations_as_methods(
    db_connection: sa.Connection, name: str
) -> None:
    user_id = _insert_user(db_connection)
    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        _raw_insert(db_connection, user_id=user_id.value, method_type=name)
    assert _repository(db_connection).list_for_user(user_id) == ()


def test_a_method_cannot_be_created_already_revoked(db_connection: sa.Connection) -> None:
    user_id = _insert_user(db_connection)
    with pytest.raises(sa.exc.DBAPIError), db_connection.begin_nested():
        _raw_insert(db_connection, user_id=user_id.value, status="REVOKED", revoked_at=_NOW)


def test_the_database_keeps_status_and_revocation_time_consistent(
    db_connection: sa.Connection,
) -> None:
    user_id = _insert_user(db_connection)
    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        _raw_insert(db_connection, user_id=user_id.value, revoked_at=_NOW)
    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        _raw_insert(db_connection, user_id=user_id.value, provenance_ref="")


def test_revoking_records_the_time_and_happens_once(db_connection: sa.Connection) -> None:
    user_id = _insert_user(db_connection)
    repository = _repository(db_connection)
    method = repository.create(
        user_id=user_id,
        method_type=AuthenticationMethodType.GOOGLE_OIDC,
        provenance_ref=_PROVENANCE,
        now=_NOW,
    )
    revoked_at = _NOW + timedelta(hours=1)

    assert repository.revoke(method.method_id, revoked_at=revoked_at) is True
    after = repository.get(method.method_id)
    assert after is not None
    assert after.status is AuthenticationMethodStatus.REVOKED and after.revoked_at == revoked_at

    assert repository.revoke(method.method_id, revoked_at=revoked_at + timedelta(hours=1)) is False
    assert repository.get(method.method_id) == after
    assert repository.revoke(AuthenticationMethodId(uuid.uuid4()), revoked_at=revoked_at) is False


def test_a_revoked_method_never_becomes_active_again(db_connection: sa.Connection) -> None:
    user_id = _insert_user(db_connection)
    repository = _repository(db_connection)
    method = repository.create(
        user_id=user_id,
        method_type=AuthenticationMethodType.LOCAL_PASSWORD,
        provenance_ref=_PROVENANCE,
        now=_NOW,
    )
    repository.revoke(method.method_id, revoked_at=_NOW + timedelta(hours=1))
    before = repository.get(method.method_id)

    for statement in (
        "UPDATE authentication_methods SET status = 'ACTIVE', revoked_at = NULL WHERE id = :id",
        "UPDATE authentication_methods SET revoked_at = now() WHERE id = :id",
        "UPDATE authentication_methods SET last_authenticated_at = now() WHERE id = :id",
    ):
        refusal = _refused(db_connection, sa.text(statement), {"id": method.method_id.value})
        assert "REVOKED" in refusal
    assert repository.get(method.method_id) == before


@pytest.mark.parametrize(
    "assignment",
    [
        "user_id = :other",
        "method_type = 'GOOGLE_OIDC'",
        "provenance_ref = 'rewritten'",
        "created_at = now()",
        "id = :other",
    ],
)
def test_the_identity_of_a_method_is_immutable(
    db_connection: sa.Connection, assignment: str
) -> None:
    user_id = _insert_user(db_connection)
    other = _insert_user(db_connection)
    repository = _repository(db_connection)
    method = repository.create(
        user_id=user_id,
        method_type=AuthenticationMethodType.LOCAL_PASSWORD,
        provenance_ref=_PROVENANCE,
        now=_NOW,
    )
    refusal = _refused(
        db_connection,
        sa.text(f"UPDATE authentication_methods SET {assignment} WHERE id = :id"),
        {"id": method.method_id.value, "other": other.value},
    )
    assert "immutable" in refusal
    assert repository.get(method.method_id) == method


def test_revoking_one_users_method_leaves_every_other_method_untouched(
    db_connection: sa.Connection,
) -> None:
    repository = _repository(db_connection)
    first_user = _insert_user(db_connection)
    second_user = _insert_user(db_connection)
    first = repository.create(
        user_id=first_user,
        method_type=AuthenticationMethodType.LOCAL_PASSWORD,
        provenance_ref=_PROVENANCE,
        now=_NOW,
    )
    second = repository.create(
        user_id=second_user,
        method_type=AuthenticationMethodType.LOCAL_PASSWORD,
        provenance_ref=_PROVENANCE,
        now=_NOW,
    )
    sibling = repository.create(
        user_id=first_user,
        method_type=AuthenticationMethodType.GOOGLE_OIDC,
        provenance_ref=_PROVENANCE,
        now=_NOW,
    )
    repository.revoke(first.method_id, revoked_at=_NOW + timedelta(hours=1))
    assert repository.get(second.method_id) == second
    assert repository.get(sibling.method_id) == sibling


def test_the_relation_has_no_email_and_is_not_workspace_scoped(
    db_connection: sa.Connection,
) -> None:
    columns = set(
        db_connection.execute(
            sa.text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'authentication_methods'"
            )
        ).scalars()
    )
    assert columns == {
        "id",
        "user_id",
        "method_type",
        "status",
        "created_at",
        "revoked_at",
        "last_authenticated_at",
        "provenance_ref",
    }
    row_security = db_connection.execute(
        sa.text("SELECT relrowsecurity FROM pg_class WHERE relname = 'authentication_methods'")
    ).scalar_one()
    assert row_security is False


def test_methods_are_related_by_user_never_by_email(db_connection: sa.Connection) -> None:
    """Two identities whose emails differ only in case stay two identities with
    two separate method sets: nothing in the model can join them by email."""
    repository = _repository(db_connection)
    local_part = uuid.uuid4().hex
    first_user = _insert_user(db_connection, email=f"{local_part}@example.test")
    second_user = _insert_user(db_connection, email=f"{local_part.upper()}@EXAMPLE.TEST")
    first = repository.create(
        user_id=first_user,
        method_type=AuthenticationMethodType.LOCAL_PASSWORD,
        provenance_ref=_PROVENANCE,
        now=_NOW,
    )
    second = repository.create(
        user_id=second_user,
        method_type=AuthenticationMethodType.GOOGLE_OIDC,
        provenance_ref=_PROVENANCE,
        now=_NOW,
    )
    assert repository.list_for_user(first_user) == (first,)
    assert repository.list_for_user(second_user) == (second,)
    public = {name for name in dir(repository) if not name.startswith("_")}
    assert public == {"create", "get", "list_for_user", "revoke"}


def test_creating_and_revoking_a_method_creates_no_authority(
    db_connection: sa.Connection,
) -> None:
    def counts() -> dict[str, int]:
        return {
            table: db_connection.execute(sa.text(f"SELECT count(*) FROM {table}")).scalar_one()
            for table in _AUTHORITY_TABLES
        }

    before = counts()
    user_id = _insert_user(db_connection)
    repository = _repository(db_connection)
    method = repository.create(
        user_id=user_id,
        method_type=AuthenticationMethodType.LOCAL_PASSWORD,
        provenance_ref=_PROVENANCE,
        now=_NOW,
    )
    repository.revoke(method.method_id, revoked_at=_NOW + timedelta(hours=1))
    assert counts() == before


def test_two_concurrent_creations_leave_one_active_local_password_method(
    db_connection: sa.Connection,
) -> None:
    """Concurrency (24 §33): the second writer waits on the first and is then
    refused by the authoritative constraint, not by process-local state."""
    engine = db_connection.engine
    user_id = UserId(uuid.uuid4())
    with engine.begin() as setup:
        from persistence.tables import users_table

        setup.execute(
            sa.insert(users_table).values(
                id=user_id.value,
                email=f"{user_id.value}@example.test",
                name="Concurrent",
                record_version=1,
                created_at=_NOW,
                updated_at=_NOW,
            )
        )
    first = engine.connect()
    second = engine.connect()
    try:
        first_tx = first.begin()
        _raw_insert(first, user_id=user_id.value)
        second_tx = second.begin()
        second.execute(sa.text("SET LOCAL lock_timeout = '300ms'"))
        with pytest.raises(sa.exc.OperationalError):
            _raw_insert(second, user_id=user_id.value)  # waits on the uncommitted first
        second_tx.rollback()
        first_tx.commit()
        second_tx = second.begin()
        with pytest.raises(sa.exc.IntegrityError):
            _raw_insert(second, user_id=user_id.value)
        second_tx.rollback()
        with engine.connect() as check:
            active = check.execute(
                sa.text(
                    "SELECT count(*) FROM authentication_methods "
                    "WHERE user_id = :u AND status = 'ACTIVE'"
                ),
                {"u": user_id.value},
            ).scalar_one()
        assert active == 1
    finally:
        first.close()
        second.close()
        with engine.begin() as cleanup:
            cleanup.execute(
                sa.text("DELETE FROM authentication_methods WHERE user_id = :u"),
                {"u": user_id.value},
            )
            cleanup.execute(sa.text("DELETE FROM users WHERE id = :u"), {"u": user_id.value})
