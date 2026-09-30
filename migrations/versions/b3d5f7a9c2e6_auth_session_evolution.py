"""AUTH WU-AUTH-04: session traceability and revocation reason (24 §15.2, §15.3, §15.7)

Revision ID: b3d5f7a9c2e6
Revises: a2c4e6f8b1d3
Create Date: 2026-09-30 00:00:00.000000

`local_auth_sessions` gains:

- `authentication_method_id` (nullable; composite FK with `user_id` to
  `authentication_methods (id, user_id)`): the method that produced the session.
- `proof_provenance` (nullable text): the proof behind a session that no
  method produced (24 §15.2 "proof provenance where auth method is not
  directly applicable"). CHECK: one of the two is present.
- `revoked_reason` (nullable text, closed vocabulary): why a session was
  revoked. CHECK: present exactly when `revoked_at` is.

A BEFORE UPDATE trigger makes the session an evidence record: id, user, token
hash, issue time, method and provenance never change; a revoked session never
changes again; `expires_at` may be shortened, never extended.

BACKFILL (24 §28.3 "Do not invalidate current sessions unexpectedly"). Every
session before this revision was created by `/auth/login`, that is by the
user's one local password credential: it is attributed to that credential's
method. A session whose user has no credential is kept and marked
`migration:b3d5f7a9c2e6:no-local-credential`. Every already revoked session
was revoked by `/auth/logout`, the only revocation that existed: `LOGOUT`.
No session is revoked, shortened or deleted by this migration.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "b3d5f7a9c2e6"
down_revision = "a2c4e6f8b1d3"
branch_labels = None
depends_on = None

_REASONS = (
    "'LOGOUT', 'ALL_SESSIONS_LOGOUT', 'SESSION_REVOKED', 'METHOD_REVOKED', "
    "'ACCOUNT_DISABLED', 'ROTATED'"
)


def upgrade() -> None:
    op.add_column(
        "local_auth_sessions", sa.Column("authentication_method_id", sa.Uuid(), nullable=True)
    )
    op.add_column("local_auth_sessions", sa.Column("proof_provenance", sa.Text(), nullable=True))
    op.add_column("local_auth_sessions", sa.Column("revoked_reason", sa.Text(), nullable=True))
    op.execute(
        """
        UPDATE local_auth_sessions s
        SET authentication_method_id = c.authentication_method_id
        FROM local_auth_credentials c
        WHERE c.user_id = s.user_id
        """
    )
    op.execute(
        """
        UPDATE local_auth_sessions
        SET proof_provenance = 'migration:b3d5f7a9c2e6:no-local-credential'
        WHERE authentication_method_id IS NULL
        """
    )
    op.execute(
        "UPDATE local_auth_sessions SET revoked_reason = 'LOGOUT' WHERE revoked_at IS NOT NULL"
    )
    op.create_foreign_key(
        "fk_local_auth_sessions_method_same_user",
        "local_auth_sessions",
        "authentication_methods",
        ["authentication_method_id", "user_id"],
        ["id", "user_id"],
        ondelete="RESTRICT",
    )
    op.create_check_constraint(
        "ck_local_auth_sessions_method_or_proof",
        "local_auth_sessions",
        "authentication_method_id IS NOT NULL "
        "OR (proof_provenance IS NOT NULL AND proof_provenance <> '')",
    )
    op.create_check_constraint(
        "ck_local_auth_sessions_revoked_reason",
        "local_auth_sessions",
        f"revoked_reason IS NULL OR revoked_reason IN ({_REASONS})",
    )
    op.create_check_constraint(
        "ck_local_auth_sessions_revocation_has_reason",
        "local_auth_sessions",
        "(revoked_at IS NULL) = (revoked_reason IS NULL)",
    )
    op.create_index(
        "ix_local_auth_sessions_authentication_method_id",
        "local_auth_sessions",
        ["authentication_method_id"],
    )
    op.execute(
        """
        CREATE FUNCTION trg_local_auth_sessions_transition() RETURNS trigger AS $$
        BEGIN
            IF OLD.revoked_at IS NOT NULL THEN
                RAISE EXCEPTION
                    'session % is revoked: terminal, kept as evidence (24 section 18.3)', OLD.id;
            END IF;
            IF NEW.id IS DISTINCT FROM OLD.id
               OR NEW.user_id IS DISTINCT FROM OLD.user_id
               OR NEW.session_token_hash IS DISTINCT FROM OLD.session_token_hash
               OR NEW.issued_at IS DISTINCT FROM OLD.issued_at
               OR NEW.authentication_method_id IS DISTINCT FROM OLD.authentication_method_id
               OR NEW.proof_provenance IS DISTINCT FROM OLD.proof_provenance THEN
                RAISE EXCEPTION
                    'session identity (id, user_id, session_token_hash, issued_at, '
                    'authentication_method_id, proof_provenance) is immutable';
            END IF;
            IF NEW.expires_at > OLD.expires_at THEN
                RAISE EXCEPTION 'a session cannot be extended';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_local_auth_sessions_transition
        BEFORE UPDATE ON local_auth_sessions
        FOR EACH ROW EXECUTE FUNCTION trg_local_auth_sessions_transition();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER trg_local_auth_sessions_transition ON local_auth_sessions")
    op.execute("DROP FUNCTION trg_local_auth_sessions_transition()")
    op.drop_index(
        "ix_local_auth_sessions_authentication_method_id", table_name="local_auth_sessions"
    )
    op.drop_constraint(
        "ck_local_auth_sessions_revocation_has_reason", "local_auth_sessions", type_="check"
    )
    op.drop_constraint(
        "ck_local_auth_sessions_revoked_reason", "local_auth_sessions", type_="check"
    )
    op.drop_constraint(
        "ck_local_auth_sessions_method_or_proof", "local_auth_sessions", type_="check"
    )
    op.drop_constraint(
        "fk_local_auth_sessions_method_same_user", "local_auth_sessions", type_="foreignkey"
    )
    op.drop_column("local_auth_sessions", "revoked_reason")
    op.drop_column("local_auth_sessions", "proof_provenance")
    op.drop_column("local_auth_sessions", "authentication_method_id")
