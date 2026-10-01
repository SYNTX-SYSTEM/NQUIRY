"""AUTH WU-AUTH-12: recovery_challenges; CREDENTIAL_RESET session reason (24 §17.3, §19.6, §22.2)

Revision ID: a8c1e3f5b7d9
Revises: f7b9d1e3a5c8
Create Date: 2026-10-01 00:00:00.000000

`recovery_challenges`: temporary, proof-bearing recovery material (type
PASSWORD_RESET). Not an authentication method (24 §17.2, §22.5): its own
relation, never listed as a method. Hash only (UNIQUE); issued to one
identity; expires; verified and consumed together, at most once; may be
revoked (superseded); counts failed attempts. Triggers: identity columns
immutable; consumed or revoked is terminal; attempts never decrease.

`local_auth_sessions.revoked_reason` gains CREDENTIAL_RESET (24 §15.7,
§19.6: a credential reset revokes dependent sessions).

Cross-Workspace (no `workspace_id`, no RLS). No DB-principal GRANT here
(WU-AUTH-17). Starts empty; no existing row is read or changed.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "a8c1e3f5b7d9"
down_revision = "f7b9d1e3a5c8"
branch_labels = None
depends_on = None

_REASONS_BEFORE = (
    "'LOGOUT', 'ALL_SESSIONS_LOGOUT', 'SESSION_REVOKED', 'METHOD_REVOKED', "
    "'ACCOUNT_DISABLED', 'ROTATED'"
)
_REASONS_AFTER = _REASONS_BEFORE + ", 'CREDENTIAL_RESET'"


def _replace_reason_check(reasons: str) -> None:
    op.drop_constraint("ck_local_auth_sessions_revoked_reason", "local_auth_sessions", type_="check")
    op.create_check_constraint(
        "ck_local_auth_sessions_revoked_reason",
        "local_auth_sessions",
        f"revoked_reason IS NULL OR revoked_reason IN ({reasons})",
    )


def upgrade() -> None:
    op.create_table(
        "recovery_challenges",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
        ),
        sa.Column("recovery_type", sa.Text(), nullable=False),
        sa.Column("challenge_hash", sa.Text(), nullable=False, unique=True),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("provenance_ref", sa.Text(), nullable=False),
        sa.CheckConstraint("recovery_type IN ('PASSWORD_RESET')", name="ck_recovery_challenges_type"),
        sa.CheckConstraint("expires_at > issued_at", name="ck_recovery_challenges_expiry"),
        sa.CheckConstraint("failed_attempts >= 0", name="ck_recovery_challenges_attempts"),
        sa.CheckConstraint(
            "(verified_at IS NULL) = (consumed_at IS NULL)",
            name="ck_recovery_challenges_verified_consumed",
        ),
        sa.CheckConstraint(
            "consumed_at IS NULL OR revoked_at IS NULL", name="ck_recovery_challenges_one_closure"
        ),
        sa.CheckConstraint("provenance_ref <> ''", name="ck_recovery_challenges_provenance"),
    )
    op.create_index(
        "ix_recovery_challenges_user", "recovery_challenges", ["user_id", "issued_at"]
    )
    op.execute(
        """
        CREATE FUNCTION trg_recovery_challenges_transition() RETURNS trigger AS $$
        BEGIN
            IF OLD.consumed_at IS NOT NULL OR OLD.revoked_at IS NOT NULL THEN
                RAISE EXCEPTION
                    'recovery challenge % is consumed or revoked: terminal (24 section 17.3)', OLD.id;
            END IF;
            IF NEW.id IS DISTINCT FROM OLD.id
               OR NEW.user_id IS DISTINCT FROM OLD.user_id
               OR NEW.recovery_type IS DISTINCT FROM OLD.recovery_type
               OR NEW.challenge_hash IS DISTINCT FROM OLD.challenge_hash
               OR NEW.issued_at IS DISTINCT FROM OLD.issued_at
               OR NEW.expires_at IS DISTINCT FROM OLD.expires_at
               OR NEW.provenance_ref IS DISTINCT FROM OLD.provenance_ref THEN
                RAISE EXCEPTION 'recovery challenge identity is immutable';
            END IF;
            IF NEW.failed_attempts < OLD.failed_attempts THEN
                RAISE EXCEPTION 'failed_attempts never decreases';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_recovery_challenges_transition
        BEFORE UPDATE ON recovery_challenges
        FOR EACH ROW EXECUTE FUNCTION trg_recovery_challenges_transition();
        """
    )
    _replace_reason_check(_REASONS_AFTER)


def downgrade() -> None:
    op.execute(
        "UPDATE local_auth_sessions SET revoked_reason = 'METHOD_REVOKED' "
        "WHERE revoked_reason = 'CREDENTIAL_RESET'"
    )
    _replace_reason_check(_REASONS_BEFORE)
    op.execute("DROP TRIGGER trg_recovery_challenges_transition ON recovery_challenges")
    op.execute("DROP FUNCTION trg_recovery_challenges_transition()")
    op.drop_index("ix_recovery_challenges_user", table_name="recovery_challenges")
    op.drop_table("recovery_challenges")
