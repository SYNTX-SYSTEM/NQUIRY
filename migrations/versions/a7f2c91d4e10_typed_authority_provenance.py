"""typed authority provenance on audit_events

Revision ID: a7f2c91d4e10
Revises: 05794035ef3c
Create Date: 2026-09-24 00:00:00.000000

F02 WU-02.6 (HD-6, 16 §41 REC-004 / NQ-DEC-034). `audit_events.
authority_source_ref` was an untyped UUID, and `CommitCoordinator` filled
it with a fresh `uuid.uuid4()` whenever no binding existed. Such a
reference pointed at nothing. Two columns make the reference typed and
reconstructable:

- `authority_source_type`: BINDING (ref = human_authority_bindings.id),
  ROLE (ref = role_assignments.id) or FOUNDING (ref = commands.id of the
  HARD-DEP-001 Option-A founding Command).
- `authority_scope_ref`: the exact scope the authority was proven at,
  e.g. `SESSION:<uuid>`, `WORKSPACE:<uuid>`.

Both are NULLABLE: rows written before this revision are historical and
immutable (audit_events rejects UPDATE by trigger). NULL therefore means
"pre-F02, untyped". Such a ref may be fabricated and is not reconstructable
as authority provenance. Every row written from this revision on carries
both (enforced by `CommitCoordinator`, which cannot produce an ALLOW
without an `AuthoritySourceProof`).
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "a7f2c91d4e10"
down_revision = "05794035ef3c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("audit_events", sa.Column("authority_source_type", sa.Text(), nullable=True))
    op.add_column("audit_events", sa.Column("authority_scope_ref", sa.Text(), nullable=True))
    op.create_check_constraint(
        "ck_audit_events_authority_source_type",
        "audit_events",
        "authority_source_type IS NULL OR authority_source_type IN ('BINDING','ROLE','FOUNDING')",
    )
    op.create_check_constraint(
        "ck_audit_events_typed_source_has_scope",
        "audit_events",
        "(authority_source_type IS NULL) = (authority_scope_ref IS NULL)",
    )


def downgrade() -> None:
    op.drop_constraint("ck_audit_events_typed_source_has_scope", "audit_events", type_="check")
    op.drop_constraint("ck_audit_events_authority_source_type", "audit_events", type_="check")
    op.drop_column("audit_events", "authority_scope_ref")
    op.drop_column("audit_events", "authority_source_type")
