"""Concrete `security.local_auth.LocalCredentialRepository`/
`LocalSessionRepository` adapters, backed by `local_auth_credentials`/
`local_auth_sessions` (migration `05794035ef3c`).

Same split as every other port/adapter pair in this codebase
(`security.workspace.WorkspaceContextPort` -> `persistence.
SqlAlchemyWorkspaceContext`, `security.identity.IdentityPort` -> the
concrete adapters in `test_support`/here): the port/types live in
`security`, the concrete SQL lives here, since `security`'s own
allow-list is `semantic_types` only (14 §3.1's forbidden-dependency
matrix) and cannot import `sqlalchemy` itself.

`local_auth_credentials` carries no `email` column of its own (see the
migration's own docstring for why authentication-secret material is
never mixed into `users`) -- `get_by_email` therefore joins to `users`
for the lookup, exactly the same "join out to the canonical Thing"
shape `challenge_session_mapping.py` already uses elsewhere in this
codebase.

WU-AUTH-03 (24 §22.4, §28.2): a local credential belongs to exactly one
LOCAL_PASSWORD authentication method. `create` is the one canonical producer
of a credential and therefore also of its method: every creator (host
operator HD-28, dev provisioning HD-3, the demo seed, test fixtures) calls it,
so none of them can produce a credential without a method. The method's
provenance names the credential row it was created for. `get_by_email` reads
the method id with the credential; `mark_authenticated` is the atomic,
authoritative "method is ACTIVE" check of a login.
"""

from __future__ import annotations

import uuid
from datetime import datetime

import sqlalchemy as sa
from security.auth_methods import AuthenticationMethodStatus, AuthenticationMethodType
from security.local_auth import LocalCredentialRecord, LocalSessionRecord
from semantic_types.ids import AuthenticationMethodId, UserId

from persistence.authentication_method_repository import (
    SqlAlchemyAuthenticationMethodRepository,
)
from persistence.tables import (
    authentication_methods_table,
    local_auth_credentials_table,
    local_auth_sessions_table,
    users_table,
)


class SqlAlchemyLocalCredentialRepository:
    """`LocalCredentialRepository` backed by `local_auth_credentials`
    joined to `users` (for the email lookup key)."""

    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def get_by_email(self, email: str) -> LocalCredentialRecord | None:
        stmt = (
            sa.select(
                local_auth_credentials_table.c.user_id,
                local_auth_credentials_table.c.password_hash,
                local_auth_credentials_table.c.authentication_method_id,
                users_table.c.email,
            )
            .select_from(
                local_auth_credentials_table.join(
                    users_table, users_table.c.id == local_auth_credentials_table.c.user_id
                )
            )
            .where(users_table.c.email == email)
        )
        row = self._connection.execute(stmt).mappings().one_or_none()
        if row is None:
            return None
        return LocalCredentialRecord(
            user_id=UserId(row["user_id"]),
            email=row["email"],
            password_hash=row["password_hash"],
            method_id=AuthenticationMethodId(row["authentication_method_id"]),
        )

    def mark_authenticated(self, method_id: AuthenticationMethodId, *, at: datetime) -> bool:
        """One conditional UPDATE: the row changes only while the method is
        ACTIVE. A revocation that commits first makes this return False."""
        result = self._connection.execute(
            sa.update(authentication_methods_table)
            .where(
                authentication_methods_table.c.id == method_id.value,
                authentication_methods_table.c.status == AuthenticationMethodStatus.ACTIVE.value,
            )
            .values(last_authenticated_at=at)
        )
        return result.rowcount == 1

    def create(self, *, user_id: UserId, password_hash: str, now: datetime) -> None:
        """Not part of the `LocalCredentialRepository` port (login only
        ever reads) -- a small, explicit convenience this concrete
        adapter also offers so a seed script can create a credential
        without hand-rolling the insert. Used by
        `scripts/seed_local_demo.py`/test fixtures only.

        WU-AUTH-03: also creates the credential's LOCAL_PASSWORD method, in
        the caller's transaction (no own savepoint, HD-6)."""
        credential_id = uuid.uuid4()
        method = SqlAlchemyAuthenticationMethodRepository(self._connection).create(
            user_id=user_id,
            method_type=AuthenticationMethodType.LOCAL_PASSWORD,
            provenance_ref=f"local-credential:{credential_id}",
            now=now,
        )
        self._connection.execute(
            sa.insert(local_auth_credentials_table).values(
                id=credential_id,
                user_id=user_id.value,
                authentication_method_id=method.method_id.value,
                password_hash=password_hash,
                created_at=now,
                updated_at=now,
            )
        )


class SqlAlchemyLocalSessionRepository:
    """`LocalSessionRepository` backed by `local_auth_sessions`."""

    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def create(
        self,
        *,
        user_id: UserId,
        session_token_hash: str,
        issued_at: datetime,
        expires_at: datetime,
    ) -> LocalSessionRecord:
        session_id = uuid.uuid4()
        self._connection.execute(
            sa.insert(local_auth_sessions_table).values(
                id=session_id,
                user_id=user_id.value,
                session_token_hash=session_token_hash,
                issued_at=issued_at,
                expires_at=expires_at,
                revoked_at=None,
            )
        )
        return LocalSessionRecord(
            session_id=session_id,
            user_id=user_id,
            session_token_hash=session_token_hash,
            issued_at=issued_at,
            expires_at=expires_at,
            revoked_at=None,
        )

    def get_by_token_hash(self, session_token_hash: str) -> LocalSessionRecord | None:
        stmt = sa.select(local_auth_sessions_table).where(
            local_auth_sessions_table.c.session_token_hash == session_token_hash
        )
        row = self._connection.execute(stmt).mappings().one_or_none()
        if row is None:
            return None
        return LocalSessionRecord(
            session_id=row["id"],
            user_id=UserId(row["user_id"]),
            session_token_hash=row["session_token_hash"],
            issued_at=row["issued_at"],
            expires_at=row["expires_at"],
            revoked_at=row["revoked_at"],
        )

    def revoke(self, session_token_hash: str, *, revoked_at: datetime) -> None:
        self._connection.execute(
            sa.update(local_auth_sessions_table)
            .where(local_auth_sessions_table.c.session_token_hash == session_token_hash)
            .values(revoked_at=revoked_at)
        )


__all__ = ["SqlAlchemyLocalCredentialRepository", "SqlAlchemyLocalSessionRepository"]
