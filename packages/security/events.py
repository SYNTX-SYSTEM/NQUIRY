"""SecurityEvent and the append-only SecurityEventRepository port.

Source: 11_SECURITY_PRIVACY_OBSERVABILITY.md section 3 ("Security Trust
Boundary Inventory" -- "The approved system is divided into the
following technical trust boundaries: TB-01 ... TB-19" -- exact,
closed, numbered list, formalized below as `TrustBoundary`), section 41
("SecurityEvent" -- [ARCHITECTURAL CLOSURE] AC-11-014: "SecurityEvent is
an operational/security record, not a 02 domain Thing and not a 09
Domain Event"; "Examples:" list of event types -- authentication
failure, credential misuse, cross-Workspace attempt, direct canonical
write attempt, AI Gateway bypass, secret-access anomaly, audit-integrity
anomaly, unexpected privileged infrastructure operation,
cross-environment attempt; "SecurityEvent may trigger alerting,
containment, investigation or a governed Command. It does not itself
authorize domain mutation"), section 42 ("SecurityEvent Minimum
Semantics" -- the field list below is taken directly from this
section's own list, which itself says "Exact physical schema belongs to
implementation materialization" -- an explicit invitation for THIS
package's own `[IMPLEMENTATION CHOICE]`, not semantic invention), section
60 ([ARCHITECTURAL CLOSURE] AC-11-017: "Development, test, staging and
production are separate security environments" -- exact, closed
4-value list, formalized below as `Environment`); 14_IMPLEMENTATION_SEQUENCE.md
section 7.1 (`security_events` core-tables row: "security operational |
Workspace key: yes where resolvable | append oriented |
security_event_writer"), section 8 (Database Principals and Workspace
Isolation -- `security_event_writer`'s own reads/writes/forbidden row).

WHY `event_type` STAYS A PLAIN STRING BUT `TrustBoundary`/`Environment`
ARE CLOSED ENUMS
--------------------------------------------------------------------
11 section 41's own event-type list is explicitly introduced with
"Examples:" -- the same non-closure language this codebase already
treats as "stays a plain string" everywhere else (07's `SourceReference.source_type`,
06's `requested_operation` on BND-017). Section 3's trust-boundary list
("divided into the following") and section 60's environment list
("[ARCHITECTURAL CLOSURE]... are separate security environments") both
use definitive-closure language instead -- formalized as closed
`Enum`s, per this codebase's own established "closure language decides
formalization" discipline.

WHY `actor_type`/`actor_id` ARE PLAIN STRINGS
--------------------------------------------------------------------
14 section 3.1 gives `security` exactly one allowed dependency:
`semantic_types` -- not `authority`. Same treatment `audit.models.AuditEvent`
already gives its own `actor_type`/`actor_id` fields, for the identical
reason.

WHY `workspace_id`/`command_id`/`generation_id`/`recovery_id` CARRY NO
FOREIGN KEY IN THIS PACKAGE'S OWN MIGRATION
--------------------------------------------------------------------
Unlike `AuditEvent` (whose own `workspace_id`/`command_id`/`commit_id`
always name a REAL, already-committed row -- an audit trail can only
ever describe what genuinely happened), a `SecurityEvent`'s entire
purpose can be to record an ILLEGITIMATE or FORGED claim -- 11 section
41's own examples name "credential misuse", "cross-Workspace attempt"
(an attempt against a Workspace the actor does NOT belong to, which
may itself be a forged/nonexistent id), and "unexpected privileged
infrastructure operation". A real foreign key would make it structurally
impossible to ever record the one class of event this type most needs
to represent: an attacker or a bug CLAIMING a reference that turns out
not to resolve at all. 14 section 7.1's own "Workspace key: yes WHERE
RESOLVABLE" already anticipates this -- "where resolvable" is a
disclosure that it sometimes is not. Every one of these four fields is
therefore a bare, unvalidated reference, the same "presence does not
prove the referenced facts" treatment `RecoveryRecord.required_authority_ref`
already established (PKG-23).

WHY THIS TYPE HAS NO `record_version`/MUTATION METHOD AT ALL
--------------------------------------------------------------------
14 section 7.1 marks `security_events` "append oriented", identical to
`audit_events`. `SecurityEventRepository` therefore has exactly one
write method (`record`), mirroring `AuditRepository.append`'s own
shape -- no update, no delete, structurally.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol, runtime_checkable

from semantic_types.ids import (
    CommandId,
    CorrelationId,
    GenerationId,
    RecoveryId,
    SecurityEventId,
    WorkspaceId,
)


class Environment(Enum):
    """11 section 60's own [ARCHITECTURAL CLOSURE] AC-11-017 exact
    4-value list."""

    DEVELOPMENT = "DEVELOPMENT"
    TEST = "TEST"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"


class TrustBoundary(Enum):
    """11 section 3's own exact, closed, numbered 19-boundary
    inventory."""

    TB_01_HUMAN_CLIENT = "TB-01"
    TB_02_FRONTEND = "TB-02"
    TB_03_API_EDGE = "TB-03"
    TB_04_APPLICATION_SERVICE = "TB-04"
    TB_05_GOVERNED_COMMAND_PROCESSOR = "TB-05"
    TB_06_GOVERNANCE_SERVICE = "TB-06"
    TB_07_CANONICAL_PERSISTENCE = "TB-07"
    TB_08_PROJECTION_READ_PERSISTENCE = "TB-08"
    TB_09_AUDIT_PERSISTENCE = "TB-09"
    TB_10_EVENT_OUTBOX_INFRASTRUCTURE = "TB-10"
    TB_11_AI_GATEWAY = "TB-11"
    TB_12_MODEL_PROVIDER = "TB-12"
    TB_13_AI_TOOL_BOUNDARY = "TB-13"
    TB_14_EXTERNAL_INTEGRATION = "TB-14"
    TB_15_BACKGROUND_WORKER = "TB-15"
    TB_16_SCHEDULER = "TB-16"
    TB_17_ADMINISTRATIVE_TOOLING = "TB-17"
    TB_18_BACKUP_RESTORE_INFRASTRUCTURE = "TB-18"
    TB_19_OBSERVABILITY_INFRASTRUCTURE = "TB-19"


@dataclass(frozen=True, slots=True)
class SecurityEvent:
    """11 section 42's own "should reconstruct, where known" field
    list -- OPERATIONAL/SECURITY record, not a 02 domain Thing and not
    a 09 Domain Event (11 section 41's own explicit classification).
    """

    security_event_id: SecurityEventId
    occurred_at: datetime
    environment: Environment
    actor_type: str
    actor_id: str
    trust_boundary: TrustBoundary
    event_type: str
    correlation_id: CorrelationId
    workspace_id: WorkspaceId | None = None
    target_ref: str | None = None
    command_id: CommandId | None = None
    generation_id: GenerationId | None = None
    recovery_id: RecoveryId | None = None
    observed_facts: str | None = None
    uncertain: bool = False
    containment_action: str | None = None
    audit_linkage: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.security_event_id, SecurityEventId):
            raise TypeError(
                f"security_event_id must be a SecurityEventId, got {type(self.security_event_id)!r}"
            )
        if self.occurred_at.tzinfo is None:
            raise ValueError("SecurityEvent.occurred_at must be timezone-aware")
        if not isinstance(self.environment, Environment):
            raise TypeError(f"environment must be an Environment, got {type(self.environment)!r}")
        if not self.actor_type:
            raise ValueError("SecurityEvent.actor_type must be non-empty")
        if not self.actor_id:
            raise ValueError("SecurityEvent.actor_id must be non-empty")
        if not isinstance(self.trust_boundary, TrustBoundary):
            raise TypeError(
                f"trust_boundary must be a TrustBoundary, got {type(self.trust_boundary)!r}"
            )
        if not self.event_type:
            raise ValueError("SecurityEvent.event_type must be non-empty")
        if not isinstance(self.correlation_id, CorrelationId):
            raise TypeError(
                f"correlation_id must be a CorrelationId, got {type(self.correlation_id)!r}"
            )
        if self.workspace_id is not None and not isinstance(self.workspace_id, WorkspaceId):
            raise TypeError("workspace_id must be a WorkspaceId or None")
        if self.command_id is not None and not isinstance(self.command_id, CommandId):
            raise TypeError("command_id must be a CommandId or None")
        if self.generation_id is not None and not isinstance(self.generation_id, GenerationId):
            raise TypeError("generation_id must be a GenerationId or None")
        if self.recovery_id is not None and not isinstance(self.recovery_id, RecoveryId):
            raise TypeError("recovery_id must be a RecoveryId or None")


@runtime_checkable
class SecurityEventRepository(Protocol):
    """14's own PUBLIC_INTERFACES for this package. "append oriented"
    (14 section 7.1) -- no method here can update or delete an
    existing row, the same structural defense
    `audit.models.AuditRepository` already established for the
    identical mandatory adversarial attack category (here: "SecurityEvent
    tamper/rewrite").
    """

    def record(self, event: SecurityEvent) -> None: ...

    def get(self, security_event_id: SecurityEventId) -> SecurityEvent | None: ...

    def list_for_correlation(self, correlation_id: CorrelationId) -> tuple[SecurityEvent, ...]: ...


__all__ = [
    "Environment",
    "TrustBoundary",
    "SecurityEvent",
    "SecurityEventRepository",
]
