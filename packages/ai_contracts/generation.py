"""AIGeneration operational lifecycle and AI_VALIDATION_PROOF.

Source: 08_AI_ARCHITECTURE_AND_CONTRACTS.md section 14 (AIGeneration
Operational Lifecycle -- "[ARCHITECTURAL CLOSURE]", the exact 6-state
vocabulary; "These are operational states. They are not domain inquiry
states."), section 15 (AIGeneration Legal Transitions -- the exact
legal-pair table; "A retry creates a new AIGeneration identity. It
does not revive a FAILED/REJECTED generation."), section 16
(AIGeneration and Canonical State -- "AIGeneration VALIDATED !=
Session transition != Decision != Evidence != ..."); 09
DATA_EVENT_API_CONTRACTS.md section 55 (DATA CONTRACT: AIGeneration --
exact field list, AC-09-022 retry-creates-new-identity), section 56
(DATA CONTRACT: AI_VALIDATION_PROOF -- exact field list, 3-value
`validation_result`), section 57 (DATA CONTRACT: SYSTEM_PROOF
Reference -- "may be evaluated transactionally without a standalone
persisted row... materialize a proof reference [only] where
persistence is required").

WHY `ai_context_manifest_id` IS A BARE `uuid.UUID`, NOT A REAL FOREIGN
KEY OR A TYPED `AIContextManifest` REFERENCE
--------------------------------------------------------------------
`ai_context_manifests` (14 section 9's own migration plan,
`007_ai_operational`) is PKG-19's own table to create -- 14's PKG-19
OBJECTIVE line ("Exclusive provider path, context manifest, prompt,
validator") assigns context-manifest assembly there, not here. This is
the identical disclosed forward-reference gap
`question_lineage.ai_generation_id` (PKG-06) and
`evidence_relations.ai_generation_id` (PKG-16) already carried before
THIS package existed to close them -- a plain nullable reference, not
a fabricated FK pointing at a table that does not exist yet.

WHY `AI_VALIDATION_PROOF` IS A PURE VALUE OBJECT, NOT ITS OWN TABLE
--------------------------------------------------------------------
14 section 7.1's own core-tables list names exactly three AI tables
for migration `007_ai_operational`: `ai_generations`,
`ai_context_manifests`, `ai_derived_artifacts` -- no fourth
`ai_validation_proofs` table. 09 section 57 already establishes the
precedent this package reuses: a proof class "may be evaluated
transactionally without a standalone persisted row" where a class-
specific persisted reference is not separately required. This
prototype's own outcome (a generation's own `status` reaching
VALIDATED/REJECTED) IS the durable record of validation having
occurred; `AIValidationProof` itself is the structured value a caller
computes and passes to
`persistence.ai_record_repository.AIRecordRepository.update_generation_status`,
not a second row this package writes.

WHY `prompt_version`/`model`/`provider` ARE PLAIN VALUES ON `AIGeneration`
DESPITE THIS PACKAGE NOT BUILDING PROMPT/PROVIDER LOGIC
--------------------------------------------------------------------
09 section 55 assigns these three fields to `AIGeneration` itself, not
to `AIContextManifest` (PKG-19's own table). Carrying the field 09
already assigns here is not "building successor behavior" -- it is
materializing THIS package's own DATA CONTRACT faithfully;
`prompt_version` reuses the existing `semantic_types.versions.
PromptVersion` type (PKG-00) rather than a second, competing version
type, the same "reuse an existing closed type where one already
exists" discipline PKG-10 applied to `human_decision_ref`/
`evidence_set_ref`/`method_version_ref`.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from semantic_types.ids import CommandId, CorrelationId, GenerationId, UserId, WorkspaceId
from semantic_types.versions import ContractVersion, PromptVersion, RecordVersion

from ai_contracts.aiop import AIOperationId


class AIGenerationStatus(Enum):
    """08 section 14's exact 6-value closed operational vocabulary."""

    REQUESTED = "REQUESTED"
    RUNNING = "RUNNING"
    OUTPUT_RECEIVED = "OUTPUT_RECEIVED"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


_LEGAL_GENERATION_TRANSITIONS: frozenset[tuple[AIGenerationStatus, AIGenerationStatus]] = frozenset(
    {
        (AIGenerationStatus.REQUESTED, AIGenerationStatus.RUNNING),
        (AIGenerationStatus.RUNNING, AIGenerationStatus.OUTPUT_RECEIVED),
        (AIGenerationStatus.RUNNING, AIGenerationStatus.FAILED),
        (AIGenerationStatus.OUTPUT_RECEIVED, AIGenerationStatus.VALIDATED),
        (AIGenerationStatus.OUTPUT_RECEIVED, AIGenerationStatus.REJECTED),
        (AIGenerationStatus.OUTPUT_RECEIVED, AIGenerationStatus.FAILED),
    }
)
"""08 section 15's exact legal-pair table. `VALIDATED`/`REJECTED`/
`FAILED` are all absent as a *from* state -- each is terminal (section
15's own illegal list: "REJECTED -> VALIDATED by silent mutation",
"FAILED -> VALIDATED", "REQUESTED -> VALIDATED", "RUNNING -> VALIDATED"
are all explicitly named illegal; no legal exit from any terminal
state exists at all, not merely a denial of the VALIDATED target)."""


def is_legal_generation_transition(
    from_status: AIGenerationStatus, to_status: AIGenerationStatus
) -> bool:
    return (from_status, to_status) in _LEGAL_GENERATION_TRANSITIONS


@dataclass(frozen=True, slots=True)
class AIGeneration:
    """09 section 55's exact field list."""

    ai_generation_id: GenerationId
    workspace_id: WorkspaceId
    ai_operation_id: AIOperationId
    ai_operation_contract_version: ContractVersion
    prompt_version: PromptVersion
    model: str
    provider: str
    status: AIGenerationStatus
    requested_at: datetime
    correlation_id: CorrelationId
    record_version: RecordVersion
    user_id: UserId | None = None
    ai_context_manifest_id: uuid.UUID | None = None
    started_at: datetime | None = None
    output_received_at: datetime | None = None
    completed_at: datetime | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    latency_ms: int | None = None
    estimated_cost: float | None = None
    retry_of_generation_id: GenerationId | None = None
    command_id: CommandId | None = None
    output_artifact_ref: uuid.UUID | None = None
    failure_code: str | None = None
    failure_detail_ref: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.ai_generation_id, GenerationId):
            raise TypeError(
                f"ai_generation_id must be a GenerationId, got {type(self.ai_generation_id)!r}"
            )
        if not isinstance(self.workspace_id, WorkspaceId):
            raise TypeError(f"workspace_id must be a WorkspaceId, got {type(self.workspace_id)!r}")
        if not isinstance(self.ai_operation_id, AIOperationId):
            raise TypeError(
                f"ai_operation_id must be an AIOperationId, got {type(self.ai_operation_id)!r}"
            )
        if not isinstance(self.ai_operation_contract_version, ContractVersion):
            raise TypeError(
                "ai_operation_contract_version must be a ContractVersion, got "
                f"{type(self.ai_operation_contract_version)!r}"
            )
        if not isinstance(self.prompt_version, PromptVersion):
            raise TypeError(
                f"prompt_version must be a PromptVersion, got {type(self.prompt_version)!r}"
            )
        if not self.model:
            raise ValueError("AIGeneration.model must be non-empty")
        if not self.provider:
            raise ValueError("AIGeneration.provider must be non-empty")
        if not isinstance(self.status, AIGenerationStatus):
            raise TypeError(f"status must be an AIGenerationStatus, got {type(self.status)!r}")
        if not isinstance(self.correlation_id, CorrelationId):
            raise TypeError(
                f"correlation_id must be a CorrelationId, got {type(self.correlation_id)!r}"
            )
        if not isinstance(self.record_version, RecordVersion):
            raise TypeError(
                f"record_version must be a RecordVersion, got {type(self.record_version)!r}"
            )
        # Mandatory package-specific attack: retry reuses GenerationId.
        # A retry's whole point (AC-09-022) is a NEW identity correlated
        # to the prior one -- a generation cannot claim to retry itself.
        if (
            self.retry_of_generation_id is not None
            and self.retry_of_generation_id == self.ai_generation_id
        ):
            raise ValueError("AIGeneration.retry_of_generation_id must not equal its own id")
        if self.user_id is not None and not isinstance(self.user_id, UserId):
            raise TypeError(f"user_id must be a UserId or None, got {type(self.user_id)!r}")
        if self.command_id is not None and not isinstance(self.command_id, CommandId):
            raise TypeError(
                f"command_id must be a CommandId or None, got {type(self.command_id)!r}"
            )
        if self.retry_of_generation_id is not None and not isinstance(
            self.retry_of_generation_id, GenerationId
        ):
            raise TypeError(
                "retry_of_generation_id must be a GenerationId or None, got "
                f"{type(self.retry_of_generation_id)!r}"
            )


class AIValidationResult(Enum):
    """09 section 56's own 3-value closed vocabulary for
    `validation_result` -- deliberately distinct from
    `AIGenerationStatus`'s own 6 values (a validation RESULT is not the
    generation's own lifecycle state)."""

    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    INDETERMINATE = "INDETERMINATE"


@dataclass(frozen=True, slots=True)
class AIValidationProof:
    """09 section 56's exact field list. "It proves only contract
    validation. It is never DOMAIN_EVIDENCE." Not persisted as its own
    row this build phase (see module docstring)."""

    ai_validation_proof_id: uuid.UUID
    ai_generation_id: GenerationId
    ai_operation_id: AIOperationId
    contract_version: ContractVersion
    validator_version: ContractVersion
    validation_result: AIValidationResult
    validated_at: datetime
    output_fingerprint: str
    validation_details_ref: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.ai_generation_id, GenerationId):
            raise TypeError(
                f"ai_generation_id must be a GenerationId, got {type(self.ai_generation_id)!r}"
            )
        if not isinstance(self.ai_operation_id, AIOperationId):
            raise TypeError(
                f"ai_operation_id must be an AIOperationId, got {type(self.ai_operation_id)!r}"
            )
        if not isinstance(self.contract_version, ContractVersion):
            raise TypeError(
                f"contract_version must be a ContractVersion, got {type(self.contract_version)!r}"
            )
        if not isinstance(self.validator_version, ContractVersion):
            raise TypeError(
                f"validator_version must be a ContractVersion, got {type(self.validator_version)!r}"
            )
        if not isinstance(self.validation_result, AIValidationResult):
            raise TypeError(
                f"validation_result must be an AIValidationResult, got "
                f"{type(self.validation_result)!r}"
            )
        if not self.output_fingerprint:
            raise ValueError("AIValidationProof.output_fingerprint must be non-empty")


__all__ = [
    "AIGenerationStatus",
    "is_legal_generation_transition",
    "AIGeneration",
    "AIValidationResult",
    "AIValidationProof",
]
