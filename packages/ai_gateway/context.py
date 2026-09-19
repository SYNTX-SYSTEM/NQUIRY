"""AIContextManifest: the allowlisted, reconstructable record of exactly
what context one AI generation actually saw.

Source: 08_AI_ARCHITECTURE_AND_CONTRACTS.md section 6 (AI Context
Manifest -- "[ARCHITECTURAL CLOSURE]. Every AI invocation must have a
reconstructable semantic AIContextManifest... it identifies the exact
context assembled for one generation... Where source material includes
Evidence or other mutable content, version identity must be
preserved."), section 6.1 (Context Manifest Does Not Grant Authority),
section 6.2 (Context Freshness), section 10 (AI Coach Modes -- "LEVEL 1
defines" the exact 7-value closed list); 09_DATA_EVENT_API_CONTRACTS.md
section 54 (DATA CONTRACT: AIContextManifest -- exact field list).

WHY THIS MODULE PERFORMS NO I/O OF ITS OWN
--------------------------------------------------------------------
14 section 48's own file-level map row for this file names "whole
Workspace dump" as the one forbidden pattern -- the structural defense
against that is not a permission check on an unrestricted query, it is
that no such query exists anywhere in this module at all.
`build_context_manifest` is a pure function over an EXPLICIT,
caller-supplied list of `(artifact_ref, version)` pairs (the same
"caller performs the read, the engine only assembles/compares" split
`commit.coordinator.CurrentVersionReader` and `evidence.freshness.
resolve_evidence_set_freshness` already established) -- there is no
parameter shape by which a caller could hand this function "everything
in the Workspace" and have it accepted as one allowlisted entry.

WHY `CoachMode` IS A CLOSED ENUM HERE
--------------------------------------------------------------------
08 section 10: "LEVEL 1 defines: Silent, Reflective, Challenger,
Socratic, Facilitator, Researcher, Strategist" -- the same definitive
closure language (a named, complete list, not "examples"/"may
include") that has driven every other closed-vocabulary decision in
this codebase (see `evidence.models`'s own module docstring for the
precedent this reasoning already established at PKG-16).

WHY `burst_mode`/`method_ref` STAY PLAIN STRINGS
--------------------------------------------------------------------
`domain.burst.BurstMode` is a real, existing closed enum -- but
`ai_gateway`'s own allowed dependencies (14 section 3.1: "ai_contracts,
security, operational persistence") do not include `domain`. Holding
the value as inert data here, never re-exporting or reinterpreting it,
is the identical "hold an identifier as inert data because the owning
type lives in a package this one cannot import" pattern
`command.envelope`'s own `requesting_actor_type: str` already
established for `authority.actor.ActorClass` (PKG-10).
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from ai_contracts.aiop import AIOperationId
from semantic_types.ids import WorkspaceId
from semantic_types.versions import ContractVersion, RecordVersion


class CoachMode(Enum):
    """08 section 10's own exact 7-value closed vocabulary."""

    SILENT = "SILENT"
    REFLECTIVE = "REFLECTIVE"
    CHALLENGER = "CHALLENGER"
    SOCRATIC = "SOCRATIC"
    FACILITATOR = "FACILITATOR"
    RESEARCHER = "RESEARCHER"
    STRATEGIST = "STRATEGIST"


@dataclass(frozen=True, slots=True)
class InputArtifactRef:
    """One allowlisted input artifact and the exact version the
    manifest is pinned to -- 08 section 6: "Where source material
    includes Evidence or other mutable content, version identity must
    be preserved." Mirrors `evidence.evidence_set.EvidenceSetMember`'s
    identical (ref, version) shape."""

    artifact_ref: str
    version: RecordVersion

    def __post_init__(self) -> None:
        if not self.artifact_ref:
            raise ValueError("InputArtifactRef.artifact_ref must be non-empty")
        if not isinstance(self.version, RecordVersion):
            raise TypeError(f"version must be a RecordVersion, got {type(self.version)!r}")


@dataclass(frozen=True, slots=True)
class AIContextManifest:
    """09 section 54's exact field list."""

    ai_context_manifest_id: uuid.UUID
    workspace_id: WorkspaceId
    ai_operation_id: AIOperationId
    ai_operation_contract_version: ContractVersion
    requesting_actor_ref: str
    input_artifact_refs_with_versions: tuple[InputArtifactRef, ...]
    source_classifications: tuple[str, ...]
    assembled_at: datetime
    context_fingerprint: str
    method_ref: str | None = None
    coach_mode: CoachMode | None = None
    burst_mode: str | None = None
    excluded_context_classes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.ai_context_manifest_id, uuid.UUID):
            raise TypeError(
                "ai_context_manifest_id must be a uuid.UUID, got "
                f"{type(self.ai_context_manifest_id)!r}"
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
        if not self.requesting_actor_ref:
            raise ValueError("AIContextManifest.requesting_actor_ref must be non-empty")
        if self.coach_mode is not None and not isinstance(self.coach_mode, CoachMode):
            raise TypeError(
                f"coach_mode must be a CoachMode or None, got {type(self.coach_mode)!r}"
            )
        if not self.context_fingerprint:
            raise ValueError("AIContextManifest.context_fingerprint must be non-empty")


def compute_context_fingerprint(
    *,
    ai_operation_id: AIOperationId,
    ai_operation_contract_version: ContractVersion,
    input_artifact_refs_with_versions: tuple[InputArtifactRef, ...],
) -> str:
    """Deterministic, order-independent -- mirrors
    `evidence.evidence_set.compute_evidence_set_fingerprint`'s own
    change-detection-aid role (09 section 54.1's own "immutable
    context" guarantee is enforced at the DB layer, not here; this is
    the aid that lets a caller detect drift, not a sufficiency score).
    """
    canonical = "|".join(
        sorted(
            f"{ref.artifact_ref}:{ref.version.value}" for ref in input_artifact_refs_with_versions
        )
    )
    payload = f"{ai_operation_id.value}:{ai_operation_contract_version}:{canonical}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_context_manifest(
    *,
    ai_context_manifest_id: uuid.UUID,
    workspace_id: WorkspaceId,
    ai_operation_id: AIOperationId,
    ai_operation_contract_version: ContractVersion,
    requesting_actor_ref: str,
    input_artifact_refs_with_versions: tuple[InputArtifactRef, ...],
    source_classifications: tuple[str, ...],
    assembled_at: datetime,
    method_ref: str | None = None,
    coach_mode: CoachMode | None = None,
    burst_mode: str | None = None,
    excluded_context_classes: tuple[str, ...] = (),
) -> AIContextManifest:
    """The allowlist builder: assembles a manifest ONLY from the exact
    refs/versions the caller already resolved -- see module docstring
    for why no broader query is even representable here."""
    fingerprint = compute_context_fingerprint(
        ai_operation_id=ai_operation_id,
        ai_operation_contract_version=ai_operation_contract_version,
        input_artifact_refs_with_versions=input_artifact_refs_with_versions,
    )
    return AIContextManifest(
        ai_context_manifest_id=ai_context_manifest_id,
        workspace_id=workspace_id,
        ai_operation_id=ai_operation_id,
        ai_operation_contract_version=ai_operation_contract_version,
        requesting_actor_ref=requesting_actor_ref,
        input_artifact_refs_with_versions=input_artifact_refs_with_versions,
        source_classifications=source_classifications,
        assembled_at=assembled_at,
        context_fingerprint=fingerprint,
        method_ref=method_ref,
        coach_mode=coach_mode,
        burst_mode=burst_mode,
        excluded_context_classes=excluded_context_classes,
    )


__all__ = [
    "CoachMode",
    "InputArtifactRef",
    "AIContextManifest",
    "compute_context_fingerprint",
    "build_context_manifest",
]
