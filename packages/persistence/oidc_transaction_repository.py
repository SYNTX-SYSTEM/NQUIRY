"""Concrete `security.oidc_transaction.OidcTransactionRepository`, backed by
`oidc_auth_transactions` (migration `c4e6a8b1d3f5`; WU-AUTH-05).

`claim` is one statement: it locks the row, moves PENDING → PROCESSING only if
the row is still PENDING and unexpired, blanks the verifier, and returns the
verifier the row held before the statement. Two concurrent callbacks are
serialized by the row lock; the second sees PROCESSING and gets None. No
process-local state takes part (24 §11.7, §22.7, §33.6).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

import sqlalchemy as sa
from security.oidc_transaction import (
    OidcFailureReason,
    OidcTransactionPurpose,
    OidcTransactionRecord,
    OidcTransactionState,
)
from semantic_types.ids import UserId

from persistence.tables import oidc_auth_transactions_table

_TERMINAL_TIMESTAMP = {
    OidcTransactionState.COMPLETED: "completed_at",
    OidcTransactionState.FAILED_TERMINAL: "failed_terminal_at",
    OidcTransactionState.EXPIRED: "expired_at",
    OidcTransactionState.CANCELLED_TERMINAL: "cancelled_at",
}


def _to_record(row: Any) -> OidcTransactionRecord:
    initiating = row["initiating_user_id"]
    reason = row["failure_reason"]
    return OidcTransactionRecord(
        transaction_id=row["id"],
        provider=row["provider"],
        purpose=OidcTransactionPurpose(row["purpose"]),
        initiating_user_id=None if initiating is None else UserId(initiating),
        state=OidcTransactionState(row["state"]),
        state_hash=row["state_hash"],
        nonce_hash=row["nonce_hash"],
        user_agent_binding_hash=row["user_agent_binding_hash"],
        code_challenge=row["pkce_code_challenge"],
        redirect_target=row["post_auth_redirect_target"],
        created_at=row["created_at"],
        expires_at=row["expires_at"],
        claimed_at=row["claimed_at"],
        failure_reason=None if reason is None else OidcFailureReason(reason),
    )


_READ_COLUMNS = [
    column
    for column in oidc_auth_transactions_table.c
    if column.name != "pkce_code_verifier"  # never part of a read
]


class SqlAlchemyOidcTransactionRepository:
    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def create(
        self,
        *,
        transaction_id: uuid.UUID,
        provider: str,
        purpose: OidcTransactionPurpose,
        initiating_user_id: UserId | None,
        state_hash: str,
        nonce_hash: str,
        user_agent_binding_hash: str,
        code_verifier: str,
        code_challenge: str,
        redirect_target: str,
        created_at: datetime,
        expires_at: datetime,
        provenance_ref: str,
    ) -> None:
        self._connection.execute(
            sa.insert(oidc_auth_transactions_table).values(
                id=transaction_id,
                provider=provider,
                purpose=purpose.value,
                initiating_user_id=None if initiating_user_id is None else initiating_user_id.value,
                state=OidcTransactionState.PENDING.value,
                state_hash=state_hash,
                nonce_hash=nonce_hash,
                user_agent_binding_hash=user_agent_binding_hash,
                pkce_code_verifier=code_verifier,
                pkce_code_challenge=code_challenge,
                post_auth_redirect_target=redirect_target,
                created_at=created_at,
                expires_at=expires_at,
                provenance_ref=provenance_ref,
            )
        )

    def _one(self, condition: Any) -> OidcTransactionRecord | None:
        row = (
            self._connection.execute(sa.select(*_READ_COLUMNS).where(condition))
            .mappings()
            .one_or_none()
        )
        return None if row is None else _to_record(row)

    def get_by_state_hash(self, state_hash: str) -> OidcTransactionRecord | None:
        return self._one(oidc_auth_transactions_table.c.state_hash == state_hash)

    def get(self, transaction_id: uuid.UUID) -> OidcTransactionRecord | None:
        return self._one(oidc_auth_transactions_table.c.id == transaction_id)

    def claim(self, transaction_id: uuid.UUID, *, now: datetime) -> str | None:
        row = self._connection.execute(
            sa.text(
                "UPDATE oidc_auth_transactions AS t "
                "SET state = 'PROCESSING', claimed_at = :now, pkce_code_verifier = NULL, "
                "    verifier_unavailable_at = :now "
                "FROM (SELECT id, pkce_code_verifier FROM oidc_auth_transactions "
                "      WHERE id = :id FOR UPDATE) AS held "
                "WHERE t.id = held.id AND t.state = 'PENDING' AND t.expires_at > :now "
                "RETURNING held.pkce_code_verifier"
            ),
            {"id": transaction_id, "now": now},
        ).first()
        if row is None or row[0] is None:
            return None
        return str(row[0])

    def terminalize(
        self,
        transaction_id: uuid.UUID,
        *,
        from_state: OidcTransactionState,
        to_state: OidcTransactionState,
        reason: OidcFailureReason | None,
        now: datetime,
    ) -> bool:
        values: dict[str, Any] = {
            "state": to_state.value,
            _TERMINAL_TIMESTAMP[to_state]: now,
            "pkce_code_verifier": None,
            "verifier_unavailable_at": sa.func.coalesce(
                oidc_auth_transactions_table.c.verifier_unavailable_at, now
            ),
        }
        if reason is not None:
            values["failure_reason"] = reason.value
        result = self._connection.execute(
            sa.update(oidc_auth_transactions_table)
            .where(
                oidc_auth_transactions_table.c.id == transaction_id,
                oidc_auth_transactions_table.c.state == from_state.value,
            )
            .values(**values)
        )
        return result.rowcount == 1


__all__ = ["SqlAlchemyOidcTransactionRepository"]
