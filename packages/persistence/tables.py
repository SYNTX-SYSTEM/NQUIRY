"""SQLAlchemy Core table definitions matching the migration DDL.

These are query-time table definitions, deliberately separate from
`migrations/versions/72e4c8ea6772_semantic_identity_workspace.py`'s own
explicit DDL: a migration is an immutable historical record (14 §9)
and must not depend on application code that changes after the
migration is written. Duplication between a migration's DDL and its
matching query-time `Table` object is the standard SQLAlchemy/Alembic
pattern, not an architecture violation.

Column set matches the migration exactly. See
`72e4c8ea6772_semantic_identity_workspace.py`'s docstring for why
`role`/`organization_id`/`preferences` are absent from `users`, and why
`workspaces.owner_id` is mandatory. See
`01a37c093cd6_membership_governance.py`'s docstring for
`workspace_memberships`/`role_assignments`/`human_authority_bindings`
(including why `facilitator_scope_bindings` is deliberately absent) and
for the two triggers that migration attaches to
`human_authority_bindings` (not representable as SQLAlchemy Core
`Table` metadata — they are pure database-side enforcement, invisible
to and unaffected by this module). See
`d467112ce46d_challenge_session.py`'s docstring for `challenges`/
`sessions` — including why neither `status` nor
`emotional_temperature` exists on `challenges`, why `sessions` carries
a *composite* foreign key into `challenges`, and for the two further
triggers enforcing 03's transition topology, likewise invisible here.
"""

from __future__ import annotations

import sqlalchemy as sa

metadata = sa.MetaData()

users_table = sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column("email", sa.Text(), nullable=False, unique=True),
    sa.Column("name", sa.Text(), nullable=False),
    sa.Column("record_version", sa.BigInteger(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
)

workspaces_table = sa.Table(
    "workspaces",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column("name", sa.Text(), nullable=False),
    sa.Column(
        "owner_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    ),
    sa.Column("record_version", sa.BigInteger(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
)

workspace_memberships_table = sa.Table(
    "workspace_memberships",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
    sa.Column("status", sa.Text(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("record_version", sa.BigInteger(), nullable=False),
)

role_assignments_table = sa.Table(
    "role_assignments",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column(
        "membership_id",
        sa.Uuid(),
        sa.ForeignKey("workspace_memberships.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("role", sa.Text(), nullable=False),
    sa.Column(
        "granted_by_user_id",
        sa.Uuid(),
        sa.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("granted_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("record_version", sa.BigInteger(), nullable=False),
)

human_authority_bindings_table = sa.Table(
    "human_authority_bindings",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column(
        "human_user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    ),
    sa.Column("authority_class", sa.Text(), nullable=False),
    sa.Column("scope_type", sa.Text(), nullable=False),
    sa.Column("scope_id", sa.Uuid(), nullable=False),
    sa.Column("authority_source", sa.Text(), nullable=False),
    sa.Column(
        "granted_by_user_id",
        sa.Uuid(),
        sa.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("granted_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column(
        "revoked_by_user_id",
        sa.Uuid(),
        sa.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    ),
    sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("state", sa.Text(), nullable=False),
    sa.Column("record_version", sa.BigInteger(), nullable=False),
)

challenges_table = sa.Table(
    "challenges",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("title", sa.Text(), nullable=False),
    sa.Column("description", sa.Text(), nullable=True),
    sa.Column("context", sa.Text(), nullable=True),
    sa.Column("desired_outcome", sa.Text(), nullable=True),
    sa.Column("constraints", sa.Text(), nullable=True),
    sa.Column("stakeholders", sa.Text(), nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("record_version", sa.BigInteger(), nullable=False),
    sa.UniqueConstraint("id", "workspace_id", name="uq_challenges_id_workspace"),
)

sessions_table = sa.Table(
    "sessions",
    metadata,
    sa.Column("id", sa.Uuid(), primary_key=True),
    sa.Column("challenge_id", sa.Uuid(), nullable=False),
    sa.Column(
        "workspace_id",
        sa.Uuid(),
        sa.ForeignKey("workspaces.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    sa.Column("applied_method_key", sa.Text(), nullable=False),
    sa.Column("applied_method_version", sa.Text(), nullable=False),
    sa.Column("state", sa.Text(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("record_version", sa.BigInteger(), nullable=False),
    # The composite FK, not a plain `challenge_id` reference: 09 §27.1
    # permits the denormalized `workspace_id` only under the constraint
    # that it equals the Challenge's Workspace.
    sa.ForeignKeyConstraint(
        ["challenge_id", "workspace_id"],
        ["challenges.id", "challenges.workspace_id"],
        name="fk_sessions_challenge_workspace",
        ondelete="RESTRICT",
    ),
)

__all__ = [
    "metadata",
    "users_table",
    "workspaces_table",
    "workspace_memberships_table",
    "role_assignments_table",
    "human_authority_bindings_table",
    "challenges_table",
    "sessions_table",
]
