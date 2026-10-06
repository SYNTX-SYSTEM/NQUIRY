"""users.established_at + REGISTRATION rate-limit key (WU-AUTH-22; HD-AUTH-13).

HD-AUTH-13 (2026-10-07): a person may create a NQUIRY identity with a local
e-mail address and password; the identity establishes nothing but itself and is
not established for normal use until its address is verified through the
existing verified-email relation. The system therefore distinguishes an
identity that EXISTS from one that is ESTABLISHED:

* `users.established_at` (timestamptz, NULL = pending). Every identity that
  exists before this migration was created by an established path — the host
  operator (HD-28) or a verified provider credential (HD-AUTH-08) — so the
  backfill sets `established_at = created_at` for all of them; nothing changes
  for them.
* `auth_rate_limits.key_kind` admits `REGISTRATION` (per-client window over
  self-registration attempts; WU-AUTH-20's table, one more kind).

Grants: unchanged — table-level privileges of `users` / `auth_rate_limits`
cover the new column and value (auth_runtime RW, test_principal RWD).

Revision ID: a7c9e1b3d5f7
Revises: e3a5c7d9f1b4
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "a7c9e1b3d5f7"
down_revision = "e3a5c7d9f1b4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("established_at", sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE users SET established_at = created_at WHERE established_at IS NULL")
    op.drop_constraint("ck_auth_rate_limits_kind", "auth_rate_limits", type_="check")
    op.create_check_constraint(
        "ck_auth_rate_limits_kind",
        "auth_rate_limits",
        "key_kind IN ('CREDENTIAL', 'CLIENT', 'REGISTRATION')",
    )


def downgrade() -> None:
    op.execute("DELETE FROM auth_rate_limits WHERE key_kind = 'REGISTRATION'")
    op.drop_constraint("ck_auth_rate_limits_kind", "auth_rate_limits", type_="check")
    op.create_check_constraint(
        "ck_auth_rate_limits_kind", "auth_rate_limits", "key_kind IN ('CREDENTIAL', 'CLIENT')"
    )
    op.drop_column("users", "established_at")
