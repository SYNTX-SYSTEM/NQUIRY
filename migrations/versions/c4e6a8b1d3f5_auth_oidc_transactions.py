"""AUTH WU-AUTH-05: oidc_auth_transactions (24 §11.3, §11.4, §22.2, §22.3, §22.6, §22.7)

Revision ID: c4e6a8b1d3f5
Revises: b3d5f7a9c2e6
Create Date: 2026-09-30 00:00:00.000000

The OIDC auth transaction: the temporary authoritative relation between a
provider login start and its callback. One row per start.

- Purpose LOGIN or ACCOUNT_LINK; an ACCOUNT_LINK row binds its initiating user
  (and only it does).
- State PENDING → PROCESSING → COMPLETED | FAILED_TERMINAL, or PENDING →
  EXPIRED | CANCELLED_TERMINAL | FAILED_TERMINAL. Every other transition, any
  change to a terminal row, and any change to the identity of a row (provider,
  purpose, initiating user, state hash, nonce hash, user-agent binding hash,
  code challenge, redirect target, creation, expiry, provenance) is refused by
  the trigger, for every writer. Each state requires exactly its timestamps.
- `state_hash`, `nonce_hash`, `user_agent_binding_hash`: SHA-256 of values
  that travel through the browser; never the values.
- `pkce_code_verifier`: the confidential, recoverable PKCE verifier. Present
  exactly while PENDING (CHECK); the claim statement returns and blanks it; it
  can never be set again (trigger). `verifier_unavailable_at` records when.
- `post_auth_redirect_target`: a local path only (24 §22.8; the validator
  that produces it is WU-AUTH-06).
- `failure_reason`: 24 §32.2's closed internal classes.

Cross-Workspace (no `workspace_id`, no RLS). No DB-principal GRANT here
(WU-AUTH-17). No existing row is read or changed. Starts empty (24 §28.4).
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "c4e6a8b1d3f5"
down_revision = "b3d5f7a9c2e6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "oidc_auth_transactions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("provider", sa.Text(), nullable=False),
        sa.Column("purpose", sa.Text(), nullable=False),
        sa.Column(
            "initiating_user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=True
        ),
        sa.Column("state", sa.Text(), nullable=False),
        sa.Column("state_hash", sa.Text(), nullable=False, unique=True),
        sa.Column("nonce_hash", sa.Text(), nullable=False),
        sa.Column("user_agent_binding_hash", sa.Text(), nullable=False),
        sa.Column("pkce_code_verifier", sa.Text(), nullable=True),
        sa.Column("pkce_code_challenge", sa.Text(), nullable=False),
        sa.Column("post_auth_redirect_target", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("claimed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_terminal_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expired_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verifier_unavailable_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("provenance_ref", sa.Text(), nullable=False),
        sa.CheckConstraint("provider <> ''", name="ck_oidc_auth_transactions_provider"),
        sa.CheckConstraint(
            "purpose IN ('LOGIN', 'ACCOUNT_LINK')", name="ck_oidc_auth_transactions_purpose"
        ),
        sa.CheckConstraint(
            "(purpose = 'ACCOUNT_LINK') = (initiating_user_id IS NOT NULL)",
            name="ck_oidc_auth_transactions_initiating_user",
        ),
        sa.CheckConstraint(
            "state IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED_TERMINAL', 'EXPIRED', "
            "'CANCELLED_TERMINAL')",
            name="ck_oidc_auth_transactions_state",
        ),
        sa.CheckConstraint(
            "(pkce_code_verifier IS NOT NULL) = (state = 'PENDING')",
            name="ck_oidc_auth_transactions_verifier_pending",
        ),
        sa.CheckConstraint(
            "post_auth_redirect_target ~ '^/([^/].*)?$'",
            name="ck_oidc_auth_transactions_local_redirect",
        ),
        sa.CheckConstraint(
            "failure_reason IS NULL OR failure_reason IN ('MISSING_TRANSACTION', 'EXPIRED_TRANSACTION', 'INVALID_STATE', 'USER_AGENT_BINDING_MISSING', 'USER_AGENT_BINDING_MISMATCH', 'PURPOSE_MISMATCH', 'INITIATING_USER_MISMATCH', 'ALREADY_PROCESSING', 'ALREADY_COMPLETED', 'CANCELLED_TERMINAL', 'FAILED_TERMINAL', 'EXPIRED', 'MISSING_PKCE_VERIFIER', 'TOKEN_EXCHANGE_REJECTED', 'TOKEN_EXCHANGE_OUTCOME_UNCERTAIN', 'INVALID_ID_TOKEN_SIGNATURE', 'INVALID_ISSUER', 'INVALID_AUDIENCE', 'EXPIRED_ID_TOKEN', 'INVALID_NONCE', 'PROVIDER_SUBJECT_MISSING', 'PROVIDER_SUBJECT_COLLISION', 'PROVIDER_ACCESS_DENIED', 'USER_CANCEL', 'PROVIDER_FAILURE', 'MALFORMED_CALLBACK', 'REDIRECT_TARGET_REJECTED', 'ACCOUNT_CREATION_POLICY_UNRESOLVED', 'ACCOUNT_LINK_AUTHORITY_FAILURE', 'LOCAL_EFFECT_FAILURE')",
            name="ck_oidc_auth_transactions_failure_reason",
        ),
        sa.CheckConstraint("(state = 'PENDING' AND claimed_at IS NULL AND completed_at IS NULL AND failed_terminal_at IS NULL AND expired_at IS NULL AND cancelled_at IS NULL AND verifier_unavailable_at IS NULL AND failure_reason IS NULL) OR (state = 'PROCESSING' AND claimed_at IS NOT NULL AND completed_at IS NULL AND failed_terminal_at IS NULL AND expired_at IS NULL AND cancelled_at IS NULL AND verifier_unavailable_at IS NOT NULL AND failure_reason IS NULL) OR (state = 'COMPLETED' AND claimed_at IS NOT NULL AND completed_at IS NOT NULL AND failed_terminal_at IS NULL AND expired_at IS NULL AND cancelled_at IS NULL AND verifier_unavailable_at IS NOT NULL AND failure_reason IS NULL) OR (state = 'FAILED_TERMINAL' AND failed_terminal_at IS NOT NULL AND completed_at IS NULL AND expired_at IS NULL AND cancelled_at IS NULL AND verifier_unavailable_at IS NOT NULL AND failure_reason IS NOT NULL) OR (state = 'EXPIRED' AND claimed_at IS NULL AND expired_at IS NOT NULL AND completed_at IS NULL AND failed_terminal_at IS NULL AND cancelled_at IS NULL AND verifier_unavailable_at IS NOT NULL AND failure_reason IS NULL) OR (state = 'CANCELLED_TERMINAL' AND claimed_at IS NULL AND cancelled_at IS NOT NULL AND completed_at IS NULL AND failed_terminal_at IS NULL AND expired_at IS NULL AND verifier_unavailable_at IS NOT NULL AND failure_reason IS NOT NULL)", name="ck_oidc_auth_transactions_state_timestamps"),
        sa.CheckConstraint("expires_at > created_at", name="ck_oidc_auth_transactions_expiry"),
        sa.CheckConstraint("provenance_ref <> ''", name="ck_oidc_auth_transactions_provenance"),
    )
    op.create_index(
        "ix_oidc_auth_transactions_initiating_user_id",
        "oidc_auth_transactions",
        ["initiating_user_id"],
    )
    op.execute(
        """
        CREATE FUNCTION trg_oidc_auth_transactions_transition() RETURNS trigger AS $$
        BEGIN
            IF OLD.state IN ('COMPLETED', 'FAILED_TERMINAL', 'EXPIRED', 'CANCELLED_TERMINAL') THEN
                RAISE EXCEPTION
                    'OIDC transaction % is % (terminal): it never changes again '
                    '(24 section 11.4)', OLD.id, OLD.state;
            END IF;
            IF NEW.id IS DISTINCT FROM OLD.id
               OR NEW.provider IS DISTINCT FROM OLD.provider
               OR NEW.purpose IS DISTINCT FROM OLD.purpose
               OR NEW.initiating_user_id IS DISTINCT FROM OLD.initiating_user_id
               OR NEW.state_hash IS DISTINCT FROM OLD.state_hash
               OR NEW.nonce_hash IS DISTINCT FROM OLD.nonce_hash
               OR NEW.user_agent_binding_hash IS DISTINCT FROM OLD.user_agent_binding_hash
               OR NEW.pkce_code_challenge IS DISTINCT FROM OLD.pkce_code_challenge
               OR NEW.post_auth_redirect_target IS DISTINCT FROM OLD.post_auth_redirect_target
               OR NEW.created_at IS DISTINCT FROM OLD.created_at
               OR NEW.expires_at IS DISTINCT FROM OLD.expires_at
               OR NEW.provenance_ref IS DISTINCT FROM OLD.provenance_ref THEN
                RAISE EXCEPTION 'OIDC transaction identity is immutable';
            END IF;
            IF NEW.state IS DISTINCT FROM OLD.state AND NOT (
                (OLD.state = 'PENDING' AND NEW.state IN
                    ('PROCESSING', 'EXPIRED', 'CANCELLED_TERMINAL', 'FAILED_TERMINAL'))
                OR (OLD.state = 'PROCESSING' AND NEW.state IN ('COMPLETED', 'FAILED_TERMINAL'))
            ) THEN
                RAISE EXCEPTION
                    'illegal OIDC transaction transition % -> % (24 section 11.4)',
                    OLD.state, NEW.state;
            END IF;
            IF NEW.pkce_code_verifier IS NOT NULL
               AND NEW.pkce_code_verifier IS DISTINCT FROM OLD.pkce_code_verifier THEN
                RAISE EXCEPTION 'the PKCE verifier can be consumed, never set again';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_oidc_auth_transactions_transition
        BEFORE UPDATE ON oidc_auth_transactions
        FOR EACH ROW EXECUTE FUNCTION trg_oidc_auth_transactions_transition();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER trg_oidc_auth_transactions_transition ON oidc_auth_transactions")
    op.execute("DROP FUNCTION trg_oidc_auth_transactions_transition()")
    op.drop_index(
        "ix_oidc_auth_transactions_initiating_user_id", table_name="oidc_auth_transactions"
    )
    op.drop_table("oidc_auth_transactions")
