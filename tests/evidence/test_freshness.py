"""T5 EVIDENCE TEST: `evidence.freshness` -- the Evidence proof
resolver, against real PostgreSQL. `SqlAlchemyEvidenceRepository`
(PKG-16, extended this package with `find_superseding_evidence_id`)
already satisfies `EvidenceFreshnessPort` structurally -- no adapter
needed.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from evidence.claim_anchor import ClaimAnchor
from evidence.evidence_set import (
    EvidenceSetMember,
    EvidenceSetReference,
    compute_evidence_set_fingerprint,
)
from evidence.freshness import (
    ClaimAnchorFreshness,
    EvidenceMemberFreshness,
    resolve_evidence_relation_freshness,
    resolve_evidence_set_freshness,
)
from evidence.models import Evidence, EvidenceType, EvidenceValidationState
from persistence.evidence_repository import SqlAlchemyEvidenceRepository
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import ClaimAnchorId, EvidenceId, EvidenceSetId, WorkspaceId
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


def _make_evidence(*, workspace_id: WorkspaceId, **overrides: object) -> Evidence:
    fields: dict[str, object] = dict(
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
    fields.update(overrides)
    return Evidence(**fields)  # type: ignore[arg-type]


def _make_set(
    *,
    workspace_id: WorkspaceId,
    members: tuple[EvidenceSetMember, ...],
    claim_anchor_refs: tuple[ClaimAnchorId, ...] = (),
) -> EvidenceSetReference:
    return EvidenceSetReference(
        evidence_set_ref_id=EvidenceSetId(_ID_GEN.new_uuid()),
        workspace_id=workspace_id,
        consumer_type="RecordHumanDecision",
        consumer_id=str(uuid.uuid4()),
        member_evidence_id_and_version_list=members,
        claim_anchor_refs=claim_anchor_refs,
        created_at=_NOW,
        fingerprint=compute_evidence_set_fingerprint(members),
    )


def test_a_fully_current_set_resolves_as_fresh(db_connection: sa.Connection) -> None:
    workspace_id = _bootstrap(db_connection, email="freshness-fresh@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    evidence = _make_evidence(workspace_id=workspace_id)
    repo.create_evidence(evidence)
    evidence_set = _make_set(
        workspace_id=workspace_id,
        members=(
            EvidenceSetMember(
                evidence_id=evidence.evidence_id, content_version=evidence.content_version
            ),
        ),
    )
    repo.create_evidence_set_reference(evidence_set)

    result = resolve_evidence_set_freshness(
        evidence_set.evidence_set_ref_id, workspace_id=workspace_id, reader=repo
    )

    assert result.is_fresh
    assert result.stale_refs == ()
    assert len(result.members) == 1
    assert result.members[0].outcome is EvidenceMemberFreshness.FRESH


def test_a_missing_evidence_set_is_not_fresh(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: forged/vanished set ref."""
    workspace_id = _bootstrap(db_connection, email="freshness-missing-set@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)

    result = resolve_evidence_set_freshness(
        EvidenceSetId(uuid.uuid4()), workspace_id=workspace_id, reader=repo
    )

    assert result.evidence_set_found is False
    assert result.is_fresh is False


def test_an_invalidated_member_after_prepare_is_stale(db_connection: sa.Connection) -> None:
    """Mandatory package-specific attack: Evidence invalidated after
    prepare."""
    workspace_id = _bootstrap(db_connection, email="freshness-invalidated@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    evidence = _make_evidence(workspace_id=workspace_id)
    repo.create_evidence(evidence)
    evidence_set = _make_set(
        workspace_id=workspace_id,
        members=(
            EvidenceSetMember(
                evidence_id=evidence.evidence_id, content_version=evidence.content_version
            ),
        ),
    )
    repo.create_evidence_set_reference(evidence_set)

    # "Prepare" happened above; now Evidence is invalidated before commit.
    repo.update_validation_state(
        evidence_id=evidence.evidence_id,
        workspace_id=workspace_id,
        expected_record_version=evidence.record_version,
        new_state=EvidenceValidationState.INVALIDATED,
    )

    result = resolve_evidence_set_freshness(
        evidence_set.evidence_set_ref_id, workspace_id=workspace_id, reader=repo
    )

    assert result.is_fresh is False
    assert result.members[0].outcome is EvidenceMemberFreshness.INVALIDATED
    assert result.stale_refs == (f"evidence:{evidence.evidence_id.value}:INVALIDATED",)


def test_an_unavailable_member_after_prepare_is_stale(db_connection: sa.Connection) -> None:
    """Mandatory package-specific attack: Evidence unavailable after
    prepare."""
    workspace_id = _bootstrap(db_connection, email="freshness-unavailable@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    evidence = _make_evidence(workspace_id=workspace_id)
    repo.create_evidence(evidence)
    evidence_set = _make_set(
        workspace_id=workspace_id,
        members=(
            EvidenceSetMember(
                evidence_id=evidence.evidence_id, content_version=evidence.content_version
            ),
        ),
    )
    repo.create_evidence_set_reference(evidence_set)
    repo.update_validation_state(
        evidence_id=evidence.evidence_id,
        workspace_id=workspace_id,
        expected_record_version=evidence.record_version,
        new_state=EvidenceValidationState.UNAVAILABLE,
    )

    result = resolve_evidence_set_freshness(
        evidence_set.evidence_set_ref_id, workspace_id=workspace_id, reader=repo
    )

    assert result.members[0].outcome is EvidenceMemberFreshness.UNAVAILABLE
    assert result.is_fresh is False


def test_a_cross_workspace_member_is_stale(db_connection: sa.Connection) -> None:
    """Mandatory package-specific attack: cross-Workspace Evidence.
    Constructs the set with a claimed workspace that does not match the
    Evidence row's real workspace -- proving the check compares against
    the CALLER's own asserted scope, not merely the set's own recorded
    workspace_id.
    """
    workspace_a = _bootstrap(db_connection, email="freshness-cross-a@nonproof.test")
    workspace_b = _bootstrap(db_connection, email="freshness-cross-b@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    evidence = _make_evidence(workspace_id=workspace_a)
    repo.create_evidence(evidence)
    evidence_set = _make_set(
        workspace_id=workspace_a,
        members=(
            EvidenceSetMember(
                evidence_id=evidence.evidence_id, content_version=evidence.content_version
            ),
        ),
    )
    repo.create_evidence_set_reference(evidence_set)

    result = resolve_evidence_set_freshness(
        evidence_set.evidence_set_ref_id, workspace_id=workspace_b, reader=repo
    )

    assert result.members[0].outcome is EvidenceMemberFreshness.WRONG_WORKSPACE
    assert result.is_fresh is False


def test_a_member_evidence_id_that_no_longer_resolves_is_stale(
    db_connection: sa.Connection,
) -> None:
    """Mandatory package-specific attack: set membership changed --
    modeled here as a member whose Evidence row is unresolvable (the
    only way membership content can appear to change, since
    `EvidenceSetReference` itself has no update method)."""
    workspace_id = _bootstrap(db_connection, email="freshness-member-vanished@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    phantom_id = EvidenceId(uuid.uuid4())
    evidence_set = _make_set(
        workspace_id=workspace_id,
        members=(
            EvidenceSetMember(evidence_id=phantom_id, content_version=RecordVersion.initial()),
        ),
    )
    repo.create_evidence_set_reference(evidence_set)

    result = resolve_evidence_set_freshness(
        evidence_set.evidence_set_ref_id, workspace_id=workspace_id, reader=repo
    )

    assert result.members[0].outcome is EvidenceMemberFreshness.MEMBER_NOT_FOUND
    assert result.is_fresh is False


def test_a_superseded_member_is_stale(db_connection: sa.Connection) -> None:
    """09 section 114: "superseded where current use requires newer
    version"."""
    workspace_id = _bootstrap(db_connection, email="freshness-superseded@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    original = _make_evidence(workspace_id=workspace_id)
    repo.create_evidence(original)
    evidence_set = _make_set(
        workspace_id=workspace_id,
        members=(
            EvidenceSetMember(
                evidence_id=original.evidence_id, content_version=original.content_version
            ),
        ),
    )
    repo.create_evidence_set_reference(evidence_set)

    successor = _make_evidence(
        workspace_id=workspace_id, supersedes_evidence_id=original.evidence_id
    )
    repo.create_evidence(successor)

    result = resolve_evidence_set_freshness(
        evidence_set.evidence_set_ref_id, workspace_id=workspace_id, reader=repo
    )

    assert result.members[0].outcome is EvidenceMemberFreshness.SUPERSEDED
    assert result.is_fresh is False


def test_a_tampered_recorded_content_version_is_detected(db_connection: sa.Connection) -> None:
    """Defense-in-depth: `content_version` is immutable on a real
    Evidence row (AC-07-001, PKG-16's own trigger), so this can only
    arise from a corrupted/fabricated set reference -- proven directly
    by constructing one that does not match reality.
    """
    workspace_id = _bootstrap(db_connection, email="freshness-tampered@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    evidence = _make_evidence(workspace_id=workspace_id)
    repo.create_evidence(evidence)
    tampered_set = _make_set(
        workspace_id=workspace_id,
        members=(
            EvidenceSetMember(evidence_id=evidence.evidence_id, content_version=RecordVersion(99)),
        ),
    )
    repo.create_evidence_set_reference(tampered_set)

    result = resolve_evidence_set_freshness(
        tampered_set.evidence_set_ref_id, workspace_id=workspace_id, reader=repo
    )

    assert result.members[0].outcome is EvidenceMemberFreshness.CONTENT_VERSION_CHANGED
    assert result.is_fresh is False


def test_a_missing_claim_anchor_is_stale(db_connection: sa.Connection) -> None:
    workspace_id = _bootstrap(db_connection, email="freshness-anchor-missing@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    evidence = _make_evidence(workspace_id=workspace_id)
    repo.create_evidence(evidence)
    phantom_anchor = ClaimAnchorId(uuid.uuid4())
    evidence_set = _make_set(
        workspace_id=workspace_id,
        members=(
            EvidenceSetMember(
                evidence_id=evidence.evidence_id, content_version=evidence.content_version
            ),
        ),
        claim_anchor_refs=(phantom_anchor,),
    )
    repo.create_evidence_set_reference(evidence_set)

    result = resolve_evidence_set_freshness(
        evidence_set.evidence_set_ref_id, workspace_id=workspace_id, reader=repo
    )

    assert result.claim_anchors[0].outcome is ClaimAnchorFreshness.CLAIM_ANCHOR_NOT_FOUND
    assert result.is_fresh is False


def test_claim_anchor_target_drift_is_detected_when_current_version_supplied(
    db_connection: sa.Connection,
) -> None:
    """Mandatory package-specific attack: stale source/ClaimAnchor
    version where required."""
    workspace_id = _bootstrap(db_connection, email="freshness-anchor-drift@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    evidence = _make_evidence(workspace_id=workspace_id)
    repo.create_evidence(evidence)
    anchor = ClaimAnchor(
        claim_anchor_id=ClaimAnchorId(_ID_GEN.new_uuid()),
        workspace_id=workspace_id,
        target_type="Decision",
        target_id=uuid.uuid4(),
        claim_field_or_fragment="rationale",
        target_content_version=RecordVersion.initial(),
        content_fingerprint=None,
        created_at=_NOW,
    )
    repo.create_claim_anchor(anchor)
    evidence_set = _make_set(
        workspace_id=workspace_id,
        members=(
            EvidenceSetMember(
                evidence_id=evidence.evidence_id, content_version=evidence.content_version
            ),
        ),
        claim_anchor_refs=(anchor.claim_anchor_id,),
    )
    repo.create_evidence_set_reference(evidence_set)

    result = resolve_evidence_set_freshness(
        evidence_set.evidence_set_ref_id,
        workspace_id=workspace_id,
        reader=repo,
        current_target_versions={anchor.claim_anchor_id: RecordVersion(2)},  # target moved on
    )

    assert result.claim_anchors[0].outcome is ClaimAnchorFreshness.TARGET_VERSION_DRIFTED
    assert result.is_fresh is False


def test_claim_anchor_drift_not_checked_without_a_supplied_current_version(
    db_connection: sa.Connection,
) -> None:
    """Honest disclosure (KNOWN_LIMITATION): with no concrete Command
    wiring a target-version lookup yet, an anchor whose drift cannot be
    checked is not silently assumed stale -- only its own continued
    existence is required.
    """
    workspace_id = _bootstrap(db_connection, email="freshness-anchor-no-check@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    evidence = _make_evidence(workspace_id=workspace_id)
    repo.create_evidence(evidence)
    anchor = ClaimAnchor(
        claim_anchor_id=ClaimAnchorId(_ID_GEN.new_uuid()),
        workspace_id=workspace_id,
        target_type="Decision",
        target_id=uuid.uuid4(),
        claim_field_or_fragment="rationale",
        target_content_version=RecordVersion.initial(),
        content_fingerprint=None,
        created_at=_NOW,
    )
    repo.create_claim_anchor(anchor)
    evidence_set = _make_set(
        workspace_id=workspace_id,
        members=(
            EvidenceSetMember(
                evidence_id=evidence.evidence_id, content_version=evidence.content_version
            ),
        ),
        claim_anchor_refs=(anchor.claim_anchor_id,),
    )
    repo.create_evidence_set_reference(evidence_set)

    result = resolve_evidence_set_freshness(
        evidence_set.evidence_set_ref_id, workspace_id=workspace_id, reader=repo
    )

    assert result.claim_anchors[0].outcome is ClaimAnchorFreshness.CURRENT
    assert result.is_fresh is True


def test_evidence_relation_freshness_detects_a_superseded_relation_target(
    db_connection: sa.Connection,
) -> None:
    """Mandatory package-specific attack: EvidenceRelation changed. 09
    section 116: "An EvidenceRelation references exact Evidence content
    version... If either changes: relation remains historical."
    """
    workspace_id = _bootstrap(db_connection, email="freshness-relation-changed@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    original = _make_evidence(workspace_id=workspace_id)
    repo.create_evidence(original)
    successor = _make_evidence(
        workspace_id=workspace_id, supersedes_evidence_id=original.evidence_id
    )
    repo.create_evidence(successor)

    outcome = resolve_evidence_relation_freshness(
        evidence_id=original.evidence_id,
        evidence_content_version=original.content_version,
        workspace_id=workspace_id,
        reader=repo,
    )

    assert outcome is EvidenceMemberFreshness.SUPERSEDED


def test_evidence_relation_freshness_is_fresh_for_an_unchanged_target(
    db_connection: sa.Connection,
) -> None:
    workspace_id = _bootstrap(db_connection, email="freshness-relation-fresh@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    evidence = _make_evidence(workspace_id=workspace_id)
    repo.create_evidence(evidence)

    outcome = resolve_evidence_relation_freshness(
        evidence_id=evidence.evidence_id,
        evidence_content_version=evidence.content_version,
        workspace_id=workspace_id,
        reader=repo,
    )

    assert outcome is EvidenceMemberFreshness.FRESH


def test_stale_refs_are_sorted_and_carry_a_stable_prefix(db_connection: sa.Connection) -> None:
    """Positive control on the pure `stale_refs`/`is_fresh` properties
    themselves, proven not vacuously strict against a real multi-member
    set with a mix of fresh and stale outcomes."""
    workspace_id = _bootstrap(db_connection, email="freshness-mixed@nonproof.test")
    repo = SqlAlchemyEvidenceRepository(db_connection)
    fresh_evidence = _make_evidence(workspace_id=workspace_id)
    stale_evidence = _make_evidence(workspace_id=workspace_id)
    repo.create_evidence(fresh_evidence)
    repo.create_evidence(stale_evidence)
    repo.update_validation_state(
        evidence_id=stale_evidence.evidence_id,
        workspace_id=workspace_id,
        expected_record_version=stale_evidence.record_version,
        new_state=EvidenceValidationState.INVALIDATED,
    )
    evidence_set = _make_set(
        workspace_id=workspace_id,
        members=(
            EvidenceSetMember(
                evidence_id=fresh_evidence.evidence_id,
                content_version=fresh_evidence.content_version,
            ),
            EvidenceSetMember(
                evidence_id=stale_evidence.evidence_id,
                content_version=stale_evidence.content_version,
            ),
        ),
    )
    repo.create_evidence_set_reference(evidence_set)

    result = resolve_evidence_set_freshness(
        evidence_set.evidence_set_ref_id, workspace_id=workspace_id, reader=repo
    )

    assert result.is_fresh is False
    assert result.stale_refs == (f"evidence:{stale_evidence.evidence_id.value}:INVALIDATED",)
