"""NonProofWorkspaceBootstrap: test/dev-only Workspace governance-root fixture.

TEST ONLY. Must never be imported by production code — see
`packages/test_support/__init__.py` and
`scripts/check_test_only_imports.py`. That static import-graph rule
*is* 14 §38's "guarded by test/development build condition and import
architecture test": there is no separate runtime environment-variable
gate to invent here, and inventing one would itself be exactly the
kind of "temporary semantic interface" this package is not authorized
to add.

Source: 12_MINIMUM_PROTOTYPE_ARCHITECTURE.md §8.1 (Required sequence)
and §8.2 (Bootstrap gap); 14_IMPLEMENTATION_SEQUENCE.md §38.

12 §8.2 is blunt about what this is not: "Until closed, bootstrap can
be represented in deterministic test fixtures for architecture
falsification, but cannot be claimed as a production-legitimate
creation path... Fixture seeding is explicitly labeled TEST
PRECONDITION, not runtime authority." `HARD-DEP-001` (legitimate first
Workspace governance-root bootstrap) and `GAP-05-001` (who may create
the first Workspace, how `owner_id` becomes authoritative) remain
fully open after calling `seed()` — nothing here closes them.

This performs only the first 4 of 12 §8.1's 10 bootstrap steps (create
Workspace -> establish owner_id root -> establish ACTIVE membership ->
establish WORKSPACE_GOVERNANCE_RIGHT). The remaining steps
(SESSION_CONTROL_RIGHT, QUESTION_SELECTION_RIGHT, DECISION_RIGHT,
FacilitatorScopeBinding, Challenge, Session) all require a scope
(a Session/Challenge/Decision) that does not exist yet — PKG-04 does
not stub one to reach further.

THE HONEST LIMIT OF THIS FIXTURE'S SAFETY: the rows `seed()` inserts
are byte-for-byte indistinguishable, at the database level, from rows
a legitimate governance operation would eventually produce (12 §38's
"not as production domain semantics" is exactly why no
`fixture_legitimacy` column exists to tell them apart in the schema).
The *only* thing preventing this fixture's output from being mistaken
for real authority is that production code can never reach this
module at all (the import-graph guard above). `fixture_legitimacy` on
`NonProofWorkspaceBootstrapResult` below exists purely so a *test*
holding the result object cannot itself forget what it is holding —
it is not, and cannot be, a database-level tamper-evidence mechanism.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Literal

import sqlalchemy as sa
from governance.authority_binding import AuthorityBindingState, AuthorityClass
from governance.membership import MembershipStatus
from persistence.tables import (
    human_authority_bindings_table,
    users_table,
    workspace_memberships_table,
    workspaces_table,
)
from semantic_types.clock import Clock
from semantic_types.id_generator import IdGenerator
from semantic_types.ids import AuthorityBindingId, UserId, WorkspaceId

FIXTURE_LEGITIMACY: Literal["NON_PROOF_FIXTURE"] = "NON_PROOF_FIXTURE"
"""The one and only value this module ever produces. Not a type alias
a caller can widen — see `NonProofWorkspaceBootstrapResult.fixture_legitimacy`.
"""


@dataclass(frozen=True, slots=True)
class NonProofWorkspaceBootstrapResult:
    """What `seed()` created. `fixture_legitimacy` is always
    `"NON_PROOF_FIXTURE"` — there is no constructor path that produces
    any other value, structurally proving this result can never be
    mistaken for a claim of legitimate bootstrap (mandatory adversarial
    attack: "fixture used to claim bootstrap legitimacy").
    """

    fixture_legitimacy: Literal["NON_PROOF_FIXTURE"]
    workspace_id: WorkspaceId
    owner_user_id: UserId
    membership_id: uuid.UUID
    governance_binding_id: AuthorityBindingId

    def __post_init__(self) -> None:
        if self.fixture_legitimacy != FIXTURE_LEGITIMACY:
            raise ValueError(
                f"NonProofWorkspaceBootstrapResult.fixture_legitimacy must be "
                f"{FIXTURE_LEGITIMACY!r}, got {self.fixture_legitimacy!r}"
            )


class NonProofWorkspaceBootstrap:
    """Seeds a Workspace governance root that does not, and cannot,
    claim to be a legitimate `HARD-DEP-001` bootstrap.

    Constructed with the same ports/connection pattern as PKG-01/02's
    repositories: a live `sa.Connection` (this is deliberately direct
    SQL — 14's "direct persistence" forbidden shortcut applies to
    production code claiming a governed path exists when it does not;
    this module claims nothing of the sort, and is walled off from
    production by the import graph, not by pretending to be governed).
    """

    def __init__(self, connection: sa.Connection, clock: Clock, id_generator: IdGenerator) -> None:
        self._connection = connection
        self._clock = clock
        self._id_generator = id_generator

    def seed(
        self,
        *,
        owner_email: str,
        workspace_name: str = "NonProof Workspace",
    ) -> NonProofWorkspaceBootstrapResult:
        now = self._clock.now()
        owner_user_id = UserId(self._id_generator.new_uuid())
        workspace_id = WorkspaceId(self._id_generator.new_uuid())
        membership_id = self._id_generator.new_uuid()
        governance_binding_id = AuthorityBindingId(self._id_generator.new_uuid())

        self._connection.execute(
            sa.insert(users_table).values(
                id=owner_user_id.value,
                email=owner_email,
                name="NonProof Fixture Owner",
                record_version=1,
                created_at=now,
                updated_at=now,
            )
        )
        self._connection.execute(
            sa.insert(workspaces_table).values(
                id=workspace_id.value,
                name=workspace_name,
                owner_id=owner_user_id.value,
                record_version=1,
                created_at=now,
                updated_at=now,
            )
        )
        self._connection.execute(
            sa.insert(workspace_memberships_table).values(
                id=membership_id,
                workspace_id=workspace_id.value,
                user_id=owner_user_id.value,
                status=MembershipStatus.ACTIVE.value,
                created_at=now,
                record_version=1,
            )
        )
        self._connection.execute(
            sa.insert(human_authority_bindings_table).values(
                id=governance_binding_id.value,
                workspace_id=workspace_id.value,
                human_user_id=owner_user_id.value,
                authority_class=AuthorityClass.WORKSPACE_GOVERNANCE_RIGHT.value,
                scope_type="WORKSPACE",
                scope_id=workspace_id.value,
                authority_source=FIXTURE_LEGITIMACY,
                # The root grants itself: honest representation of why this
                # is NOT a legitimate path (12 §8.2: "seed_owner = authority"
                # is a refused shortcut) -- a real bootstrap cannot have the
                # first authority come from nothing except by fiat, which is
                # exactly what GAP-05-001 leaves unresolved.
                granted_by_user_id=owner_user_id.value,
                granted_at=now,
                state=AuthorityBindingState.ACTIVE.value,
                record_version=1,
            )
        )

        return NonProofWorkspaceBootstrapResult(
            fixture_legitimacy=FIXTURE_LEGITIMACY,
            workspace_id=workspace_id,
            owner_user_id=owner_user_id,
            membership_id=membership_id,
            governance_binding_id=governance_binding_id,
        )


__all__ = ["FIXTURE_LEGITIMACY", "NonProofWorkspaceBootstrapResult", "NonProofWorkspaceBootstrap"]
