"""audit and outbox

Revision ID: 6119c9dcf073
Revises: b5b33834b7ea
Create Date: 2026-09-18 16:00:00.000000

PKG-12 scope (14_IMPLEMENTATION_SEQUENCE.md section 9's conceptual
"009_commit_audit_outbox" bucket lists "creates: commit_units,
audit_events, outbox_events | depends on: 008" as one summary row. This
migration materializes only the `audit_events`/`outbox_events` half --
PKG-12's own manifest is "Append AuditEvent and durable outbox
semantics" (PUBLIC_INTERFACES: AuditRepository, OutboxRepository).
`commit_units` is PKG-13's own PUBLIC_INTERFACES ("Commit coordinator
and BND-014") and is deliberately NOT created here -- the same
one-conceptual-bucket-across-two-Alembic-revisions split PKG-02/PKG-05,
PKG-06/PKG-07, and PKG-10/PKG-11 already established.

No `commit writer`/`outbox worker` DB principal or GRANT is created
here. 14 section 7.1 names those as the eventual write owners, but
every DB-principal/GRANT/RLS change in this codebase so far has been
deferred to migration `012_security_events_rls` -- consistent with
every migration since `001`.

Tables created:

- `audit_events` (09 section 58, 11 sections 33-35; 14 section 7.1):
  the append-only reconstruction record. Columns map 09 section 58's
  field list exactly (`audit_event_id` as this table's own `id`;
  `operation/command_type` as `command_type`; `metadata_ref/payload`
  as `metadata_ref`). Composite FK `(command_id, workspace_id) ->
  commands(id, workspace_id)` (PKG-10's own anchor) makes an audit
  event referencing a forged or cross-Workspace `command_id`
  structurally unrepresentable -- 11 section 34's own "boundary result
  references" integrity property is satisfied transitively through this
  FK, joining to `command_attempts.boundary_evaluation_summary_ref`
  (PKG-10) for the same `command_id`, rather than duplicating that
  reference onto this table (see `packages/audit/models.py`'s own
  docstring for the full reasoning).

  `commit_id` carries no foreign key: `commit_units` (14 section 7.1)
  is not created until PKG-13's own migration revision -- the same
  disclosed forward-reference gap `command_attempts.commit_id`
  (PKG-10) and `idempotency_records.commit_id` (PKG-11) already
  established.

  `result` is CHECK-constrained to 14 section 6's exact 4-value Command
  outcome vocabulary (`DENIED`, `FAILED_PRECOMMIT`, `COMMITTED`,
  `INDETERMINATE`) at the database layer only -- `packages/audit/models.py`'s
  own Python type keeps `result` a plain string, since `audit`'s
  allowed dependencies (14 section 3.1: "semantic_types") do not
  include `command`, so it cannot import `CommandOutcome` itself.

  Immutable against BOTH UPDATE and DELETE (trigger 1, below) -- 09
  section 58.1: "AuditEvent is append-only... Correction creates a new
  audit event"; 11 section 35: "Ordinary application principals cannot
  rewrite established audit history." This is the first table in this
  codebase's migration chain to reject DELETE as well as UPDATE (every
  prior immutability trigger -- `question_lineage`, `burst_question_memberships`,
  `commands`, `idempotency_records` -- only guarded UPDATE), because 09
  and 11 both explicitly name deletion as a violation this table must
  resist, not only mutation-in-place -- the mandatory adversarial
  attacks "audit update" and "audit delete" are two distinct named
  attacks for this package, unlike any prior package's immutability
  requirement.

- `outbox_events` (09 sections 14-15, 122; 14 section 7.1): the
  transactional-outbox delivery-tracking record. Columns map 09
  section 15's field list exactly, plus `workspace_id` (14 section
  7.1's own Workspace-keyed requirement, a technical isolation column
  09's minimal semantic list does not itemize -- the same disclosed
  addition PKG-11 made for `idempotency_records`). `event_id` is
  `UNIQUE` (14 section 7.3: "outbox_events.event_id is unique") --
  the mandatory adversarial attack "outbox duplicate" is therefore
  structurally impossible to represent, not merely checked in
  application code. `commit_id` carries no foreign key, the identical
  disclosed forward-reference gap `audit_events.commit_id` has.

  `delivery_status` is CHECK-constrained to 09 section 15.1's exact
  3-value closed vocabulary (`PENDING`, `DELIVERED`, `FAILED_DELIVERY`).

  Trigger 2 (below) locks every field except `delivery_status`/
  `delivery_attempt_count`/`next_attempt_at`/`delivered_at` -- the
  field-level half of 14 section 7.1's own write-owner split ("commit
  writer, then outbox worker delivery fields only"); the remaining
  half (a distinct DB principal per writer) is deferred to migration
  `012_security_events_rls`, the same disclosed gap as every prior
  migration.

  Trigger 3 (below) enforces 09 section 15's own delivery-status
  topology: `PENDING -> {DELIVERED, FAILED_DELIVERY}` and
  `FAILED_DELIVERY -> {PENDING, DELIVERED}` are the only legal moves;
  `DELIVERED` is terminal (09 section 15.2's "at-least-once delivery"
  describes a *consumer's* obligation to tolerate re-delivery, not a
  license for this record to un-deliver itself).

No cascading delete anywhere (14 section 49 default). Schema downgrade
is infrastructure rollback only, not domain rollback (14 section 9).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6119c9dcf073"
down_revision: str | None = "b5b33834b7ea"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# 14 section 6's exact 4-value closed vocabulary, enforced here at the
# database layer only (see module docstring).
_AUDIT_RESULTS = ("DENIED", "FAILED_PRECOMMIT", "COMMITTED", "INDETERMINATE")

# 09 section 15.1's exact 3-value closed vocabulary.
_DELIVERY_STATUSES = ("PENDING", "DELIVERED", "FAILED_DELIVERY")

# 09 section 15's own delivery-status topology.
_LEGAL_DELIVERY_TRANSITIONS_SQL = ", ".join(
    f"('{source}', '{target}')"
    for source, target in (
        ("PENDING", "DELIVERED"),
        ("PENDING", "FAILED_DELIVERY"),
        ("FAILED_DELIVERY", "PENDING"),
        ("FAILED_DELIVERY", "DELIVERED"),
    )
)


def upgrade() -> None:
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("event_schema_version", sa.Text(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actor_type", sa.Text(), nullable=False),
        sa.Column("actor_id", sa.Text(), nullable=False),
        sa.Column("command_type", sa.Text(), nullable=False),
        sa.Column("command_id", sa.Uuid(), nullable=False),
        sa.Column("commit_id", sa.Uuid(), nullable=False),
        sa.Column("correlation_id", sa.Uuid(), nullable=False),
        sa.Column("causation_id", sa.Uuid(), nullable=True),
        sa.Column("target_refs", sa.ARRAY(sa.Text()), nullable=False, server_default="{}"),
        sa.Column("authority_source_ref", sa.Uuid(), nullable=False),
        sa.Column("result", sa.Text(), nullable=False),
        sa.Column("human_decision_ref", sa.Uuid(), nullable=True),
        sa.Column("evidence_set_ref", sa.Uuid(), nullable=True),
        sa.Column("state_before_ref", sa.Text(), nullable=True),
        sa.Column("state_after_ref", sa.Text(), nullable=True),
        sa.Column("failure_code", sa.Text(), nullable=True),
        sa.Column("metadata_ref", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_audit_events"),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name="fk_audit_events_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["command_id", "workspace_id"],
            ["commands.id", "commands.workspace_id"],
            name="fk_audit_events_command_workspace",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint("event_type <> ''", name="ck_audit_events_event_type_nonempty"),
        sa.CheckConstraint(
            "event_schema_version ~ '^[0-9]+(\\.[0-9]+)*$'",
            name="ck_audit_events_event_schema_version_shape",
        ),
        sa.CheckConstraint("actor_type <> ''", name="ck_audit_events_actor_type_nonempty"),
        sa.CheckConstraint("actor_id <> ''", name="ck_audit_events_actor_id_nonempty"),
        sa.CheckConstraint("command_type <> ''", name="ck_audit_events_command_type_nonempty"),
        sa.CheckConstraint(
            "result IN (" + ", ".join(f"'{r}'" for r in _AUDIT_RESULTS) + ")",
            name="ck_audit_events_result_vocabulary",
        ),
    )
    op.create_index("ix_audit_events_workspace", "audit_events", ["workspace_id"])
    op.create_index("ix_audit_events_correlation", "audit_events", ["correlation_id"])
    op.create_index("ix_audit_events_command", "audit_events", ["command_id"])

    op.create_table(
        "outbox_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("event_id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("commit_id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("event_payload_ref", sa.Text(), nullable=True),
        sa.Column("delivery_status", sa.Text(), nullable=False),
        sa.Column("delivery_attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_outbox_events"),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name="fk_outbox_events_workspace",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("event_id", name="uq_outbox_events_event_id"),
        sa.CheckConstraint("event_type <> ''", name="ck_outbox_events_event_type_nonempty"),
        sa.CheckConstraint(
            "delivery_status IN (" + ", ".join(f"'{s}'" for s in _DELIVERY_STATUSES) + ")",
            name="ck_outbox_events_delivery_status_vocabulary",
        ),
        sa.CheckConstraint(
            "delivery_attempt_count >= 0", name="ck_outbox_events_delivery_attempt_count_valid"
        ),
        sa.CheckConstraint(
            "(delivery_status = 'DELIVERED') = (delivered_at IS NOT NULL)",
            name="ck_outbox_events_delivered_at_requires_delivered",
        ),
    )
    op.create_index("ix_outbox_events_workspace", "outbox_events", ["workspace_id"])
    op.create_index("ix_outbox_events_delivery_status", "outbox_events", ["delivery_status"])

    # Trigger 1: audit_events is immutable against BOTH UPDATE and
    # DELETE (09 section 58.1, 11 section 35).
    op.execute(
        """
        CREATE FUNCTION trg_audit_events_reject_update() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION
                'audit_events rows are append-only; a correction creates a new '
                'audit event (09 section 58.1)';
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_audit_events_reject_update
        BEFORE UPDATE ON audit_events
        FOR EACH ROW EXECUTE FUNCTION trg_audit_events_reject_update();
        """
    )
    op.execute(
        """
        CREATE FUNCTION trg_audit_events_reject_delete() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION
                'audit_events rows cannot be deleted; established audit history is '
                'append-only (11 section 35)';
            RETURN OLD;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_audit_events_reject_delete
        BEFORE DELETE ON audit_events
        FOR EACH ROW EXECUTE FUNCTION trg_audit_events_reject_delete();
        """
    )

    # Trigger 2: only delivery-tracking fields on outbox_events are
    # ever legitimately mutable (14 section 7.1's write-owner split).
    op.execute(
        """
        CREATE FUNCTION trg_outbox_events_enforce_identity_immutable() RETURNS trigger AS $$
        BEGIN
            IF NEW.event_id IS DISTINCT FROM OLD.event_id
                OR NEW.workspace_id IS DISTINCT FROM OLD.workspace_id
                OR NEW.commit_id IS DISTINCT FROM OLD.commit_id
                OR NEW.event_type IS DISTINCT FROM OLD.event_type
                OR NEW.event_payload_ref IS DISTINCT FROM OLD.event_payload_ref
                OR NEW.created_at IS DISTINCT FROM OLD.created_at
            THEN
                RAISE EXCEPTION
                    'outbox_events identity/content fields are immutable once set '
                    '(14 section 7.1)';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_outbox_events_enforce_identity_immutable
        BEFORE UPDATE ON outbox_events
        FOR EACH ROW EXECUTE FUNCTION trg_outbox_events_enforce_identity_immutable();
        """
    )

    # Trigger 3: 09 section 15's own delivery-status topology.
    op.execute(
        f"""
        CREATE FUNCTION trg_outbox_events_enforce_delivery_transition() RETURNS trigger AS $$
        BEGIN
            IF OLD.delivery_status = 'DELIVERED' THEN
                RAISE EXCEPTION
                    'outbox_events delivery_status DELIVERED is terminal (09 section 15)';
            END IF;
            IF NEW.delivery_status IS DISTINCT FROM OLD.delivery_status THEN
                IF NOT ((OLD.delivery_status, NEW.delivery_status) IN
                    ({_LEGAL_DELIVERY_TRANSITIONS_SQL})) THEN
                    RAISE EXCEPTION
                        'illegal outbox delivery_status transition % -> % (09 section 15)',
                        OLD.delivery_status, NEW.delivery_status;
                END IF;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_outbox_events_enforce_delivery_transition
        BEFORE UPDATE ON outbox_events
        FOR EACH ROW EXECUTE FUNCTION trg_outbox_events_enforce_delivery_transition();
        """
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_outbox_events_enforce_delivery_transition ON outbox_events;"
    )
    op.execute("DROP FUNCTION IF EXISTS trg_outbox_events_enforce_delivery_transition();")
    op.execute(
        "DROP TRIGGER IF EXISTS trg_outbox_events_enforce_identity_immutable ON outbox_events;"
    )
    op.execute("DROP FUNCTION IF EXISTS trg_outbox_events_enforce_identity_immutable();")
    op.execute("DROP TRIGGER IF EXISTS trg_audit_events_reject_delete ON audit_events;")
    op.execute("DROP FUNCTION IF EXISTS trg_audit_events_reject_delete();")
    op.execute("DROP TRIGGER IF EXISTS trg_audit_events_reject_update ON audit_events;")
    op.execute("DROP FUNCTION IF EXISTS trg_audit_events_reject_update();")
    op.drop_index("ix_outbox_events_delivery_status", table_name="outbox_events")
    op.drop_index("ix_outbox_events_workspace", table_name="outbox_events")
    op.drop_table("outbox_events")
    op.drop_index("ix_audit_events_command", table_name="audit_events")
    op.drop_index("ix_audit_events_correlation", table_name="audit_events")
    op.drop_index("ix_audit_events_workspace", table_name="audit_events")
    op.drop_table("audit_events")
