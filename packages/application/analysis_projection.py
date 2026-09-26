"""F04 WU-04.7: `position.analysis`, the derived field as a server projection.

HD-22 (16 §41 REC-024): the audience is the HD-13 frozen-set audience, decided
HERE on the server by the same read chain (`session_position` has already
proven identity + Workspace membership; the analysis block is served exactly
when the full frozen set is served, i.e. once the Burst is COMPLETED). The
client computes nothing.

Every derived item carries its origin explicitly: `origin = AI`,
`derived = true`, `kind = PROPOSAL`, the provider, and for the mock the
marker `MOCK / NON_PROOF` (HD-19); a mock result is never presented as
analysis of the real Questions. Human Questions stay in `questionSet`,
separately and verbatim (G4). Nothing here writes.

Status vocabulary (honest states, never an error):
- NOT_BEGUN: the Session is not in ANALYSIS.
- PENDING: the latest authorization exists and no generation carries it.
- RUNNING: a generation is non-terminal.
- UNAVAILABLE: the latest generation FAILED / REJECTED (08 §23 "Session
  remains ANALYSIS").
- ACCEPTED: an accepted artifact exists.
Clustering additionally has NOT_RUN (no accepted AIOP-001 artifact: HD-23,
"clustering must not run").
"""

from __future__ import annotations

import json
from typing import Any

from ai_contracts.aiop import AIOperationId
from ai_contracts.derived_artifact import AIDerivedArtifact, ProofClass
from ai_contracts.generation import AIGeneration, AIGenerationStatus
from domain.session import Session, SessionState

from application.composition import GovernedPorts

_NON_TERMINAL = frozenset(
    {AIGenerationStatus.REQUESTED, AIGenerationStatus.RUNNING, AIGenerationStatus.OUTPUT_RECEIVED}
)


def marker(provider: str | None) -> dict[str, object]:
    mock = provider == "mock"
    return {
        "origin": "AI",
        "derived": True,
        "kind": "PROPOSAL",
        "provider": provider,
        "proof": "MOCK / NON_PROOF" if mock else "NON_PROOF",
        "isMock": mock,
        "note": (
            "Produced by the development MockProvider. It is not an analysis of these "
            "Questions and is not proof of anything."
            if mock
            else "AI-derived proposal. Not a human decision and not evidence."
        ),
    }


def _generation_json(ports: GovernedPorts, g: AIGeneration) -> dict[str, object]:
    oa = (
        None
        if g.operation_authorization_id is None
        else ports.ai_authorizations.get(g.operation_authorization_id)
    )
    return {
        "generationId": str(g.ai_generation_id.value),
        "operation": g.ai_operation_id.value,
        "status": g.status.value,
        "provider": g.provider,
        "model": g.model,
        "failureCode": g.failure_code,
        "retryOf": None
        if g.retry_of_generation_id is None
        else str(g.retry_of_generation_id.value),
        "authorization": None
        if oa is None
        else {
            "shape": oa.shape.value,
            "requestCase": None if oa.request_case is None else oa.request_case.value,
            "authorizingCommandId": str(oa.authorizing_command_id.value),
            "chainRootCommandId": str(oa.chain_root_command_id.value),
        },
        "requestedAt": g.requested_at.isoformat(),
        "completedAt": None if g.completed_at is None else g.completed_at.isoformat(),
    }


def _status(ports: GovernedPorts, session: Session, op: AIOperationId) -> tuple[str, str | None]:
    sid = session.session_id
    if session.state is not SessionState.ANALYSIS:
        return "NOT_BEGUN", None
    if ports.ai_records.get_accepted_artifact(sid, op) is not None:
        return "ACCEPTED", None
    if op is AIOperationId.AIOP_002 and (
        ports.ai_records.get_accepted_artifact(sid, AIOperationId.AIOP_001) is None
    ):
        return "NOT_RUN", "NO_ACCEPTED_ANALYSIS"
    gens = ports.ai_records.list_session_generations(sid, op)
    if any(g.status in _NON_TERMINAL for g in gens):
        return "RUNNING", None
    latest = ports.ai_authorizations.latest(sid, op)
    if latest is None:
        return "NOT_RUN", None
    carrier = ports.ai_records.get_generation_for_authorization(latest.authorization_id)
    if carrier is None:
        return "PENDING", "AUTHORIZATION_NOT_EXECUTED"
    return "UNAVAILABLE", carrier.failure_code


def _artifact_json(artifact: AIDerivedArtifact, provider: str | None) -> dict[str, object]:
    return {
        "artifactId": str(artifact.ai_derived_artifact_id),
        "generationId": str(artifact.ai_generation_id.value),
        "proofClass": None if artifact.proof_class is None else artifact.proof_class.value,
        "isMockNonProof": artifact.proof_class is ProofClass.MOCK_NON_PROOF,
        "acceptedAt": artifact.created_at.isoformat(),
        "acceptedByCommandId": None
        if artifact.accepted_by_command_id is None
        else str(artifact.accepted_by_command_id.value),
        "marker": marker(provider),
        "content": _refs_to_ids(json.loads(artifact.content)),
    }


def _refs_to_ids(value: Any) -> Any:
    """`question:<uuid>` → `<uuid>`, so the client joins derived items to the
    human Questions it already holds; the text itself is never duplicated."""
    if isinstance(value, dict):
        return {k.replace("question_ref", "question_id"): _refs_to_ids(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_refs_to_ids(v) for v in value]
    if isinstance(value, str) and value.startswith("question:"):
        return value.split(":", 1)[1]
    return value


def analysis_view(ports: GovernedPorts, session: Session, *, visible: bool) -> dict[str, object]:
    if not visible:
        return {"visible": False}
    sid = session.session_id
    records = ports.ai_records
    gens = records.list_session_generations(sid)
    analysis_status, analysis_reason = _status(ports, session, AIOperationId.AIOP_001)
    cluster_status, cluster_reason = _status(ports, session, AIOperationId.AIOP_002)
    analysis_artifact = records.get_accepted_artifact(sid, AIOperationId.AIOP_001)
    cluster_artifact = records.get_accepted_artifact(sid, AIOperationId.AIOP_002)

    def provider_of(artifact: AIDerivedArtifact | None) -> str | None:
        if artifact is None:
            return None
        generation = records.get_generation(artifact.ai_generation_id)
        return None if generation is None else generation.provider

    clusters = [
        {
            "clusterId": str(c.cluster_id),
            "label": c.label,
            "description": c.description,
            "questionIds": [str(q.value) for q in c.question_ids],
            "generationId": str(c.analysis_generation_id.value),
        }
        for c in ports.question_clusters.list_run(sid)
    ]
    providers = {g.provider for g in gens}
    return {
        "visible": True,
        "audience": "FROZEN_SET_AUDIENCE",
        "marker": marker(next(iter(providers)) if len(providers) == 1 else None),
        "analysis": {
            "status": analysis_status,
            "reasonCode": analysis_reason,
            "artifact": None
            if analysis_artifact is None
            else _artifact_json(analysis_artifact, provider_of(analysis_artifact)),
        },
        "clustering": {
            "status": cluster_status,
            "reasonCode": cluster_reason,
            "runId": None
            if cluster_artifact is None
            else str(cluster_artifact.ai_derived_artifact_id),
            "marker": marker(provider_of(cluster_artifact)) if cluster_artifact else None,
            "clusters": clusters,
        },
        "generations": [_generation_json(ports, g) for g in gens],
    }


__all__ = ["analysis_view", "marker"]
