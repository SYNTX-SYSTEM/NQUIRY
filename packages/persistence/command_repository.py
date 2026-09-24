"""CommandRepository: "immutable Command plus attempt records" (14
section 10, REPOSITORY PORTS).

THIS REPOSITORY IS NOT ITSELF A GOVERNED DISPATCH PATH
-----------------------------------------------------------
Exactly like `BurstRepository` (PKG-07) and `QuestionRepository`
(PKG-06), every method here performs a real INSERT/UPDATE, backed
independently by `b2f3a5d5096c`'s own triggers, but nothing here
resolves authority, evaluates a boundary, or produces a canonical
mutation of domain state -- `commands`/`command_attempts` are
themselves 14 section 7.1's "operational" semantic class, not
canonical. `record_outcome` exists because 14 section 10's
`CommandRepository` port is a single, non-phase-tagged list ("immutable
Command plus attempt records" -- record*s*, plural, spanning the full
attempt lifecycle), but no caller in this codebase invokes it yet: the
commit coordinator that would actually determine a real outcome is
PKG-13's scope. Exercised only by this package's own tests, the same
disclosed "built but unwired" pattern already established twice.

WHY `record_attempt` DOES THE CONFLICT CHECK IN PYTHON, NOT JUST IN SQL
------------------------------------------------------------------------
The `commands` table's own immutability trigger (`b2f3a5d5096c`)
already rejects any UPDATE unconditionally, so a payload-fingerprint or
Workspace mismatch under a reused `command_id` could not silently
succeed even if this method's own checks below were deleted. The
Python-level checks exist so the caller receives a specific, named
exception (`CommandPayloadConflict`/`CommandWorkspaceMismatch`)
distinguishing *which* invariant was violated, rather than a generic
database trigger exception string -- the same "checked at two
independent layers" discipline `d467112ce46d`/`d8a1147fde30`'s own
transition triggers already established relative to
`domain.session_transitions`/`domain.burst_transitions`.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable

import sqlalchemy as sa
from command.envelope import CommandEnvelope, CommandOutcome, compute_payload_fingerprint
from semantic_types.ids import AttemptId, CommandId, CommitId, WorkspaceId
from semantic_types.versions import ContractVersion

from persistence.tables import command_attempts_table, commands_table, recovery_records_table


@dataclass(frozen=True, slots=True)
class CommandRecord:
    """One row of `commands`: the stable identity of one logical
    requested consequential operation (09 section 4.3), independent of
    how many attempts have been made against it.
    """

    command_id: CommandId
    workspace_id: WorkspaceId
    command_type: str
    contract_version: ContractVersion
    payload_fingerprint: str
    created_at: datetime
    target_refs: tuple[str, ...] = ()
    """F03 WU-03.4 (FBR-F03-3): the refs this Command targets (09 §9),
    persisted at birth. Empty on rows written before migration f6b2c4d9a318."""


@dataclass(frozen=True, slots=True)
class CommandAttempt:
    """09 section 59's `CommandExecutionRecord` field list exactly."""

    command_id: CommandId
    attempt_id: AttemptId
    workspace_id: WorkspaceId
    actor_ref: str
    received_at: datetime
    boundary_evaluation_summary_ref: uuid.UUID | None
    commit_id: CommitId | None
    outcome: CommandOutcome | None
    completed_at: datetime | None
    failure_code: str | None


class CommandWorkspaceMismatch(Exception):
    """Raised when an envelope reuses a `command_id` already recorded
    under a *different* Workspace. Mandatory adversarial attack: wrong
    Workspace.
    """


class CommandTypeMismatch(Exception):
    """Raised when an envelope reuses a `command_id` already recorded
    for a *different* Command type (F02 WU-02.12, FBR-B). 09 section 4.3:
    `command_id` is "the stable identity of one logical requested
    consequential operation". Two Command types can share a payload shape
    (so the fingerprint alone cannot tell them apart), and accepting the
    second one would make the first Command's `commands` row the
    provenance of an effect it never requested.
    """


class CommandPayloadConflict(Exception):
    """Raised when an envelope reuses a `command_id` already recorded
    with a *different* payload fingerprint (09 section 139/AC-09-013).
    Mandatory adversarial attack: changed payload under same command
    identity.
    """


class AttemptAlreadyRecorded(Exception):
    """Raised when `attempt_id` has already been recorded -- for any
    command_id. An `attempt_id` is a one-time identity (09 section 4.4);
    replaying one is never a legitimate new fact.
    """


class AttemptOutcomeAlreadyFinal(Exception):
    """Raised by `record_outcome` when the targeted attempt already has
    a determined outcome. Mirrors the `commands` table's own
    immutability trigger (`b2f3a5d5096c`) at the Python layer: an
    outcome is terminal once set (09 section 18).
    """


class AttemptNotFound(Exception):
    """Raised by `record_outcome` when `attempt_id` has no matching row."""


@runtime_checkable
class CommandRepository(Protocol):
    def record_attempt(
        self, envelope: CommandEnvelope, *, received_at: datetime
    ) -> CommandAttempt: ...

    def record_outcome(
        self,
        *,
        attempt_id: AttemptId,
        workspace_id: WorkspaceId,
        outcome: CommandOutcome,
        completed_at: datetime,
        commit_id: CommitId | None = None,
        boundary_evaluation_summary_ref: uuid.UUID | None = None,
        failure_code: str | None = None,
    ) -> None: ...

    def get_command(self, command_id: CommandId) -> CommandRecord | None: ...

    def list_unresolved_for_target(
        self, *, workspace_id: WorkspaceId, command_type: str, target_ref: str
    ) -> tuple[CommandId, ...]: ...

    def get_attempt(self, attempt_id: AttemptId) -> CommandAttempt | None: ...

    def list_attempts(self, command_id: CommandId) -> tuple[CommandAttempt, ...]: ...


class SqlAlchemyCommandRepository:
    """`CommandRepository` backed by `commands`/`command_attempts` via a
    SQLAlchemy Core connection.
    """

    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def record_attempt(self, envelope: CommandEnvelope, *, received_at: datetime) -> CommandAttempt:
        if self.get_attempt(envelope.attempt_id) is not None:
            raise AttemptAlreadyRecorded(f"attempt_id {envelope.attempt_id!r} already recorded")

        fingerprint = compute_payload_fingerprint(envelope.payload)
        existing = self.get_command(envelope.command_id)
        if existing is None:
            self._connection.execute(
                sa.insert(commands_table).values(
                    id=envelope.command_id.value,
                    workspace_id=envelope.workspace_scope_ref.value,
                    command_type=envelope.command_type,
                    contract_version=envelope.command_contract_version.value,
                    payload_fingerprint=fingerprint,
                    created_at=received_at,
                    target_refs=list(envelope.target_refs),
                )
            )
        else:
            # Mandatory adversarial attack: wrong Workspace.
            if existing.workspace_id != envelope.workspace_scope_ref:
                raise CommandWorkspaceMismatch(
                    f"command_id {envelope.command_id!r} already recorded at Workspace "
                    f"{existing.workspace_id!r}, envelope claims "
                    f"{envelope.workspace_scope_ref!r}"
                )
            # F02 WU-02.12 (FBR-B): same id, different Command type is a
            # different logical operation (09 section 4.3), whatever the
            # payload fingerprint says.
            if existing.command_type != envelope.command_type:
                raise CommandTypeMismatch(
                    f"command_id {envelope.command_id!r} already recorded as "
                    f"{existing.command_type}, envelope claims {envelope.command_type}"
                )
            # Mandatory adversarial attack: changed payload under same
            # command identity. A legitimate retry (09 section 12.1)
            # has an unchanged fingerprint and falls through to record
            # a new attempt row only.
            if existing.payload_fingerprint != fingerprint:
                raise CommandPayloadConflict(
                    f"command_id {envelope.command_id!r} already recorded with a different "
                    "payload fingerprint; a changed payload requires a new command_id "
                    "(09 section 12.4/139)"
                )

        self._connection.execute(
            sa.insert(command_attempts_table).values(
                id=envelope.attempt_id.value,
                command_id=envelope.command_id.value,
                workspace_id=envelope.workspace_scope_ref.value,
                actor_ref=envelope.requesting_actor_id,
                received_at=received_at,
                boundary_evaluation_summary_ref=None,
                commit_id=None,
                outcome=None,
                completed_at=None,
                failure_code=None,
            )
        )
        return CommandAttempt(
            command_id=envelope.command_id,
            attempt_id=envelope.attempt_id,
            workspace_id=envelope.workspace_scope_ref,
            actor_ref=envelope.requesting_actor_id,
            received_at=received_at,
            boundary_evaluation_summary_ref=None,
            commit_id=None,
            outcome=None,
            completed_at=None,
            failure_code=None,
        )

    def record_outcome(
        self,
        *,
        attempt_id: AttemptId,
        workspace_id: WorkspaceId,
        outcome: CommandOutcome,
        completed_at: datetime,
        commit_id: CommitId | None = None,
        boundary_evaluation_summary_ref: uuid.UUID | None = None,
        failure_code: str | None = None,
    ) -> None:
        current = self.get_attempt(attempt_id)
        if current is None:
            raise AttemptNotFound(f"attempt_id {attempt_id!r} not found")
        if current.outcome is not None:
            raise AttemptOutcomeAlreadyFinal(
                f"attempt_id {attempt_id!r} already has a determined outcome ({current.outcome!r})"
            )
        result = self._connection.execute(
            sa.update(command_attempts_table)
            .where(
                command_attempts_table.c.id == attempt_id.value,
                command_attempts_table.c.workspace_id == workspace_id.value,
            )
            .values(
                outcome=outcome.value,
                completed_at=completed_at,
                commit_id=None if commit_id is None else commit_id.value,
                boundary_evaluation_summary_ref=boundary_evaluation_summary_ref,
                failure_code=failure_code,
            )
        )
        if result.rowcount == 0:
            raise AttemptNotFound(
                f"attempt_id {attempt_id!r} not found at workspace {workspace_id!r}"
            )

    def get_command(self, command_id: CommandId) -> CommandRecord | None:
        stmt = sa.select(commands_table).where(commands_table.c.id == command_id.value)
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else _command_from_row(row)

    def list_unresolved_for_target(
        self, *, workspace_id: WorkspaceId, command_type: str, target_ref: str
    ) -> tuple[CommandId, ...]:
        """F03 WU-03.4 (FBR-F03-3). Commands of `command_type` that target
        `target_ref` and are UNRESOLVED: some attempt has no outcome yet
        (IN_PROGRESS) or is INDETERMINATE (09 §18; 10 §4.4: never assumed
        either way), no attempt of the same Command COMMITTED, and no recovery
        record for the Command has left UNRESOLVED (10 §64: recovery is the
        architecture's resolution path for an uncertain consequence)."""
        c, a, r = commands_table, command_attempts_table, recovery_records_table
        committed = sa.exists().where(
            a.c.command_id == c.c.id,
            a.c.workspace_id == c.c.workspace_id,
            a.c.outcome == CommandOutcome.COMMITTED.value,
        )
        uncertain = sa.exists().where(
            a.c.command_id == c.c.id,
            a.c.workspace_id == c.c.workspace_id,
            sa.or_(a.c.outcome.is_(None), a.c.outcome == CommandOutcome.INDETERMINATE.value),
        )
        recovered = sa.exists().where(
            r.c.original_command_id == c.c.id,
            r.c.workspace_id == c.c.workspace_id,
            r.c.result != "UNRESOLVED",
        )
        rows = self._connection.execute(
            sa.select(c.c.id)
            .where(
                c.c.workspace_id == workspace_id.value,
                c.c.command_type == command_type,
                c.c.target_refs.any(target_ref),
                uncertain,
                sa.not_(committed),
                sa.not_(recovered),
            )
            .order_by(c.c.created_at.asc(), c.c.id.asc())
        ).all()
        return tuple(CommandId(row[0]) for row in rows)

    def get_attempt(self, attempt_id: AttemptId) -> CommandAttempt | None:
        stmt = sa.select(command_attempts_table).where(
            command_attempts_table.c.id == attempt_id.value
        )
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else _attempt_from_row(row)

    def list_attempts(self, command_id: CommandId) -> tuple[CommandAttempt, ...]:
        stmt = (
            sa.select(command_attempts_table)
            .where(command_attempts_table.c.command_id == command_id.value)
            .order_by(command_attempts_table.c.received_at.asc())
        )
        rows = self._connection.execute(stmt).mappings().all()
        return tuple(_attempt_from_row(row) for row in rows)


def _command_from_row(row: sa.RowMapping) -> CommandRecord:
    return CommandRecord(
        command_id=CommandId(row["id"]),
        workspace_id=WorkspaceId(row["workspace_id"]),
        command_type=row["command_type"],
        contract_version=ContractVersion(row["contract_version"]),
        payload_fingerprint=row["payload_fingerprint"],
        created_at=row["created_at"],
        target_refs=tuple(row["target_refs"] or ()),
    )


def _attempt_from_row(row: sa.RowMapping) -> CommandAttempt:
    return CommandAttempt(
        command_id=CommandId(row["command_id"]),
        attempt_id=AttemptId(row["id"]),
        workspace_id=WorkspaceId(row["workspace_id"]),
        actor_ref=row["actor_ref"],
        received_at=row["received_at"],
        boundary_evaluation_summary_ref=row["boundary_evaluation_summary_ref"],
        commit_id=None if row["commit_id"] is None else CommitId(row["commit_id"]),
        outcome=None if row["outcome"] is None else CommandOutcome(row["outcome"]),
        completed_at=row["completed_at"],
        failure_code=row["failure_code"],
    )


__all__ = [
    "CommandRecord",
    "CommandAttempt",
    "CommandWorkspaceMismatch",
    "CommandPayloadConflict",
    "CommandTypeMismatch",
    "AttemptAlreadyRecorded",
    "AttemptOutcomeAlreadyFinal",
    "AttemptNotFound",
    "CommandRepository",
    "SqlAlchemyCommandRepository",
]
