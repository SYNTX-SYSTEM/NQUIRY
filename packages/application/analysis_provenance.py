"""F04 inverse provenance: accepted artifact → BEGIN_ANALYSIS → controller.

Reconstruction §11 items 2a/2b and 4a/4b; §0.1 rule 8; falsifiers E16, K17,
K19. The walk reads ONLY write-once records through
`persistence.provenance_reader.SqlAlchemyImmutableProvenanceReader` (no Session
state, no generation status, no "current accepted artifact"):

    artifact → its VALIDATED proof (same operation; sha256(content) =
    content_fingerprint = proof.output_fingerprint; review R1) →
    generation identity (OA, retry_of, X) → OA row (shape, case,
    superseded OA, chain root) → the OA's authorizing Command's COMMITTED audit
    → (for AIOP-002) X → X's generation → X's OA … → the chain root
    BEGIN_ANALYSIS audit (BINDING, SESSION:<id>, the controller).

It returns the chain as data. Any missing link raises `ProvenanceBroken`: a
chain that cannot be reconstructed is never presented as complete.
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from typing import Protocol

from persistence.provenance_reader import (
    ArtifactFact,
    AuthorizationFact,
    CommittedAuditFact,
    GenerationIdentityFact,
    ProofFact,
)

BEGIN_ANALYSIS = "CMD_BEGIN_ANALYSIS"


class ImmutableProvenanceReader(Protocol):
    def artifact(self, artifact_id: uuid.UUID) -> ArtifactFact | None: ...
    def validation_proof(self, generation_id: uuid.UUID) -> ProofFact | None: ...
    def generation_identity(self, generation_id: uuid.UUID) -> GenerationIdentityFact | None: ...
    def authorization(self, authorization_id: uuid.UUID) -> AuthorizationFact | None: ...
    def committed_audit(self, command_id: uuid.UUID) -> CommittedAuditFact | None: ...


class ProvenanceBroken(Exception):
    pass


@dataclass(frozen=True)
class ChainLink:
    artifact_id: uuid.UUID
    ai_operation_id: str
    generation_id: uuid.UUID
    provider: str
    proof_id: uuid.UUID
    """The VALIDATED AI_VALIDATION_PROOF the accepted bytes are bound to (R1)."""
    output_fingerprint: str
    authorization: AuthorizationFact
    branch: str
    """ORIGINAL | RETRY | RECOVERY"""
    retry_of_generation_id: uuid.UUID | None
    superseded_authorization_id: uuid.UUID | None
    authorizing_audit: CommittedAuditFact
    acceptance_audit: CommittedAuditFact


@dataclass(frozen=True)
class ProvenanceChain:
    links: tuple[ChainLink, ...]
    """The accepted artifact first; for AIOP-002 the AIOP-001 X follows."""
    root: CommittedAuditFact
    """The BEGIN_ANALYSIS audit: BINDING, SESSION:<id>, the controller."""
    steps: tuple[str, ...] = field(default=())


def _need(value: object, what: str) -> object:
    if value is None:
        raise ProvenanceBroken(f"missing persisted link: {what}")
    return value


def _link(reader: ImmutableProvenanceReader, artifact_id: uuid.UUID) -> ChainLink:
    artifact: ArtifactFact = _need(reader.artifact(artifact_id), f"artifact {artifact_id}")  # type: ignore[assignment]
    # R1 (09 §118, PI-1, §11 "← BND-010 ← persisted proof VALIDATED"): the chain
    # passes through the immutable proof, and the accepted bytes are the
    # validated bytes. No re-derivation, no trust in code.
    proof: ProofFact = _need(  # type: ignore[assignment]
        reader.validation_proof(artifact.ai_generation_id), "validation proof"
    )
    if proof.validation_result != "VALIDATED":
        raise ProvenanceBroken(f"the proof is {proof.validation_result}, not VALIDATED")
    if proof.ai_operation_id != artifact.ai_operation_id:
        raise ProvenanceBroken("the proof validated a different operation")
    content_sha = hashlib.sha256(artifact.content.encode("utf-8")).hexdigest()
    if not (content_sha == artifact.content_fingerprint == proof.output_fingerprint):
        raise ProvenanceBroken("the accepted content is not the validated output")
    generation: GenerationIdentityFact = _need(  # type: ignore[assignment]
        reader.generation_identity(artifact.ai_generation_id), "generation"
    )
    oa_id = _need(generation.operation_authorization_id, "generation OA")
    oa: AuthorizationFact = _need(reader.authorization(oa_id), "authorization")  # type: ignore[arg-type,assignment]
    if generation.authorizing_command_id != oa.authorizing_command_id:
        raise ProvenanceBroken("generation OA fields disagree with the OA row")
    branch = oa.request_case or "ORIGINAL"
    if branch == "RETRY" and generation.retry_of_generation_id != oa.retry_of_generation_id:
        raise ProvenanceBroken("RETRY lineage disagrees")
    authorizing: CommittedAuditFact = _need(  # type: ignore[assignment]
        reader.committed_audit(oa.authorizing_command_id), "authorizing command audit"
    )
    accepting: CommittedAuditFact = _need(  # type: ignore[assignment]
        reader.committed_audit(_need(artifact.accepted_by_command_id, "acceptance")),  # type: ignore[arg-type]
        "acceptance audit",
    )
    if (
        accepting.authority_source_type != "SYSTEM_OPERATION"
        or accepting.authority_source_ref != oa.authorizing_command_id
    ):
        raise ProvenanceBroken("acceptance is not SYSTEM_OPERATION under the OA's Command")
    return ChainLink(
        artifact_id=artifact.artifact_id,
        ai_operation_id=artifact.ai_operation_id,
        generation_id=generation.generation_id,
        provider=generation.provider,
        proof_id=proof.proof_id,
        output_fingerprint=proof.output_fingerprint,
        authorization=oa,
        branch=branch,
        retry_of_generation_id=generation.retry_of_generation_id,
        superseded_authorization_id=oa.supersedes_authorization_id,
        authorizing_audit=authorizing,
        acceptance_audit=accepting,
    )


def resolve_provenance(
    reader: ImmutableProvenanceReader, artifact_id: uuid.UUID
) -> ProvenanceChain:
    links = [_link(reader, artifact_id)]
    if links[0].ai_operation_id == "AIOP-002":
        x = _need(links[0].authorization.precondition_artifact_ref, "precondition artifact X")
        x_link = _link(reader, x)  # type: ignore[arg-type]
        if x_link.ai_operation_id != "AIOP-001":
            raise ProvenanceBroken("X is not an AIOP-001 artifact")
        if (
            links[0].authorization.shape == "OA-3"
            and x_link.authorization.authorizing_command_id
            != links[0].authorization.authorizing_command_id
        ):
            raise ProvenanceBroken("OA-3 is not authorized by the Command that authorized X")
        links.append(x_link)
    roots = {link.authorization.chain_root_command_id for link in links}
    if len(roots) != 1:
        raise ProvenanceBroken("links resolve to different BEGIN_ANALYSIS roots")
    root: CommittedAuditFact = _need(reader.committed_audit(roots.pop()), "root audit")  # type: ignore[assignment]
    if (
        root.command_type != BEGIN_ANALYSIS
        or root.authority_source_type != "BINDING"
        or root.actor_type != "HUMAN_USER"
    ):
        raise ProvenanceBroken("the chain root is not a human BINDING BEGIN_ANALYSIS")
    for link in links:
        if link.authorization.shape in ("OA-2", "OA-4") and (
            link.authorizing_audit.authority_source_type != "BINDING"
            or link.authorizing_audit.actor_type != "HUMAN_USER"
        ):
            raise ProvenanceBroken("a controller request is not a human BINDING Command")
    steps = tuple(
        f"{link.ai_operation_id} artifact {link.artifact_id} ← proof {link.proof_id} VALIDATED "
        f"(sha256 {link.output_fingerprint[:16]}…) ← generation {link.generation_id} "
        f"({link.provider}) ← {link.authorization.shape} {link.branch} ← "
        f"{link.authorizing_audit.command_type} ({link.authorizing_audit.authority_source_type})"
        for link in links
    ) + (f"root {root.command_type} ({root.authority_source_type} {root.authority_scope_ref})",)
    return ProvenanceChain(links=tuple(links), root=root, steps=steps)


__all__ = ["ChainLink", "ProvenanceBroken", "ProvenanceChain", "resolve_provenance"]
