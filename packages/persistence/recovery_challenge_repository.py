"""Concrete `security.recovery.RecoveryChallengeRepository`, backed by
`recovery_challenges` (migration `a8c1e3f5b7d9`; WU-AUTH-12). Same conditional
consume discipline as the verification challenge (24 §33.7, §33.11)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

import sqlalchemy as sa
from security.recovery import RecoveryChallengeRecord, RecoveryType
from semantic_types.ids import UserId

from persistence.tables import recovery_challenges_table


def _to_record(row: Any) -> RecoveryChallengeRecord:
    return RecoveryChallengeRecord(
        recovery_id=row["id"],
        user_id=UserId(row["user_id"]),
        recovery_type=RecoveryType(row["recovery_type"]),
        issued_at=row["issued_at"],
        expires_at=row["expires_at"],
        verified_at=row["verified_at"],
        consumed_at=row["consumed_at"],
        revoked_at=row["revoked_at"],
        failed_attempts=int(row["failed_attempts"]),
    )


class SqlAlchemyRecoveryChallengeRepository:
    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def create(
        self,
        *,
        user_id: UserId,
        recovery_type: RecoveryType,
        challenge_hash: str,
        issued_at: datetime,
        expires_at: datetime,
        provenance_ref: str,
    ) -> RecoveryChallengeRecord:
        recovery_id = uuid.uuid4()
        self._connection.execute(
            sa.insert(recovery_challenges_table).values(
                id=recovery_id,
                user_id=user_id.value,
                recovery_type=recovery_type.value,
                challenge_hash=challenge_hash,
                issued_at=issued_at,
                expires_at=expires_at,
                verified_at=None,
                consumed_at=None,
                revoked_at=None,
                failed_attempts=0,
                provenance_ref=provenance_ref,
            )
        )
        return RecoveryChallengeRecord(
            recovery_id=recovery_id,
            user_id=user_id,
            recovery_type=recovery_type,
            issued_at=issued_at,
            expires_at=expires_at,
            verified_at=None,
            consumed_at=None,
            revoked_at=None,
            failed_attempts=0,
        )

    def _open(self, user_id: UserId, recovery_type: RecoveryType) -> Any:
        return sa.and_(
            recovery_challenges_table.c.user_id == user_id.value,
            recovery_challenges_table.c.recovery_type == recovery_type.value,
            recovery_challenges_table.c.consumed_at.is_(None),
            recovery_challenges_table.c.revoked_at.is_(None),
        )

    def latest_open(
        self, *, user_id: UserId, recovery_type: RecoveryType
    ) -> RecoveryChallengeRecord | None:
        row = (
            self._connection.execute(
                sa.select(recovery_challenges_table)
                .where(self._open(user_id, recovery_type))
                .order_by(recovery_challenges_table.c.issued_at.desc())
                .limit(1)
            )
            .mappings()
            .one_or_none()
        )
        return None if row is None else _to_record(row)

    def revoke_open(
        self, *, user_id: UserId, recovery_type: RecoveryType, revoked_at: datetime
    ) -> int:
        result = self._connection.execute(
            sa.update(recovery_challenges_table)
            .where(self._open(user_id, recovery_type))
            .values(revoked_at=revoked_at)
        )
        return int(result.rowcount)

    def get_for_update(self, recovery_id: uuid.UUID) -> RecoveryChallengeRecord | None:
        row = (
            self._connection.execute(
                sa.select(recovery_challenges_table)
                .where(recovery_challenges_table.c.id == recovery_id)
                .with_for_update()
            )
            .mappings()
            .one_or_none()
        )
        return None if row is None else _to_record(row)

    def verify_and_consume(
        self,
        recovery_id: uuid.UUID,
        *,
        challenge_hash: str,
        now: datetime,
        max_failed_attempts: int,
    ) -> RecoveryChallengeRecord | None:
        row = (
            self._connection.execute(
                sa.update(recovery_challenges_table)
                .where(
                    recovery_challenges_table.c.id == recovery_id,
                    recovery_challenges_table.c.consumed_at.is_(None),
                    recovery_challenges_table.c.revoked_at.is_(None),
                    recovery_challenges_table.c.expires_at > now,
                    recovery_challenges_table.c.failed_attempts < max_failed_attempts,
                    recovery_challenges_table.c.challenge_hash == challenge_hash,
                )
                .values(verified_at=now, consumed_at=now)
                .returning(recovery_challenges_table)
            )
            .mappings()
            .one_or_none()
        )
        return None if row is None else _to_record(row)

    def count_failed_attempt(self, recovery_id: uuid.UUID) -> int:
        row = self._connection.execute(
            sa.update(recovery_challenges_table)
            .where(
                recovery_challenges_table.c.id == recovery_id,
                recovery_challenges_table.c.consumed_at.is_(None),
            )
            .values(failed_attempts=recovery_challenges_table.c.failed_attempts + 1)
            .returning(recovery_challenges_table.c.failed_attempts)
        ).first()
        return 0 if row is None else int(row[0])


__all__ = ["SqlAlchemyRecoveryChallengeRepository"]
