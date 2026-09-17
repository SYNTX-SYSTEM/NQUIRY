"""AuthorityBindingRepository: HumanAuthorityBinding reads.

Source: 14_IMPLEMENTATION_SEQUENCE.md §10 (REPOSITORY PORTS):
"`AuthorityBindingRepository`: current/historical HABB reads, no
direct grant/revoke outside governance Command." PKG-02's
`PUBLIC_INTERFACES` authorizes only the read half; no Command/
CommitUnit exists yet for the write half to go through.

Non-collapse rule — read carefully, this is the load-bearing boundary
of this whole module: `list_current_bindings` returns rows whose
*stored* `state` column is `ACTIVE`. It does **not** cross-check
whether the binding is currently *effective* (09 §51, written for
FacilitatorScopeBinding but identically true for HumanAuthorityBinding
per 05 AC-05-004: "Stored ACTIVE alone does not prove effective
authority" — effectiveness additionally requires the target's
WorkspaceMembership to still be ACTIVE, 05 §18's Effectiveness
Predicate). Joining across membership to compute effectiveness is
exactly the kind of authority *resolution* PKG-02's own prompt forbids
("AUTHORITY: Persist authority facts only, do not resolve them") —
that is `AuthorityResolver`'s job (PKG-03). A caller of this repository
that treats a returned row as "this user is currently authorized"
without separately checking membership has reintroduced the exact
non-collapse violation this module exists to make visible, not to
paper over. See `tests/authority/test_authority_binding_repository.py`
for the proof that this repository deliberately does not do that join.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable

import sqlalchemy as sa
from governance.authority_binding import AuthorityBindingState, AuthorityClass
from semantic_types.ids import AuthorityBindingId, UserId, WorkspaceId
from semantic_types.versions import RecordVersion

from persistence.tables import human_authority_bindings_table


@dataclass(frozen=True, slots=True)
class HumanAuthorityBindingRecord:
    """A `human_authority_bindings` row as actually read from storage."""

    id: AuthorityBindingId
    workspace_id: WorkspaceId
    human_user_id: UserId
    authority_class: AuthorityClass
    scope_type: str
    scope_id: (
        uuid.UUID
    )  # polymorphic reference; no single semantic ID type spans every scope kind yet
    authority_source: str
    granted_by_user_id: UserId
    granted_at: datetime
    revoked_by_user_id: UserId | None
    revoked_at: datetime | None
    state: AuthorityBindingState
    record_version: RecordVersion


@runtime_checkable
class AuthorityBindingRepository(Protocol):
    """Port: HumanAuthorityBinding reads only (14 §10)."""

    def list_current_bindings(
        self, workspace_id: WorkspaceId, human_user_id: UserId
    ) -> tuple[HumanAuthorityBindingRecord, ...]:
        """Rows whose stored `state` is `ACTIVE` for this (workspace,
        human). Raw fact only — see this module's docstring for why
        this is deliberately *not* an effectiveness check."""
        ...

    def list_binding_history(
        self, workspace_id: WorkspaceId, human_user_id: UserId
    ) -> tuple[HumanAuthorityBindingRecord, ...]:
        """Every binding (ACTIVE and REVOKED) for this (workspace,
        human), oldest first."""
        ...


class SqlAlchemyAuthorityBindingRepository:
    """`AuthorityBindingRepository` backed by `human_authority_bindings`
    via a SQLAlchemy Core connection. Read-only by construction — no
    `grant`/`revoke` method exists; those require a governance Command
    this package does not implement.
    """

    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def list_current_bindings(
        self, workspace_id: WorkspaceId, human_user_id: UserId
    ) -> tuple[HumanAuthorityBindingRecord, ...]:
        stmt = sa.select(human_authority_bindings_table).where(
            human_authority_bindings_table.c.workspace_id == workspace_id.value,
            human_authority_bindings_table.c.human_user_id == human_user_id.value,
            human_authority_bindings_table.c.state == AuthorityBindingState.ACTIVE.value,
        )
        rows = self._connection.execute(stmt).mappings().all()
        return tuple(_record_from_row(row) for row in rows)

    def list_binding_history(
        self, workspace_id: WorkspaceId, human_user_id: UserId
    ) -> tuple[HumanAuthorityBindingRecord, ...]:
        stmt = (
            sa.select(human_authority_bindings_table)
            .where(
                human_authority_bindings_table.c.workspace_id == workspace_id.value,
                human_authority_bindings_table.c.human_user_id == human_user_id.value,
            )
            .order_by(human_authority_bindings_table.c.granted_at.asc())
        )
        rows = self._connection.execute(stmt).mappings().all()
        return tuple(_record_from_row(row) for row in rows)


def _record_from_row(row: sa.RowMapping) -> HumanAuthorityBindingRecord:
    return HumanAuthorityBindingRecord(
        id=AuthorityBindingId(row["id"]),
        workspace_id=WorkspaceId(row["workspace_id"]),
        human_user_id=UserId(row["human_user_id"]),
        authority_class=AuthorityClass(row["authority_class"]),
        scope_type=row["scope_type"],
        scope_id=row["scope_id"],
        authority_source=row["authority_source"],
        granted_by_user_id=UserId(row["granted_by_user_id"]),
        granted_at=row["granted_at"],
        revoked_by_user_id=None
        if row["revoked_by_user_id"] is None
        else UserId(row["revoked_by_user_id"]),
        revoked_at=row["revoked_at"],
        state=AuthorityBindingState(row["state"]),
        record_version=RecordVersion(row["record_version"]),
    )


__all__ = [
    "HumanAuthorityBindingRecord",
    "AuthorityBindingRepository",
    "SqlAlchemyAuthorityBindingRepository",
]
