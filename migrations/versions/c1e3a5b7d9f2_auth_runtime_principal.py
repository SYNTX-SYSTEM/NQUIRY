"""AUTH WU-AUTH-17: auth_runtime principal capabilities; session resolution reads (24 §21.18)

Revision ID: c1e3a5b7d9f2
Revises: b9d2f4a6c8e1
Create Date: 2026-10-01 00:00:00.000000

Grants the scoped runtime principal of authentication persistence,
`auth_runtime` (created by `infra/local/db_roles.sql`, like the nine PKG-25
principals; a missing role is a real error here, not a silent no-op), exactly
the capability map of `security.db_capabilities.AUTH_PERSISTENCE_CAPABILITIES`:
SELECT / INSERT / UPDATE on the authentication relations (including the
pre-existing `users`, `local_auth_credentials`, `local_auth_sessions`: the
existing live path follows the same discipline as the new tables, 24 §21.18
"avoid partial security hardening") and INSERT only on `security_events`.
No DELETE anywhere (24 §18.3), nothing of the business / authority field.

The business principals that serve HTTP (`api_reader`, `governed_commit_writer`)
receive SELECT on the three tables a session resolution reads
(`local_auth_sessions`, `authentication_methods`, `users` — the latter
already readable by `api_reader`). `test_principal`, the disclosed NON_PROOF
fixture authority, receives DML on the authentication tables as it has on
every other protected table (migration 2feb99a01f9d).

No data change. Cross-Workspace (no RLS on these relations).
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision = "c1e3a5b7d9f2"
down_revision = "b9d2f4a6c8e1"
branch_labels = None
depends_on = None

_AUTH_RUNTIME = "auth_runtime"
_RW_TABLES: Sequence[str] = (
    "users",
    "local_auth_credentials",
    "local_auth_sessions",
    "authentication_methods",
    "external_provider_identities",
    "oidc_auth_transactions",
    "auth_challenges",
    "verified_emails",
    "recovery_challenges",
)
_APPEND_ONLY_TABLES: Sequence[str] = ("security_events",)
_SESSION_RESOLUTION_TABLES: Sequence[str] = (
    "local_auth_sessions",
    "authentication_methods",
    "users",
)
_SESSION_RESOLVING_PRINCIPALS: Sequence[str] = ("api_reader", "governed_commit_writer")
_AUTH_TABLES_ADDED_SINCE_2FEB: Sequence[str] = (
    "local_auth_credentials",
    "local_auth_sessions",
    "authentication_methods",
    "external_provider_identities",
    "oidc_auth_transactions",
    "auth_challenges",
    "verified_emails",
    "recovery_challenges",
)


def _tables(tables: Sequence[str]) -> str:
    return ", ".join(tables)


def upgrade() -> None:
    op.execute(f"GRANT USAGE ON SCHEMA public TO {_AUTH_RUNTIME}")
    op.execute(f"GRANT SELECT, INSERT, UPDATE ON {_tables(_RW_TABLES)} TO {_AUTH_RUNTIME}")
    op.execute(f"GRANT INSERT ON {_tables(_APPEND_ONLY_TABLES)} TO {_AUTH_RUNTIME}")
    for principal in _SESSION_RESOLVING_PRINCIPALS:
        op.execute(f"GRANT SELECT ON {_tables(_SESSION_RESOLUTION_TABLES)} TO {principal}")
    op.execute(
        "GRANT SELECT, INSERT, UPDATE, DELETE ON "
        f"{_tables(_AUTH_TABLES_ADDED_SINCE_2FEB)} TO test_principal"
    )


def downgrade() -> None:
    op.execute(f"REVOKE ALL ON {_tables(_AUTH_TABLES_ADDED_SINCE_2FEB)} FROM test_principal")
    for principal in _SESSION_RESOLVING_PRINCIPALS:
        op.execute(
            f"REVOKE SELECT ON {_tables(('local_auth_sessions', 'authentication_methods'))} "
            f"FROM {principal}"
        )
    op.execute("REVOKE SELECT ON users FROM governed_commit_writer")
    op.execute(f"REVOKE ALL ON {_tables(_APPEND_ONLY_TABLES)} FROM {_AUTH_RUNTIME}")
    op.execute(f"REVOKE ALL ON {_tables(_RW_TABLES)} FROM {_AUTH_RUNTIME}")
    op.execute(f"REVOKE USAGE ON SCHEMA public FROM {_AUTH_RUNTIME}")
