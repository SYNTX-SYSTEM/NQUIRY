"""Idempotency lifecycle: IdempotencyPort, IdempotencyRecord, and the
pure decision engine 09 section 11 / 14 section 27 both define.

Source: 09_DATA_EVENT_API_CONTRACTS.md section 11 (IdempotencyRecord --
the authoritative field list and 4-value outcome vocabulary), section
11.1 (Idempotency Does Not Authorize), section 12 (Command Retry
Semantics), section 139-140 (AC-09-013 Idempotency Payload Binding);
14_IMPLEMENTATION_SEQUENCE.md section 27 (IDEMPOTENCY -- the 6
dispositions a new request against a possibly-existing record must
resolve to), section 48 (file-level map: `packages/commit/idempotency.py`,
"idempotency lifecycle", allowed imports "command/persistence ports",
forbidden "retry guess").

WHY `IdempotencyOutcome` HAS 4 VALUES DIFFERENT FROM `CommandOutcome`
--------------------------------------------------------------------
`command.envelope.CommandOutcome` (PKG-10) is {DENIED, FAILED_PRECOMMIT,
COMMITTED, INDETERMINATE} -- a disposition of one *attempt*, recorded on
every attempt regardless of whether execution ever began.
`IdempotencyOutcome` (this module) is {IN_PROGRESS, FAILED_PRECOMMIT,
COMMITTED, INDETERMINATE} per 09 section 11's own explicit list -- note
DENIED is absent and IN_PROGRESS is present instead. This is not an
oversight: an `IdempotencyRecord` exists to protect against *duplicate
consequence*, which only becomes a risk once a request has passed
boundaries and genuine execution has begun. A `DENIED` attempt never
reaches that point -- nothing about it needs duplicate-suppression,
since re-submitting a denied request is harmless (09 section 11.1: a
matching key "does not skip Identity, Scope, Authority, Boundary,
Commit-time freshness... for a new operation"). `command_attempts`
(PKG-10) is where a DENIED disposition is recorded; `idempotency_records`
(this package) never sees one.

WHY THE DECISION LOGIC IS PURE, EVEN THOUGH THE CONCRETE ADAPTER LIVES
IN THIS SAME FILE
--------------------------------------------------------------------
14 section 48's file-level map assigns this exact file "command/
persistence ports" as its allowed imports and "retry guess" as
forbidden -- i.e. no invented retry-eligibility heuristic. Unlike
PKG-10's `command`/`persistence` split (forced because `command`'s own
allowed-deps explicitly exclude `persistence` -- "no direct write"),
`commit`'s own directory-ownership row (14 section 3.1) already permits
"persistence ports" and forbids no DB driver at all -- `commit` is
"exclusive governed writer" by design, the one package meant to touch
persistence directly once BND-014/CommitUnit exist (PKG-13). The
concrete `SqlAlchemyIdempotencyRepository` therefore lives in this same
file rather than in `persistence/`, the opposite direction from
`command.envelope`/`persistence.command_repository` -- no new
`INTERNAL_ALLOWED` extension was needed for this package.
`decide_idempotency_action` itself remains a pure function with no I/O
regardless of which file calls it, so it stays independently testable
without a database exactly like `domain.session_transitions`'s
topology evaluators.

WHY A COMMAND-ID MISMATCH IS ALSO TREATED AS A COLLISION
--------------------------------------------------------------------
14 section 27 states only "same key different payload -> reject
collision" -- it does not explicitly mention `command_id`. This module
additionally rejects a mismatched `command_id` under an otherwise
identical idempotency identity (same Workspace/command_type/
idempotency_key) even when the payload fingerprint happens to match,
because 09 section 4.3 defines `command_id` as "the stable identity of
one logical requested consequential operation" -- a different
`command_id` is, by that definition, a different logical operation,
regardless of what its payload happens to contain. Treating it as a
legitimate retry would let a client silently substitute one logical
Command for another by reusing an idempotency_key. Disclosed here as a
deliberate, literal application of 09's own identity definition, not an
invented rule.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol, runtime_checkable

import sqlalchemy as sa
from command.envelope import CommandEnvelope, compute_payload_fingerprint
from persistence.tables import idempotency_records_table
from semantic_types.ids import AttemptId, CommandId, CommitId, WorkspaceId


class IdempotencyOutcome(Enum):
    """09 section 11's exact 4-value closed vocabulary for
    IdempotencyRecord.outcome. See module docstring for why this
    differs from `command.envelope.CommandOutcome`.
    """

    IN_PROGRESS = "IN_PROGRESS"
    FAILED_PRECOMMIT = "FAILED_PRECOMMIT"
    COMMITTED = "COMMITTED"
    INDETERMINATE = "INDETERMINATE"


@dataclass(frozen=True, slots=True)
class IdempotencyRecord:
    """09 section 11's exact field list."""

    idempotency_key: str
    workspace_id: WorkspaceId
    command_type: str
    command_id: CommandId
    payload_fingerprint: str
    first_seen_at: datetime
    latest_attempt_id: AttemptId
    outcome: IdempotencyOutcome
    commit_id: CommitId | None = None
    result_ref: str | None = None

    def __post_init__(self) -> None:
        if not self.idempotency_key:
            raise ValueError("IdempotencyRecord.idempotency_key must be non-empty")
        if not isinstance(self.workspace_id, WorkspaceId):
            raise TypeError(f"workspace_id must be a WorkspaceId, got {type(self.workspace_id)!r}")
        if not self.command_type:
            raise ValueError("IdempotencyRecord.command_type must be non-empty")
        if not isinstance(self.command_id, CommandId):
            raise TypeError(f"command_id must be a CommandId, got {type(self.command_id)!r}")
        if not self.payload_fingerprint:
            raise ValueError("IdempotencyRecord.payload_fingerprint must be non-empty")
        if not isinstance(self.latest_attempt_id, AttemptId):
            raise TypeError(
                f"latest_attempt_id must be an AttemptId, got {type(self.latest_attempt_id)!r}"
            )
        if not isinstance(self.outcome, IdempotencyOutcome):
            raise TypeError(f"outcome must be an IdempotencyOutcome, got {type(self.outcome)!r}")
        # 09 section 11: "commit_id if committed", "response_ref if safe
        # to replay" -- only COMMITTED is ever safe to replay.
        if (self.outcome is IdempotencyOutcome.COMMITTED) != (self.commit_id is not None):
            raise ValueError(
                "IdempotencyRecord.commit_id must be set if and only if outcome is COMMITTED"
            )
        if self.result_ref is not None and self.outcome is not IdempotencyOutcome.COMMITTED:
            raise ValueError(
                "IdempotencyRecord.result_ref may only be set when outcome is COMMITTED"
            )


class IdempotencyDecision(Enum):
    """The 6 dispositions 14 section 27 defines for a new request
    evaluated against a possibly-existing `IdempotencyRecord`.
    """

    PROCEED_NEW = "PROCEED_NEW"
    RETURN_IN_PROGRESS_NO_EXECUTION = "RETURN_IN_PROGRESS_NO_EXECUTION"
    RETURN_COMMITTED_RESULT = "RETURN_COMMITTED_RESULT"
    REJECT_PAYLOAD_COLLISION = "REJECT_PAYLOAD_COLLISION"
    PROCEED_FRESH_ATTEMPT_AFTER_FAILED_PRECOMMIT = "PROCEED_FRESH_ATTEMPT_AFTER_FAILED_PRECOMMIT"
    BLOCK_INDETERMINATE_NO_BLIND_RETRY = "BLOCK_INDETERMINATE_NO_BLIND_RETRY"


class IdempotencyLifecycleError(Exception):
    """Base class for every non-proceeding disposition. Carries the
    `existing` record so a caller can inspect it (e.g. to return a
    prior committed result) without a second database read.
    """

    def __init__(self, existing: IdempotencyRecord) -> None:
        self.existing = existing
        super().__init__(f"{type(self).__name__}: {existing.idempotency_key!r}")


class IdempotencyInProgress(IdempotencyLifecycleError):
    """14 section 27: "same identity IN_PROGRESS -> return in-progress
    state, no second execution."
    """


class IdempotencyAlreadyCommitted(IdempotencyLifecycleError):
    """14 section 27: "same identity COMMITTED -> return prior
    committed result." Mandatory adversarial attack: committed
    duplicate.
    """


class IdempotencyPayloadCollision(IdempotencyLifecycleError):
    """14 section 27: "same key different payload -> reject collision."
    Mandatory adversarial attack: same key different payload. Also
    raised for a command_id mismatch under the same idempotency
    identity (see module docstring).
    """


class IdempotencyIndeterminateBlocked(IdempotencyLifecycleError):
    """14 section 27: "INDETERMINATE -> no blind retry, route
    BND-017/BND-018." Mandatory adversarial attack: INDETERMINATE
    retry. Routing to BND-017/BND-018 is SUCCESSOR_NOT_BUILT (recovery,
    PKG-18+); this exception is the structural block itself.
    """


def decide_idempotency_action(
    *,
    existing: IdempotencyRecord | None,
    requested_command_id: CommandId,
    requested_payload_fingerprint: str,
) -> IdempotencyDecision:
    """Pure function: given whatever currently exists (already fetched
    by the caller, by the identity triple Workspace/command_type/
    idempotency_key) and the new request's command_id/payload
    fingerprint, decide the one legitimate disposition. No I/O, no
    retry-count heuristic, no timing input -- exactly 14 section 27's 6
    rules, nothing inferred beyond them.
    """
    if existing is None:
        return IdempotencyDecision.PROCEED_NEW
    if (
        existing.command_id != requested_command_id
        or existing.payload_fingerprint != requested_payload_fingerprint
    ):
        return IdempotencyDecision.REJECT_PAYLOAD_COLLISION
    if existing.outcome is IdempotencyOutcome.IN_PROGRESS:
        return IdempotencyDecision.RETURN_IN_PROGRESS_NO_EXECUTION
    if existing.outcome is IdempotencyOutcome.COMMITTED:
        return IdempotencyDecision.RETURN_COMMITTED_RESULT
    if existing.outcome is IdempotencyOutcome.FAILED_PRECOMMIT:
        return IdempotencyDecision.PROCEED_FRESH_ATTEMPT_AFTER_FAILED_PRECOMMIT
    if existing.outcome is IdempotencyOutcome.INDETERMINATE:
        return IdempotencyDecision.BLOCK_INDETERMINATE_NO_BLIND_RETRY
    raise AssertionError(
        "unreachable: IdempotencyOutcome is a closed 4-value enum"
    )  # pragma: no cover


def raise_for_decision(decision: IdempotencyDecision, existing: IdempotencyRecord) -> None:
    """Raises the exception matching every non-proceeding disposition.
    Callers branch on `PROCEED_NEW`/`PROCEED_FRESH_ATTEMPT_AFTER_FAILED_PRECOMMIT`
    before ever reaching this function (`PROCEED_NEW` in particular has
    no `existing` record to attach to an exception).
    """
    if decision is IdempotencyDecision.RETURN_IN_PROGRESS_NO_EXECUTION:
        raise IdempotencyInProgress(existing)
    if decision is IdempotencyDecision.RETURN_COMMITTED_RESULT:
        raise IdempotencyAlreadyCommitted(existing)
    if decision is IdempotencyDecision.REJECT_PAYLOAD_COLLISION:
        raise IdempotencyPayloadCollision(existing)
    if decision is IdempotencyDecision.BLOCK_INDETERMINATE_NO_BLIND_RETRY:
        raise IdempotencyIndeterminateBlocked(existing)
    raise AssertionError(
        f"raise_for_decision called with a proceeding decision {decision!r} -- "
        "caller must handle PROCEED_* before calling this function"
    )  # pragma: no cover


@runtime_checkable
class IdempotencyPort(Protocol):
    """The durable idempotency lifecycle port (14 section 46 PUBLIC
    INTERFACES: IdempotencyPort). `begin` is the single entry point
    that reads current state, applies `decide_idempotency_action`, and
    either returns a fresh IN_PROGRESS record (a legitimate new
    request or a FAILED_PRECOMMIT retry) or raises the matching
    `IdempotencyLifecycleError` subclass. No method here grants,
    caches, or infers authority -- 14 PKG-11 BOUNDARIES: "No authority
    cached in idempotency."
    """

    def begin(self, envelope: CommandEnvelope, *, seen_at: datetime) -> IdempotencyRecord: ...

    def get(
        self, *, workspace_id: WorkspaceId, command_type: str, idempotency_key: str
    ) -> IdempotencyRecord | None: ...

    def mark_committed(
        self,
        *,
        workspace_id: WorkspaceId,
        command_type: str,
        idempotency_key: str,
        commit_id: CommitId,
        result_ref: str | None,
    ) -> None: ...

    def mark_failed_precommit(
        self, *, workspace_id: WorkspaceId, command_type: str, idempotency_key: str
    ) -> None: ...

    def mark_indeterminate(
        self, *, workspace_id: WorkspaceId, command_type: str, idempotency_key: str
    ) -> None: ...


class IdempotencyRecordNotFound(Exception):
    """Raised by `mark_committed`/`mark_failed_precommit`/`mark_indeterminate`
    when no record exists for the given identity -- those methods only
    ever transition an existing IN_PROGRESS record, they never create one.
    """


class SqlAlchemyIdempotencyRepository:
    """`IdempotencyPort` backed by `idempotency_records` via a
    SQLAlchemy Core connection.

    `begin()` cannot simply "SELECT, decide, then INSERT if new" -- two
    concurrent callers could both SELECT and see nothing, then both
    attempt to INSERT (the mandatory adversarial attack "in-progress
    duplicate" is exactly this race). `idempotency_records`' own
    PRIMARY KEY, `(workspace_id, command_type, idempotency_key)`
    (`b5b33834b7ea_idempotency_records.py`), is what actually prevents
    two rows from ever existing for one identity -- this method's job
    is to turn the *loser* of that race into the correct decision
    (re-read the row the winner just created, and raise the exact same
    `IdempotencyLifecycleError` a caller who arrived microseconds later
    would have seen) instead of leaking a raw `sa.exc.IntegrityError`.
    See `test_begin_survives_a_concurrent_insert_race` for the
    deterministic proof (no sleep, no thread) -- it seeds the "as if a
    concurrent process already committed the INSERT" row directly,
    before calling `begin()`, which exercises the identical code path a
    real race's loser would.
    """

    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def begin(self, envelope: CommandEnvelope, *, seen_at: datetime) -> IdempotencyRecord:
        if not envelope.idempotency_key:
            raise ValueError("begin() requires envelope.idempotency_key to be set")

        existing = self.get(
            workspace_id=envelope.workspace_scope_ref,
            command_type=envelope.command_type,
            idempotency_key=envelope.idempotency_key,
        )
        fingerprint = compute_payload_fingerprint(envelope.payload)
        decision = decide_idempotency_action(
            existing=existing,
            requested_command_id=envelope.command_id,
            requested_payload_fingerprint=fingerprint,
        )

        if decision is IdempotencyDecision.PROCEED_NEW:
            try:
                # A SAVEPOINT, not the outer transaction: if the INSERT
                # loses the race below, only this nested transaction
                # rolls back -- the caller's own outer transaction (and
                # any subsequent statement on this connection, notably
                # this method's own re-read) remains usable.
                with self._connection.begin_nested():
                    self._connection.execute(
                        sa.insert(idempotency_records_table).values(
                            idempotency_key=envelope.idempotency_key,
                            workspace_id=envelope.workspace_scope_ref.value,
                            command_type=envelope.command_type,
                            command_id=envelope.command_id.value,
                            payload_fingerprint=fingerprint,
                            first_seen_at=seen_at,
                            latest_attempt_id=envelope.attempt_id.value,
                            outcome=IdempotencyOutcome.IN_PROGRESS.value,
                            commit_id=None,
                            result_ref=None,
                        )
                    )
            except sa.exc.IntegrityError as exc:
                # Mandatory adversarial attack: in-progress duplicate,
                # exact race -- another process won the INSERT between
                # our get() and this statement. Re-read and decide
                # again against what actually exists now. This is NOT
                # the only possible cause of an IntegrityError here (a
                # command_id with no matching `commands` row -- the
                # composite FK -- raises one too); `_resolve_after_race`
                # re-raises `exc` unchanged whenever no row turns up,
                # so a genuine caller error is never misreported as a
                # resolved race.
                return self._resolve_after_race(envelope, fingerprint, original_exc=exc)
            resolved = self.get(
                workspace_id=envelope.workspace_scope_ref,
                command_type=envelope.command_type,
                idempotency_key=envelope.idempotency_key,
            )
            assert resolved is not None  # just inserted above
            return resolved

        if decision is IdempotencyDecision.PROCEED_FRESH_ATTEMPT_AFTER_FAILED_PRECOMMIT:
            assert existing is not None  # decision implies a record exists
            result = self._connection.execute(
                sa.update(idempotency_records_table)
                .where(
                    idempotency_records_table.c.workspace_id == envelope.workspace_scope_ref.value,
                    idempotency_records_table.c.command_type == envelope.command_type,
                    idempotency_records_table.c.idempotency_key == envelope.idempotency_key,
                )
                .values(
                    outcome=IdempotencyOutcome.IN_PROGRESS.value,
                    latest_attempt_id=envelope.attempt_id.value,
                )
            )
            if result.rowcount == 0:
                raise IdempotencyRecordNotFound(
                    f"idempotency_key {envelope.idempotency_key!r} vanished between read and write"
                )
            resolved = self.get(
                workspace_id=envelope.workspace_scope_ref,
                command_type=envelope.command_type,
                idempotency_key=envelope.idempotency_key,
            )
            assert resolved is not None  # just updated above
            return resolved

        assert existing is not None  # every remaining decision implies a record exists
        raise_for_decision(decision, existing)
        raise AssertionError("unreachable")  # pragma: no cover

    def _resolve_after_race(
        self, envelope: CommandEnvelope, fingerprint: str, *, original_exc: sa.exc.IntegrityError
    ) -> IdempotencyRecord:
        assert envelope.idempotency_key is not None  # begin() already validated this
        existing = self.get(
            workspace_id=envelope.workspace_scope_ref,
            command_type=envelope.command_type,
            idempotency_key=envelope.idempotency_key,
        )
        if existing is None:
            # No row exists after all, so the IntegrityError was not a
            # PK-collision race on `idempotency_records` -- most likely
            # `envelope.command_id` has no matching `commands` row (the
            # composite FK), i.e. a genuine caller error: `begin()` must
            # be called only after `CommandRepository.record_attempt`
            # has already recorded the command. Re-raise the real cause
            # rather than reporting a misleading `IdempotencyRecordNotFound`.
            raise original_exc
        decision = decide_idempotency_action(
            existing=existing,
            requested_command_id=envelope.command_id,
            requested_payload_fingerprint=fingerprint,
        )
        if decision is IdempotencyDecision.PROCEED_NEW:
            raise AssertionError(  # pragma: no cover
                "PROCEED_NEW cannot recur once a row exists after IntegrityError"
            )
        raise_for_decision(decision, existing)
        raise AssertionError("unreachable")  # pragma: no cover

    def mark_committed(
        self,
        *,
        workspace_id: WorkspaceId,
        command_type: str,
        idempotency_key: str,
        commit_id: CommitId,
        result_ref: str | None,
    ) -> None:
        self._transition(
            workspace_id=workspace_id,
            command_type=command_type,
            idempotency_key=idempotency_key,
            values={
                "outcome": IdempotencyOutcome.COMMITTED.value,
                "commit_id": commit_id.value,
                "result_ref": result_ref,
            },
        )

    def mark_failed_precommit(
        self, *, workspace_id: WorkspaceId, command_type: str, idempotency_key: str
    ) -> None:
        self._transition(
            workspace_id=workspace_id,
            command_type=command_type,
            idempotency_key=idempotency_key,
            values={"outcome": IdempotencyOutcome.FAILED_PRECOMMIT.value},
        )

    def mark_indeterminate(
        self, *, workspace_id: WorkspaceId, command_type: str, idempotency_key: str
    ) -> None:
        self._transition(
            workspace_id=workspace_id,
            command_type=command_type,
            idempotency_key=idempotency_key,
            values={"outcome": IdempotencyOutcome.INDETERMINATE.value},
        )

    def _transition(
        self,
        *,
        workspace_id: WorkspaceId,
        command_type: str,
        idempotency_key: str,
        values: dict[str, object],
    ) -> None:
        result = self._connection.execute(
            sa.update(idempotency_records_table)
            .where(
                idempotency_records_table.c.workspace_id == workspace_id.value,
                idempotency_records_table.c.command_type == command_type,
                idempotency_records_table.c.idempotency_key == idempotency_key,
            )
            .values(**values)
        )
        if result.rowcount == 0:
            raise IdempotencyRecordNotFound(
                f"idempotency_key {idempotency_key!r} not found at workspace {workspace_id!r}"
            )

    def get(
        self, *, workspace_id: WorkspaceId, command_type: str, idempotency_key: str
    ) -> IdempotencyRecord | None:
        stmt = sa.select(idempotency_records_table).where(
            idempotency_records_table.c.workspace_id == workspace_id.value,
            idempotency_records_table.c.command_type == command_type,
            idempotency_records_table.c.idempotency_key == idempotency_key,
        )
        row = self._connection.execute(stmt).mappings().one_or_none()
        return None if row is None else _record_from_row(row)


def _record_from_row(row: sa.RowMapping) -> IdempotencyRecord:
    return IdempotencyRecord(
        idempotency_key=row["idempotency_key"],
        workspace_id=WorkspaceId(row["workspace_id"]),
        command_type=row["command_type"],
        command_id=CommandId(row["command_id"]),
        payload_fingerprint=row["payload_fingerprint"],
        first_seen_at=row["first_seen_at"],
        latest_attempt_id=AttemptId(row["latest_attempt_id"]),
        outcome=IdempotencyOutcome(row["outcome"]),
        commit_id=None if row["commit_id"] is None else CommitId(row["commit_id"]),
        result_ref=row["result_ref"],
    )


__all__ = [
    "IdempotencyOutcome",
    "IdempotencyRecord",
    "IdempotencyDecision",
    "IdempotencyLifecycleError",
    "IdempotencyInProgress",
    "IdempotencyAlreadyCommitted",
    "IdempotencyPayloadCollision",
    "IdempotencyIndeterminateBlocked",
    "decide_idempotency_action",
    "raise_for_decision",
    "IdempotencyPort",
    "IdempotencyRecordNotFound",
    "SqlAlchemyIdempotencyRepository",
]
