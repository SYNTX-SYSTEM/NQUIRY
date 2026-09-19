"""AIGateway: the exclusive orchestration path from an authorized AI
operation request through to a persisted, validated derived artifact.

Source: 14_IMPLEMENTATION_SEQUENCE.md PKG-19 package manifest ("PUBLIC
INTERFACES: AIGateway"); 06_BOUNDARY_ARCHITECTURE.md section 15
(BND-009 -- "All LLM traffic passes through internal AI Gateway
abstraction"; "NEXT PERMITTED PATH: AI provider execution then BND-010
for returned output"); 08_AI_ARCHITECTURE_AND_CONTRACTS.md section 3
(All LLM Traffic Through Gateway), section 14/15 (AIGeneration
lifecycle and legal transitions).

WHY THIS FILE IS NOT NAMED IN 14 SECTION 48'S OWN FILE-LEVEL MAP ROW
LIST, YET IS CREATED HERE
--------------------------------------------------------------------
14 section 48's own file tree is declared "Representative" -- four
rows exist for this package (`context.py`/`prompt.py`/`validator.py`/
`adapters/providers/mock.py`), each mapped to one named COMPONENT
(allowlisted manifest, prompt, AI_VALIDATION_PROOF, deterministic
mock). None of those four rows' own "Purpose" column claims the
identity 14's OWN package manifest explicitly names as this package's
PUBLIC_INTERFACES: "AIGateway" itself -- the orchestrator tying the
four components together. This file is that orchestrator, the same
"the file map names every load-bearing component; the thin composition
root gets its own file when no existing row already claims that
identity" reasoning already applied without incident by every prior
package's own disclosed extension points.

WHY `run_operation` TAKES `invocation_authorized: bool` INSTEAD OF
EVALUATING BND-008/BND-009 ITSELF
--------------------------------------------------------------------
14 section 3.1's own "May depend on" row for `ai_gateway` is exactly
"ai_contracts, security, operational persistence" -- it does NOT
include `boundaries`. This is not an oversight this package may
correct by adding an extension: 14's own table is authoritative, and
`packages/boundaries/bnd_009_ai_invocation.py`/`bnd_010_ai_output.py`
(built by this package, see their own modules) are real, independently
testable evaluators that live where boundaries always live, RATHER
THAN being importable from here. The identical split
`commit.coordinator.CommitCoordinator.commit()` already established
for BND-014 (`upstream_chain_result: BoundaryResult`, a caller-supplied
FACT, not a `boundaries` import) is reused here with a plain `bool`
in place of `BoundaryResult` specifically because `commit`'s own
allowed set DOES include `boundaries` (so it can type that parameter
precisely) while `ai_gateway`'s does not -- accepting an untyped
`bool` here is the honest, minimal-erasure choice available within
this package's own dependency ceiling, not a preference for weaker
typing. A future package (not this one -- `packages/application` is
outside `FILES_ALLOWED_TO_CREATE` for PKG-19) is expected to evaluate
BND-001 through BND-009 for real via `boundaries.registry.evaluate_chain`
and pass its own chain's `is_allowed` property here, the same
hand-off shape `application.question_selection_handler` (PKG-14)
already established one layer up for `commit.coordinator`.

WHY BND-010 IS SIMILARLY NOT INVOKED FROM INSIDE THIS FILE
--------------------------------------------------------------------
`AIRecordRepository` (this package's only write capability, built at
PKG-18) is structurally incapable of writing anything BND-010's own
DENY list names (Decision/Selection/HABB/Session transition/Assumption
status) -- proven directly by
`tests/ai/test_generation.py::test_ai_record_repository_has_no_domain_mutation_capability`.
BND-010's own evaluator (`boundaries.bnd_010_ai_output`) is built and
independently tested by this package to prove its OWN logic correct in
isolation (14 PKG-19 BOUNDARIES: "BND-008 and AI invocation boundaries
as mapped by 14"); wiring it as an active caller of THIS orchestrator
would face the identical `ai_gateway -> boundaries` ceiling described
above.

WHY `run_operation` PERSISTS `context_manifest` ITSELF RATHER THAN
REQUIRING THE CALLER TO HAVE DONE SO ALREADY
--------------------------------------------------------------------
`ai_generations.ai_context_manifest_id` carries a real composite
foreign key to `ai_context_manifests(id, workspace_id)` (this
package's own migration) -- a generation cannot legitimately reference
a manifest that was never stored. 08 section 54.1: "One generation
points to one immutable manifest. A retry ... may reuse or create a
new manifest according to actual context." This method therefore
checks for an existing row first (supporting a legitimate retry that
reuses the same manifest) and creates it only if absent, rather than
silently assuming the caller already persisted it -- an assumption
that would either violate the FK or require every caller to duplicate
this same existence check.

WHY `model`/`provider` ARE KNOWN AT `AIGeneration` CREATION TIME
--------------------------------------------------------------------
14 PKG-19's OBJECTIVE names a "minimal Model Router" -- minimal because
exactly one provider is currently eligible (12 section 12.3, AC-12-008:
"One eligible provider is sufficient"). The router's own decision is
therefore a constant for this build phase (`self._provider_adapter`'s
own `model`/`provider` identity), not a runtime search -- 09 section
55 assigns `model`/`provider` to `AIGeneration` with no "nullable"
annotation, so this package materializes them at REQUESTED time
honestly, rather than inventing an intermediate nullable state 09
never describes.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from ai_contracts.aiop import AIOperationId
from ai_contracts.derived_artifact import AIDerivedArtifact
from ai_contracts.generation import AIGeneration, AIGenerationStatus, AIValidationResult
from persistence.ai_record_repository import AIRecordRepository
from semantic_types.ids import CommandId, CorrelationId, GenerationId, UserId, WorkspaceId
from semantic_types.versions import ContractVersion, RecordVersion

from ai_gateway.adapters.providers.mock import (
    MockProviderAdapter,
    MockProviderOutcome,
    ProviderError,
    ProviderTimeout,
)
from ai_gateway.context import AIContextManifest
from ai_gateway.prompt import InvocationPrompt
from ai_gateway.validator import validate_response


class InvocationNotAuthorized(Exception):
    """Raised when `run_operation` is called with `invocation_authorized=False`
    -- BND-008/BND-009 did not both ALLOW upstream. No `AIGeneration`
    row is ever created for a call that raises this (06 section 15's
    own "no generation/provider call" framing for a blocked
    invocation)."""


class ContextManifestWorkspaceMismatch(Exception):
    """Defense in depth: the supplied `AIContextManifest`'s own
    `workspace_id` must match the request's declared Workspace, even
    though a caller that legitimately built the manifest via
    `ai_gateway.context.build_context_manifest` could never produce a
    mismatch honestly."""


@dataclass(frozen=True, slots=True)
class AIGatewayResult:
    ai_generation_id: GenerationId
    status: AIGenerationStatus
    validation_result: AIValidationResult | None
    ai_derived_artifact_id: uuid.UUID | None
    failure_code: str | None


class AIGateway:
    """The exclusive path. Holds the one `MockProviderAdapter` instance
    -- "Provider credentials only Gateway" (14 PKG-19 OBJECTIVE) means
    concretely that nothing outside this class ever touches
    `self._provider_adapter` directly."""

    def __init__(
        self,
        *,
        record_repository: AIRecordRepository,
        provider_adapter: MockProviderAdapter,
        validator_version: ContractVersion,
    ) -> None:
        self._record_repository = record_repository
        self._provider_adapter = provider_adapter
        self._validator_version = validator_version

    def run_operation(
        self,
        *,
        invocation_authorized: bool,
        workspace_id: WorkspaceId,
        ai_operation_id: AIOperationId,
        ai_operation_contract_version: ContractVersion,
        context_manifest: AIContextManifest,
        prompt: InvocationPrompt,
        correlation_id: CorrelationId,
        occurred_at: datetime,
        user_id: UserId | None = None,
        command_id: CommandId | None = None,
        retry_of_generation_id: GenerationId | None = None,
        scripted_outcome: MockProviderOutcome = MockProviderOutcome.SUCCESS,
    ) -> AIGatewayResult:
        # Mandatory adversarial attack: active Burst invocation (and
        # every other upstream-boundary denial) -- proven at the caller
        # layer per this module's own docstring; this is the fail-closed
        # gate on the fact itself.
        if not invocation_authorized:
            raise InvocationNotAuthorized(
                f"invocation of {ai_operation_id.value} was not authorized upstream"
            )
        # Mandatory adversarial attack: wrong Workspace artifact.
        if context_manifest.workspace_id != workspace_id:
            raise ContextManifestWorkspaceMismatch(
                f"context manifest workspace {context_manifest.workspace_id!r} != "
                f"requested workspace {workspace_id!r}"
            )

        # 08 section 54.1: "One generation points to one immutable
        # manifest. A retry ... may reuse or create a new manifest
        # according to actual context." -- persist it here if this is
        # its first use; a retry that legitimately reuses the same
        # manifest finds it already stored and does not re-insert it.
        if (
            self._record_repository.get_context_manifest(context_manifest.ai_context_manifest_id)
            is None
        ):
            self._record_repository.create_context_manifest(context_manifest)

        ai_generation_id = GenerationId(uuid.uuid4())
        generation = AIGeneration(
            ai_generation_id=ai_generation_id,
            workspace_id=workspace_id,
            ai_operation_id=ai_operation_id,
            ai_operation_contract_version=ai_operation_contract_version,
            prompt_version=prompt.prompt_version,
            model=self._provider_adapter.model,
            provider=self._provider_adapter.provider,
            status=AIGenerationStatus.REQUESTED,
            requested_at=occurred_at,
            correlation_id=correlation_id,
            record_version=RecordVersion.initial(),
            user_id=user_id,
            ai_context_manifest_id=context_manifest.ai_context_manifest_id,
            command_id=command_id,
            retry_of_generation_id=retry_of_generation_id,
        )
        self._record_repository.create_generation(generation)
        version = RecordVersion.initial()

        version = self._advance(
            ai_generation_id,
            workspace_id,
            version,
            AIGenerationStatus.RUNNING,
            started_at=occurred_at,
        )

        try:
            response = self._provider_adapter.invoke(prompt, scripted_outcome=scripted_outcome)
        except (ProviderTimeout, ProviderError) as exc:
            # Mandatory adversarial attacks: timeout, provider error.
            self._advance(
                ai_generation_id,
                workspace_id,
                version,
                AIGenerationStatus.FAILED,
                completed_at=occurred_at,
                failure_code=type(exc).__name__,
            )
            return AIGatewayResult(
                ai_generation_id=ai_generation_id,
                status=AIGenerationStatus.FAILED,
                validation_result=None,
                ai_derived_artifact_id=None,
                failure_code=type(exc).__name__,
            )

        version = self._advance(
            ai_generation_id,
            workspace_id,
            version,
            AIGenerationStatus.OUTPUT_RECEIVED,
            output_received_at=occurred_at,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            latency_ms=response.latency_ms,
        )

        proof = validate_response(
            response=response,
            ai_generation_id=ai_generation_id,
            ai_operation_id=ai_operation_id,
            contract_version=ai_operation_contract_version,
            validator_version=self._validator_version,
            validated_at=occurred_at,
        )

        if proof.validation_result is not AIValidationResult.VALIDATED:
            # Mandatory adversarial attack: invalid schema (REJECTED)
            # and the partial-response INDETERMINATE case (08 section
            # 14.5: "Output was received but failed operation-contract
            # validation" -- both map to REJECTED, 08's own 6-state
            # vocabulary has no separate "indeterminate" generation
            # status to hold the finer-grained validator distinction).
            self._advance(
                ai_generation_id,
                workspace_id,
                version,
                AIGenerationStatus.REJECTED,
                completed_at=occurred_at,
                failure_code=proof.validation_result.value,
            )
            return AIGatewayResult(
                ai_generation_id=ai_generation_id,
                status=AIGenerationStatus.REJECTED,
                validation_result=proof.validation_result,
                ai_derived_artifact_id=None,
                failure_code=proof.validation_result.value,
            )

        ai_derived_artifact_id = uuid.uuid4()
        artifact = AIDerivedArtifact(
            ai_derived_artifact_id=ai_derived_artifact_id,
            workspace_id=workspace_id,
            ai_generation_id=ai_generation_id,
            ai_operation_id=ai_operation_id,
            content=response.raw_content,
            content_fingerprint=proof.output_fingerprint,
            created_at=occurred_at,
            record_version=RecordVersion.initial(),
            provenance_ref=str(proof.ai_validation_proof_id),
        )
        self._record_repository.create_derived_artifact(artifact)
        self._advance(
            ai_generation_id,
            workspace_id,
            version,
            AIGenerationStatus.VALIDATED,
            completed_at=occurred_at,
            output_artifact_ref=ai_derived_artifact_id,
        )
        return AIGatewayResult(
            ai_generation_id=ai_generation_id,
            status=AIGenerationStatus.VALIDATED,
            validation_result=AIValidationResult.VALIDATED,
            ai_derived_artifact_id=ai_derived_artifact_id,
            failure_code=None,
        )

    def _advance(
        self,
        ai_generation_id: GenerationId,
        workspace_id: WorkspaceId,
        expected_record_version: RecordVersion,
        new_status: AIGenerationStatus,
        **fields: object,
    ) -> RecordVersion:
        self._record_repository.update_generation_status(
            ai_generation_id=ai_generation_id,
            workspace_id=workspace_id,
            expected_record_version=expected_record_version,
            new_status=new_status,
            **fields,  # type: ignore[arg-type]
        )
        return expected_record_version.next()


__all__ = [
    "InvocationNotAuthorized",
    "ContextManifestWorkspaceMismatch",
    "AIGatewayResult",
    "AIGateway",
]
