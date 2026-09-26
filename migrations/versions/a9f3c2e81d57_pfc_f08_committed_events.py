"""PFC F08-1: the durable, immutable committed Event basis

Revision ID: a9f3c2e81d57
Revises: e7c1d4a9b206
Create Date: 2026-09-26 00:00:00.000000

WU-PFC-F08-1. FIRST BROKEN RELATION: CommitUnit -> durable immutable Event
basis. `outbox_events` is delivery bookkeeping only (09 section 15); nothing
durably holds `aggregate_ref`, `aggregate_version_after_commit` or `payload`,
so no exact EventEnvelope (09 section 16) can be reconstructed
(19 section 28 HISTORICAL EVENT BASIS).

STORAGE FREEDOM choice (19 section 28: "separate committed event table"):
one `committed_events` row per outbox row, written by CommitCoordinator in the
same CommitUnit transaction. It holds the 14 EventEnvelope fields exactly.

Structural guarantees:
- `event_id` references `outbox_events(event_id)`, and `(commit_id,
  workspace_id)` references `commit_units`. An Event cannot exist without its
  commit and its outbox record (AC-09-003, events are post-commit facts).
- BEFORE INSERT: the outbox row named by `event_id` must carry the same
  `workspace_id`, `commit_id` and `event_type`, so the two records can never
  describe different facts.
- BEFORE UPDATE / BEFORE DELETE: rejected (09 section 72: "Correction: new
  event, not: edit historical event").
- `aggregate_version_after_commit >= 1`; `payload` is a JSON object.

Principals (14 section 8, migration 2feb99a01f9d): `governed_commit_writer`
may INSERT and SELECT only, never UPDATE or DELETE. `api_reader`,
`projection_writer` and `audit_reader` may SELECT. `test_principal` gets the
same grants as on every protected table.

Rows committed before this revision have no basis. None is backfilled:
`aggregate_ref`, version and payload of past commits are not recoverable
without guesswork (10 section 17), so those outbox rows stay unresolvable
(`EventBasisMissing`).
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "a9f3c2e81d57"
down_revision = "e7c1d4a9b206"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "committed_events",
        sa.Column("event_id", sa.Uuid(), primary_key=True),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("event_schema_version", sa.Text(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "workspace_id",
            sa.Uuid(),
            sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("aggregate_ref", sa.Text(), nullable=False),
        sa.Column("aggregate_version_after_commit", sa.BigInteger(), nullable=False),
        sa.Column("command_id", sa.Uuid(), nullable=False),
        sa.Column("commit_id", sa.Uuid(), nullable=False),
        sa.Column("correlation_id", sa.Uuid(), nullable=False),
        sa.Column("causation_id", sa.Uuid(), nullable=True),
        sa.Column("actor_ref", sa.Text(), nullable=False),
        sa.Column("authority_source_ref", sa.Uuid(), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.ForeignKeyConstraint(
            ["event_id"],
            ["outbox_events.event_id"],
            name="fk_committed_events_outbox_event",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["commit_id", "workspace_id"],
            ["commit_units.id", "commit_units.workspace_id"],
            name="fk_committed_events_commit_workspace",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "aggregate_version_after_commit >= 1",
            name="ck_committed_events_aggregate_version_positive",
        ),
        sa.CheckConstraint(
            "jsonb_typeof(payload) = 'object'", name="ck_committed_events_payload_object"
        ),
        sa.CheckConstraint("event_type <> ''", name="ck_committed_events_event_type_nonempty"),
        sa.CheckConstraint(
            "aggregate_ref ~ '^[a-z_]+:[0-9a-f-]{36}$'",
            name="ck_committed_events_aggregate_ref_shape",
        ),
    )
    op.create_index("ix_committed_events_workspace", "committed_events", ["workspace_id"])
    op.create_index(
        "ix_committed_events_aggregate",
        "committed_events",
        ["aggregate_ref", "aggregate_version_after_commit"],
    )

    op.execute(
        """
        CREATE FUNCTION trg_committed_events_bind_outbox() RETURNS trigger AS $$
        DECLARE
            o outbox_events%ROWTYPE;
        BEGIN
            SELECT * INTO o FROM outbox_events WHERE event_id = NEW.event_id;
            IF NOT FOUND
               OR o.workspace_id <> NEW.workspace_id
               OR o.commit_id <> NEW.commit_id
               OR o.event_type <> NEW.event_type
               OR o.created_at <> NEW.occurred_at THEN
                RAISE EXCEPTION
                    'committed_events.% must describe exactly the outbox record of the '
                    'same event_id (workspace, commit, event_type, time)', NEW.event_id;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_committed_events_bind_outbox
        BEFORE INSERT ON committed_events
        FOR EACH ROW EXECUTE FUNCTION trg_committed_events_bind_outbox();
        """
    )
    op.execute(
        """
        CREATE FUNCTION trg_committed_events_reject_change() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION
                'committed_events rows are immutable historical facts; a correction '
                'is a new event (09 section 72)';
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_committed_events_reject_change
        BEFORE UPDATE OR DELETE ON committed_events
        FOR EACH ROW EXECUTE FUNCTION trg_committed_events_reject_change();
        """
    )

    op.execute("GRANT SELECT, INSERT ON committed_events TO governed_commit_writer")
    op.execute("GRANT SELECT ON committed_events TO api_reader")
    op.execute("GRANT SELECT ON committed_events TO projection_writer")
    op.execute("GRANT SELECT ON committed_events TO audit_reader")
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON committed_events TO test_principal")


def downgrade() -> None:
    op.execute("REVOKE ALL ON committed_events FROM test_principal")
    op.execute("REVOKE ALL ON committed_events FROM audit_reader")
    op.execute("REVOKE ALL ON committed_events FROM projection_writer")
    op.execute("REVOKE ALL ON committed_events FROM api_reader")
    op.execute("REVOKE ALL ON committed_events FROM governed_commit_writer")
    op.execute("DROP TRIGGER trg_committed_events_reject_change ON committed_events")
    op.execute("DROP FUNCTION trg_committed_events_reject_change()")
    op.execute("DROP TRIGGER trg_committed_events_bind_outbox ON committed_events")
    op.execute("DROP FUNCTION trg_committed_events_bind_outbox()")
    op.drop_index("ix_committed_events_aggregate", table_name="committed_events")
    op.drop_index("ix_committed_events_workspace", table_name="committed_events")
    op.drop_table("committed_events")
