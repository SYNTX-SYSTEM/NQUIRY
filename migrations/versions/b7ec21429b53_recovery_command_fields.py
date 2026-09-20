"""recovery command fields

Revision ID: b7ec21429b53
Revises: fb881bc022b1
Create Date: 2026-09-20 16:00:00.000000

PKG-24 scope (14_IMPLEMENTATION_SEQUENCE.md section 9's own
`011_recovery` bucket -- PKG-23 built `recovery_records` itself; this
migration is 14's own explicitly named "persistence migration 011
completion" for PKG-24: "RecoveryRecord and explicit dependency/block
refs as mapped by 14").

Columns added to `recovery_records`:

- `record_version` (`BIGINT NOT NULL DEFAULT 1`): 14 section 7.1's own
  core-tables row for `recovery_records` names its Version column
  literally as "record_version" -- PKG-23's own migration disclosed no
  such column (a genuine, now-closed gap in that package's own field
  list, which followed 10 section 63's "Minimum semantics" list
  literally; that list has no version field of its own). This
  retrofit, not a new invention, gives the deterministic Recovery
  Command a real optimistic-concurrency value to compare, the same
  role `record_version` plays on every other governed-mutation table.
- `blocked_target_refs` (`TEXT[] NOT NULL DEFAULT '{}'`): 14 section 29's
  own "dependency blocking metadata tied to the affected command/
  target/dependency graph" -- the ORIGINAL failed operation's own
  target refs this RecoveryRecord's own existence (while UNRESOLVED)
  blocks. Deliberately NOT a separate join table: "is target X
  blocked" is answered by `result = 'UNRESOLVED' AND :target_ref = ANY
  (blocked_target_refs)` against this same table -- once a record
  resolves, `result` leaves `UNRESOLVED` and every one of its own
  formerly-blocked refs is automatically excluded from that predicate
  without any separate "unblock" write, migration, or table.

No new trigger: the existing identity-immutability trigger (PKG-23)
does not reference either new column (both are legitimately mutable
over the record's own lifecycle -- 10 section 65's own "may accumulate
new findings"), and the existing result-transition trigger already
governs `result` alone, unaffected by this migration.

No `recovery_reader`/any `RecoveryRepository` DB-principal GRANT is
created here, consistent with every migration since `001` (deferred to
`012_security_events_rls`). Schema downgrade is infrastructure rollback
only, not domain rollback (14 section 9).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b7ec21429b53"
down_revision: str | None = "fb881bc022b1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "recovery_records",
        sa.Column("record_version", sa.BigInteger(), nullable=False, server_default="1"),
    )
    op.add_column(
        "recovery_records",
        sa.Column(
            "blocked_target_refs", postgresql.ARRAY(sa.Text()), nullable=False, server_default="{}"
        ),
    )
    op.create_check_constraint(
        "ck_recovery_records_record_version_positive",
        "recovery_records",
        "record_version >= 1",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_recovery_records_record_version_positive", "recovery_records", type_="check"
    )
    op.drop_column("recovery_records", "blocked_target_refs")
    op.drop_column("recovery_records", "record_version")
