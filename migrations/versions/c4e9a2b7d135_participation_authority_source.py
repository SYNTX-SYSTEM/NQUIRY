"""PARTICIPATION as a typed authority source on audit_events

Revision ID: c4e9a2b7d135
Revises: b3d8e5f0a2c7
Create Date: 2026-09-24 00:00:02.000000

F03 WU-03.1 (HD-15, 16 §41 REC-016 / NQ-DEC-043; FBR-F03-5). The effect gate
gains a fourth typed authority source, PARTICIPATION (ref =
`session_participations.id`, scope `SESSION:<uuid>`), the source-explicit
question-submission right of 04 AUTH-DEP-Q-001. Only the closed CHECK on
`audit_events.authority_source_type` changes. Historical rows are untouched
(audit_events rejects UPDATE by trigger), and every existing row still
satisfies the wider vocabulary.
"""

from __future__ import annotations

from alembic import op

revision = "c4e9a2b7d135"
down_revision = "b3d8e5f0a2c7"
branch_labels = None
depends_on = None

_OLD = "authority_source_type IS NULL OR authority_source_type IN ('BINDING','ROLE','FOUNDING')"
_NEW = (
    "authority_source_type IS NULL OR authority_source_type IN "
    "('BINDING','ROLE','FOUNDING','PARTICIPATION')"
)


def upgrade() -> None:
    op.drop_constraint("ck_audit_events_authority_source_type", "audit_events", type_="check")
    op.create_check_constraint("ck_audit_events_authority_source_type", "audit_events", _NEW)


def downgrade() -> None:
    op.drop_constraint("ck_audit_events_authority_source_type", "audit_events", type_="check")
    op.create_check_constraint("ck_audit_events_authority_source_type", "audit_events", _OLD)
