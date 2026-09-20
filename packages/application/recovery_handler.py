"""RecoveryService: the governed, deterministic Recovery Command path.

Source: 14_IMPLEMENTATION_SEQUENCE.md PKG-24's own OBJECTIVE ("Implement
BND-017 INDETERMINATE blocking, dependent-operation detection, BND-018
reconciliation routing, Recovery Command through normal identity,
Workspace, current authority, Evidence if required, boundaries, BND-014
and CommitUnit. Deterministic recovery only restores already-established
legitimate state. Discretionary domain choice requires existing human
authority."); 06_BOUNDARY_ARCHITECTURE.md section 25 (BND-018 REQUESTING
ACTOR: "SYSTEM_SERVICE for deterministic reconciliation"); 10_FAILURE_RECOVERY_ROLLBACK.md
section 32 (AC-10-005: deterministic recovery consumes the already-
approved 04/05 SYSTEM_DERIVED procedural model);
12_MINIMUM_PROTOTYPE_ARCHITECTURE.md's own minimum-proof list (RecoveryRecord,
BND-018, service identity, Workspace isolation -- no human discretionary
recovery flow named).

WHY THIS SERVICE DOES NOT CALL `commit.coordinator.CommitCoordinator`
--------------------------------------------------------------------
[HUMAN-CONFIRMED ARCHITECTURAL DECISION, PKG-24] `CommitCoordinator.commit()`
hard-requires a `required_authority_class: governance.authority_binding.
AuthorityClass` -- a closed 7-value enum whose every member is a HUMAN
Decision Right (04 section 9). None represents 04 section 563's own
"SYSTEM_DERIVED" authority category a deterministic, SYSTEM_SERVICE-driven
recovery actor would need, and no BND-011 (SYSTEM_DERIVED AUTHORITY
BOUNDARY) evaluator exists anywhere in this codebase to resolve one --
BND-011 is neither built nor assigned to PKG-24 or any earlier package.
Passing any of the 7 human-shaped classes for a SYSTEM_SERVICE actor
here would itself BE "recovery inherits human authority" -- exactly the
P-21 violation (10 section 34: "A Saga engine or recovery worker cannot
inherit the original actor's human authority") this package's own
OBJECTIVE exists to prevent, and exactly the kind of "inferred
authority" this package's own FORBIDDEN_SHORTCUTS names.

This tension was surfaced to the user as a genuine STOP-shaped decision
(14 section 35: "STOP if required authority is undefined") rather than
resolved silently. The confirmed resolution: the deterministic
(SYSTEM_SERVICE) Recovery Command performs its own governed write --
BND-001/002/017/018 evaluated via the real `boundaries.registry.evaluate_chain`,
followed by a real atomic transaction (`connection.begin_nested()`, the
identical SAVEPOINT-as-production-transaction-boundary `[IMPLEMENTATION
CHOICE]` `CommitCoordinator` itself already uses internally, PKG-13)
wrapping `RecoveryRepository.mark_resolved` -- WITHOUT producing a
`commit_units`/`CommitUnit` row. This is not merely a workaround: 10
section 63 itself classifies `RecoveryRecord` as an "OPERATIONAL_RECORD,
not domain Thing" and its own exact field list (unlike `QuestionSelection`/
`Decision`) carries no `commit_id`/`audit_event_ids`/`outbox_ids` fields
at all -- RecoveryRecord's own resolution was never modeled as a
CommitUnit-producing canonical write to begin with. The HUMAN_USER
discretionary path (RC-07), which WOULD have a real, applicable
`AuthorityClass` to check through the full `CommitCoordinator`, remains
`SUCCESSOR_NOT_BUILT` -- disclosed, not fabricated; this prototype's own
MINIMUM scope never exercises it (12's own minimum-proof list names only
the deterministic/SYSTEM_SERVICE path).

WHY BND-001's `required_actor_classes` IS `{SYSTEM_SERVICE}` ONLY FOR
THIS COMMAND
--------------------------------------------------------------------
Mandatory adversarial attack: admin recovery. A HUMAN_USER (Owner, Admin,
or otherwise) invoking THIS specific, deterministic command is denied at
BND-001 before anything else runs -- the discretionary human path, were
it ever built, would be a SEPARATE registered operation with its own
`required_actor_classes` and a real `AuthorityClass`, never this one
widened to accept both.

WHY THE VERSION CHECK IS PERFORMED HERE DIRECTLY, NOT VIA BND-014
--------------------------------------------------------------------
BND-014 itself is exactly the machinery this module cannot use (see
above) -- its own internal `AuthorityResolver.resolve()` call has the
identical problem. `RecoveryResolutionStaleVersion` is this module's own
narrower, disclosed adaptation of BND-014's own "no stale ALLOW" spirit
(06 section 20) applied to the one fact this command actually needs
fresh: `RecoveryRecord.record_version`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from authority.actor import ActorClass, ActorIdentity
from boundaries.bnd_001_identity import Bnd001IdentityEvaluator, Bnd001Input
from boundaries.bnd_002_workspace import Bnd002Input, Bnd002WorkspaceEvaluator
from boundaries.bnd_017_failure_indeterminate import (
    Bnd017FailureIndeterminateEvaluator,
    Bnd017Input,
)
from boundaries.bnd_018_recovery_rollback import Bnd018Input, Bnd018RecoveryRollbackEvaluator
from boundaries.registry import BoundaryChainResult, BoundaryRegistry, evaluate_chain
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from persistence.recovery_repository import RecoveryRecordNotFound
from persistence.workspace_repository import WorkspaceRepository
from recovery.certainty import ConsequenceCertainty
from recovery.models import RecoveryClass, RecoveryOutcome, RecoveryRecord, RecoveryRepository
from semantic_types.ids import CorrelationId, RecoveryId, WorkspaceId
from semantic_types.versions import RecordVersion

_PRECOMMIT_CHAIN = (
    BoundaryId.BND_001,
    BoundaryId.BND_002,
    BoundaryId.BND_017,
    BoundaryId.BND_018,
)


@dataclass(frozen=True, slots=True)
class RecoveryResolutionFacts:
    """Every caller-supplied fact this governed write needs, already
    resolved (typically via `recovery.lpvs.resolve_lpvs` for the LPVS
    dimensions). See `boundaries.bnd_018_recovery_rollback`'s own module
    docstring for why none of these is re-derived here.
    """

    known_consequence_certainty: ConsequenceCertainty
    lpvs_resolved: bool
    last_proven_valid_state_ref: str | None
    restores_already_legitimized_state: bool
    workspace_scope_preserved: bool
    question_immutability_preserved: bool
    raw_burst_integrity_preserved: bool
    human_ai_distinction_preserved: bool
    authority_history_preserved: bool
    audit_reconstruction_preserved: bool
    no_duplicate_consequence: bool
    result: RecoveryOutcome


class RecoveryResolutionDenied(Exception):
    """The precommit boundary chain (BND-001/002/017/018) did not reach
    ALLOW. No write of any kind was performed.
    """

    def __init__(self, chain_result: BoundaryChainResult) -> None:
        self.chain_result = chain_result
        super().__init__(
            f"RecoveryResolutionDenied: {chain_result.result.value} at "
            f"{chain_result.terminal_boundary_id}"
        )


class RecoveryResolutionStaleVersion(Exception):
    """The `RecoveryRecord`'s own `record_version` changed between when
    the caller resolved `RecoveryResolutionFacts` and this write attempt
    -- mirrors BND-014's own "no stale ALLOW" (06 section 20), narrowed
    to this one fact (see this module's own docstring for why the full
    BND-014 machinery does not apply here).
    """


class RecoveryService:
    """PUBLIC_INTERFACES: "RecoveryService through Command." The one
    production caller of `Bnd017FailureIndeterminateEvaluator`/
    `Bnd018RecoveryRollbackEvaluator`.
    """

    def __init__(
        self,
        *,
        workspace_repository: WorkspaceRepository,
        recovery_repository: RecoveryRepository,
    ) -> None:
        self._workspace_repository = workspace_repository
        self._recovery_repository = recovery_repository

    def _build_registry(self) -> BoundaryRegistry:
        registry = BoundaryRegistry()
        registry.register(Bnd001IdentityEvaluator())  # type: ignore[arg-type]
        registry.register(Bnd002WorkspaceEvaluator(self._workspace_repository))  # type: ignore[arg-type]
        registry.register(
            Bnd017FailureIndeterminateEvaluator(self._recovery_repository)  # type: ignore[arg-type]
        )
        registry.register(Bnd018RecoveryRollbackEvaluator())  # type: ignore[arg-type]
        return registry

    def resolve_recovery(
        self,
        connection: Any,
        *,
        actor: ActorIdentity,
        workspace_id: WorkspaceId,
        recovery_id: RecoveryId,
        original_target_ref: str,
        requested_operation: str,
        expected_record_version: RecordVersion,
        facts: RecoveryResolutionFacts,
        correlation_id: CorrelationId,
        occurred_at: datetime,
    ) -> RecoveryRecord:
        """Materializes this package's own governed Recovery Command
        end to end. Raises `RecoveryResolutionDenied` if the precommit
        chain does not reach ALLOW; `RecoveryRecordNotFound` if
        `recovery_id` does not name a real record;
        `RecoveryResolutionStaleVersion` if the record changed since the
        caller last observed it.
        """
        record = self._recovery_repository.get(recovery_id, workspace_id)
        resolved_object_workspace_ids = (record.workspace_scope_ref,) if record is not None else ()

        context = BoundaryContext(
            workspace_id=workspace_id,
            operation=requested_operation,
            actor=actor,
            correlation_id=correlation_id,
            evaluated_at=occurred_at,
        )
        boundary_inputs: dict[BoundaryId, object] = {
            BoundaryId.BND_001: Bnd001Input(
                boundary_id=BoundaryId.BND_001,
                context=context,
                required_actor_classes=frozenset({ActorClass.SYSTEM_SERVICE}),
            ),
            BoundaryId.BND_002: Bnd002Input(
                boundary_id=BoundaryId.BND_002,
                context=context,
                resolved_object_workspace_ids=resolved_object_workspace_ids,
            ),
            BoundaryId.BND_017: Bnd017Input(
                boundary_id=BoundaryId.BND_017,
                context=context,
                requested_operation=requested_operation,
                known_consequence_certainty=facts.known_consequence_certainty,
                target_ref=original_target_ref,
                exclude_recovery_id=recovery_id,
            ),
            BoundaryId.BND_018: Bnd018Input(
                boundary_id=BoundaryId.BND_018,
                context=context,
                recovery_class=record.recovery_class
                if record is not None
                else RecoveryClass.RC_02_RECONCILIATION,
                lpvs_resolved=facts.lpvs_resolved,
                restores_already_legitimized_state=facts.restores_already_legitimized_state,
                current_human_authority_confirmed=False,
                workspace_scope_preserved=facts.workspace_scope_preserved,
                question_immutability_preserved=facts.question_immutability_preserved,
                raw_burst_integrity_preserved=facts.raw_burst_integrity_preserved,
                human_ai_distinction_preserved=facts.human_ai_distinction_preserved,
                authority_history_preserved=facts.authority_history_preserved,
                audit_reconstruction_preserved=facts.audit_reconstruction_preserved,
                no_duplicate_consequence=facts.no_duplicate_consequence,
            ),
        }

        registry = self._build_registry()
        chain_result = evaluate_chain(registry, _PRECOMMIT_CHAIN, boundary_inputs, context)  # type: ignore[arg-type]
        if chain_result.result is not BoundaryResult.ALLOW:
            raise RecoveryResolutionDenied(chain_result)

        if record is None:
            raise RecoveryRecordNotFound(f"recovery_id {recovery_id!r} not found")

        # Fresh, commit-adjacent re-read immediately before the write --
        # see this module's own docstring for why this replaces BND-014
        # for this one fact rather than instantiating it.
        fresh_record = self._recovery_repository.get(recovery_id, workspace_id)
        if fresh_record is None:
            raise RecoveryRecordNotFound(f"recovery_id {recovery_id!r} not found")
        if fresh_record.record_version != expected_record_version:
            raise RecoveryResolutionStaleVersion(
                f"expected {expected_record_version}, found {fresh_record.record_version}"
            )

        with connection.begin_nested():
            self._recovery_repository.mark_resolved(
                recovery_id,
                workspace_id,
                result=facts.result,
                resolved_at=occurred_at,
                last_proven_valid_state_ref=facts.last_proven_valid_state_ref,
            )

        resolved = self._recovery_repository.get(recovery_id, workspace_id)
        assert resolved is not None  # the write above just succeeded
        return resolved


__all__ = [
    "RecoveryResolutionFacts",
    "RecoveryResolutionDenied",
    "RecoveryResolutionStaleVersion",
    "RecoveryService",
]
