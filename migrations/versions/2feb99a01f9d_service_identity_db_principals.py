"""service identity db principals

Revision ID: 2feb99a01f9d
Revises: b7ec21429b53
Create Date: 2026-09-20 18:00:00.000000

PKG-25 scope (14_IMPLEMENTATION_SEQUENCE.md section 9's own
`012_security_events_rls` bucket -- this is 14's own "principal/grant
definitions only" half; PKG-26's own later revision in the same bucket
creates `security_events` itself plus RLS policies).

Grants table-level DML privileges to the 8 DML-capable principals named
by this package's own OBJECTIVE (`api_reader`, `governed_commit_writer`,
`ai_gateway_writer`, `projection_writer`, `recovery_reader`,
`audit_reader`, `test_principal`, plus `CREATE ON SCHEMA public` for
`migration_owner`) against every table that already exists as of head
`b7ec21429b53`. `security_event_writer`'s own role is created by
`infra/local/db_roles.sql`, but its one GRANT (on `security_events`) is
deliberately deferred to PKG-26's own migration -- that table does not
exist yet (the identical "role exists now, grant deferred to the
package that creates the target" pattern
`b7ec21429b53_recovery_command_fields.py`'s own docstring already
disclosed for `recovery_reader` one package earlier).

PRECONDITION, DISCLOSED: this migration assumes `infra/local/db_roles.sql`
has already been run against this database (roles are cluster-wide
objects, outside Alembic's own schema-migration scope -- see that
file's own docstring for why). If a named role does not exist, the
`GRANT ... TO <role>` statement below raises a real Postgres error
(`role "..." does not exist`) and the migration fails -- the correct
"fail technically" behavior (14 PKG-25's own FAILURE_RECOVERY line),
not a silent no-op.

Every table -> principal assignment here is IDENTICAL to
`packages.security.identity.SECURITY_CAPABILITY_MAP` (see that
module's own "WHY THIS CAPABILITY MAP IS CODE-GROUNDED" docstring
section for how each assignment was derived by tracing real
INSERT/UPDATE/DELETE call sites, not invented) --
`tests/security/test_db_principals.py` queries
`information_schema.role_table_grants` directly against a live database
to prove the two never drift apart, rather than trusting this
migration's own SQL text as self-certifying.

`REVOKE ALL ... FROM PUBLIC` (schema + every table) is defense-in-depth
hardening matching this package's own "No runtime superuser" /
privilege-separation OBJECTIVE -- without it, PostgreSQL's own default
`CREATE`/`USAGE` grant to `PUBLIC` on the `public` schema would let ANY
future role connect and create objects there unless explicitly
revoked.

Schema downgrade is infrastructure rollback only, not domain rollback
(14 section 9). Downgrade reverses every explicit GRANT/REVOKE this
migration performs; it does not attempt to reconstruct PostgreSQL's own
original pre-migration `PUBLIC` schema defaults byte-for-byte, the same
disclosed limitation every schema-rollback migration in this codebase
already carries.
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2feb99a01f9d"
down_revision: str | None = "b7ec21429b53"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_GOVERNED_COMMIT_WRITER_TABLES = (
    "questions",
    "question_lineage",
    "question_bursts",
    "burst_question_memberships",
    "commands",
    "command_attempts",
    "idempotency_records",
    "audit_events",
    "outbox_events",
    "commit_units",
    "question_selections",
    "decisions",
    "source_references",
    "evidence",
    "claim_anchors",
    "evidence_relations",
    "evidence_set_references",
)
_AI_GATEWAY_WRITER_TABLES = ("ai_generations", "ai_derived_artifacts", "ai_context_manifests")
_PROJECTION_WRITER_TABLES = ("projection_checkpoints", "session_read_model", "inquiry_read_model")
_RECOVERY_READER_TABLES = ("recovery_records",)
_AUDIT_READER_TABLES = ("audit_events",)

_ALL_PROTECTED_TABLES = (
    "users",
    "workspaces",
    "workspace_memberships",
    "role_assignments",
    "human_authority_bindings",
    "challenges",
    "sessions",
    *_GOVERNED_COMMIT_WRITER_TABLES,
    *_AI_GATEWAY_WRITER_TABLES,
    *_PROJECTION_WRITER_TABLES,
    *_RECOVERY_READER_TABLES,
)

_DML_PRINCIPALS = (
    "migration_owner",
    "api_reader",
    "governed_commit_writer",
    "ai_gateway_writer",
    "projection_writer",
    "recovery_reader",
    "security_event_writer",
    "audit_reader",
    "test_principal",
)


def upgrade() -> None:
    op.execute("REVOKE ALL ON SCHEMA public FROM PUBLIC")
    for principal in _DML_PRINCIPALS:
        op.execute(f"GRANT USAGE ON SCHEMA public TO {principal}")
    op.execute("GRANT CREATE ON SCHEMA public TO migration_owner")

    op.execute(_grant_sql("SELECT", _ALL_PROTECTED_TABLES, "api_reader"))
    op.execute(
        _grant_sql("SELECT, INSERT, UPDATE, DELETE", _ALL_PROTECTED_TABLES, "test_principal")
    )
    op.execute(
        _grant_sql(
            "SELECT, INSERT, UPDATE", _GOVERNED_COMMIT_WRITER_TABLES, "governed_commit_writer"
        )
    )
    op.execute(_grant_sql("SELECT, INSERT, UPDATE", _AI_GATEWAY_WRITER_TABLES, "ai_gateway_writer"))
    op.execute(
        _grant_sql("SELECT, INSERT, UPDATE, DELETE", _PROJECTION_WRITER_TABLES, "projection_writer")
    )
    op.execute(_grant_sql("SELECT, INSERT, UPDATE", _RECOVERY_READER_TABLES, "recovery_reader"))
    op.execute(_grant_sql("SELECT", _AUDIT_READER_TABLES, "audit_reader"))


def downgrade() -> None:
    op.execute(_revoke_sql(_AUDIT_READER_TABLES, "audit_reader"))
    op.execute(_revoke_sql(_RECOVERY_READER_TABLES, "recovery_reader"))
    op.execute(_revoke_sql(_PROJECTION_WRITER_TABLES, "projection_writer"))
    op.execute(_revoke_sql(_AI_GATEWAY_WRITER_TABLES, "ai_gateway_writer"))
    op.execute(_revoke_sql(_GOVERNED_COMMIT_WRITER_TABLES, "governed_commit_writer"))
    op.execute(_revoke_sql(_ALL_PROTECTED_TABLES, "test_principal"))
    op.execute(_revoke_sql(_ALL_PROTECTED_TABLES, "api_reader"))

    op.execute("REVOKE CREATE ON SCHEMA public FROM migration_owner")
    for principal in _DML_PRINCIPALS:
        op.execute(f"REVOKE USAGE ON SCHEMA public FROM {principal}")
    op.execute("GRANT ALL ON SCHEMA public TO PUBLIC")


def _grant_sql(privileges: str, tables: Sequence[str], principal: str) -> str:
    table_list = ", ".join(tables)
    return f"GRANT {privileges} ON {table_list} TO {principal}"


def _revoke_sql(tables: Sequence[str], principal: str) -> str:
    table_list = ", ".join(tables)
    return f"REVOKE ALL ON {table_list} FROM {principal}"
