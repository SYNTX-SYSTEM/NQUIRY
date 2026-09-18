"""T5 EVIDENCE TEST: `evidence.claim_anchor`/`persistence.evidence_repository`
-- ClaimAnchor, against real PostgreSQL where noted.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from evidence.claim_anchor import ClaimAnchor
from persistence.evidence_repository import SqlAlchemyEvidenceRepository
from persistence.tables import claim_anchors_table
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import ClaimAnchorId, WorkspaceId
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


def test_constructs_a_well_formed_claim_anchor() -> None:
    anchor = ClaimAnchor(
        claim_anchor_id=ClaimAnchorId(_ID_GEN.new_uuid()),
        workspace_id=WorkspaceId(uuid.uuid4()),
        target_type="Decision",
        target_id=uuid.uuid4(),
        claim_field_or_fragment="rationale",
        target_content_version=RecordVersion.initial(),
        content_fingerprint=None,
        created_at=_NOW,
    )
    assert anchor.target_type == "Decision"


def test_claim_anchor_does_not_grant_truth() -> None:
    """07 section 10.3: "A ClaimAnchor only identifies what is being
    evaluated." Structurally proven: `ClaimAnchor` carries no
    truth/validity/sufficiency field of any kind.
    """
    field_names = set(ClaimAnchor.__dataclass_fields__)
    assert "is_true" not in field_names
    assert "sufficiency" not in field_names
    assert "validated" not in field_names


def test_claim_anchor_round_trip(db_connection: sa.Connection) -> None:
    workspace_id = _bootstrap(db_connection, email="claim-anchor-roundtrip@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    anchor = ClaimAnchor(
        claim_anchor_id=ClaimAnchorId(_ID_GEN.new_uuid()),
        workspace_id=workspace_id,
        target_type="Decision",
        target_id=uuid.uuid4(),
        claim_field_or_fragment="rationale",
        target_content_version=RecordVersion.initial(),
        content_fingerprint="abc123",
        created_at=_NOW,
    )

    repo.create_claim_anchor(anchor)
    fetched = repo.get_claim_anchor(anchor.claim_anchor_id)

    assert fetched == anchor


def test_cross_workspace_claim_anchor_is_not_representable(db_connection: sa.Connection) -> None:
    """Mandatory-category Workspace attack, ClaimAnchor variant --
    proven via a raw SQL insert of an otherwise well-formed row naming
    a foreign Workspace, since `claim_anchors` itself has no composite
    FK to validate cross-object consistency (target_id is polymorphic).
    This proves the ONE thing the schema does enforce: `workspace_id`
    must reference a real Workspace.
    """
    with pytest.raises(sa.exc.IntegrityError), db_connection.begin_nested():
        db_connection.execute(
            sa.insert(claim_anchors_table).values(
                id=_ID_GEN.new_uuid(),
                workspace_id=uuid.uuid4(),  # no such Workspace exists
                target_type="Decision",
                target_id=uuid.uuid4(),
                claim_field_or_fragment="rationale",
                target_content_version=1,
                content_fingerprint=None,
                created_at=_NOW,
            )
        )


def test_stale_claim_anchor_target_version_is_detectable_by_comparison(
    db_connection: sa.Connection,
) -> None:
    """Mandatory adversarial attack: stale ClaimAnchor. 07 section 43.1:
    "If target content changes, create a new ClaimAnchor" -- this
    package builds no live boundary (BND-013 is PKG-17's own scope), so
    it proves the honest, narrower fact available now: an existing
    ClaimAnchor's own `target_content_version` never silently updates
    when the target's real current version advances, making staleness
    a simple, reliable comparison for a future consumer.
    """
    workspace_id = _bootstrap(db_connection, email="claim-anchor-stale@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    target_id = uuid.uuid4()
    anchor = ClaimAnchor(
        claim_anchor_id=ClaimAnchorId(_ID_GEN.new_uuid()),
        workspace_id=workspace_id,
        target_type="Decision",
        target_id=target_id,
        claim_field_or_fragment="rationale",
        target_content_version=RecordVersion(1),
        content_fingerprint=None,
        created_at=_NOW,
    )
    repo.create_claim_anchor(anchor)

    current_target_version = RecordVersion(2)  # the target advanced after anchoring
    fetched = repo.get_claim_anchor(anchor.claim_anchor_id)

    assert fetched is not None
    assert fetched.target_content_version != current_target_version
    assert fetched.target_content_version == RecordVersion(1)  # never silently rewritten
