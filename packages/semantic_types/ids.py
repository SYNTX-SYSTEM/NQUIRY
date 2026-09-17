"""Strong identity value objects.

Source: 14_IMPLEMENTATION_SEQUENCE.md §5 (SEMANTIC TYPE SYSTEM).

`[IMPLEMENTATION CHOICE]` (14 §5): frozen wrapper value objects around
UUIDv7-compatible values. Tests may use deterministic generators.

Non-collapse rule: IDs carry no authority and no semantic state. An ID
being well-formed proves identity only; it proves nothing about
authority, governance state, or domain legitimacy. Do not attach
behavior, authority checks, or domain meaning to these types anywhere
in this codebase.

Each identity below is a distinct, non-interchangeable type. A
`WorkspaceId` is not assignable where a `UserId` is expected, and vice
versa; mixing them is a semantic error the type system must reject.
Each class is therefore written out explicitly rather than generated,
so static type checkers see 28 concrete, incompatible types instead of
one collapsed shape.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass


class InvalidIdentityValue(ValueError):
    """Raised when a value cannot legitimately construct a strong identity."""


@dataclass(frozen=True, slots=True)
class _StrongId:
    """Shared validation shape. Not exported; every identity below is its
    own concrete subclass so identities of different kinds remain
    structurally distinct types, never interchangeable by the type
    checker or at runtime.
    """

    value: uuid.UUID

    def __post_init__(self) -> None:
        if not isinstance(self.value, uuid.UUID):
            raise InvalidIdentityValue(
                f"{type(self).__name__} requires a uuid.UUID value, got {type(self.value)!r}"
            )

    def __str__(self) -> str:
        return str(self.value)


def _from_str(cls: type[_StrongId], value: str) -> _StrongId:
    try:
        return cls(uuid.UUID(value))
    except ValueError as exc:
        raise InvalidIdentityValue(
            f"{cls.__name__} received an invalid UUID string: {value!r}"
        ) from exc


# Closed list of strong identities required by 14_IMPLEMENTATION_SEQUENCE.md §5.
# An identity not defined here does not yet exist architecturally; a later
# package must not invent one informally to fill a gap.


@dataclass(frozen=True, slots=True)
class WorkspaceId(_StrongId):
    """Strong, non-semantic identity: WorkspaceId."""

    @classmethod
    def from_str(cls, value: str) -> WorkspaceId:
        return _from_str(cls, value)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class UserId(_StrongId):
    """Strong, non-semantic identity: UserId."""

    @classmethod
    def from_str(cls, value: str) -> UserId:
        return _from_str(cls, value)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class ServiceIdentityId(_StrongId):
    """Strong, non-semantic identity: ServiceIdentityId."""

    @classmethod
    def from_str(cls, value: str) -> ServiceIdentityId:
        return _from_str(cls, value)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class ThingId(_StrongId):
    """Strong, non-semantic identity: ThingId."""

    @classmethod
    def from_str(cls, value: str) -> ThingId:
        return _from_str(cls, value)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class RelationId(_StrongId):
    """Strong, non-semantic identity: RelationId."""

    @classmethod
    def from_str(cls, value: str) -> RelationId:
        return _from_str(cls, value)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class ChallengeId(_StrongId):
    """Strong, non-semantic identity: ChallengeId."""

    @classmethod
    def from_str(cls, value: str) -> ChallengeId:
        return _from_str(cls, value)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class SessionId(_StrongId):
    """Strong, non-semantic identity: SessionId."""

    @classmethod
    def from_str(cls, value: str) -> SessionId:
        return _from_str(cls, value)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class BurstId(_StrongId):
    """Strong, non-semantic identity: BurstId."""

    @classmethod
    def from_str(cls, value: str) -> BurstId:
        return _from_str(cls, value)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class QuestionId(_StrongId):
    """Strong, non-semantic identity: QuestionId."""

    @classmethod
    def from_str(cls, value: str) -> QuestionId:
        return _from_str(cls, value)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class QuestionSelectionId(_StrongId):
    """Strong, non-semantic identity: QuestionSelectionId."""

    @classmethod
    def from_str(cls, value: str) -> QuestionSelectionId:
        return _from_str(cls, value)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class DecisionId(_StrongId):
    """Strong, non-semantic identity: DecisionId."""

    @classmethod
    def from_str(cls, value: str) -> DecisionId:
        return _from_str(cls, value)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class EvidenceId(_StrongId):
    """Strong, non-semantic identity: EvidenceId."""

    @classmethod
    def from_str(cls, value: str) -> EvidenceId:
        return _from_str(cls, value)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class SourceReferenceId(_StrongId):
    """Strong, non-semantic identity: SourceReferenceId."""

    @classmethod
    def from_str(cls, value: str) -> SourceReferenceId:
        return _from_str(cls, value)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class ClaimAnchorId(_StrongId):
    """Strong, non-semantic identity: ClaimAnchorId."""

    @classmethod
    def from_str(cls, value: str) -> ClaimAnchorId:
        return _from_str(cls, value)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class EvidenceRelationId(_StrongId):
    """Strong, non-semantic identity: EvidenceRelationId."""

    @classmethod
    def from_str(cls, value: str) -> EvidenceRelationId:
        return _from_str(cls, value)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class EvidenceSetId(_StrongId):
    """Strong, non-semantic identity: EvidenceSetId."""

    @classmethod
    def from_str(cls, value: str) -> EvidenceSetId:
        return _from_str(cls, value)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class CommandId(_StrongId):
    """Strong, non-semantic identity: CommandId."""

    @classmethod
    def from_str(cls, value: str) -> CommandId:
        return _from_str(cls, value)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class AttemptId(_StrongId):
    """Strong, non-semantic identity: AttemptId."""

    @classmethod
    def from_str(cls, value: str) -> AttemptId:
        return _from_str(cls, value)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class CommitId(_StrongId):
    """Strong, non-semantic identity: CommitId."""

    @classmethod
    def from_str(cls, value: str) -> CommitId:
        return _from_str(cls, value)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class EventId(_StrongId):
    """Strong, non-semantic identity: EventId."""

    @classmethod
    def from_str(cls, value: str) -> EventId:
        return _from_str(cls, value)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class GenerationId(_StrongId):
    """Strong, non-semantic identity: GenerationId."""

    @classmethod
    def from_str(cls, value: str) -> GenerationId:
        return _from_str(cls, value)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class RecoveryId(_StrongId):
    """Strong, non-semantic identity: RecoveryId."""

    @classmethod
    def from_str(cls, value: str) -> RecoveryId:
        return _from_str(cls, value)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class CorrelationId(_StrongId):
    """Strong, non-semantic identity: CorrelationId."""

    @classmethod
    def from_str(cls, value: str) -> CorrelationId:
        return _from_str(cls, value)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class CausationId(_StrongId):
    """Strong, non-semantic identity: CausationId."""

    @classmethod
    def from_str(cls, value: str) -> CausationId:
        return _from_str(cls, value)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class AuthorityBindingId(_StrongId):
    """Strong, non-semantic identity: AuthorityBindingId."""

    @classmethod
    def from_str(cls, value: str) -> AuthorityBindingId:
        return _from_str(cls, value)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class FacilitatorScopeBindingId(_StrongId):
    """Strong, non-semantic identity: FacilitatorScopeBindingId."""

    @classmethod
    def from_str(cls, value: str) -> FacilitatorScopeBindingId:
        return _from_str(cls, value)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class AuditEventId(_StrongId):
    """Strong, non-semantic identity: AuditEventId."""

    @classmethod
    def from_str(cls, value: str) -> AuditEventId:
        return _from_str(cls, value)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class SecurityEventId(_StrongId):
    """Strong, non-semantic identity: SecurityEventId."""

    @classmethod
    def from_str(cls, value: str) -> SecurityEventId:
        return _from_str(cls, value)  # type: ignore[return-value]


__all__ = [
    "InvalidIdentityValue",
    "WorkspaceId",
    "UserId",
    "ServiceIdentityId",
    "ThingId",
    "RelationId",
    "ChallengeId",
    "SessionId",
    "BurstId",
    "QuestionId",
    "QuestionSelectionId",
    "DecisionId",
    "EvidenceId",
    "SourceReferenceId",
    "ClaimAnchorId",
    "EvidenceRelationId",
    "EvidenceSetId",
    "CommandId",
    "AttemptId",
    "CommitId",
    "EventId",
    "GenerationId",
    "RecoveryId",
    "CorrelationId",
    "CausationId",
    "AuthorityBindingId",
    "FacilitatorScopeBindingId",
    "AuditEventId",
    "SecurityEventId",
]
