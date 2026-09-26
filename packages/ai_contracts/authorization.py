"""Operation authorization identity (F04 reconstruction §0.1; HD-16, HD-17, HD-23).

LAW: ROOT AUTHORITY CHAIN ≠ OPERATION AUTHORIZATION IDENTITY.

An operation authorization is OA = (authorizing_command_id, ai_operation_id)
within one Session. It is created, write-once, by the commit of the human
Command that authorizes it (OA-1, OA-2, OA-4) or by the acceptance of an
AIOP-001 artifact X (OA-3, whose authorizing command is the command C that
authorized X). It is consumed by AT MOST ONE generation (rule 3); it may stay
unconsumed; only the latest OA of a (Session, operation) is executable, and
only right after its own commit (rule 5). A controller request supersedes the
latest OA as RETRY (its generation FAILED / REJECTED) or RECOVERY (it was never
consumed) (rule 9). The root chain to BEGIN_ANALYSIS is provenance, not
identity (rule 6).

This module is the pure shape. Persistence (`ai_operation_authorizations`,
migration a8d3f1c6e902) enforces the same shape with CHECK constraints and an
insert trigger, and rejects every UPDATE / DELETE.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from semantic_types.ids import CommandId, GenerationId, SessionId, WorkspaceId

from ai_contracts.aiop import AIOperationId


class AuthorizationShape(Enum):
    """§0.1 rule 2: the four legal OA shapes."""

    OA_1 = "OA-1"
    """CMD_BEGIN_ANALYSIS → AIOP-001."""
    OA_2 = "OA-2"
    """CMD_REQUEST_QUESTION_ANALYSIS → AIOP-001 (RETRY / RECOVERY)."""
    OA_3 = "OA-3"
    """Acceptance of AIOP-001 artifact X → AIOP-002, authorized by C (X's command)."""
    OA_4 = "OA-4"
    """CMD_REQUEST_QUESTION_CLUSTERING → AIOP-002 (RETRY / RECOVERY)."""


class RequestCase(Enum):
    """§0.1 rule 9. Recorded write-once by the request command."""

    RETRY = "RETRY"
    RECOVERY = "RECOVERY"


_OPERATION_OF_SHAPE = {
    AuthorizationShape.OA_1: AIOperationId.AIOP_001,
    AuthorizationShape.OA_2: AIOperationId.AIOP_001,
    AuthorizationShape.OA_3: AIOperationId.AIOP_002,
    AuthorizationShape.OA_4: AIOperationId.AIOP_002,
}
_REQUEST_SHAPES = frozenset({AuthorizationShape.OA_2, AuthorizationShape.OA_4})


class OperationAuthorizationShapeError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class OperationAuthorization:
    authorization_id: uuid.UUID
    workspace_id: WorkspaceId
    session_id: SessionId
    ai_operation_id: AIOperationId
    shape: AuthorizationShape
    authorizing_command_id: CommandId
    sequence_no: int
    chain_root_command_id: CommandId
    created_at: datetime
    request_case: RequestCase | None = None
    supersedes_authorization_id: uuid.UUID | None = None
    retry_of_generation_id: GenerationId | None = None
    precondition_artifact_ref: uuid.UUID | None = None
    """X, the accepted AIOP-001 artifact an AIOP-002 authorization depends on."""

    def __post_init__(self) -> None:
        def fail(reason: str) -> None:
            raise OperationAuthorizationShapeError(f"{self.shape.value}: {reason}")

        if _OPERATION_OF_SHAPE[self.shape] is not self.ai_operation_id:
            fail(f"operation {self.ai_operation_id.value} does not match the shape")
        is_request = self.shape in _REQUEST_SHAPES
        if is_request:
            if self.request_case is None:
                fail("a controller request records RETRY or RECOVERY")
            if self.sequence_no < 2 or self.supersedes_authorization_id is None:
                fail("a controller request supersedes the latest authorization")
            if (self.request_case is RequestCase.RETRY) != (
                self.retry_of_generation_id is not None
            ):
                fail("retry_of exists exactly for RETRY")
        else:
            if self.sequence_no != 1:
                fail("OA-1 / OA-3 are the first authorization of their operation")
            if (
                self.request_case is not None
                or self.supersedes_authorization_id is not None
                or self.retry_of_generation_id is not None
            ):
                fail("OA-1 / OA-3 carry no request case, supersession or retry lineage")
        if self.shape is AuthorizationShape.OA_1 and (
            self.authorizing_command_id != self.chain_root_command_id
        ):
            fail("OA-1 is authorized by the chain root BEGIN_ANALYSIS itself")
        needs_x = self.ai_operation_id is AIOperationId.AIOP_002
        if needs_x != (self.precondition_artifact_ref is not None):
            fail("AIOP-002 authorizations, and only they, carry the precondition artifact X")

    @property
    def oa(self) -> tuple[CommandId, AIOperationId]:
        """The authorization identity (§0.1 rule 1)."""
        return (self.authorizing_command_id, self.ai_operation_id)


__all__ = [
    "AuthorizationShape",
    "OperationAuthorization",
    "OperationAuthorizationShapeError",
    "RequestCase",
]
