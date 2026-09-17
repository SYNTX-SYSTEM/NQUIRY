"""semantic identity workspace

Revision ID: 72e4c8ea6772
Revises:
Create Date: 2026-09-17 15:55:01.373201

PKG-01 scope (14_IMPLEMENTATION_SEQUENCE.md §9: "001_semantic_identity_workspace |
creates: users, workspaces | depends on: none"). Minimal column set actually
used by PKG-01 (14 §7.1/§7.2, 02 §5/§6, 04 AC-04-001):

- `users`: canonical identity reference (14 §7.1: "Workspace key: no").
  `role`/`organization_id`/`preferences` from 02 §5.2's LEVEL-1 field list
  are deliberately deferred: `role` is explicitly non-authoritative
  (04 §4: "User.role remains underdefined and is not used as the
  authoritative Workspace permission role") and `organization_id` depends
  on the still-open GAP-01-001 (Tenant vs Workspace semantics). Adding
  unused columns now would be exactly the "future-generic abstraction"
  PKG-01's prompt forbids.
- `workspaces`: canonical, Workspace-key "yes, self" (14 §7.1). `owner_id`
  is mandatory and FK-constrained to `users.id`: 04 AC-04-001 establishes
  `Workspace.owner_id` as the root human governance authority for that
  Workspace, so the column must exist even though PKG-01 does not yet
  implement any governance behavior over it.

No cascading delete (14 §49: "Default is restrictive foreign-key
behavior"). Schema downgrade here is infrastructure rollback only, not
domain rollback (14 §9).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "72e4c8ea6772"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("record_version", sa.BigInteger(), nullable=False, server_default="1"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.CheckConstraint("record_version >= 1", name="ck_users_record_version_positive"),
    )

    op.create_table(
        "workspaces",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("record_version", sa.BigInteger(), nullable=False, server_default="1"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("id", name="pk_workspaces"),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
            name="fk_workspaces_owner_id_users",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint("record_version >= 1", name="ck_workspaces_record_version_positive"),
    )
    op.create_index("ix_workspaces_owner_id", "workspaces", ["owner_id"])


def downgrade() -> None:
    op.drop_index("ix_workspaces_owner_id", table_name="workspaces")
    op.drop_table("workspaces")
    op.drop_table("users")
