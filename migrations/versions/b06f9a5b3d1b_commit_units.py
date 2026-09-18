"""commit units

Revision ID: b06f9a5b3d1b
Revises: 6119c9dcf073
Create Date: 2026-09-18 18:00:00.000000

PKG-13 scope (14_IMPLEMENTATION_SEQUENCE.md section 9's conceptual
"009_commit_audit_outbox" bucket lists "creates: commit_units,
audit_events, outbox_events | depends on: 008" as one summary row.
PKG-12 materialized the audit_events/outbox_events half; this migration
completes the bucket with `commit_units` -- the same
one-conceptual-bucket-across-two-Alembic-revisions split PKG-02/PKG-05,
PKG-06/PKG-07, and PKG-10/PKG-11 already established, applied a fourth
time by PKG-12/PKG-13.

No `governed_commit_writer` DB principal or GRANT is created here. 14
section 7.1 names it as the eventual exclusive write owner of this
table (and, per 11's own security model, of every canonical/governance/
audit/outbox table this commit atomically touches), but every
DB-principal/GRANT/RLS change in this codebase so far has been deferred
to migration `012_security_events_rls` -- consistent with every
migration since `001`.

Table created:

- `commit_units` (09 section 13, 14 section 7.1): the operational proof
  record of one governed persistence attempt. Columns map 09 section
  13's field list exactly (`commit_id` as this table's own `id`).
  `UNIQUE(id, workspace_id)` is the same composite-FK anchor pattern
  every prior migration has used -- here it is itself the *target* of
  four retrofitted composite FKs (below), not merely a source.

  `outcome` is CHECK-constrained to 09 section 13's exact 3-value
  closed vocabulary (`FAILED_PRECOMMIT`, `COMMITTED`, `INDETERMINATE`)
  -- deliberately *not* the same 4 values as `command_attempts.outcome`
  (no `DENIED` -- a denied request never produces a CommitUnit at all)
  nor the same 4 as `idempotency_records.outcome` (no `IN_PROGRESS` --
  a CommitUnit is only ever written once an attempt has resolved to one
  of these 3 terminal shapes). See `packages/commit/coordinator.py`'s
  own module docstring for why these are three genuinely distinct
  vocabularies, not a copy-paste of one into another.

  `target_refs`/`relation_refs`/`governance_refs` (opaque ref arrays)
  and `audit_event_ids`/`outbox_ids` (identity arrays) reuse the same
  `ARRAY(TEXT)`/`ARRAY(UUID)` technical choice `audit_events.target_refs`
  (PKG-12) already established for an unbounded opaque-ref list, rather
  than a normalized join table -- 14 does not specify a separate
  relation table for any of these, and a CommitUnit's own reference list
  is fixed at the moment it is written, never queried by an individual
  ref the way `command_attempts`/`idempotency_records` are queried by
  their own primary identities.

  `commit_time_proof_ref` carries no foreign key: no persisted
  `BoundaryProof`/`AuthorityResolutionProof` table exists anywhere in
  this codebase (both remain in-memory dataclasses, PKG-08/PKG-03) --
  disclosed as an opaque, currently-unpopulated reference, the same
  treatment `command.envelope.CommandEnvelope.authority_context_ref`
  already established for a comparable forward-reference gap.

Retrofit: composite FKs from `commit_id` on four predecessor tables
-----------------------------------------------------------------------
`command_attempts.commit_id` (PKG-10), `idempotency_records.commit_id`
(PKG-11), `audit_events.commit_id` and `outbox_events.commit_id`
(PKG-12) were each created nullable with no foreign key, every one of
those migrations' own docstrings disclosing "commit_units does not
exist until PKG-13's own migration revision" as the explicit reason.
This migration closes that forward reference exactly as disclosed --
the same additive-retrofit pattern `d8a1147fde30` (PKG-07) already
established for `uq_sessions_id_workspace` on `sessions`. All four
retrofitted FKs are composite `(commit_id, workspace_id) ->
commit_units(id, workspace_id)`, since all four tables already carry
their own `workspace_id` column -- a CommitUnit referenced from a
different Workspace than the one it was actually written under becomes
structurally unrepresentable, the identical cross-Workspace-reference
defense every composite FK in this codebase already provides. The
columns remain nullable (a `command_attempts`/`idempotency_records` row
legitimately has no `commit_id` at all until/unless its attempt
actually reaches a determined outcome -- see each table's own prior
migration for why).

No cascading delete anywhere (14 section 49 default). Schema downgrade
is infrastructure rollback only, not domain rollback (14 section 9).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b06f9a5b3d1b"
down_revision: str | None = "6119c9dcf073"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# 09 section 13's exact 3-value closed vocabulary.
_COMMIT_OUTCOMES = ("FAILED_PRECOMMIT", "COMMITTED", "INDETERMINATE")


def upgrade() -> None:
    op.create_table(
        "commit_units",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("command_id", sa.Uuid(), nullable=False),
        sa.Column("attempt_id", sa.Uuid(), nullable=False),
        sa.Column("target_refs", sa.ARRAY(sa.Text()), nullable=False, server_default="{}"),
        sa.Column("relation_refs", sa.ARRAY(sa.Text()), nullable=False, server_default="{}"),
        sa.Column("governance_refs", sa.ARRAY(sa.Text()), nullable=False, server_default="{}"),
        sa.Column("audit_event_ids", sa.ARRAY(sa.Uuid()), nullable=False, server_default="{}"),
        sa.Column("outbox_ids", sa.ARRAY(sa.Uuid()), nullable=False, server_default="{}"),
        sa.Column("commit_time_proof_ref", sa.Uuid(), nullable=True),
        sa.Column("committed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("outcome", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_commit_units"),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name="fk_commit_units_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["command_id", "workspace_id"],
            ["commands.id", "commands.workspace_id"],
            name="fk_commit_units_command_workspace",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["attempt_id"],
            ["command_attempts.id"],
            name="fk_commit_units_attempt",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("id", "workspace_id", name="uq_commit_units_id_workspace"),
        sa.CheckConstraint(
            "outcome IN (" + ", ".join(f"'{o}'" for o in _COMMIT_OUTCOMES) + ")",
            name="ck_commit_units_outcome_vocabulary",
        ),
    )
    op.create_index("ix_commit_units_workspace", "commit_units", ["workspace_id"])
    op.create_index("ix_commit_units_command", "commit_units", ["command_id"])

    op.create_foreign_key(
        "fk_command_attempts_commit_workspace",
        "command_attempts",
        "commit_units",
        ["commit_id", "workspace_id"],
        ["id", "workspace_id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_idempotency_records_commit_workspace",
        "idempotency_records",
        "commit_units",
        ["commit_id", "workspace_id"],
        ["id", "workspace_id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_audit_events_commit_workspace",
        "audit_events",
        "commit_units",
        ["commit_id", "workspace_id"],
        ["id", "workspace_id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_outbox_events_commit_workspace",
        "outbox_events",
        "commit_units",
        ["commit_id", "workspace_id"],
        ["id", "workspace_id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint("fk_outbox_events_commit_workspace", "outbox_events", type_="foreignkey")
    op.drop_constraint("fk_audit_events_commit_workspace", "audit_events", type_="foreignkey")
    op.drop_constraint(
        "fk_idempotency_records_commit_workspace", "idempotency_records", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_command_attempts_commit_workspace", "command_attempts", type_="foreignkey"
    )
    op.drop_index("ix_commit_units_command", table_name="commit_units")
    op.drop_index("ix_commit_units_workspace", table_name="commit_units")
    op.drop_table("commit_units")
