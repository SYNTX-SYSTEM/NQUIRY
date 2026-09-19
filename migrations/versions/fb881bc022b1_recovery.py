"""recovery

Revision ID: fb881bc022b1
Revises: 1bc6021cb651
Create Date: 2026-09-20 14:00:00.000000

PKG-23 scope (14_IMPLEMENTATION_SEQUENCE.md section 9's own
`011_recovery` bucket: "recovery_records | depends on: 009 | gate: 10
semantics tests").

Table created:

- `recovery_records` (10 section 63: "[ARCHITECTURAL CLOSURE]
  AC-10-009", the exact "Minimum semantics" field list). Real composite
  foreign keys into `commands(id, workspace_id)` and
  `commit_units(id, workspace_id)` (both already carry a
  `UNIQUE(id, workspace_id)` anchor); `original_attempt_id` and
  `human_decision_ref` carry NO foreign key -- `command_attempts` and
  `decisions` have no such anchor yet, the same disclosed-gap treatment
  `claim_anchors.target_id`/`human_authority_bindings.scope_id` already
  established for a polymorphic/unanchored reference. `canonical_state_certainty`/
  `external_consequence_certainty` are CHECK-constrained to
  `recovery.certainty.ConsequenceCertainty`'s own 7-value closed list
  (PKG-22); `recovery_class` to 10 section 30's own exact RC-01..RC-07
  7-value list; `result` to 10 section 64's own exact 5-value
  RecoveryOutcome list.

Two triggers, mirroring `outbox_events`' own precedent (PKG-12):

- `trg_recovery_records_enforce_identity_immutable`: every field that
  identifies WHICH failure this record is about (`workspace_id`,
  `failure_correlation_ref`, `original_command_id`,
  `original_attempt_id`, `original_commit_id`, `recovery_actor_type`,
  `recovery_actor_id`, `created_at`) is immutable once set.
- `trg_recovery_records_enforce_result_transition`: `result` starts
  `UNRESOLVED` (enforced by a companion initial-state trigger) and may
  transition exactly once, `UNRESOLVED` -> one of the four terminal
  outcomes (`RECOVERED`/`RECONCILED`/`COMPENSATED`/`NO_ACTION_REQUIRED`)
  -- every terminal outcome is then itself terminal (10 section 64
  gives RecoveryRecord's own outcomes no further legal transition; 10
  section 65's own "may accumulate new findings and attempts" applies
  to the array/ref columns, not to `result` itself once resolved).

No `recovery_reader`/`RecoveryRepository` DB-principal GRANT is created
here, consistent with every migration since `001` (deferred to
`012_security_events_rls`). No cascading delete anywhere (14 section 49
default). Schema downgrade is infrastructure rollback only, not domain
rollback (14 section 9).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "fb881bc022b1"
down_revision: str | None = "1bc6021cb651"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# 10 section 5's exact 7-value closed vocabulary (PKG-22).
_CONSEQUENCE_CERTAINTY_VALUES = (
    "PROVEN_COMMITTED",
    "PROVEN_NOT_COMMITTED",
    "EXTERNAL_CONSEQUENCE_PROVEN",
    "EXTERNAL_CONSEQUENCE_PROVEN_ABSENT",
    "EXTERNAL_CONSEQUENCE_UNKNOWN",
    "CANONICAL_STATE_UNKNOWN",
    "GOVERNANCE_STATE_UNKNOWN",
)
# 10 section 30's exact 7-value closed vocabulary.
_RECOVERY_CLASS_VALUES = ("RC-01", "RC-02", "RC-03", "RC-04", "RC-05", "RC-06", "RC-07")
# 10 section 64's exact 5-value closed vocabulary.
_RECOVERY_OUTCOME_VALUES = (
    "RECOVERED",
    "RECONCILED",
    "COMPENSATED",
    "NO_ACTION_REQUIRED",
    "UNRESOLVED",
)
_TERMINAL_RECOVERY_OUTCOMES = ("RECOVERED", "RECONCILED", "COMPENSATED", "NO_ACTION_REQUIRED")


def _in_list(values: tuple[str, ...]) -> str:
    return ", ".join(f"'{v}'" for v in values)


def upgrade() -> None:
    op.create_table(
        "recovery_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("failure_correlation_ref", sa.Uuid(), nullable=False),
        sa.Column("original_command_id", sa.Uuid(), nullable=False),
        sa.Column("original_attempt_id", sa.Uuid(), nullable=False),
        sa.Column("original_commit_id", sa.Uuid(), nullable=True),
        sa.Column(
            "failure_classifications",
            postgresql.ARRAY(sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("known_canonical_state_ref", sa.Text(), nullable=True),
        sa.Column("canonical_state_certainty", sa.Text(), nullable=False),
        sa.Column("known_external_consequence_ref", sa.Text(), nullable=True),
        sa.Column("external_consequence_certainty", sa.Text(), nullable=False),
        sa.Column("unknown_consequence_description", sa.Text(), nullable=True),
        sa.Column("last_proven_valid_state_ref", sa.Text(), nullable=True),
        sa.Column("recovery_class", sa.Text(), nullable=False),
        sa.Column("recovery_actor_type", sa.Text(), nullable=False),
        sa.Column("recovery_actor_id", sa.Text(), nullable=False),
        sa.Column("required_authority_ref", sa.Uuid(), nullable=True),
        sa.Column("current_authority_binding_ref", sa.Uuid(), nullable=True),
        sa.Column("human_decision_ref", sa.Uuid(), nullable=True),
        sa.Column(
            "evidence_proof_refs", postgresql.ARRAY(sa.Text()), nullable=False, server_default="{}"
        ),
        sa.Column(
            "recovery_command_ids", postgresql.ARRAY(sa.Uuid()), nullable=False, server_default="{}"
        ),
        sa.Column(
            "recovery_attempt_refs",
            postgresql.ARRAY(sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("result", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("audit_linkage", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_recovery_records"),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name="fk_recovery_records_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["original_command_id", "workspace_id"],
            ["commands.id", "commands.workspace_id"],
            name="fk_recovery_records_original_command_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["original_commit_id", "workspace_id"],
            ["commit_units.id", "commit_units.workspace_id"],
            name="fk_recovery_records_original_commit_workspace",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            f"canonical_state_certainty IN ({_in_list(_CONSEQUENCE_CERTAINTY_VALUES)})",
            name="ck_recovery_records_canonical_state_certainty",
        ),
        sa.CheckConstraint(
            f"external_consequence_certainty IN ({_in_list(_CONSEQUENCE_CERTAINTY_VALUES)})",
            name="ck_recovery_records_external_consequence_certainty",
        ),
        sa.CheckConstraint(
            f"recovery_class IN ({_in_list(_RECOVERY_CLASS_VALUES)})",
            name="ck_recovery_records_recovery_class",
        ),
        sa.CheckConstraint(
            f"result IN ({_in_list(_RECOVERY_OUTCOME_VALUES)})",
            name="ck_recovery_records_result",
        ),
        sa.CheckConstraint(
            "(result = 'UNRESOLVED') = (resolved_at IS NULL)",
            name="ck_recovery_records_resolved_at_biconditional",
        ),
    )
    op.create_index("ix_recovery_records_workspace", "recovery_records", ["workspace_id"])

    op.execute(
        """
        CREATE FUNCTION trg_recovery_records_enforce_initial_state() RETURNS trigger AS $$
        BEGIN
            IF NEW.result IS DISTINCT FROM 'UNRESOLVED' THEN
                RAISE EXCEPTION
                    'recovery_records must be created with result = UNRESOLVED (10 section 64)';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_recovery_records_enforce_initial_state
        BEFORE INSERT ON recovery_records
        FOR EACH ROW EXECUTE FUNCTION trg_recovery_records_enforce_initial_state();
        """
    )

    op.execute(
        """
        CREATE FUNCTION trg_recovery_records_enforce_identity_immutable() RETURNS trigger AS $$
        BEGIN
            IF NEW.workspace_id IS DISTINCT FROM OLD.workspace_id
                OR NEW.failure_correlation_ref IS DISTINCT FROM OLD.failure_correlation_ref
                OR NEW.original_command_id IS DISTINCT FROM OLD.original_command_id
                OR NEW.original_attempt_id IS DISTINCT FROM OLD.original_attempt_id
                OR NEW.original_commit_id IS DISTINCT FROM OLD.original_commit_id
                OR NEW.recovery_actor_type IS DISTINCT FROM OLD.recovery_actor_type
                OR NEW.recovery_actor_id IS DISTINCT FROM OLD.recovery_actor_id
                OR NEW.created_at IS DISTINCT FROM OLD.created_at
            THEN
                RAISE EXCEPTION
                    'recovery_records identity fields are immutable once set (10 section 63)';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_recovery_records_enforce_identity_immutable
        BEFORE UPDATE ON recovery_records
        FOR EACH ROW EXECUTE FUNCTION trg_recovery_records_enforce_identity_immutable();
        """
    )

    op.execute(
        f"""
        CREATE FUNCTION trg_recovery_records_enforce_result_transition() RETURNS trigger AS $$
        BEGIN
            IF OLD.result IN ({_in_list(_TERMINAL_RECOVERY_OUTCOMES)}) THEN
                IF NEW.result IS DISTINCT FROM OLD.result THEN
                    RAISE EXCEPTION
                        'recovery_records result % is terminal (10 section 64)', OLD.result;
                END IF;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_recovery_records_enforce_result_transition
        BEFORE UPDATE ON recovery_records
        FOR EACH ROW EXECUTE FUNCTION trg_recovery_records_enforce_result_transition();
        """
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_recovery_records_enforce_result_transition ON recovery_records;"
    )
    op.execute("DROP FUNCTION IF EXISTS trg_recovery_records_enforce_result_transition();")
    op.execute(
        "DROP TRIGGER IF EXISTS trg_recovery_records_enforce_identity_immutable "
        "ON recovery_records;"
    )
    op.execute("DROP FUNCTION IF EXISTS trg_recovery_records_enforce_identity_immutable();")
    op.execute(
        "DROP TRIGGER IF EXISTS trg_recovery_records_enforce_initial_state ON recovery_records;"
    )
    op.execute("DROP FUNCTION IF EXISTS trg_recovery_records_enforce_initial_state();")

    op.drop_index("ix_recovery_records_workspace", table_name="recovery_records")
    op.drop_table("recovery_records")
