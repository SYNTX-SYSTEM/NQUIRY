"""T5 EVIDENCE TEST: `evidence.evidence_set`/`persistence.evidence_repository`
-- EvidenceSetReference, against real PostgreSQL where noted.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from evidence.evidence_set import (
    EvidenceSetMember,
    EvidenceSetReference,
    compute_evidence_set_fingerprint,
)
from evidence.models import Evidence, EvidenceType, EvidenceValidationState
from persistence.evidence_repository import SqlAlchemyEvidenceRepository
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import EvidenceId, EvidenceSetId, WorkspaceId
from semantic_types.versions import RecordVersion
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()


def _bootstrap(db_connection: sa.Connection, *, email: str) -> WorkspaceId:
    result = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN).seed(
        owner_email=email
    )
    return result.workspace_id


def test_denies_an_empty_evidence_set() -> None:
    """Mandatory-category adversarial attack: Evidence existence
    treated as sufficiency, inverted shape -- an "exact Evidence
    context" naming zero Evidence is not a legitimate consumed set at
    all (09 section 45's own purpose: "Required when a consequential
    operation depends on an exact Evidence context").
    """
    with pytest.raises(ValueError, match="must be non-empty"):
        EvidenceSetReference(
            evidence_set_ref_id=EvidenceSetId(uuid.uuid4()),
            workspace_id=WorkspaceId(uuid.uuid4()),
            consumer_type="RecordHumanDecision",
            consumer_id=None,
            member_evidence_id_and_version_list=(),
            claim_anchor_refs=(),
            created_at=_NOW,
            fingerprint="irrelevant",
        )


def test_fingerprint_is_deterministic_and_order_independent() -> None:
    member_a = EvidenceSetMember(
        evidence_id=EvidenceId(uuid.uuid4()), content_version=RecordVersion(1)
    )
    member_b = EvidenceSetMember(
        evidence_id=EvidenceId(uuid.uuid4()), content_version=RecordVersion(3)
    )

    forward = compute_evidence_set_fingerprint((member_a, member_b))
    backward = compute_evidence_set_fingerprint((member_b, member_a))

    assert forward == backward
    assert len(forward) == 64  # SHA-256 hex digest


def test_fingerprint_changes_when_a_member_version_changes() -> None:
    evidence_id = EvidenceId(uuid.uuid4())
    before = compute_evidence_set_fingerprint(
        (EvidenceSetMember(evidence_id=evidence_id, content_version=RecordVersion(1)),)
    )
    after = compute_evidence_set_fingerprint(
        (EvidenceSetMember(evidence_id=evidence_id, content_version=RecordVersion(2)),)
    )

    assert before != after


def test_evidence_set_reference_round_trip(db_connection: sa.Connection) -> None:
    workspace_id = _bootstrap(db_connection, email="evidence-set-roundtrip@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    evidence = Evidence(
        evidence_id=EvidenceId(_ID_GEN.new_uuid()),
        workspace_id=workspace_id,
        type=EvidenceType.DOMAIN_EVIDENCE,
        content="Users reported drop-off at step 2.",
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
    repo.create_evidence(evidence)
    members = (
        EvidenceSetMember(
            evidence_id=evidence.evidence_id, content_version=evidence.content_version
        ),
    )
    evidence_set = EvidenceSetReference(
        evidence_set_ref_id=EvidenceSetId(_ID_GEN.new_uuid()),
        workspace_id=workspace_id,
        consumer_type="RecordHumanDecision",
        consumer_id=str(uuid.uuid4()),
        member_evidence_id_and_version_list=members,
        claim_anchor_refs=(),
        created_at=_NOW,
        fingerprint=compute_evidence_set_fingerprint(members),
    )

    repo.create_evidence_set_reference(evidence_set)
    fetched = repo.get_evidence_set_reference(evidence_set.evidence_set_ref_id)

    assert fetched == evidence_set


def test_evidence_set_reference_does_not_become_evidence() -> None:
    """09 section 45.2: "EvidenceSetReference does not itself become
    Evidence." Structurally proven: `EvidenceSetReference` has no
    `content`/`validation_state`/`type` field of its own -- it is a
    reference list, not a fact.
    """
    field_names = set(EvidenceSetReference.__dataclass_fields__)
    assert "content" not in field_names
    assert "validation_state" not in field_names
    assert "type" not in field_names
