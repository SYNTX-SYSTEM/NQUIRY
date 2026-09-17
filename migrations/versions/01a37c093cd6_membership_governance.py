"""membership governance

Revision ID: 01a37c093cd6
Revises: 72e4c8ea6772
Create Date: 2026-09-17 16:30:16.201392

PKG-02 scope (14_IMPLEMENTATION_SEQUENCE.md §9: "002_membership_governance
| creates: memberships, HABB, facilitator scope | depends on: 001").

Deliberately NOT created here: `facilitator_scope_bindings`.
09_DATA_EVENT_API_CONTRACTS.md §51 requires it to carry a `session_id`
FK, but `sessions` does not exist until PKG-05 (migration 003). 14 §9's
one-line summary is imprecise about this real cross-table dependency;
09's detailed contract (upstream, higher authority) governs. PKG-02's
own `PUBLIC_INTERFACES` also never requires a
`FacilitatorScopeBindingRepository` — only `MembershipRepository` and
`AuthorityBindingRepository`. Deferred, not stubbed, to whichever
migration introduces `sessions`.

Tables created:

- `workspace_memberships` (09 §23): the User-to-Workspace relation.
  `status`/`revoked_at` materialize "active/effective status
  representation" (09's field name; the concrete representation is an
  implementation choice). A partial unique index prevents a second
  ACTIVE membership for the same (workspace, user) pair (05 GOV-002
  precondition: "target User is not already an active member under
  conflicting membership").

- `role_assignments` (09 §23.1, §24): kept separate from
  `workspace_memberships` on purpose — "Role history must not be
  irreversibly embedded as one mutable string if authority
  reconstruction requires change history. Use RoleAssignment."
  `role` values match 02/05's literal source casing (`Owner`,
  `Facilitator`, ...), not an invented ALL_CAPS vocabulary — 14 §6's
  closed-vocabulary section does not cover Workspace roles, so there is
  no competing convention to follow. A partial unique index enforces
  "at most one ACTIVE role per membership at a time" (05 GOV-004:
  changing role is revoke-old + grant-new, never two simultaneously
  active).

- `human_authority_bindings` (04 §6, 09 §50): the HABB authority
  record. `authority_class` is CHECK-constrained to the exact 7 Decision
  Right classes 04 §9 defines — closed vocabulary, not extensible here.
  `scope_type`/`scope_id` are a polymorphic reference (SQL cannot
  express one FK across many not-yet-existing target tables — Session,
  Challenge, Experiment, Decision, Assumption are all future packages);
  left as plain columns per 14 §7.3 ("application plus trigger/
  constraint enforcement where SQL cannot express a cross-table
  invariant directly"). Two triggers enforce what a foreign key
  cannot:

  1. `trg_habb_check_grant_preconditions` (BEFORE INSERT): the target
     human must have an ACTIVE `workspace_memberships` row in the same
     Workspace (05 GOV-005 precondition: "target User has active
     WorkspaceMembership") — the mandatory "absent membership" attack
     is rejected here, at the database, not merely documented as a
     read-side caveat. For `WORKSPACE_GOVERNANCE_RIGHT` specifically,
     `scope_id` must equal `workspace_id` (05 GOV-002 TARGET SCOPE:
     "Exactly the governed Workspace").
  2. `trg_habb_check_immutable` (BEFORE UPDATE): enforces 09 §50.1
     ("immutable after grant": human_user_id, authority_class,
     scope_type, scope_id, authority_source, granted_by_user_id,
     granted_at) and 05 §8.1 ("REVOKED is terminal for that binding
     record" — no update at all is permitted once REVOKED, and no
     UPDATE may set state back to ACTIVE).

No cascading delete anywhere (14 §49 default). Schema downgrade is
infrastructure rollback only, not domain rollback (14 §9).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "01a37c093cd6"
down_revision: str | None = "72e4c8ea6772"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_AUTHORITY_CLASSES = (
    "SESSION_CONTROL_RIGHT",
    "QUESTION_SELECTION_RIGHT",
    "ASSUMPTION_INTERPRETATION_RIGHT",
    "EXPERIMENT_DECISION_RIGHT",
    "DECISION_RIGHT",
    "ACTION_DECISION_RIGHT",
    "WORKSPACE_GOVERNANCE_RIGHT",
)

_ROLES = ("Owner", "Facilitator", "Contributor", "Observer", "Viewer")


def upgrade() -> None:
    op.create_table(
        "workspace_memberships",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("record_version", sa.BigInteger(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id", name="pk_workspace_memberships"),
        sa.ForeignKeyConstraint(
            ["workspace_id"], ["workspaces.id"], name="fk_workspace_memberships_workspace", ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_workspace_memberships_user", ondelete="RESTRICT"
        ),
        sa.CheckConstraint("status IN ('ACTIVE', 'REVOKED')", name="ck_workspace_memberships_status"),
        sa.CheckConstraint(
            "(status = 'REVOKED') = (revoked_at IS NOT NULL)",
            name="ck_workspace_memberships_revoked_consistency",
        ),
        sa.CheckConstraint(
            "record_version >= 1", name="ck_workspace_memberships_record_version_positive"
        ),
    )
    op.create_index(
        "uq_workspace_memberships_active_pair",
        "workspace_memberships",
        ["workspace_id", "user_id"],
        unique=True,
        postgresql_where=sa.text("status = 'ACTIVE'"),
    )

    op.create_table(
        "role_assignments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("membership_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("granted_by_user_id", sa.Uuid(), nullable=False),
        sa.Column(
            "granted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("record_version", sa.BigInteger(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id", name="pk_role_assignments"),
        sa.ForeignKeyConstraint(
            ["workspace_id"], ["workspaces.id"], name="fk_role_assignments_workspace", ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["membership_id"],
            ["workspace_memberships.id"],
            name="fk_role_assignments_membership",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["granted_by_user_id"], ["users.id"], name="fk_role_assignments_granted_by", ondelete="RESTRICT"
        ),
        sa.CheckConstraint(
            "role IN (" + ", ".join(f"'{r}'" for r in _ROLES) + ")", name="ck_role_assignments_role"
        ),
        sa.CheckConstraint("record_version >= 1", name="ck_role_assignments_record_version_positive"),
    )
    op.create_index(
        "uq_role_assignments_active_per_membership",
        "role_assignments",
        ["membership_id"],
        unique=True,
        postgresql_where=sa.text("revoked_at IS NULL"),
    )

    op.create_table(
        "human_authority_bindings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("human_user_id", sa.Uuid(), nullable=False),
        sa.Column("authority_class", sa.Text(), nullable=False),
        sa.Column("scope_type", sa.Text(), nullable=False),
        sa.Column("scope_id", sa.Uuid(), nullable=False),
        sa.Column("authority_source", sa.Text(), nullable=False),
        sa.Column("granted_by_user_id", sa.Uuid(), nullable=False),
        sa.Column(
            "granted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("revoked_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("state", sa.Text(), nullable=False),
        sa.Column("record_version", sa.BigInteger(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id", name="pk_human_authority_bindings"),
        sa.ForeignKeyConstraint(
            ["workspace_id"], ["workspaces.id"], name="fk_habb_workspace", ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["human_user_id"], ["users.id"], name="fk_habb_human_user", ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["granted_by_user_id"], ["users.id"], name="fk_habb_granted_by", ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["revoked_by_user_id"], ["users.id"], name="fk_habb_revoked_by", ondelete="RESTRICT"
        ),
        sa.CheckConstraint(
            "authority_class IN (" + ", ".join(f"'{c}'" for c in _AUTHORITY_CLASSES) + ")",
            name="ck_habb_authority_class",
        ),
        sa.CheckConstraint("state IN ('ACTIVE', 'REVOKED')", name="ck_habb_state"),
        sa.CheckConstraint(
            "(state = 'REVOKED') = (revoked_at IS NOT NULL AND revoked_by_user_id IS NOT NULL)",
            name="ck_habb_revoked_consistency",
        ),
        sa.CheckConstraint("record_version >= 1", name="ck_habb_record_version_positive"),
    )

    # Trigger 1: GOV-005 grant preconditions (05 §15) — a foreign key
    # cannot express "target has an ACTIVE membership in this
    # Workspace", nor "WORKSPACE_GOVERNANCE_RIGHT scope is exactly the
    # governed Workspace" (05 §11 GOV-002 TARGET SCOPE).
    op.execute(
        """
        CREATE FUNCTION trg_habb_check_grant_preconditions() RETURNS trigger AS $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM workspace_memberships
                WHERE workspace_id = NEW.workspace_id
                  AND user_id = NEW.human_user_id
                  AND status = 'ACTIVE'
            ) THEN
                RAISE EXCEPTION
                    'human_authority_bindings: target user % has no ACTIVE workspace_membership in workspace % (05 GOV-005 precondition)',
                    NEW.human_user_id, NEW.workspace_id;
            END IF;

            IF NEW.authority_class = 'WORKSPACE_GOVERNANCE_RIGHT' AND NEW.scope_id != NEW.workspace_id THEN
                RAISE EXCEPTION
                    'human_authority_bindings: WORKSPACE_GOVERNANCE_RIGHT scope_id must equal workspace_id (05 GOV-002 TARGET SCOPE)';
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_habb_check_grant_preconditions
        BEFORE INSERT ON human_authority_bindings
        FOR EACH ROW EXECUTE FUNCTION trg_habb_check_grant_preconditions();
        """
    )

    # Trigger 2: immutability + terminal REVOKED state (09 §50.1, 05 §8.1).
    op.execute(
        """
        CREATE FUNCTION trg_habb_check_immutable() RETURNS trigger AS $$
        BEGIN
            IF OLD.state = 'REVOKED' THEN
                RAISE EXCEPTION
                    'human_authority_bindings: binding % is REVOKED, which is terminal (05 §8.1) — no further update is permitted',
                    OLD.id;
            END IF;

            IF NEW.human_user_id != OLD.human_user_id
                OR NEW.authority_class != OLD.authority_class
                OR NEW.scope_type != OLD.scope_type
                OR NEW.scope_id != OLD.scope_id
                OR NEW.authority_source != OLD.authority_source
                OR NEW.granted_by_user_id != OLD.granted_by_user_id
                OR NEW.granted_at != OLD.granted_at
            THEN
                RAISE EXCEPTION
                    'human_authority_bindings: subject/class/scope/source/grantor/grant time are immutable after grant (09 §50.1)';
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_habb_check_immutable
        BEFORE UPDATE ON human_authority_bindings
        FOR EACH ROW EXECUTE FUNCTION trg_habb_check_immutable();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_habb_check_immutable ON human_authority_bindings;")
    op.execute("DROP FUNCTION IF EXISTS trg_habb_check_immutable();")
    op.execute("DROP TRIGGER IF EXISTS trg_habb_check_grant_preconditions ON human_authority_bindings;")
    op.execute("DROP FUNCTION IF EXISTS trg_habb_check_grant_preconditions();")
    op.drop_table("human_authority_bindings")
    op.drop_index("uq_role_assignments_active_per_membership", table_name="role_assignments")
    op.drop_table("role_assignments")
    op.drop_index("uq_workspace_memberships_active_pair", table_name="workspace_memberships")
    op.drop_table("workspace_memberships")
