"""AuditEvent and the append-only AuditRepository port.

Source: 09_DATA_EVENT_API_CONTRACTS.md section 58 (DATA CONTRACT:
AuditEvent -- the exact field list, section 58.1 "AuditEvent is
append-only... Correction creates a new audit event", section 58.2
"Audit Event Is Not State"), section 120 (Audit and Domain Event
Coupling -- shares command_id/commit_id/correlation_id with the domain
event, without either becoming state), section 121 (Audit Failure
Semantics); 11_SECURITY_PRIVACY_OBSERVABILITY.md section 33 (AC-11-012:
AuditEvent stays distinct from operational/security logs and domain
Events), section 34 (Audit Integrity -- required properties this type's
fields materialize), section 35 (Audit Mutation Control -- "Ordinary
application principals cannot rewrite established audit history"; a
correction is a NEW row, never an UPDATE); 14_IMPLEMENTATION_SEQUENCE.md
section 3.1 (`audit`'s exact "semantic_types"-only allow-list), section
7.1/7.3 (audit_events table row and constraints), section 10
(AuditRepository: "append only").

WHY `actor_type`/`actor_id`/`command_type`/`result`/`failure_code` ARE
PLAIN STRINGS
--------------------------------------------------------------------
14 section 3.1 gives `audit` exactly one allowed dependency:
`semantic_types` -- not `authority`, not `command`. `actor_type`/
`actor_id` are therefore inert references, the same treatment PKG-10
gave `CommandEnvelope.requesting_actor_type`/`requesting_actor_id` for
the identical reason. `result` conceptually mirrors 14 section 6's
Command outcome vocabulary (DENIED/FAILED_PRECOMMIT/COMMITTED/
INDETERMINATE) -- the database CHECK constraint in this package's own
migration restricts the column to those exact 4 values -- but the
Python type stays a plain string here too, since importing
`command.envelope.CommandOutcome` would violate the same allow-list.
This is the third package to apply this exact "closed vocabulary
enforced in SQL, held as inert string in Python" pattern (after
`domain.session_transitions`'s `AuthorityDependency`/`BoundaryDependency`
and `command.envelope`'s own actor fields).

WHY THERE IS NO `boundary_evaluation_summary_ref` FIELD HERE
--------------------------------------------------------------------
11 section 34 requires "boundary result references" among an audit
store's integrity properties, but 09 section 58's own AuditEvent field
list does not name a dedicated field for it. `command_attempts`
(PKG-10) already carries `boundary_evaluation_summary_ref` for the same
`command_id` an AuditEvent references -- the requirement is satisfied
transitively via `command_id`, not duplicated onto this type. Inventing
a second, parallel reference here would risk the two drifting apart
with no way to reconcile which is authoritative.

WHY `metadata_ref` IS OPTIONAL DESPITE NO EXPLICIT "nullable" MARKER
IN 09's FIELD LIST
--------------------------------------------------------------------
09 marks `human_decision_ref`/`evidence_set_ref`/`state_before_ref`/
`state_after_ref`/`failure_code` explicitly "nullable" and leaves
`metadata_ref/payload` unmarked. The simplest legitimate audit fact
(e.g. a plain state transition with no extra structured detail) has
nothing to put there; requiring every future caller to invent a payload
object even when none applies would itself be a form of semantic
invention. Disclosed deviation, not a silent one.

WHY `causation_id` IS NULLABLE DESPITE NO EXPLICIT MARKER EITHER
--------------------------------------------------------------------
09 section 4.8 defines `causation_id` generally as "points to the
immediate cause" with illustrative examples, never as universally
mandatory -- PKG-10's `CommandEnvelope.causation_id` already treats it
as `CausationId | None` for the identical reason. Consistency across
packages for the same general-purpose identity type takes precedence
over this one field's silence in the AuditEvent-specific list.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable

from semantic_types.ids import (
    AuditEventId,
    CausationId,
    CommandId,
    CommitId,
    CorrelationId,
    DecisionId,
    EvidenceSetId,
    WorkspaceId,
)
from semantic_types.versions import ContractVersion


@dataclass(frozen=True, slots=True)
class AuditEvent:
    """09 section 58's exact field list."""

    audit_event_id: AuditEventId
    event_type: str
    event_schema_version: ContractVersion
    workspace_id: WorkspaceId
    occurred_at: datetime
    actor_type: str
    actor_id: str
    command_type: str
    command_id: CommandId
    commit_id: CommitId
    correlation_id: CorrelationId
    target_refs: tuple[str, ...]
    authority_source_ref: uuid.UUID
    result: str
    causation_id: CausationId | None = None
    human_decision_ref: DecisionId | None = None
    evidence_set_ref: EvidenceSetId | None = None
    state_before_ref: str | None = None
    state_after_ref: str | None = None
    failure_code: str | None = None
    metadata_ref: str | None = None
    authority_source_type: str | None = None
    """F02 HD-6: BINDING / ROLE / FOUNDING; F03 HD-15: PARTICIPATION.
    `None` only on pre-F02 rows."""
    authority_scope_ref: str | None = None
    """F02 HD-6: exact scope of the authority source, e.g. "SESSION:<uuid>"."""

    def __post_init__(self) -> None:
        if not isinstance(self.audit_event_id, AuditEventId):
            raise TypeError(
                f"audit_event_id must be an AuditEventId, got {type(self.audit_event_id)!r}"
            )
        if not self.event_type:
            raise ValueError("AuditEvent.event_type must be non-empty")
        if not isinstance(self.event_schema_version, ContractVersion):
            raise TypeError(
                f"event_schema_version must be a ContractVersion, got "
                f"{type(self.event_schema_version)!r}"
            )
        if not isinstance(self.workspace_id, WorkspaceId):
            raise TypeError(f"workspace_id must be a WorkspaceId, got {type(self.workspace_id)!r}")
        if not self.actor_type:
            raise ValueError("AuditEvent.actor_type must be non-empty")
        if not self.actor_id:
            raise ValueError("AuditEvent.actor_id must be non-empty")
        if not self.command_type:
            raise ValueError("AuditEvent.command_type must be non-empty")
        if not isinstance(self.command_id, CommandId):
            raise TypeError(f"command_id must be a CommandId, got {type(self.command_id)!r}")
        if not isinstance(self.commit_id, CommitId):
            raise TypeError(f"commit_id must be a CommitId, got {type(self.commit_id)!r}")
        if not isinstance(self.correlation_id, CorrelationId):
            raise TypeError(
                f"correlation_id must be a CorrelationId, got {type(self.correlation_id)!r}"
            )
        if self.causation_id is not None and not isinstance(self.causation_id, CausationId):
            raise TypeError("causation_id must be a CausationId or None")
        if not isinstance(self.authority_source_ref, uuid.UUID):
            raise TypeError(
                f"authority_source_ref must be a uuid.UUID, got {type(self.authority_source_ref)!r}"
            )
        if not self.result:
            raise ValueError("AuditEvent.result must be non-empty")
        if (self.authority_source_type is None) != (self.authority_scope_ref is None):
            raise ValueError(
                "authority_source_type and authority_scope_ref must be set together (HD-6)"
            )
        if self.authority_source_type not in (None, "BINDING", "ROLE", "FOUNDING", "PARTICIPATION"):
            raise ValueError(f"unknown authority_source_type {self.authority_source_type!r}")
        if self.human_decision_ref is not None and not isinstance(
            self.human_decision_ref, DecisionId
        ):
            raise TypeError("human_decision_ref must be a DecisionId or None")
        if self.evidence_set_ref is not None and not isinstance(
            self.evidence_set_ref, EvidenceSetId
        ):
            raise TypeError("evidence_set_ref must be an EvidenceSetId or None")


@runtime_checkable
class AuditRepository(Protocol):
    """14 section 10: "append only". No method here can update or
    delete an existing row -- the Protocol's own shape is the
    structural defense against the mandatory adversarial attacks
    "audit update"/"audit delete", independent of whatever DB
    privilege/trigger enforcement backs it in `persistence`.
    """

    def append(self, event: AuditEvent) -> None: ...

    def get(self, audit_event_id: AuditEventId) -> AuditEvent | None: ...

    def list_for_correlation(self, correlation_id: CorrelationId) -> tuple[AuditEvent, ...]: ...


__all__ = ["AuditEvent", "AuditRepository"]
