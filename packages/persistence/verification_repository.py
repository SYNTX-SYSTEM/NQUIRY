"""Concrete `security.verification` repositories, backed by `auth_challenges`
and `verified_emails` (migration `f7b9d1e3a5c8`; WU-AUTH-11).

`consume` is the single conditional write of a verification commit (24
§33.11): the row is locked and moved to consumed only if it is still open,
unexpired, under the attempt limit and the presented token's hash matches.
Two parallel completions are serialized on the row; one wins at most.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

import sqlalchemy as sa
from security.verification import (
    ChallengeRecord,
    ChallengeType,
    VerificationMethod,
    VerifiedEmail,
)
from semantic_types.ids import UserId

from persistence.tables import auth_challenges_table, verified_emails_table


def _to_challenge(row: Any) -> ChallengeRecord:
    return ChallengeRecord(
        challenge_id=row["id"],
        challenge_type=ChallengeType(row["challenge_type"]),
        user_id=UserId(row["user_id"]),
        email=row["email"],
        issued_at=row["issued_at"],
        expires_at=row["expires_at"],
        consumed_at=row["consumed_at"],
        revoked_at=row["revoked_at"],
        failed_attempts=int(row["failed_attempts"]),
    )


def _to_verified(row: Any) -> VerifiedEmail:
    return VerifiedEmail(
        relation_id=row["id"],
        user_id=UserId(row["user_id"]),
        email=row["email"],
        verified_at=row["verified_at"],
        verification_method=VerificationMethod(row["verification_method"]),
        superseded_at=row["superseded_at"],
        revoked_at=row["revoked_at"],
    )


class SqlAlchemyChallengeRepository:
    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def create(
        self,
        *,
        challenge_type: ChallengeType,
        user_id: UserId,
        email: str,
        token_hash: str,
        issued_at: datetime,
        expires_at: datetime,
        provenance_ref: str,
    ) -> ChallengeRecord:
        challenge_id = uuid.uuid4()
        self._connection.execute(
            sa.insert(auth_challenges_table).values(
                id=challenge_id,
                challenge_type=challenge_type.value,
                user_id=user_id.value,
                email=email,
                token_hash=token_hash,
                issued_at=issued_at,
                expires_at=expires_at,
                consumed_at=None,
                revoked_at=None,
                failed_attempts=0,
                provenance_ref=provenance_ref,
            )
        )
        return ChallengeRecord(
            challenge_id=challenge_id,
            challenge_type=challenge_type,
            user_id=user_id,
            email=email,
            issued_at=issued_at,
            expires_at=expires_at,
            consumed_at=None,
            revoked_at=None,
            failed_attempts=0,
        )

    def _open(self, challenge_type: ChallengeType, user_id: UserId, email: str) -> Any:
        return sa.and_(
            auth_challenges_table.c.challenge_type == challenge_type.value,
            auth_challenges_table.c.user_id == user_id.value,
            auth_challenges_table.c.email == email,
            auth_challenges_table.c.consumed_at.is_(None),
            auth_challenges_table.c.revoked_at.is_(None),
        )

    def latest_open(
        self, *, challenge_type: ChallengeType, user_id: UserId, email: str
    ) -> ChallengeRecord | None:
        row = (
            self._connection.execute(
                sa.select(auth_challenges_table)
                .where(self._open(challenge_type, user_id, email))
                .order_by(auth_challenges_table.c.issued_at.desc())
                .limit(1)
            )
            .mappings()
            .one_or_none()
        )
        return None if row is None else _to_challenge(row)

    def revoke_open(
        self, *, challenge_type: ChallengeType, user_id: UserId, email: str, revoked_at: datetime
    ) -> int:
        result = self._connection.execute(
            sa.update(auth_challenges_table)
            .where(self._open(challenge_type, user_id, email))
            .values(revoked_at=revoked_at)
        )
        return int(result.rowcount)

    def get_for_update(self, challenge_id: uuid.UUID) -> ChallengeRecord | None:
        row = (
            self._connection.execute(
                sa.select(auth_challenges_table)
                .where(auth_challenges_table.c.id == challenge_id)
                .with_for_update()
            )
            .mappings()
            .one_or_none()
        )
        return None if row is None else _to_challenge(row)

    def consume(
        self,
        challenge_id: uuid.UUID,
        *,
        token_hash: str,
        now: datetime,
        max_failed_attempts: int,
    ) -> ChallengeRecord | None:
        row = (
            self._connection.execute(
                sa.update(auth_challenges_table)
                .where(
                    auth_challenges_table.c.id == challenge_id,
                    auth_challenges_table.c.consumed_at.is_(None),
                    auth_challenges_table.c.revoked_at.is_(None),
                    auth_challenges_table.c.expires_at > now,
                    auth_challenges_table.c.failed_attempts < max_failed_attempts,
                    auth_challenges_table.c.token_hash == token_hash,
                )
                .values(consumed_at=now)
                .returning(auth_challenges_table)
            )
            .mappings()
            .one_or_none()
        )
        return None if row is None else _to_challenge(row)

    def count_failed_attempt(self, challenge_id: uuid.UUID) -> int:
        row = self._connection.execute(
            sa.update(auth_challenges_table)
            .where(
                auth_challenges_table.c.id == challenge_id,
                auth_challenges_table.c.consumed_at.is_(None),
            )
            .values(failed_attempts=auth_challenges_table.c.failed_attempts + 1)
            .returning(auth_challenges_table.c.failed_attempts)
        ).first()
        return 0 if row is None else int(row[0])


class SqlAlchemyVerifiedEmailRepository:
    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def _active(self) -> Any:
        return sa.and_(
            verified_emails_table.c.superseded_at.is_(None),
            verified_emails_table.c.revoked_at.is_(None),
        )

    def active_for_email(self, email: str) -> VerifiedEmail | None:
        row = (
            self._connection.execute(
                sa.select(verified_emails_table).where(
                    verified_emails_table.c.email == email, self._active()
                )
            )
            .mappings()
            .one_or_none()
        )
        return None if row is None else _to_verified(row)

    def list_for_user(self, user_id: UserId) -> tuple[VerifiedEmail, ...]:
        rows = (
            self._connection.execute(
                sa.select(verified_emails_table)
                .where(verified_emails_table.c.user_id == user_id.value)
                .order_by(verified_emails_table.c.verified_at)
            )
            .mappings()
            .all()
        )
        return tuple(_to_verified(row) for row in rows)

    def supersede_active(self, *, user_id: UserId, email: str, superseded_at: datetime) -> int:
        result = self._connection.execute(
            sa.update(verified_emails_table)
            .where(
                verified_emails_table.c.user_id == user_id.value,
                verified_emails_table.c.email == email,
                self._active(),
            )
            .values(superseded_at=superseded_at)
        )
        return int(result.rowcount)

    def create(
        self,
        *,
        user_id: UserId,
        email: str,
        verified_at: datetime,
        verification_method: VerificationMethod,
        provenance_ref: str,
    ) -> VerifiedEmail:
        relation_id = uuid.uuid4()
        self._connection.execute(
            sa.insert(verified_emails_table).values(
                id=relation_id,
                user_id=user_id.value,
                email=email,
                verified_at=verified_at,
                verification_method=verification_method.value,
                superseded_at=None,
                revoked_at=None,
                provenance_ref=provenance_ref,
            )
        )
        return VerifiedEmail(
            relation_id=relation_id,
            user_id=user_id,
            email=email,
            verified_at=verified_at,
            verification_method=verification_method,
            superseded_at=None,
            revoked_at=None,
        )


__all__ = ["SqlAlchemyChallengeRepository", "SqlAlchemyVerifiedEmailRepository"]
