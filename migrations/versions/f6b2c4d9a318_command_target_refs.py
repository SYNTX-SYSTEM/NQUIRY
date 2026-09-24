"""commands.target_refs: a persisted link from a Command to what it targets

Revision ID: f6b2c4d9a318
Revises: e5a1b3c8f204
Create Date: 2026-09-24 00:00:04.000000

F03 WU-03.4 (FBR-F03-3). TRN-BURST-005: "No capture write acknowledged to the
user remains unresolved." 06 BND-008: "Capture uncertainty blocks Burst
completion." A capture attempt that is IN_PROGRESS or INDETERMINATE has no
persisted link to its Burst (`commands` carried no target refs; audit exists
only for commits), so completion could not tell it existed. 09 §9 makes
`target_refs` part of the CommandEnvelope. It is now persisted with the
immutable Command row (`commands` rejects UPDATE, so it is written once, at
birth). Rows written before this revision carry an empty array: their targets
were never recorded and are not guessed.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "f6b2c4d9a318"
down_revision = "e5a1b3c8f204"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "commands",
        sa.Column(
            "target_refs",
            sa.ARRAY(sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::text[]"),
        ),
    )
    op.create_index(
        "ix_commands_target_refs", "commands", ["target_refs"], postgresql_using="gin"
    )


def downgrade() -> None:
    op.drop_index("ix_commands_target_refs", table_name="commands")
    op.drop_column("commands", "target_refs")
