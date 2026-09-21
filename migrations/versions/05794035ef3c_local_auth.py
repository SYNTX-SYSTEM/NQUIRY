"""local auth credentials and sessions

Revision ID: 05794035ef3c
Revises: 047bdf9bc528
Create Date: 2026-09-21 00:00:00.000000

Local login field (docs/architecture/18_LOCAL_AUTHENTICATION_ADAPTER.md).
Closes the disclosed GAP-14-001 weakness recorded in
`docs/architecture/17_LIVE_APPLICATION_RUNTIME_MATERIALIZATION.md`
("no cryptographic verification occurs anywhere in this path"):
`application.http_dispatch.resolve_actor` trusted a bare
`x-nquiry-actor-user-id` request header at face value. This migration
adds the two real, DB-persisted tables a genuine local login needs.
14 section 32's own authorized pair is "pluggable OIDC adapter plus
deterministic test adapter `[IMPLEMENTATION CHOICE]`" -- this is the
"deterministic test adapter" half, hardened into a real, browser-usable
local login. GAP-14-001 itself (real OIDC provider selection) remains
open; this migration does not add, touch, or reference an external
identity provider.

Tables created:

- `local_auth_credentials` -- one password credential per `users` row
  (`user_id` UNIQUE). `password_hash` is PBKDF2-HMAC-SHA256, random
  per-row salt (`packages/security/local_auth.py::hash_password`),
  never the plaintext. This is deliberately NOT a column added to
  `users` itself -- `users` is 14 section 32's own canonical identity
  Thing (already disclosed as "role/organization_id/preferences are
  absent from users" by design, see `72e4c8ea6772`'s own docstring);
  mixing authentication-secret material into it would blur the same
  IDENTITY != AUTHORITY (and here, IDENTITY != CREDENTIAL) separation
  `packages/security/identity.py`'s own module docstring already
  establishes for `AuthenticatedPrincipal` vs `ServicePrincipal`. This
  table can be dropped/rotated/migrated to a real OIDC provider later
  without ever touching `users`.

- `local_auth_sessions` -- one row per issued HTTP session.
  `session_token_hash` (SHA-256 of the real, 256-bit random cookie
  value, UNIQUE) is stored, never the raw token -- a database read
  alone can never reconstruct a usable session, only the browser's own
  `nquiry_session` cookie can. `expires_at` (server-computed at issue
  time, 12h lifetime, `application.auth_handler.SESSION_LIFETIME`) and
  `revoked_at` (set by `/auth/logout`) are both checked by
  `application.auth_handler.resolve_session` on every request -- an
  expired-but-not-yet-revoked and a revoked-but-not-yet-expired session
  are both rejected, independently.

Neither table carries a `workspace_id` column (both are genuinely
cross-Workspace, exactly like `users` itself) -- consistent with
`047bdf9bc528`'s own RLS scope note ("every table that already carries
a direct workspace_id column EXCEPT users/workspaces themselves");
these two tables are excluded from RLS for the identical reason.

Deliberately NOT extended in this migration: `packages/security/
identity.py`'s `SECURITY_CAPABILITY_MAP`/`ServicePrincipal` DB-principal
system (PKG-25/26). The real runtime HTTP path
(`packages/application/http_dispatch.py` and now `auth_handler.py`)
still connects as the bootstrap `nquiry` superuser via
`persistence.engine.connect()`, exactly like every other repository
call that path already makes -- no table `http_dispatch.py` touches is
scoped to a specific `ServicePrincipal` at connection time yet (already
disclosed as `SUCCESSOR_NOT_BUILT` since Architecture 17; PKG-25's own
DB-principal separation is proven only against direct `SET ROLE`
connections in `tests/security/test_db_principals.py`, not against the
live HTTP path). Extending the capability map for only these two new
tables, while every other Architecture-17-era table remains
unscoped, would be a disproportionate, inconsistent partial fix --
flagged here as a known, disclosed limitation, not silently done.

No RLS, no new DB principal, no `workspace_id`, no new trigger. Pure
additive DDL.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "05794035ef3c"
down_revision: str | None = "047bdf9bc528"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "local_auth_credentials",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
            unique=True,
        ),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "local_auth_sessions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
        ),
        sa.Column("session_token_hash", sa.Text(), nullable=False, unique=True),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_local_auth_sessions_user_id", "local_auth_sessions", ["user_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_local_auth_sessions_user_id", table_name="local_auth_sessions")
    op.drop_table("local_auth_sessions")
    op.drop_table("local_auth_credentials")
