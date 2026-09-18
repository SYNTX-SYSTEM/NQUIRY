"""T5 EVIDENCE TEST: `evidence.provenance` -- ProvenanceEnvelope
reconstruction. Pure Python, no database required.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from evidence.models import (
    Evidence,
    EvidenceType,
    EvidenceValidationState,
    ProvenanceOrigin,
    SourceReference,
)
from evidence.provenance import build_evidence_provenance_envelope
from semantic_types.ids import EvidenceId, SourceReferenceId, UserId, WorkspaceId
from semantic_types.versions import RecordVersion

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)


def _base_evidence(**overrides: object) -> Evidence:
    fields: dict[str, object] = dict(
        evidence_id=EvidenceId(uuid.uuid4()),
        workspace_id=WorkspaceId(uuid.uuid4()),
        type=EvidenceType.DOMAIN_EVIDENCE,
        content="a captured claim",
        source_reference_id=None,
        human_source_user_id=None,
        reliability=None,
        captured_at=_NOW,
        validation_state=EvidenceValidationState.UNVALIDATED,
        content_version=RecordVersion.initial(),
        record_version=RecordVersion.initial(),
        supersedes_evidence_id=None,
        provenance_ref=None,
    )
    fields.update(overrides)
    return Evidence(**fields)  # type: ignore[arg-type]


def test_human_sourced_evidence_reconstructs_human_origin() -> None:
    user_id = UserId(uuid.uuid4())
    evidence = _base_evidence(human_source_user_id=user_id)

    envelope = build_evidence_provenance_envelope(evidence)

    assert envelope.origin is ProvenanceOrigin.HUMAN
    assert envelope.producer_ref == str(user_id.value)
    assert envelope.target_artifact_id == evidence.evidence_id
    assert envelope.artifact_version == evidence.content_version


def test_system_derived_evidence_reconstructs_system_origin_when_no_source() -> None:
    """07 section 24: `system-derived` applies to "operational/proof
    artifacts where origin is deterministic System computation" --
    exercised here for `SYSTEM_PROOF` typed Evidence with neither a
    human source nor an external SourceReference.
    """
    evidence = _base_evidence(type=EvidenceType.SYSTEM_PROOF)

    envelope = build_evidence_provenance_envelope(evidence)

    assert envelope.origin is ProvenanceOrigin.SYSTEM_DERIVED
    assert envelope.producer_ref == "SYSTEM_PROOF"


def test_source_referenced_evidence_reconstructs_source_origin() -> None:
    source = SourceReference(
        source_reference_id=SourceReferenceId(uuid.uuid4()),
        workspace_id=WorkspaceId(uuid.uuid4()),
        source_type="interview",
        locator="transcript-1",
        external_id=None,
        title=None,
        retrieved_at=_NOW,
        source_published_at=None,
        content_fingerprint="fp-1",
        snapshot_ref=None,
        created_by_ref="import-process-1",
        origin=ProvenanceOrigin.IMPORTED,
        validation_status="RESOLVED",
        created_at=_NOW,
        record_version=RecordVersion.initial(),
    )
    evidence = _base_evidence(source_reference_id=source.source_reference_id)

    envelope = build_evidence_provenance_envelope(evidence, source_reference=source)

    assert envelope.origin is ProvenanceOrigin.IMPORTED
    assert envelope.producer_ref == "import-process-1"
    assert envelope.source_version_ref == "fp-1"
    assert envelope.source_reference_id == source.source_reference_id


def test_envelope_carries_supersession_reference() -> None:
    prior_id = EvidenceId(uuid.uuid4())
    evidence = _base_evidence(supersedes_evidence_id=prior_id)

    envelope = build_evidence_provenance_envelope(evidence)

    assert envelope.supersession_ref == prior_id


def test_envelope_discloses_unbuilt_dimensions_honestly() -> None:
    """No AIGeneration/method-version/consumption infrastructure exists
    yet -- these dimensions must be honestly empty, not fabricated.
    """
    evidence = _base_evidence()

    envelope = build_evidence_provenance_envelope(evidence)

    assert envelope.ai_generation_id is None
    assert envelope.method_version_ref is None
    assert envelope.consumption_refs == ()
