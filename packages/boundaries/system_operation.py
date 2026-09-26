"""The SYSTEM_OPERATION right (F04 HD-17; reconstruction §0.1, §5).

One definition, used by BOTH the system handlers' precommit check and the
effect gate (BND-014, SYSTEM_OPERATION source), so the two can never disagree
(the same pattern as `participation_right`).

A SYSTEM_SERVICE may commit under operation authorization OA only if, re-read
live from persisted records:

- the actor is SYSTEM_SERVICE with the fixed F04 service identity (PI-3);
- OA exists in this Workspace and this Session;
- OA's authorizing Command and the chain-root BEGIN_ANALYSIS are COMMITTED
  Commands of this Workspace targeting this Session (rule 6);
- the Session is in ANALYSIS (the only phase F04 AI work happens in);
- OA is the latest authorization of its (Session, operation) (rule 5: a
  superseded OA never executes);
- no accepted result exists for the operation (R2 / R8);
- for AIOP-002: the PERSISTED precondition artifact X is an accepted AIOP-001
  artifact of this Session, and for OA-3 X's generation carries the same
  authorizing Command C (R7, K18). It never substitutes a "current accepted
  artifact" read for the persisted reference;
- EXECUTE: no generation carries OA yet (rule 3);
- ACCEPT: exactly the named generation carries OA and is not terminal.

It is not SYSTEM_DERIVED authority and nothing here is cached.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Protocol

from ai_contracts.aiop import AIOperationId
from ai_contracts.authorization import AuthorizationShape, OperationAuthorization
from ai_contracts.derived_artifact import AIDerivedArtifact
from ai_contracts.generation import AIGeneration, AIGenerationStatus
from authority.actor import ActorClass, ActorIdentity
from authority.system_service import F04_ANALYSIS_SERVICE_ID
from domain.session import SessionState
from semantic_types.ids import CommandId, GenerationId, SessionId, WorkspaceId

from boundaries.authority_source import (
    AuthoritySourceProof,
    AuthoritySourceType,
    SystemOperationAuthority,
    SystemOperationPurpose,
)

BEGIN_ANALYSIS_COMMAND = "CMD_BEGIN_ANALYSIS"
_AUTHORIZING_COMMAND_TYPES = {
    AuthorizationShape.OA_1: frozenset({BEGIN_ANALYSIS_COMMAND}),
    AuthorizationShape.OA_2: frozenset({"CMD_REQUEST_QUESTION_ANALYSIS"}),
    AuthorizationShape.OA_3: frozenset({BEGIN_ANALYSIS_COMMAND, "CMD_REQUEST_QUESTION_ANALYSIS"}),
    AuthorizationShape.OA_4: frozenset({"CMD_REQUEST_QUESTION_CLUSTERING"}),
}
_NON_TERMINAL = frozenset(
    {AIGenerationStatus.REQUESTED, AIGenerationStatus.RUNNING, AIGenerationStatus.OUTPUT_RECEIVED}
)


class CommittedCommand(Protocol):
    """A Command with a COMMITTED attempt (structural; persistence supplies it)."""

    @property
    def command_id(self) -> CommandId: ...
    @property
    def workspace_id(self) -> WorkspaceId: ...
    @property
    def command_type(self) -> str: ...
    @property
    def target_refs(self) -> tuple[str, ...]: ...


class SystemOperationReader(Protocol):
    """Fresh persisted facts. Implemented by
    `persistence.system_operation_reader.SqlAlchemySystemOperationReader`."""

    def authorization(self, authorization_id: uuid.UUID) -> OperationAuthorization | None: ...
    def latest_sequence(
        self, session_id: SessionId, ai_operation_id: AIOperationId
    ) -> int | None: ...
    def committed_command(self, command_id: CommandId) -> CommittedCommand | None: ...
    def session_state(self, session_id: SessionId) -> tuple[WorkspaceId, SessionState] | None: ...
    def generation_for_authorization(self, authorization_id: uuid.UUID) -> AIGeneration | None: ...
    def generation(self, ai_generation_id: GenerationId) -> AIGeneration | None: ...
    def artifact(self, artifact_id: uuid.UUID) -> AIDerivedArtifact | None: ...
    def accepted_artifact(
        self, session_id: SessionId, ai_operation_id: AIOperationId
    ) -> AIDerivedArtifact | None: ...


@dataclass(frozen=True, slots=True)
class SystemOperationResolution:
    granted: bool
    reason_code: str
    source: AuthoritySourceProof | None = None
    authorization: OperationAuthorization | None = None


def _deny(code: str) -> SystemOperationResolution:
    return SystemOperationResolution(False, f"SYSTEM_OPERATION_{code}")


def resolve_system_operation(
    *,
    reader: SystemOperationReader | None,
    actor: ActorIdentity,
    workspace_id: WorkspaceId,
    authority: SystemOperationAuthority,
) -> SystemOperationResolution:
    if reader is None:
        return _deny("READER_NOT_CONFIGURED")
    if actor.actor_class is not ActorClass.SYSTEM_SERVICE:
        return _deny(f"ACTOR_NOT_SYSTEM_SERVICE:{actor.actor_class.value}")
    if actor.user_id != F04_ANALYSIS_SERVICE_ID:
        return _deny("SERVICE_IDENTITY_UNKNOWN")

    oa = reader.authorization(authority.operation_authorization_id)
    if oa is None:
        return _deny("AUTHORIZATION_NOT_FOUND")
    session_id = SessionId(authority.session_id)
    if oa.workspace_id != workspace_id or oa.session_id != session_id:
        return _deny("FOREIGN_SCOPE")
    session_ref = f"session:{authority.session_id}"

    command = reader.committed_command(oa.authorizing_command_id)
    if command is None or command.workspace_id != workspace_id:
        return _deny("AUTHORIZING_COMMAND_NOT_COMMITTED")
    if command.command_type not in _AUTHORIZING_COMMAND_TYPES[oa.shape]:
        return _deny(f"AUTHORIZING_COMMAND_TYPE:{command.command_type}")
    if session_ref not in command.target_refs:
        return _deny("AUTHORIZING_COMMAND_FOREIGN_SESSION")
    root = reader.committed_command(oa.chain_root_command_id)
    if (
        root is None
        or root.workspace_id != workspace_id
        or root.command_type != BEGIN_ANALYSIS_COMMAND
        or session_ref not in root.target_refs
    ):
        return _deny("CHAIN_ROOT_INVALID")

    state = reader.session_state(session_id)
    if state is None or state[0] != workspace_id:
        return _deny("SESSION_NOT_FOUND")
    if state[1] is not SessionState.ANALYSIS:
        return _deny(f"SESSION_NOT_ANALYSIS:{state[1].value}")

    if reader.latest_sequence(session_id, oa.ai_operation_id) != oa.sequence_no:
        return _deny("SUPERSEDED")
    if reader.accepted_artifact(session_id, oa.ai_operation_id) is not None:
        return _deny("RESULT_ALREADY_ACCEPTED")

    if oa.ai_operation_id is AIOperationId.AIOP_002:
        x = (
            None
            if oa.precondition_artifact_ref is None
            else reader.artifact(oa.precondition_artifact_ref)
        )
        if (
            x is None
            or x.ai_operation_id is not AIOperationId.AIOP_001
            or x.session_id != session_id
            or x.workspace_id != workspace_id
            or x.accepted_by_command_id is None
        ):
            return _deny("PRECONDITION_ARTIFACT_INVALID")
        x_generation = reader.generation(x.ai_generation_id)
        if x_generation is None or x_generation.authorizing_command_id is None:
            return _deny("PRECONDITION_ARTIFACT_INVALID")
        if (
            oa.shape is AuthorizationShape.OA_3
            and x_generation.authorizing_command_id != oa.authorizing_command_id
        ):
            return _deny("PRECONDITION_AUTHORIZER_MISMATCH")

    carrier = reader.generation_for_authorization(oa.authorization_id)
    if authority.purpose is SystemOperationPurpose.EXECUTE:
        if carrier is not None:
            return _deny("ALREADY_CONSUMED")
    else:
        if carrier is None or carrier.ai_generation_id.value != authority.ai_generation_id:
            return _deny("GENERATION_MISMATCH")
        if carrier.status not in _NON_TERMINAL:
            return _deny(f"GENERATION_TERMINAL:{carrier.status.value}")

    return SystemOperationResolution(
        True,
        "SYSTEM_OPERATION_CURRENT",
        source=AuthoritySourceProof(
            source_type=AuthoritySourceType.SYSTEM_OPERATION,
            source_ref=oa.authorizing_command_id.value,
            scope_ref=f"SESSION:{authority.session_id}",
            detail=(
                f"{oa.shape.value}|{oa.ai_operation_id.value}|{authority.purpose.value}"
                f"|OA:{oa.authorization_id}|root:{oa.chain_root_command_id.value}"
                f" ({authority.operation_authority_ref})"
            ),
        ),
        authorization=oa,
    )


__all__ = [
    "BEGIN_ANALYSIS_COMMAND",
    "CommittedCommand",
    "SystemOperationReader",
    "SystemOperationResolution",
    "resolve_system_operation",
]
