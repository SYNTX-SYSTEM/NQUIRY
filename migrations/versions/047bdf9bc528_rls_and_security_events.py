"""rls and security events

Revision ID: 047bdf9bc528
Revises: 2feb99a01f9d
Create Date: 2026-09-20 20:00:00.000000

PKG-26 scope (14_IMPLEMENTATION_SEQUENCE.md section 9's own
`012_security_events_rls` bucket -- PKG-25 built the 9 DB principals
and their table-level GRANTs; this migration is the bucket's own
"security_events, RLS/policies/grants" half).

Table created:

- `security_events` (11_SECURITY_PRIVACY_OBSERVABILITY.md section 42
  "SecurityEvent Minimum Semantics" -- the field list is this package's
  own disclosed `[IMPLEMENTATION CHOICE]` materialization; section 42
  itself says "Exact physical schema belongs to implementation
  materialization"). `environment` CHECK-constrained to section 60's
  own exact 4-value closed list; `trust_boundary` CHECK-constrained to
  section 3's own exact, closed, numbered 19-boundary inventory.
  Deliberately NO foreign key on `workspace_id`/`command_id`/
  `generation_id`/`recovery_id` -- see `packages/security/events.py`'s
  own module docstring for why a real FK would make it structurally
  impossible to ever record the one class of event this type most
  needs to represent (a forged/unresolvable claim). Two triggers
  (`trg_security_events_reject_update`/`trg_security_events_reject_delete`)
  mirror `audit_events`' own append-only precedent (PKG-12) exactly --
  defense-in-depth against "SecurityEvent tamper/rewrite", independent
  of and in addition to `SecurityEventRepository`'s own Protocol shape
  (which has no update/delete method at all).

Grants:

- `security_event_writer` receives `SELECT, INSERT` on `security_events`
  -- the ONE grant PKG-25's own migration (`2feb99a01f9d`) deliberately
  deferred to this package, since the table did not exist yet.
- `governed_commit_writer` loses its own previously-granted `UPDATE` on
  `audit_events`. Disclosed retrofit, discovered while cross-checking
  PKG-25's own grants against 14 section 8's explicit
  "governed_commit_writer ... Forbidden: arbitrary audit update/delete"
  row (not fully consulted at PKG-25 authoring time): no production
  code anywhere in this codebase calls `sa.update(audit_events_table)`
  (`audit.models.AuditRepository`/`persistence.audit_repository.
  SqlAlchemyAuditRepository` are both append-only, INSERT-only) --
  PKG-25's own uniform per-principal grant (SELECT/INSERT/UPDATE across
  its whole table set, disclosed at the time as "deliberately not
  narrowed per additional verb-level precision") over-granted this one
  verb on this one table. `SELECT`/`INSERT` are retained (still
  code-grounded and required). This is the identical "retrofit a
  predecessor's own now-discovered gap in the package that discovers
  it" pattern already used repeatedly in this codebase (PKG-13's FK
  retrofits, PKG-24's `record_version` retrofit).

RLS (defense-in-depth, 14 section 8's own `[IMPLEMENTATION CHOICE]`:
"PostgreSQL RLS is enabled for Workspace-keyed protected tables using
transaction-local Workspace context set only by trusted server
adapter. RLS is defense-in-depth and is never used as the authority
oracle."):

- Enabled on every one of the 29 tables that already carry a direct
  `workspace_id` column (every table in `persistence.tables`
  EXCEPT `users`/`workspaces` themselves, neither of which is a
  Workspace-scoped protected object -- `users` is deliberately
  cross-Workspace, `workspaces` IS the scoping table).
- One identical policy per table:
  `USING (workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid)`,
  with an identical `WITH CHECK` clause. Unset (or explicitly cleared)
  context reads back as SQL `NULL` via `NULLIF(..., '')`, and
  `workspace_id = NULL` is never `true` -- the DEFAULT is therefore
  FAIL-CLOSED (zero rows visible/writable), not "see everything",
  independent of and in addition to BND-002's own semantic Workspace
  enforcement (this package's own BOUNDARIES line: "BND-002 remains
  semantic enforcement in addition to RLS").
- Every one of PKG-25's own 9 principals is a non-owner, non-superuser
  role (verified live, PKG-25's own report) -- RLS therefore applies to
  all of them unconditionally; no `FORCE ROW LEVEL SECURITY` is needed
  and none is set, since forcing would also apply RLS to the
  bootstrap `nquiry` owner/superuser role this session's own existing
  ~1000-test suite already depends on running unrestricted (RLS is
  bypassed for superusers and table owners by default -- confirmed live
  before this migration was written: `nquiry` is both).

Downgrade drops every policy and disables RLS on all 29 tables, restores
`governed_commit_writer`'s own `UPDATE` grant on `audit_events`, revokes
`security_event_writer`'s own grant, then drops `security_events`
itself. Schema downgrade is infrastructure rollback only, not domain
rollback (14 section 9).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "047bdf9bc528"
down_revision: str | None = "2feb99a01f9d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# 11 section 60's own exact 4-value closed vocabulary.
_ENVIRONMENT_VALUES = ("DEVELOPMENT", "TEST", "STAGING", "PRODUCTION")
# 11 section 3's own exact, closed, numbered 19-boundary inventory.
_TRUST_BOUNDARY_VALUES = tuple(f"TB-{i:02d}" for i in range(1, 20))

# Every table with a direct `workspace_id` column, per `persistence.tables`
# (`users`/`workspaces` themselves are deliberately excluded -- see this
# migration's own docstring).
_WORKSPACE_SCOPED_TABLES = (
    "workspace_memberships",
    "role_assignments",
    "human_authority_bindings",
    "challenges",
    "sessions",
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
    "ai_generations",
    "ai_derived_artifacts",
    "ai_context_manifests",
    "projection_checkpoints",
    "session_read_model",
    "inquiry_read_model",
    "recovery_records",
)

_RLS_POLICY_NAME = "workspace_isolation"
_RLS_EXPR = "workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid"


def _in_list(values: tuple[str, ...]) -> str:
    return ", ".join(f"'{v}'" for v in values)


def upgrade() -> None:
    op.create_table(
        "security_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("workspace_id", sa.Uuid(), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("environment", sa.Text(), nullable=False),
        sa.Column("actor_type", sa.Text(), nullable=False),
        sa.Column("actor_id", sa.Text(), nullable=False),
        sa.Column("trust_boundary", sa.Text(), nullable=False),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("correlation_id", sa.Uuid(), nullable=False),
        sa.Column("target_ref", sa.Text(), nullable=True),
        sa.Column("command_id", sa.Uuid(), nullable=True),
        sa.Column("generation_id", sa.Uuid(), nullable=True),
        sa.Column("recovery_id", sa.Uuid(), nullable=True),
        sa.Column("observed_facts", sa.Text(), nullable=True),
        sa.Column("uncertain", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("containment_action", sa.Text(), nullable=True),
        sa.Column("audit_linkage", sa.Text(), nullable=True),
        sa.CheckConstraint(
            f"environment IN ({_in_list(_ENVIRONMENT_VALUES)})",
            name="ck_security_events_environment",
        ),
        sa.CheckConstraint(
            f"trust_boundary IN ({_in_list(_TRUST_BOUNDARY_VALUES)})",
            name="ck_security_events_trust_boundary",
        ),
    )

    op.execute(
        """
        CREATE FUNCTION trg_security_events_reject_update() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION
                'security_events rows are append-only; a correction records a new '
                'SecurityEvent (11 section 41/42)';
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_security_events_reject_update
        BEFORE UPDATE ON security_events
        FOR EACH ROW EXECUTE FUNCTION trg_security_events_reject_update();
        """
    )
    op.execute(
        """
        CREATE FUNCTION trg_security_events_reject_delete() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION
                'security_events rows cannot be deleted; established security history '
                'is append-only (11 section 41/42)';
            RETURN OLD;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_security_events_reject_delete
        BEFORE DELETE ON security_events
        FOR EACH ROW EXECUTE FUNCTION trg_security_events_reject_delete();
        """
    )

    op.execute("GRANT SELECT, INSERT ON security_events TO security_event_writer")
    op.execute("REVOKE UPDATE ON audit_events FROM governed_commit_writer")

    op.execute(
        "DO $$\n"
        "DECLARE\n"
        "    tbl text;\n"
        "BEGIN\n"
        f"    FOREACH tbl IN ARRAY ARRAY[{_in_list(_WORKSPACE_SCOPED_TABLES)}] LOOP\n"
        "        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', tbl);\n"
        "        EXECUTE format(\n"
        f"            $fmt$CREATE POLICY {_RLS_POLICY_NAME} ON %I "
        f"USING ({_RLS_EXPR}) WITH CHECK ({_RLS_EXPR})$fmt$,\n"
        "            tbl\n"
        "        );\n"
        "    END LOOP;\n"
        "END\n"
        "$$;"
    )


def downgrade() -> None:
    op.execute(
        "DO $$\n"
        "DECLARE\n"
        "    tbl text;\n"
        "BEGIN\n"
        f"    FOREACH tbl IN ARRAY ARRAY[{_in_list(_WORKSPACE_SCOPED_TABLES)}] LOOP\n"
        f"        EXECUTE format('DROP POLICY {_RLS_POLICY_NAME} ON %I', tbl);\n"
        "        EXECUTE format('ALTER TABLE %I DISABLE ROW LEVEL SECURITY', tbl);\n"
        "    END LOOP;\n"
        "END\n"
        "$$;"
    )

    op.execute("GRANT UPDATE ON audit_events TO governed_commit_writer")
    op.execute("REVOKE SELECT, INSERT ON security_events FROM security_event_writer")

    op.execute("DROP TRIGGER IF EXISTS trg_security_events_reject_delete ON security_events;")
    op.execute("DROP FUNCTION IF EXISTS trg_security_events_reject_delete();")
    op.execute("DROP TRIGGER IF EXISTS trg_security_events_reject_update ON security_events;")
    op.execute("DROP FUNCTION IF EXISTS trg_security_events_reject_update();")

    op.drop_table("security_events")
