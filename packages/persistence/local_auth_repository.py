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
from typing import Any

import sqlalchemy as sa
from security.auth_methods import AuthenticationMethodStatus, AuthenticationMethodType
from security.local_auth import (
    LocalCredentialRecord,
    LocalSessionRecord,
    SessionRevocationReason,
)
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

    def replace_password(self, *, user_id: UserId, password_hash: str, now: datetime) -> bool:
        """WU-AUTH-12 (24 §19.6): the credential replacement effect of a
        verified recovery. One row per user; the previous hash is replaced,
        the credential's method is unchanged. False when the identity has no
        local credential (nothing to replace)."""
        result = self._connection.execute(
            sa.update(local_auth_credentials_table)
            .where(local_auth_credentials_table.c.user_id == user_id.value)
            .values(password_hash=password_hash, updated_at=now)
        )
        return result.rowcount == 1

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


def _session_select() -> sa.Select[tuple[object, ...]]:
    """A session with the type and status of its method, read in one statement."""
    return sa.select(
        local_auth_sessions_table,
        authentication_methods_table.c.method_type.label("method_type"),
        authentication_methods_table.c.status.label("method_status"),
    ).select_from(
        local_auth_sessions_table.outerjoin(
            authentication_methods_table,
            authentication_methods_table.c.id
            == local_auth_sessions_table.c.authentication_method_id,
        )
    )


def _to_session(row: Any) -> LocalSessionRecord:
    method_id = row["authentication_method_id"]
    return LocalSessionRecord(
        session_id=row["id"],
        user_id=UserId(row["user_id"]),
        session_token_hash=row["session_token_hash"],
        issued_at=row["issued_at"],
        expires_at=row["expires_at"],
        revoked_at=row["revoked_at"],
        method_id=None if method_id is None else AuthenticationMethodId(method_id),
        proof_provenance=row["proof_provenance"],
        revoked_reason=(
            None
            if row["revoked_reason"] is None
            else SessionRevocationReason(row["revoked_reason"])
        ),
        method_type=(
            None if row["method_type"] is None else AuthenticationMethodType(row["method_type"])
        ),
        method_status=(
            None
            if row["method_status"] is None
            else AuthenticationMethodStatus(row["method_status"])
        ),
    )


class SqlAlchemyLocalSessionRepository:
    """`LocalSessionRepository` backed by `local_auth_sessions`.

    WU-AUTH-04: every revocation is one conditional UPDATE
    (`WHERE revoked_at IS NULL`), so a session is revoked once, by one writer,
    with one reason; the database refuses any later change to it."""

    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def create(
        self,
        *,
        user_id: UserId,
        session_token_hash: str,
        issued_at: datetime,
        expires_at: datetime,
        method_id: AuthenticationMethodId | None,
        proof_provenance: str | None = None,
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
                authentication_method_id=None if method_id is None else method_id.value,
                proof_provenance=proof_provenance,
                revoked_reason=None,
            )
        )
        return LocalSessionRecord(
            session_id=session_id,
            user_id=user_id,
            session_token_hash=session_token_hash,
            issued_at=issued_at,
            expires_at=expires_at,
            revoked_at=None,
            method_id=method_id,
            proof_provenance=proof_provenance,
        )

    def get_by_token_hash(self, session_token_hash: str) -> LocalSessionRecord | None:
        row = (
            self._connection.execute(
                _session_select().where(
                    local_auth_sessions_table.c.session_token_hash == session_token_hash
                )
            )
            .mappings()
            .one_or_none()
        )
        return None if row is None else _to_session(row)

    def list_live_for_user(
        self, user_id: UserId, *, now: datetime
    ) -> tuple[LocalSessionRecord, ...]:
        rows = (
            self._connection.execute(
                _session_select()
                .where(
                    local_auth_sessions_table.c.user_id == user_id.value,
                    local_auth_sessions_table.c.revoked_at.is_(None),
                    local_auth_sessions_table.c.expires_at > now,
                    sa.or_(
                        local_auth_sessions_table.c.authentication_method_id.is_(None),
                        authentication_methods_table.c.status
                        == AuthenticationMethodStatus.ACTIVE.value,
                    ),
                )
                .order_by(local_auth_sessions_table.c.issued_at, local_auth_sessions_table.c.id)
            )
            .mappings()
            .all()
        )
        return tuple(_to_session(row) for row in rows)

    def _revoke_where(
        self, *conditions: Any, revoked_at: datetime, reason: SessionRevocationReason
    ) -> int:
        result = self._connection.execute(
            sa.update(local_auth_sessions_table)
            .where(local_auth_sessions_table.c.revoked_at.is_(None), *conditions)
            .values(revoked_at=revoked_at, revoked_reason=reason.value)
        )
        return int(result.rowcount)

    def revoke(
        self, session_token_hash: str, *, revoked_at: datetime, reason: SessionRevocationReason
    ) -> bool:
        return (
            self._revoke_where(
                local_auth_sessions_table.c.session_token_hash == session_token_hash,
                revoked_at=revoked_at,
                reason=reason,
            )
            == 1
        )

    def revoke_own(
        self,
        session_id: uuid.UUID,
        *,
        user_id: UserId,
        revoked_at: datetime,
        reason: SessionRevocationReason,
    ) -> bool:
        """Revokes the session only if it belongs to `user_id`."""
        return (
            self._revoke_where(
                local_auth_sessions_table.c.id == session_id,
                local_auth_sessions_table.c.user_id == user_id.value,
                revoked_at=revoked_at,
                reason=reason,
            )
            == 1
        )

    def revoke_all_for_user(
        self, user_id: UserId, *, revoked_at: datetime, reason: SessionRevocationReason
    ) -> int:
        return self._revoke_where(
            local_auth_sessions_table.c.user_id == user_id.value,
            revoked_at=revoked_at,
            reason=reason,
        )

    def revoke_for_method(
        self,
        method_id: AuthenticationMethodId,
        *,
        revoked_at: datetime,
        reason: SessionRevocationReason,
    ) -> int:
        return self._revoke_where(
            local_auth_sessions_table.c.authentication_method_id == method_id.value,
            revoked_at=revoked_at,
            reason=reason,
        )


__all__ = ["SqlAlchemyLocalCredentialRepository", "SqlAlchemyLocalSessionRepository"]
