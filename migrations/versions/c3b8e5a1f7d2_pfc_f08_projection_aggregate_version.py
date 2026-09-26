"""PFC F08-2: projections remember the aggregate version they reflect

Revision ID: c3b8e5a1f7d2
Revises: a9f3c2e81d57
Create Date: 2026-09-26 00:00:01.000000

WU-PFC-F08-2. Once events are delivered at least once (09 section 15.2) and
failed deliveries are retried later (10 section 17), an older event of an
aggregate can arrive after a newer one. `projection.consumer` deduplicated
only on `last_event_id` equality, so a late retry would overwrite a newer
projected state with an older one: a projection inconsistency created by
delivery itself.

Both read models record the `aggregate_version_after_commit` (09 section 16)
of the event they currently reflect. The consumer never applies an event whose
aggregate version is lower (09 section 74: redelivery must not duplicate or
regress projection rows).

Nullable: the projection tables are derived and rebuildable (AS-007). Rows
projected before this revision simply have no recorded version until their
next event or a rebuild. No canonical table is touched.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "c3b8e5a1f7d2"
down_revision = "a9f3c2e81d57"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "session_read_model", sa.Column("last_aggregate_version", sa.BigInteger(), nullable=True)
    )
    op.add_column(
        "inquiry_read_model", sa.Column("last_aggregate_version", sa.BigInteger(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("inquiry_read_model", "last_aggregate_version")
    op.drop_column("session_read_model", "last_aggregate_version")
