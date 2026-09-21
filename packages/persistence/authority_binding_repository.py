"""AuthorityBindingRepository: HumanAuthorityBinding reads and grant.

Source: 14_IMPLEMENTATION_SEQUENCE.md §10 (REPOSITORY PORTS):
"`AuthorityBindingRepository`: current/historical HABB reads, no
direct grant/revoke outside governance Command." PKG-02's
`PUBLIC_INTERFACES` authorized only the read half at that time; no
Command/CommitUnit existed yet for the write half to go through.

[F01 WU-01.4, human-confirmed 2026-09-21] `grant()` below IS that
governance Command's write, not a grant "outside" one --
`application.workspace_creation_handler.create_workspace` is its one
legitimate caller, and it is the only concrete `HumanAuthorityBinding`
write path in this codebase with `authority_source ==
"LEVEL_1_EXPLICIT"` (04 §9) rather than
`test_support.nonproof_bootstrap.NonProofWorkspaceBootstrap`'s own
`"NON_PROOF_FIXTURE"`. `grant()` performs no authority evaluation
itself (14 §10 non-collapse rule below still holds) -- the caller must
have already evaluated BND-001 and the eligibility check.

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

[F01 WU-01.6] `get_by_id`/`revoke`/`authority_binding_target_ref`/
`SqlAlchemyAuthorityBindingVersionReader` are this Work Unit's own
addition — the "revoke" half `grant()`'s own docstring named as
"a later Field's scope (F01 WU-01.6)". `revoke()` mirrors
`persistence.decision_repository.record_decision`'s exact shape (a
version-guarded `UPDATE`, `AuthorityBindingConflict` on a 0-row
result), not `grant()`'s plain insert — revoking mutates an EXISTING
row, and 05 §8.1's own "REVOKED is terminal for that binding record"
is enforced by the same `WHERE ... state = ACTIVE` clause that makes a
second revoke of an already-`REVOKED` row fail the identical way as a
concurrent-version conflict, with no separate "already revoked"
exception needed. `revoke()` performs no authority evaluation itself
(same non-collapse rule as `grant()`) — the caller
(`application.authority_binding_handler.revoke_human_authority_binding`)
must have already evaluated BND-001..005 and its own
`GovernanceRootOrphaningRefused` guard before calling it.
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


def authority_binding_target_ref(binding_id: AuthorityBindingId) -> str:
    """The `CommandEnvelope.target_refs`/`CurrentVersionReader` ref
    string naming a HumanAuthorityBinding as a commit-sensitive target
    -- mirrors `persistence.workspace_repository.workspace_target_ref`/
    `domain.decision.challenge_target_ref`'s own precedent exactly."""
    return f"authority_binding:{binding_id.value}"


class AuthorityBindingConflict(Exception):
    """Raised by `revoke()` when the guarded `UPDATE` affects zero rows
    -- the binding does not exist, or its stored `state` is no longer
    `ACTIVE` (including "already `REVOKED`", 05 §8.1's own "terminal"
    rule), or `record_version` no longer matches. Mirrors
    `persistence.decision_repository.DecisionConflict` exactly."""


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

    def get_by_id(self, binding_id: AuthorityBindingId) -> HumanAuthorityBindingRecord | None:
        """Return the one `human_authority_bindings` row for `binding_id`,
        or `None` if no such row exists. Never raises for "not found" —
        same discipline as `WorkspaceRepository.get`."""
        ...

    def grant(
        self,
        binding_id: AuthorityBindingId,
        *,
        workspace_id: WorkspaceId,
        human_user_id: UserId,
        authority_class: AuthorityClass,
        scope_type: str,
        scope_id: uuid.UUID,
        authority_source: str,
        granted_by_user_id: UserId,
        granted_at: datetime,
    ) -> HumanAuthorityBindingRecord:
        """Insert a new ACTIVE `human_authority_bindings` row."""
        ...

    def revoke(
        self,
        binding_id: AuthorityBindingId,
        *,
        expected_record_version: RecordVersion,
        revoked_by_user_id: UserId,
        revoked_at: datetime,
    ) -> None:
        """`ACTIVE` -> `REVOKED` (05 §8.1, terminal). Raises
        `AuthorityBindingConflict` if `binding_id` does not resolve to a
        row whose stored `state` is `ACTIVE` AND whose `record_version`
        equals `expected_record_version` — including "no such row",
        "already REVOKED", and "someone else committed a change to this
        row first", all collapsed into the one exception, mirroring
        `DecisionRepository.record_decision`'s own `DecisionConflict`
        (module docstring)."""
        ...


class SqlAlchemyAuthorityBindingRepository:
    """`AuthorityBindingRepository` backed by `human_authority_bindings`
    via a SQLAlchemy Core connection.
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

    def get_by_id(self, binding_id: AuthorityBindingId) -> HumanAuthorityBindingRecord | None:
        stmt = sa.select(human_authority_bindings_table).where(
            human_authority_bindings_table.c.id == binding_id.value
        )
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else _record_from_row(row)

    def grant(
        self,
        binding_id: AuthorityBindingId,
        *,
        workspace_id: WorkspaceId,
        human_user_id: UserId,
        authority_class: AuthorityClass,
        scope_type: str,
        scope_id: uuid.UUID,
        authority_source: str,
        granted_by_user_id: UserId,
        granted_at: datetime,
    ) -> HumanAuthorityBindingRecord:
        record_version = RecordVersion.initial()
        self._connection.execute(
            sa.insert(human_authority_bindings_table).values(
                id=binding_id.value,
                workspace_id=workspace_id.value,
                human_user_id=human_user_id.value,
                authority_class=authority_class.value,
                scope_type=scope_type,
                scope_id=scope_id,
                authority_source=authority_source,
                granted_by_user_id=granted_by_user_id.value,
                granted_at=granted_at,
                revoked_by_user_id=None,
                revoked_at=None,
                state=AuthorityBindingState.ACTIVE.value,
                record_version=record_version.value,
            )
        )
        return HumanAuthorityBindingRecord(
            id=binding_id,
            workspace_id=workspace_id,
            human_user_id=human_user_id,
            authority_class=authority_class,
            scope_type=scope_type,
            scope_id=scope_id,
            authority_source=authority_source,
            granted_by_user_id=granted_by_user_id,
            granted_at=granted_at,
            revoked_by_user_id=None,
            revoked_at=None,
            state=AuthorityBindingState.ACTIVE,
            record_version=record_version,
        )

    def revoke(
        self,
        binding_id: AuthorityBindingId,
        *,
        expected_record_version: RecordVersion,
        revoked_by_user_id: UserId,
        revoked_at: datetime,
    ) -> None:
        result = self._connection.execute(
            sa.update(human_authority_bindings_table)
            .where(
                human_authority_bindings_table.c.id == binding_id.value,
                human_authority_bindings_table.c.state == AuthorityBindingState.ACTIVE.value,
                human_authority_bindings_table.c.record_version == expected_record_version.value,
            )
            .values(
                state=AuthorityBindingState.REVOKED.value,
                revoked_by_user_id=revoked_by_user_id.value,
                revoked_at=revoked_at,
                record_version=expected_record_version.next().value,
            )
        )
        if result.rowcount == 0:
            raise AuthorityBindingConflict(
                f"binding {binding_id!r} not found, not ACTIVE, or not at expected "
                f"record_version {expected_record_version.value}"
            )


class SqlAlchemyAuthorityBindingVersionReader:
    """`commit.coordinator.CurrentVersionReader` reading the REAL, fresh
    `human_authority_bindings.record_version` for one binding -- no
    caching, mirrors `persistence.workspace_repository.
    SqlAlchemyWorkspaceVersionReader`/`persistence.decision_repository.
    SqlAlchemyDecisionVersionReader` exactly. Lives here, not in
    `application.authority_binding_handler`, for the identical reason:
    `application` may not import `sqlalchemy` directly (14 §3.1/§4).
    """

    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def read(self, target_ref: str) -> RecordVersion | None:
        prefix = "authority_binding:"
        if not target_ref.startswith(prefix):
            return None
        binding_id = uuid.UUID(target_ref[len(prefix) :])
        stmt = sa.select(human_authority_bindings_table.c.record_version).where(
            human_authority_bindings_table.c.id == binding_id
        )
        row = self._connection.execute(stmt).one_or_none()
        return None if row is None else RecordVersion(row[0])


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
    "AuthorityBindingConflict",
    "SqlAlchemyAuthorityBindingRepository",
    "SqlAlchemyAuthorityBindingVersionReader",
    "authority_binding_target_ref",
]
