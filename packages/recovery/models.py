"""RecoveryRecord, RecoveryOutcome, RecoveryClass and the
RecoveryRepository port.

Source: 10_FAILURE_RECOVERY_ROLLBACK.md section 63 ("[ARCHITECTURAL
CLOSURE] AC-10-009" -- the exact "Minimum semantics" field list;
classification "OPERATIONAL_RECORD, not domain Thing, not authority
token, not Evidence by itself"; "RecoveryRecord may contain references
to proof. Its presence does not prove the referenced facts."), section
64 (RecoveryRecord Outcomes -- the exact 5-value closed vocabulary;
"These are operational recovery outcomes only. They do not replace:
DENIED/FAILED_PRECOMMIT/COMMITTED/INDETERMINATE"), section 65
(RecoveryRecord Mutability -- "may accumulate new findings and
attempts... Do not rewrite UNKNOWN -> PROVEN_ABSENT without preserving
the proof and the prior uncertainty history"), section 30 (Recovery
Classes -- the exact 7-value RC-01..RC-07 closed list);
14_IMPLEMENTATION_SEQUENCE.md section 7.1 (`recovery_records` core
table row: "operational recovery | Workspace key: yes | record_version
| recovery orchestration through governed path"), section 10
("RecoveryRepository: RecoveryRecord reads and bounded operational
updates" -- "bounded", not a generic setter), this package's own
AUTHORITY line ("Historical authority proves prior legitimacy only,
never current recovery authority").

WHY `failure_classifications`/`canonical_state_certainty`/
`external_consequence_certainty` REUSE PKG-22's OWN TYPES
--------------------------------------------------------------------
`recovery.failure_classifier.FailureClass` and `recovery.certainty.
ConsequenceCertainty` already materialize 10 sections 9/5's own closed
vocabularies (PKG-22) -- both live in this SAME package, so reusing
them directly is the identical "reuse an existing closed type instead
of re-deriving it" discipline already applied throughout this
codebase, not a new cross-package dependency.

WHY `required_authority_ref`/`current_authority_binding_ref` ARE BARE
`uuid.UUID`, NOT A REAL AuthorityBindingRepository TYPE
--------------------------------------------------------------------
`recovery` cannot import `authority`/`governance` (not on its own 14
section 3.1 allow-list). Same precedent as
`command.envelope.CommandEnvelope.authority_context_ref`: a generic
operational identifier with no reachable closed type uses a bare
`uuid.UUID`.

WHY `RecoveryRepository` HAS NO GENERIC "SET RESULT" METHOD
--------------------------------------------------------------------
14's own FORBIDDEN_SHORTCUTS for this package explicitly names
"generic status setters" as erasing semantics. `mark_resolved` is the
one, bounded, terminal-transition method (UNRESOLVED -> one of the
four terminal outcomes); `record_attempt` is the one, bounded,
accumulating-findings method (10 section 65). Neither can express an
arbitrary field mutation.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol, runtime_checkable

from semantic_types.ids import (
    AttemptId,
    CommandId,
    CommitId,
    CorrelationId,
    DecisionId,
    RecoveryId,
    WorkspaceId,
)

from recovery.certainty import ConsequenceCertainty
from recovery.failure_classifier import FailureClass


class RecoveryOutcome(Enum):
    """10 section 64's exact 5-value closed vocabulary. These do not
    replace `command.envelope.CommandOutcome`'s own 4 values -- a
    RecoveryRecord's own operational outcome is a distinct dimension.
    """

    RECOVERED = "RECOVERED"
    RECONCILED = "RECONCILED"
    COMPENSATED = "COMPENSATED"
    NO_ACTION_REQUIRED = "NO_ACTION_REQUIRED"
    UNRESOLVED = "UNRESOLVED"


class RecoveryClass(Enum):
    """10 section 30's exact 7-value closed vocabulary. "These classes
    are not authority classes" -- 10's own explicit disclaimer.
    """

    RC_01_DETERMINISTIC_TECHNICAL_RECOVERY = "RC-01"
    RC_02_RECONCILIATION = "RC-02"
    RC_03_COMPENSATION = "RC-03"
    RC_04_ROLLBACK = "RC-04"
    RC_05_PROJECTION_REBUILD = "RC-05"
    RC_06_RETRY = "RC-06"
    RC_07_MANUAL_DISCRETIONARY_RECOVERY = "RC-07"


@dataclass(frozen=True, slots=True)
class RecoveryRecord:
    """10 section 63's exact "Minimum semantics" field list.
    OPERATIONAL_RECORD -- not a domain Thing, not an authority token,
    not Evidence by itself (10's own explicit classification).
    """

    recovery_id: RecoveryId
    workspace_scope_ref: WorkspaceId
    failure_correlation_ref: CorrelationId
    original_command_id: CommandId
    original_attempt_id: AttemptId
    failure_classifications: tuple[FailureClass, ...]
    canonical_state_certainty: ConsequenceCertainty
    external_consequence_certainty: ConsequenceCertainty
    recovery_class: RecoveryClass
    recovery_actor_type: str
    recovery_actor_id: str
    result: RecoveryOutcome
    created_at: datetime
    updated_at: datetime
    original_commit_id: CommitId | None = None
    known_canonical_state_ref: str | None = None
    known_external_consequence_ref: str | None = None
    unknown_consequence_description: str | None = None
    last_proven_valid_state_ref: str | None = None
    required_authority_ref: uuid.UUID | None = None
    current_authority_binding_ref: uuid.UUID | None = None
    human_decision_ref: DecisionId | None = None
    evidence_proof_refs: tuple[str, ...] = ()
    recovery_command_ids: tuple[CommandId, ...] = ()
    recovery_attempt_refs: tuple[str, ...] = ()
    resolved_at: datetime | None = None
    audit_linkage: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.recovery_id, RecoveryId):
            raise TypeError(f"recovery_id must be a RecoveryId, got {type(self.recovery_id)!r}")
        if not isinstance(self.workspace_scope_ref, WorkspaceId):
            raise TypeError(
                f"workspace_scope_ref must be a WorkspaceId, got {type(self.workspace_scope_ref)!r}"
            )
        if not isinstance(self.failure_correlation_ref, CorrelationId):
            raise TypeError(
                "failure_correlation_ref must be a CorrelationId, got "
                f"{type(self.failure_correlation_ref)!r}"
            )
        if not isinstance(self.original_command_id, CommandId):
            raise TypeError(
                f"original_command_id must be a CommandId, got {type(self.original_command_id)!r}"
            )
        if not isinstance(self.original_attempt_id, AttemptId):
            raise TypeError(
                f"original_attempt_id must be an AttemptId, got {type(self.original_attempt_id)!r}"
            )
        if not all(isinstance(fc, FailureClass) for fc in self.failure_classifications):
            raise TypeError("failure_classifications must contain only FailureClass members")
        if not isinstance(self.canonical_state_certainty, ConsequenceCertainty):
            raise TypeError(
                "canonical_state_certainty must be a ConsequenceCertainty, got "
                f"{type(self.canonical_state_certainty)!r}"
            )
        if not isinstance(self.external_consequence_certainty, ConsequenceCertainty):
            raise TypeError(
                "external_consequence_certainty must be a ConsequenceCertainty, got "
                f"{type(self.external_consequence_certainty)!r}"
            )
        if not isinstance(self.recovery_class, RecoveryClass):
            raise TypeError(
                f"recovery_class must be a RecoveryClass, got {type(self.recovery_class)!r}"
            )
        if not self.recovery_actor_type:
            raise ValueError("RecoveryRecord.recovery_actor_type must be non-empty")
        if not self.recovery_actor_id:
            raise ValueError("RecoveryRecord.recovery_actor_id must be non-empty")
        if not isinstance(self.result, RecoveryOutcome):
            raise TypeError(f"result must be a RecoveryOutcome, got {type(self.result)!r}")
        # 10 §64: UNRESOLVED alone leaves `resolved_at` meaningless;
        # every terminal outcome must record when it resolved -- mirrors
        # `OutboxRecord.delivered_at`'s own DELIVERED biconditional
        # (PKG-12/20).
        if (self.result is RecoveryOutcome.UNRESOLVED) and (self.resolved_at is not None):
            raise ValueError("RecoveryRecord.resolved_at must be unset while result is UNRESOLVED")
        if (self.result is not RecoveryOutcome.UNRESOLVED) and (self.resolved_at is None):
            raise ValueError(
                "RecoveryRecord.resolved_at must be set once result is a terminal outcome"
            )


@runtime_checkable
class RecoveryRepository(Protocol):
    """14 section 10: "RecoveryRecord reads and bounded operational
    updates." No method here can grant, escalate, or reuse authority --
    see this module's own docstring and `tests/recovery/
    test_recovery_non_authority.py` (P-21) for the structural proof.
    """

    def create(self, record: RecoveryRecord) -> None: ...

    def get(self, recovery_id: RecoveryId, workspace_id: WorkspaceId) -> RecoveryRecord | None: ...

    def record_attempt(
        self,
        recovery_id: RecoveryId,
        workspace_id: WorkspaceId,
        *,
        attempt_ref: str,
        updated_at: datetime,
    ) -> None:
        """10 section 65: "RecoveryRecord may accumulate new findings
        and attempts." Appends one ref; never removes or reorders
        history.
        """
        ...

    def mark_resolved(
        self,
        recovery_id: RecoveryId,
        workspace_id: WorkspaceId,
        *,
        result: RecoveryOutcome,
        resolved_at: datetime,
        last_proven_valid_state_ref: str | None,
    ) -> None:
        """The one bounded, terminal transition
        (UNRESOLVED -> a terminal `RecoveryOutcome`). Not a generic
        setter -- `result` must be a terminal member (enforced by the
        real implementation's own database trigger, defense in depth)."""
        ...


__all__ = [
    "RecoveryOutcome",
    "RecoveryClass",
    "RecoveryRecord",
    "RecoveryRepository",
]
