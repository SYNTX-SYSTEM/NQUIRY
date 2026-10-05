"""AUTH WU-AUTH-20: auth_rate_limits — the login lockout boundary (24 §21.16, §22.3)

Revision ID: e3a5c7d9f1b4
Revises: d2f4a6b8c1e3
Create Date: 2026-10-05 00:00:00.000000

One row per (key_kind, key_hash): a sliding failure window and an optional
lock. Keys are SHA-256 digests of the normalized login address
(`CREDENTIAL`) and of the client address (`CLIENT`) — never the values
(24 §31.3), and a key exists for addresses that name no account, so the
boundary cannot disclose whether an account exists (24 §21.16). Rows are
evidence of pressure, not of identity: no foreign key, never deleted by
the runtime. Grants: auth_runtime RW (the login path), test_principal RWD.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "e3a5c7d9f1b4"
down_revision = "d2f4a6b8c1e3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "auth_rate_limits",
        sa.Column("key_kind", sa.Text(), nullable=False),
        sa.Column("key_hash", sa.Text(), nullable=False),
        sa.Column("window_started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("failures", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("key_kind", "key_hash", name="pk_auth_rate_limits"),
        sa.CheckConstraint("key_kind IN ('CREDENTIAL', 'CLIENT')", name="ck_auth_rate_limits_kind"),
        sa.CheckConstraint("failures >= 0", name="ck_auth_rate_limits_failures"),
        sa.CheckConstraint("length(key_hash) = 64", name="ck_auth_rate_limits_hash"),
    )
    op.execute("GRANT SELECT, INSERT, UPDATE ON auth_rate_limits TO auth_runtime")
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON auth_rate_limits TO test_principal")


def downgrade() -> None:
    op.execute("REVOKE ALL ON auth_rate_limits FROM test_principal")
    op.execute("REVOKE ALL ON auth_rate_limits FROM auth_runtime")
    op.drop_table("auth_rate_limits")
