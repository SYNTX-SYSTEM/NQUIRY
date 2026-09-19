"""projection

Revision ID: 1bc6021cb651
Revises: 7c2e8a4f1d6b
Create Date: 2026-09-20 12:00:00.000000

PKG-21 scope (14_IMPLEMENTATION_SEQUENCE.md section 9:
"010_projection | read models, checkpoints | depends on: 009 | gate:
rebuild tests"). First migration in Phase 8 (Event/Projection); PKG-20
built the outbox delivery half, this one builds the projection-read
half.

Tables created:

- `projection_checkpoints` (14 section 7.1: "projection | Workspace
  key: yes | checkpoint version | projection_writer"). Composite
  primary key `(projection_name, workspace_id)` -- no surrogate id,
  the same "natural composite key, no surrogate" precedent
  `idempotency_records` already established (PKG-11). `checkpoint_version`
  is a plain `BIGINT` counter, deliberately NOT a `RecordVersion` reuse
  (see `packages/projection/models.py`'s own docstring for why: it
  counts applied Events for one projection, not a canonical row's
  optimistic-concurrency version). `last_processed_event_id` is
  nullable (a fresh projection that has processed nothing yet has no
  event to name) and carries no foreign key -- `outbox_events`/
  `commit_units` composite identity is `(id, workspace_id)`, but an
  `EventEnvelope.event_id` (09 section 16) is a distinct identity from
  `outbox_events.id`, and no table in this schema is keyed by
  `event_id` alone.

- `session_read_model` (14 section 7.1, same row). One row per Session,
  keyed by the SAME `session_id` as the canonical `sessions` row it
  mirrors -- a real composite foreign key to `sessions(id, workspace_id)`
  is the structural defense for the mandatory "corrupt projection"
  adversarial attack: a `SessionReadModel` claiming a Workspace that
  does not match the real Session's own Workspace is rejected by the
  database, not merely by application convention.
  `current_state`/`projection_version` are plain `TEXT`/`BIGINT` --
  `packages/projection` cannot import `domain.session.SessionState`
  (14 section 3.1's own allow-list excludes `domain`), the same
  "closed vocabulary enforced elsewhere, held as inert string here"
  pattern `audit_events.result` already established (PKG-12).

- `inquiry_read_model` (14 section 7.1, same row). A deliberately
  generic per-aggregate snapshot (`aggregate_ref` + `JSONB snapshot`),
  NOT the full InquiryGraph -- 12_MINIMUM_PROTOTYPE_ARCHITECTURE.md
  explicitly excludes that graph from this build's required proof
  ("Full Inquiry Graph | EXCLUDED | Projection semantics not required
  for proof"; "DEC-A001 | graph scope | later"). `UNIQUE(aggregate_ref,
  workspace_id)` is this table's own natural key (no canonical table
  it could carry a composite foreign key into, since `aggregate_ref`
  spans multiple, structurally different aggregate classes by design).

No `projection_writer` DB-principal/GRANT is created here, consistent
with every migration since `001` (deferred to `012_security_events_rls`).
No cascading delete anywhere (14 section 49 default). Schema downgrade
is infrastructure rollback only, not domain rollback (14 section 9) --
dropping these tables never un-applies a canonical mutation, since
projection state was never authoritative to begin with (AS-007, 02/09).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "1bc6021cb651"
down_revision: str | None = "7c2e8a4f1d6b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "projection_checkpoints",
        sa.Column("projection_name", sa.Text(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("last_processed_event_id", sa.Uuid(), nullable=True),
        sa.Column("checkpoint_version", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint(
            "projection_name", "workspace_id", name="pk_projection_checkpoints"
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name="fk_projection_checkpoints_workspace",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "checkpoint_version >= 0", name="ck_projection_checkpoints_version_nonnegative"
        ),
    )

    op.create_table(
        "session_read_model",
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("current_state", sa.Text(), nullable=False),
        sa.Column("projection_version", sa.BigInteger(), nullable=False),
        sa.Column("last_event_id", sa.Uuid(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("session_id", name="pk_session_read_model"),
        sa.ForeignKeyConstraint(
            ["session_id", "workspace_id"],
            ["sessions.id", "sessions.workspace_id"],
            name="fk_session_read_model_session_workspace",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "projection_version >= 1", name="ck_session_read_model_version_positive"
        ),
    )
    op.create_index("ix_session_read_model_workspace", "session_read_model", ["workspace_id"])

    op.create_table(
        "inquiry_read_model",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("aggregate_ref", sa.Text(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("projection_version", sa.BigInteger(), nullable=False),
        sa.Column("snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("last_event_id", sa.Uuid(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_inquiry_read_model"),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name="fk_inquiry_read_model_workspace",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "aggregate_ref", "workspace_id", name="uq_inquiry_read_model_aggregate_workspace"
        ),
        sa.CheckConstraint(
            "projection_version >= 1", name="ck_inquiry_read_model_version_positive"
        ),
    )
    op.create_index("ix_inquiry_read_model_workspace", "inquiry_read_model", ["workspace_id"])


def downgrade() -> None:
    op.drop_index("ix_inquiry_read_model_workspace", table_name="inquiry_read_model")
    op.drop_table("inquiry_read_model")

    op.drop_index("ix_session_read_model_workspace", table_name="session_read_model")
    op.drop_table("session_read_model")

    op.drop_table("projection_checkpoints")
