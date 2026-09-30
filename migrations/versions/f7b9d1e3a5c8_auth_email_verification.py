"""AUTH WU-AUTH-11: auth_challenges and verified_emails (24 §13.9, §16.1, §22.2, §22.3)

Revision ID: f7b9d1e3a5c8
Revises: e6a8c1d3f5b9
Create Date: 2026-10-01 00:00:00.000000

`auth_challenges`: temporary, proof-bearing challenges (type EMAIL_VERIFICATION
here; never an authentication method, 24 §13.2). Only the SHA-256 of the
token is stored (UNIQUE). A challenge is issued to one identity for one
address, expires, is consumed at most once, may be revoked (superseded), and
counts failed attempts. Triggers: identity columns immutable; a consumed or
revoked challenge never changes again; `failed_attempts` never decreases.

`verified_emails`: the persisted relation created only after a challenge
proof (24 §19.4). At most ONE active relation per address across all
identities (partial unique index; 24 §14.5 collision boundary); the same
identity re-verifying supersedes its earlier relation. Triggers: identity
columns immutable; `superseded_at` / `revoked_at` are set once.

Cross-Workspace (no `workspace_id`, no RLS). No DB-principal GRANT here
(WU-AUTH-17). Both tables start empty; no existing row is read or changed.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "f7b9d1e3a5c8"
down_revision = "e6a8c1d3f5b9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "auth_challenges",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("challenge_type", sa.Text(), nullable=False),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
        ),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("token_hash", sa.Text(), nullable=False, unique=True),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("provenance_ref", sa.Text(), nullable=False),
        sa.CheckConstraint(
            "challenge_type IN ('EMAIL_VERIFICATION')", name="ck_auth_challenges_type"
        ),
        sa.CheckConstraint("email = lower(email) AND email <> ''", name="ck_auth_challenges_email"),
        sa.CheckConstraint("expires_at > issued_at", name="ck_auth_challenges_expiry"),
        sa.CheckConstraint("failed_attempts >= 0", name="ck_auth_challenges_attempts"),
        sa.CheckConstraint(
            "consumed_at IS NULL OR revoked_at IS NULL", name="ck_auth_challenges_one_closure"
        ),
        sa.CheckConstraint("provenance_ref <> ''", name="ck_auth_challenges_provenance"),
    )
    op.create_index(
        "ix_auth_challenges_user_email", "auth_challenges", ["user_id", "email", "issued_at"]
    )
    op.execute(
        """
        CREATE FUNCTION trg_auth_challenges_transition() RETURNS trigger AS $$
        BEGIN
            IF OLD.consumed_at IS NOT NULL OR OLD.revoked_at IS NOT NULL THEN
                RAISE EXCEPTION
                    'challenge % is consumed or revoked: terminal (24 section 16.1)', OLD.id;
            END IF;
            IF NEW.id IS DISTINCT FROM OLD.id
               OR NEW.challenge_type IS DISTINCT FROM OLD.challenge_type
               OR NEW.user_id IS DISTINCT FROM OLD.user_id
               OR NEW.email IS DISTINCT FROM OLD.email
               OR NEW.token_hash IS DISTINCT FROM OLD.token_hash
               OR NEW.issued_at IS DISTINCT FROM OLD.issued_at
               OR NEW.expires_at IS DISTINCT FROM OLD.expires_at
               OR NEW.provenance_ref IS DISTINCT FROM OLD.provenance_ref THEN
                RAISE EXCEPTION 'challenge identity is immutable';
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
        CREATE TRIGGER trg_auth_challenges_transition
        BEFORE UPDATE ON auth_challenges
        FOR EACH ROW EXECUTE FUNCTION trg_auth_challenges_transition();
        """
    )
    op.create_table(
        "verified_emails",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
        ),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("verification_method", sa.Text(), nullable=False),
        sa.Column("superseded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("provenance_ref", sa.Text(), nullable=False),
        sa.CheckConstraint(
            "verification_method IN ('EMAIL_CHALLENGE')", name="ck_verified_emails_method"
        ),
        sa.CheckConstraint("email = lower(email) AND email <> ''", name="ck_verified_emails_email"),
        sa.CheckConstraint("provenance_ref <> ''", name="ck_verified_emails_provenance"),
    )
    op.create_index("ix_verified_emails_user_id", "verified_emails", ["user_id"])
    op.create_index(
        "uq_verified_emails_one_active_per_address",
        "verified_emails",
        ["email"],
        unique=True,
        postgresql_where=sa.text("superseded_at IS NULL AND revoked_at IS NULL"),
    )
    op.execute(
        """
        CREATE FUNCTION trg_verified_emails_transition() RETURNS trigger AS $$
        BEGIN
            IF NEW.id IS DISTINCT FROM OLD.id
               OR NEW.user_id IS DISTINCT FROM OLD.user_id
               OR NEW.email IS DISTINCT FROM OLD.email
               OR NEW.verified_at IS DISTINCT FROM OLD.verified_at
               OR NEW.verification_method IS DISTINCT FROM OLD.verification_method
               OR NEW.provenance_ref IS DISTINCT FROM OLD.provenance_ref THEN
                RAISE EXCEPTION 'verified email identity is immutable';
            END IF;
            IF (OLD.superseded_at IS NOT NULL AND NEW.superseded_at IS DISTINCT FROM OLD.superseded_at)
               OR (OLD.revoked_at IS NOT NULL AND NEW.revoked_at IS DISTINCT FROM OLD.revoked_at) THEN
                RAISE EXCEPTION 'a superseded or revoked verified email stays so';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_verified_emails_transition
        BEFORE UPDATE ON verified_emails
        FOR EACH ROW EXECUTE FUNCTION trg_verified_emails_transition();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER trg_verified_emails_transition ON verified_emails")
    op.execute("DROP FUNCTION trg_verified_emails_transition()")
    op.drop_index("uq_verified_emails_one_active_per_address", table_name="verified_emails")
    op.drop_index("ix_verified_emails_user_id", table_name="verified_emails")
    op.drop_table("verified_emails")
    op.execute("DROP TRIGGER trg_auth_challenges_transition ON auth_challenges")
    op.execute("DROP FUNCTION trg_auth_challenges_transition()")
    op.drop_index("ix_auth_challenges_user_email", table_name="auth_challenges")
    op.drop_table("auth_challenges")
