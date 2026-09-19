"""CommitCoordinator: the atomic governed CommitUnit orchestrator.

Source: 09_DATA_EVENT_API_CONTRACTS.md section 13 (CommitUnit -- exact
field list, 3-value outcome vocabulary), section 14 (AC-09-002 Governed
Commit Unit: "canonical state mutation + required relation mutation +
required audit record + required durable event-outbox entry must be
persisted as one atomic commit unit... If the architecture cannot prove
atomicity: outcome = INDETERMINATE, dependent consequence blocked"),
section 121 (Audit Failure Semantics: "Before commit: FAILED_PRECOMMIT.
After database commit but delivery failure: Canonical commit remains
COMMITTED... Commit result uncertain: INDETERMINATE");
14_IMPLEMENTATION_SEQUENCE.md section 25 (the 16-step commit sequence
this coordinator materializes literally), section 40 (FailureInjector's
11 named hook points), section 46 (PKG-13 OBJECTIVE, the exact step
list transcribed as this module's own `_commit_inner` body).

WHY "BEGIN TRANSACTION"/"COMMIT DATABASE TRANSACTION" ARE A SAVEPOINT
(`connection.begin_nested()`), NOT A TOP-LEVEL TRANSACTION
--------------------------------------------------------------------
`[IMPLEMENTATION CHOICE]`, disclosed: every test fixture in this
codebase already wraps its `db_connection` in an outer
`connection.begin()` for rollback-based test isolation (established
since PKG-01). A production deployment's request-scoped session
management (Phase 10+, not yet built) would own that outer transaction
boundary for real; this package cannot invent that infrastructure
without exceeding its own scope. A SAVEPOINT nested inside whatever
transaction the caller already has open is the mechanism available at
this build phase that still proves genuine all-or-nothing atomicity for
the bundle (mutation + audit + outbox + commit_units + idempotency
update) -- 09's own semantic requirement -- without requiring a second
real database connection per commit attempt. `[IMPLEMENTATION CHOICE]`,
same status as 09/14's own "one PostgreSQL database... one transactional
authority" choice (14 section 4).

WHY GENUINE INDETERMINATE CANNOT BE FULLY MANUFACTURED HERE, AND WHAT
THIS MODULE DOES INSTEAD
--------------------------------------------------------------------
True INDETERMINATE (a network partition where the server may or may not
have committed and the client cannot tell) is a distributed-systems
condition this single-process, single-connection prototype coordinator
cannot genuinely reproduce -- proving it exhaustively is 10's Recovery/
reconciliation machinery, Phase 9+ (SUCCESSOR_NOT_BUILT). What this
module does: if `FailureInjectionPort` raises
`AmbiguousCommitFailure` at or after the `BEFORE_DB_COMMIT` hook (i.e.
after every write this coordinator's own SAVEPOINT contains has already
been *attempted*, unlike an earlier-point failure which is a *proven*
rollback), the coordinator cannot locally distinguish "committed" from
"not committed" for that SAVEPOINT release, so it records the honest
`INDETERMINATE` disposition via a **separate**, independent write (its
own commit_units row, outside the ambiguous SAVEPOINT) rather than
guessing either way -- 09 section 14's own "dependent consequence
blocked" is exactly why a real caller must treat this identically to a
failure, never as a success.

WHY THIS MODULE RESOLVES EVIDENCE FRESHNESS ITSELF (PKG-17), THE SAME
WAY IT ALREADY RESOLVES `current_versions`
--------------------------------------------------------------------
09 section 114: "BND-014 compares member versions/current states."
The freshness this requires is "immediately before commit" -- the
identical reasoning `boundaries.bnd_014_commit`'s own module docstring
already gives for why `current_versions` is read by this coordinator,
not supplied stale by an earlier caller. When `envelope.evidence_set_ref`
is set, `commit()` re-resolves it via a caller-supplied
`evidence_freshness_reader` (optional, defaults to `None` -- every
existing caller commits envelopes with no `evidence_set_ref` at all,
so this is a non-breaking widening, the same precedent
`MutationOutcome.relation_refs` already established at PKG-14) and
passes the result into `Bnd014Input.evidence_freshness`. A caller that
sets `evidence_set_ref` but supplies no reader fails closed (06
section 19 FAILURE BEHAVIOR) rather than silently skipping the check.

WHY "connection loss after commit" IS NOT A SEPARATE CODE PATH HERE
--------------------------------------------------------------------
Once a commit genuinely succeeds (COMMITTED, real rows exist), a caller
who never received the response and retries is already fully covered
by `commit.idempotency.decide_idempotency_action`'s own
`RETURN_COMMITTED_RESULT` disposition (PKG-11) -- the retry finds the
IdempotencyRecord already COMMITTED and returns the prior `result_ref`
without this coordinator doing anything special. Inventing a second
mechanism here would duplicate an invariant PKG-11 already proves.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol, runtime_checkable

import sqlalchemy as sa
from audit.models import AuditEvent, AuditRepository
from authority.actor import ActorIdentity
from boundaries.bnd_014_commit import Bnd014CommitEvaluator, Bnd014Input
from boundaries.types import BoundaryContext, BoundaryId, BoundaryProof, BoundaryResult
from command.envelope import CommandEnvelope, CommandOutcome
from events.outbox import DeliveryStatus, OutboxRecord, OutboxRepository
from evidence.freshness import (
    EvidenceFreshnessPort,
    EvidenceSetFreshnessResult,
    resolve_evidence_set_freshness,
)
from governance.authority_binding import AuthorityClass
from persistence.command_repository import CommandRepository
from semantic_types.ids import (
    AttemptId,
    AuditEventId,
    CommandId,
    CommitId,
    EventId,
    WorkspaceId,
)
from semantic_types.versions import ContractVersion, RecordVersion

from commit.idempotency import IdempotencyPort


class CommitOutcome(Enum):
    """09 section 13's exact 3-value closed vocabulary for
    CommitUnit.outcome. Deliberately *not* the same 4 values as
    `command.envelope.CommandOutcome` (no `DENIED` here -- a denied
    request never produces a CommitUnit at all, per 09's own field
    list) and not the same 4 as `commit.idempotency.IdempotencyOutcome`
    either (no `IN_PROGRESS` here -- a CommitUnit is only ever written
    once an attempt has resolved to one of these 3 terminal shapes).
    """

    FAILED_PRECOMMIT = "FAILED_PRECOMMIT"
    COMMITTED = "COMMITTED"
    INDETERMINATE = "INDETERMINATE"


class CommitInjectionPoint(Enum):
    """14 section 40's exact 11 named `FailureInjector` hook points."""

    BEFORE_TRANSACTION = "BEFORE_TRANSACTION"
    AFTER_AUTHORITY_EVALUATION = "AFTER_AUTHORITY_EVALUATION"
    AFTER_BND014 = "AFTER_BND014"
    AFTER_FIRST_CANONICAL_MUTATION = "AFTER_FIRST_CANONICAL_MUTATION"
    AFTER_RELATION_MUTATION = "AFTER_RELATION_MUTATION"
    BEFORE_AUDIT = "BEFORE_AUDIT"
    AFTER_AUDIT = "AFTER_AUDIT"
    BEFORE_OUTBOX = "BEFORE_OUTBOX"
    AFTER_OUTBOX = "AFTER_OUTBOX"
    BEFORE_DB_COMMIT = "BEFORE_DB_COMMIT"
    AFTER_DB_COMMIT_BEFORE_RESPONSE = "AFTER_DB_COMMIT_BEFORE_RESPONSE"


class AmbiguousCommitFailure(Exception):
    """A `FailureInjectionPort` implementation raises this specific
    exception type (never a bare `Exception`) to signal the one
    injected scenario `CommitCoordinator` treats as genuinely
    uncertain rather than a proven rollback. Production code never
    raises this itself.
    """


@runtime_checkable
class FailureInjectionPort(Protocol):
    """14 section 40's deterministic failure-injection hooks, as a
    production-importable Protocol (mirrors `semantic_types.clock.Clock`
    vs `test_support.clock.FixedClock`: the port lives here, the
    concrete deterministic double lives in `test_support`, so this
    production module never imports `test_support` -- see
    `scripts/check_test_only_imports.py`).
    """

    def before(self, point: CommitInjectionPoint) -> None: ...


class NullFailureInjector:
    """Production default: never raises."""

    def before(self, point: CommitInjectionPoint) -> None:
        return None


@dataclass(frozen=True, slots=True)
class MutationOutcome:
    """The facts `CommitCoordinator` needs back from a caller-supplied
    `MutationExecutor` beyond "it did not raise": opaque before/after
    state references for the AuditEvent this coordinator writes, and
    (PKG-14) any relation refs the mutation created -- 09 section 14's
    own AC-09-002 distinguishes "canonical state mutation" from
    "required relation mutation"; `target_refs` (from the envelope)
    covers the former, `relation_refs` covers the latter. Deliberately
    minimal -- 09's own `state_before_ref`/`state_after_ref` are themselves
    optional opaque references, not structured objects, and every
    existing caller (PKG-13's own tests) leaves `relation_refs` at its
    default empty tuple, matching a mutation that touches no relation.
    """

    state_before_ref: str | None = None
    state_after_ref: str | None = None
    relation_refs: tuple[str, ...] = ()


class StaleVersionConflict(Exception):
    """Raised by a `MutationExecutor` implementation when its own
    expected-version-guarded write affects zero rows -- a race between
    BND-014's fresh read and this attempt's actual write (mandatory
    adversarial attack: "concurrent Commands" / "state version changed"
    at the persistence layer, the second, narrower line of defense
    behind BND-014's own application-layer version check).
    """


@runtime_checkable
class MutationExecutor(Protocol):
    """Caller-supplied unit of canonical/relation mutation work. No
    concrete implementation exists in this package -- PKG-13 builds only
    the generic orchestration engine, the same "engine now, concrete
    instances later" split PKG-08/PKG-10 already established. This
    package's own tests supply a `MutationExecutor` wrapping a REAL
    predecessor repository method (`persistence.burst_repository.
    BurstRepository.start`, PKG-07) rather than inventing a new
    concrete Command.
    """

    def apply(self) -> MutationOutcome: ...


@runtime_checkable
class CurrentVersionReader(Protocol):
    """Caller-supplied fresh current-version lookup, invoked by this
    coordinator immediately before BND-014 -- see
    `boundaries.bnd_014_commit`'s own module docstring for why this
    generic engine cannot perform that read itself.
    """

    def read(self, target_ref: str) -> RecordVersion | None: ...


@dataclass(frozen=True, slots=True)
class CommitUnit:
    """09 section 13's exact field list."""

    commit_id: CommitId
    command_id: CommandId
    attempt_id: AttemptId
    workspace_id: WorkspaceId
    target_refs: tuple[str, ...]
    relation_refs: tuple[str, ...]
    governance_refs: tuple[str, ...]
    audit_event_ids: tuple[AuditEventId, ...]
    outbox_ids: tuple[uuid.UUID, ...]
    committed_at: datetime
    outcome: CommitOutcome
    commit_time_proof_ref: uuid.UUID | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.commit_id, CommitId):
            raise TypeError(f"commit_id must be a CommitId, got {type(self.commit_id)!r}")
        if not isinstance(self.command_id, CommandId):
            raise TypeError(f"command_id must be a CommandId, got {type(self.command_id)!r}")
        if not isinstance(self.attempt_id, AttemptId):
            raise TypeError(f"attempt_id must be an AttemptId, got {type(self.attempt_id)!r}")
        if not isinstance(self.workspace_id, WorkspaceId):
            raise TypeError(f"workspace_id must be a WorkspaceId, got {type(self.workspace_id)!r}")
        if not isinstance(self.outcome, CommitOutcome):
            raise TypeError(f"outcome must be a CommitOutcome, got {type(self.outcome)!r}")


@runtime_checkable
class CommitRepository(Protocol):
    """14 section 10: "CommitRepository: CommitUnit proof records."""

    def append(self, commit_unit: CommitUnit) -> None: ...

    def get(self, commit_id: CommitId) -> CommitUnit | None: ...


class EvidenceFreshnessReaderRequired(Exception):
    """Raised when `envelope.evidence_set_ref` is set but no
    `evidence_freshness_reader` was supplied to `commit()` -- 06
    section 19 FAILURE BEHAVIOR: "Fail closed when Evidence is
    required and validity cannot be proven," applied to a caller
    misconfiguration rather than silently treating Evidence as
    not-required.
    """


class CommitDenied(Exception):
    """BND-014 itself denied; no CommitUnit was ever created (09's own
    3-value CommitUnit.outcome vocabulary has no DENIED member -- a
    denial never reaches the point of having a CommitUnit at all).
    """

    def __init__(self, boundary_proof: BoundaryProof) -> None:
        self.boundary_proof = boundary_proof
        super().__init__(f"CommitDenied: {boundary_proof.reason_code}")


class CommitFailedPrecommit(Exception):
    """The atomic bundle was proven rolled back before any durable
    write took effect (SAVEPOINT rollback) -- 09 section 121: "Before
    commit: FAILED_PRECOMMIT."
    """

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"CommitFailedPrecommit: {reason}")


class CommitIndeterminate(Exception):
    """The commit's own fate could not be locally proven either way --
    09 section 14: "outcome = INDETERMINATE, dependent consequence
    blocked." See module docstring for what this coordinator can and
    cannot prove about this disposition at this build phase.
    """

    def __init__(self, commit_id: CommitId) -> None:
        self.commit_id = commit_id
        super().__init__(f"CommitIndeterminate: {commit_id}")


class CommitCoordinator:
    """The generic atomic-commit orchestration engine (14 PUBLIC
    INTERFACES: CommitCoordinator). No concrete Command is wired
    through this class in production yet -- 14 section 46 assigns no
    concrete Command to PKG-13 either (COMMANDS: NOT_APPLICABLE, "If
    none are assigned").
    """

    def __init__(
        self,
        connection: sa.Connection,
        *,
        bnd014_evaluator: Bnd014CommitEvaluator,
        command_repository: CommandRepository,
        audit_repository: AuditRepository,
        outbox_repository: OutboxRepository,
        commit_repository: CommitRepository,
        idempotency_port: IdempotencyPort,
        failure_injector: FailureInjectionPort | None = None,
    ) -> None:
        self._connection = connection
        self._bnd014_evaluator = bnd014_evaluator
        self._command_repository = command_repository
        self._audit_repository = audit_repository
        self._outbox_repository = outbox_repository
        self._commit_repository = commit_repository
        self._idempotency_port = idempotency_port
        self._failure_injector = failure_injector or NullFailureInjector()

    def commit(
        self,
        *,
        envelope: CommandEnvelope,
        actor: ActorIdentity,
        required_authority_class: AuthorityClass,
        authority_scope_type: str,
        authority_scope_id: uuid.UUID,
        upstream_chain_result: BoundaryResult,
        current_version_reader: CurrentVersionReader,
        mutation: MutationExecutor,
        occurred_at: datetime,
        commit_id: CommitId,
        evidence_freshness_reader: EvidenceFreshnessPort | None = None,
    ) -> CommitUnit:
        self._failure_injector.before(CommitInjectionPoint.BEFORE_TRANSACTION)

        current_versions: dict[str, RecordVersion | None] = {
            ref: current_version_reader.read(ref) for ref in envelope.target_refs
        }

        evidence_freshness: EvidenceSetFreshnessResult | None = None
        if envelope.evidence_set_ref is not None:
            if evidence_freshness_reader is None:
                raise EvidenceFreshnessReaderRequired(
                    f"envelope {envelope.command_id!r} names evidence_set_ref "
                    f"{envelope.evidence_set_ref!r} but no evidence_freshness_reader was supplied"
                )
            evidence_freshness = resolve_evidence_set_freshness(
                envelope.evidence_set_ref,
                workspace_id=envelope.workspace_scope_ref,
                reader=evidence_freshness_reader,
            )

        context = BoundaryContext(
            workspace_id=envelope.workspace_scope_ref,
            operation=envelope.command_type,
            actor=actor,
            correlation_id=envelope.correlation_id,
            evaluated_at=occurred_at,
        )
        self._failure_injector.before(CommitInjectionPoint.AFTER_AUTHORITY_EVALUATION)
        bnd014_input = Bnd014Input(
            boundary_id=BoundaryId.BND_014,
            context=context,
            required_authority_class=required_authority_class,
            authority_scope_type=authority_scope_type,
            authority_scope_id=authority_scope_id,
            expected_versions=envelope.expected_versions,
            current_versions=current_versions,
            upstream_chain_result=upstream_chain_result,
            evidence_freshness=evidence_freshness,
        )
        proof = self._bnd014_evaluator.evaluate(bnd014_input, context)
        self._failure_injector.before(CommitInjectionPoint.AFTER_BND014)
        if proof.result is not BoundaryResult.ALLOW:
            raise CommitDenied(proof)

        try:
            commit_unit = self._commit_inner(
                envelope=envelope,
                proof=proof,
                mutation=mutation,
                occurred_at=occurred_at,
                commit_id=commit_id,
            )
        except AmbiguousCommitFailure:
            self._record_indeterminate(
                envelope=envelope, occurred_at=occurred_at, commit_id=commit_id
            )
            raise CommitIndeterminate(commit_id) from None
        except StaleVersionConflict as exc:
            self._mark_failed_precommit(envelope, occurred_at=occurred_at)
            raise CommitFailedPrecommit(reason=str(exc)) from exc
        except Exception as exc:  # noqa: BLE001 -- any other failure inside the SAVEPOINT is a proven rollback
            self._mark_failed_precommit(envelope, occurred_at=occurred_at)
            raise CommitFailedPrecommit(reason=f"{type(exc).__name__}: {exc}") from exc

        self._failure_injector.before(CommitInjectionPoint.AFTER_DB_COMMIT_BEFORE_RESPONSE)
        return commit_unit

    def _commit_inner(
        self,
        *,
        envelope: CommandEnvelope,
        proof: BoundaryProof,
        mutation: MutationExecutor,
        occurred_at: datetime,
        commit_id: CommitId,
    ) -> CommitUnit:
        audit_event_id = AuditEventId(uuid.uuid4())
        outbox_id = uuid.uuid4()
        authority_source_ref = (
            proof.authority_proof.binding_id.value
            if proof.authority_proof is not None and proof.authority_proof.binding_id is not None
            else uuid.uuid4()
        )

        with self._connection.begin_nested():
            mutation_outcome = mutation.apply()
            self._failure_injector.before(CommitInjectionPoint.AFTER_FIRST_CANONICAL_MUTATION)
            self._failure_injector.before(CommitInjectionPoint.AFTER_RELATION_MUTATION)

            # `commit_units` is written BEFORE `audit_events`/`outbox_events`
            # deliberately: their composite FK to `commit_units(id,
            # workspace_id)` (migration `b06f9a5b3d1b`) requires the row
            # to already exist, while `commit_units.audit_event_ids`/
            # `outbox_ids` need only the *values* (already generated
            # above), not the rows themselves -- no FK is declared on
            # those two array columns, so this ordering has no circular
            # dependency at all, unlike the naive "audit/outbox first"
            # ordering it replaces.
            commit_unit = CommitUnit(
                commit_id=commit_id,
                command_id=envelope.command_id,
                attempt_id=envelope.attempt_id,
                workspace_id=envelope.workspace_scope_ref,
                target_refs=envelope.target_refs,
                relation_refs=mutation_outcome.relation_refs,
                governance_refs=(),
                audit_event_ids=(audit_event_id,),
                outbox_ids=(outbox_id,),
                committed_at=occurred_at,
                outcome=CommitOutcome.COMMITTED,
            )
            self._commit_repository.append(commit_unit)

            self._failure_injector.before(CommitInjectionPoint.BEFORE_AUDIT)
            audit_event = AuditEvent(
                audit_event_id=audit_event_id,
                event_type=f"{envelope.command_type}_COMMITTED",
                event_schema_version=ContractVersion("1.0"),
                workspace_id=envelope.workspace_scope_ref,
                occurred_at=occurred_at,
                actor_type=envelope.requesting_actor_type,
                actor_id=envelope.requesting_actor_id,
                command_type=envelope.command_type,
                command_id=envelope.command_id,
                commit_id=commit_id,
                correlation_id=envelope.correlation_id,
                causation_id=envelope.causation_id,
                target_refs=envelope.target_refs,
                authority_source_ref=authority_source_ref,
                result=CommitOutcome.COMMITTED.value,
                human_decision_ref=envelope.human_decision_ref,
                evidence_set_ref=envelope.evidence_set_ref,
                state_before_ref=mutation_outcome.state_before_ref,
                state_after_ref=mutation_outcome.state_after_ref,
            )
            self._audit_repository.append(audit_event)
            self._failure_injector.before(CommitInjectionPoint.AFTER_AUDIT)

            self._failure_injector.before(CommitInjectionPoint.BEFORE_OUTBOX)
            outbox_record = OutboxRecord(
                outbox_id=outbox_id,
                event_id=EventId(uuid.uuid4()),
                workspace_id=envelope.workspace_scope_ref,
                commit_id=commit_id,
                event_type=f"{envelope.command_type}_COMMITTED",
                created_at=occurred_at,
                delivery_status=DeliveryStatus.PENDING,
                delivery_attempt_count=0,
            )
            self._outbox_repository.append(outbox_record)
            self._failure_injector.before(CommitInjectionPoint.AFTER_OUTBOX)

            self._command_repository.record_outcome(
                attempt_id=envelope.attempt_id,
                workspace_id=envelope.workspace_scope_ref,
                outcome=CommandOutcome.COMMITTED,
                completed_at=occurred_at,
                commit_id=commit_id,
            )

            if envelope.idempotency_key is not None:
                self._idempotency_port.mark_committed(
                    workspace_id=envelope.workspace_scope_ref,
                    command_type=envelope.command_type,
                    idempotency_key=envelope.idempotency_key,
                    commit_id=commit_id,
                    result_ref=str(commit_id.value),
                )

            self._failure_injector.before(CommitInjectionPoint.BEFORE_DB_COMMIT)

        return commit_unit

    def _mark_failed_precommit(self, envelope: CommandEnvelope, *, occurred_at: datetime) -> None:
        with self._connection.begin_nested():
            self._command_repository.record_outcome(
                attempt_id=envelope.attempt_id,
                workspace_id=envelope.workspace_scope_ref,
                outcome=CommandOutcome.FAILED_PRECOMMIT,
                completed_at=occurred_at,
            )
            if envelope.idempotency_key is not None:
                self._idempotency_port.mark_failed_precommit(
                    workspace_id=envelope.workspace_scope_ref,
                    command_type=envelope.command_type,
                    idempotency_key=envelope.idempotency_key,
                )

    def _record_indeterminate(
        self, *, envelope: CommandEnvelope, occurred_at: datetime, commit_id: CommitId
    ) -> None:
        """A separate, independent write (its own SAVEPOINT) recording
        the honest "cannot prove either way" disposition -- deliberately
        not inside the ambiguous attempt's own SAVEPOINT. See module
        docstring. The caller raises `CommitIndeterminate` once this
        returns.
        """
        commit_unit = CommitUnit(
            commit_id=commit_id,
            command_id=envelope.command_id,
            attempt_id=envelope.attempt_id,
            workspace_id=envelope.workspace_scope_ref,
            target_refs=(),
            relation_refs=(),
            governance_refs=(),
            audit_event_ids=(),
            outbox_ids=(),
            committed_at=occurred_at,
            outcome=CommitOutcome.INDETERMINATE,
        )
        with self._connection.begin_nested():
            self._commit_repository.append(commit_unit)
            self._command_repository.record_outcome(
                attempt_id=envelope.attempt_id,
                workspace_id=envelope.workspace_scope_ref,
                outcome=CommandOutcome.INDETERMINATE,
                completed_at=occurred_at,
                commit_id=commit_id,
            )
            if envelope.idempotency_key is not None:
                self._idempotency_port.mark_indeterminate(
                    workspace_id=envelope.workspace_scope_ref,
                    command_type=envelope.command_type,
                    idempotency_key=envelope.idempotency_key,
                )


__all__ = [
    "CommitOutcome",
    "CommitInjectionPoint",
    "AmbiguousCommitFailure",
    "FailureInjectionPort",
    "NullFailureInjector",
    "MutationOutcome",
    "StaleVersionConflict",
    "MutationExecutor",
    "CurrentVersionReader",
    "CommitUnit",
    "CommitRepository",
    "EvidenceFreshnessReaderRequired",
    "CommitDenied",
    "CommitFailedPrecommit",
    "CommitIndeterminate",
    "CommitCoordinator",
]
