"""T4 BOUNDARY TEST: BND-014 Commit Evaluator, against real PostgreSQL,
wrapping the real `AuthorityResolver` (PKG-03).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from authority.actor import ActorClass, ActorIdentity
from authority.resolver import AuthorityResolver
from boundaries.bnd_014_commit import Bnd014CommitEvaluator, Bnd014Input
from boundaries.types import BoundaryContext, BoundaryId, BoundaryResult
from evidence.evidence_set import (
    EvidenceSetMember,
    EvidenceSetReference,
    compute_evidence_set_fingerprint,
)
from evidence.freshness import resolve_evidence_set_freshness
from evidence.models import Evidence, EvidenceType, EvidenceValidationState
from governance.authority_binding import AuthorityBindingState, AuthorityClass
from persistence.authority_binding_repository import SqlAlchemyAuthorityBindingRepository
from persistence.evidence_repository import SqlAlchemyEvidenceRepository
from persistence.membership_repository import SqlAlchemyMembershipRepository
from persistence.tables import human_authority_bindings_table
from semantic_types.id_generator import SystemIdGenerator
from semantic_types.ids import CorrelationId, EvidenceId, EvidenceSetId, WorkspaceId
from semantic_types.versions import RecordVersion
from test_support.clock import FixedClock
from test_support.nonproof_bootstrap import NonProofWorkspaceBootstrap

_NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)
_ID_GEN = SystemIdGenerator()


def _context(*, workspace_id: WorkspaceId, actor: ActorIdentity) -> BoundaryContext:
    return BoundaryContext(
        workspace_id=workspace_id,
        operation="CMD_TEST_OPERATION",
        actor=actor,
        correlation_id=CorrelationId(uuid.uuid4()),
        evaluated_at=_NOW,
    )


def _grant(
    connection: sa.Connection,
    *,
    workspace_id: WorkspaceId,
    user_id: uuid.UUID,
    authority_class: AuthorityClass,
) -> None:
    connection.execute(
        sa.insert(human_authority_bindings_table).values(
            id=_ID_GEN.new_uuid(),
            workspace_id=workspace_id.value,
            human_user_id=user_id,
            authority_class=authority_class.value,
            scope_type="WORKSPACE",
            scope_id=workspace_id.value,
            authority_source="LEVEL_1_EXPLICIT",
            granted_by_user_id=user_id,
            granted_at=_NOW,
            state=AuthorityBindingState.ACTIVE.value,
            record_version=1,
        )
    )


def _evaluator(db_connection: sa.Connection) -> Bnd014CommitEvaluator:
    resolver = AuthorityResolver(
        SqlAlchemyMembershipRepository(db_connection),
        SqlAlchemyAuthorityBindingRepository(db_connection),
        FixedClock(_NOW),
    )
    return Bnd014CommitEvaluator(resolver)


def _base_input(
    *, workspace_id: WorkspaceId, context: BoundaryContext, **overrides: object
) -> Bnd014Input:
    kwargs: dict[str, object] = {
        "boundary_id": BoundaryId.BND_014,
        "context": context,
        "required_authority_class": AuthorityClass.SESSION_CONTROL_RIGHT,
        "authority_scope_type": "WORKSPACE",
        "authority_scope_id": workspace_id.value,
        "expected_versions": {"burst-1": RecordVersion(1)},
        "current_versions": {"burst-1": RecordVersion(1)},
        "upstream_chain_result": BoundaryResult.ALLOW,
    }
    kwargs.update(overrides)
    return Bnd014Input(**kwargs)  # type: ignore[arg-type]


def test_allows_when_every_commit_sensitive_predicate_is_current(
    db_connection: sa.Connection,
) -> None:
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd014-allow@nonproof.test")
    _grant(
        db_connection,
        workspace_id=result.workspace_id,
        user_id=result.owner_user_id.value,
        authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
    )
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
    )
    boundary_input = _base_input(workspace_id=result.workspace_id, context=context)

    proof = _evaluator(db_connection).evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.ALLOW
    assert proof.reason_code == "COMMIT_SENSITIVE_PREDICATES_CURRENT"
    assert proof.authority_proof is not None
    assert proof.authority_proof.reason.value == "GRANTED_EFFECTIVE_BINDING"


def test_denies_when_upstream_chain_did_not_allow(db_connection: sa.Connection) -> None:
    """06 section 20 PRECONDITIONS: "Every applicable upstream boundary
    currently allows."
    """
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd014-upstream-deny@nonproof.test")
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
    )
    boundary_input = _base_input(
        workspace_id=result.workspace_id, context=context, upstream_chain_result=BoundaryResult.DENY
    )

    proof = _evaluator(db_connection).evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code.startswith("UPSTREAM_CHAIN_NOT_ALLOW")


def test_denies_a_stale_expected_version(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: state version changed."""
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd014-stale-version@nonproof.test")
    _grant(
        db_connection,
        workspace_id=result.workspace_id,
        user_id=result.owner_user_id.value,
        authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
    )
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
    )
    boundary_input = _base_input(
        workspace_id=result.workspace_id,
        context=context,
        expected_versions={"burst-1": RecordVersion(1)},
        current_versions={"burst-1": RecordVersion(2)},  # competing operation advanced it
    )

    proof = _evaluator(db_connection).evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "STALE_VERSION:burst-1"


def test_denies_a_target_that_no_longer_exists(db_connection: sa.Connection) -> None:
    """Novel/adapted attack: the target ref vanished entirely (current
    version unresolvable) between preparation and commit.
    """
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd014-vanished-target@nonproof.test")
    _grant(
        db_connection,
        workspace_id=result.workspace_id,
        user_id=result.owner_user_id.value,
        authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
    )
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
    )
    boundary_input = _base_input(
        workspace_id=result.workspace_id,
        context=context,
        expected_versions={"burst-1": RecordVersion(1)},
        current_versions={"burst-1": None},
    )

    proof = _evaluator(db_connection).evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "STALE_VERSION:burst-1"


def test_denies_authority_revoked_after_preparation(db_connection: sa.Connection) -> None:
    """Mandatory adversarial attack: authority revoked after
    preparation."""
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd014-revoked@nonproof.test")
    _grant(
        db_connection,
        workspace_id=result.workspace_id,
        user_id=result.owner_user_id.value,
        authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
    )
    db_connection.execute(
        sa.update(human_authority_bindings_table)
        .where(human_authority_bindings_table.c.human_user_id == result.owner_user_id.value)
        .values(
            state=AuthorityBindingState.REVOKED.value,
            revoked_at=_NOW,
            revoked_by_user_id=result.owner_user_id.value,
        )
    )
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
    )
    boundary_input = _base_input(workspace_id=result.workspace_id, context=context)

    proof = _evaluator(db_connection).evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code.startswith("AUTHORITY_NOT_CURRENT")


def test_denies_a_never_granted_authority(db_connection: sa.Connection) -> None:
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd014-never-granted@nonproof.test")
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
    )
    boundary_input = _base_input(workspace_id=result.workspace_id, context=context)

    proof = _evaluator(db_connection).evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "AUTHORITY_NOT_CURRENT:DENIED_NO_MATCHING_BINDING"


def _seed_fresh_evidence_set(
    db_connection: sa.Connection, *, workspace_id: WorkspaceId
) -> EvidenceSetReference:
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
    return evidence_set


def test_allows_when_evidence_freshness_is_current(db_connection: sa.Connection) -> None:
    """PKG-17: 09 section 114's commit-freshness linkage, positive
    control."""
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd014-evidence-fresh@nonproof.test")
    _grant(
        db_connection,
        workspace_id=result.workspace_id,
        user_id=result.owner_user_id.value,
        authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
    )
    evidence_set = _seed_fresh_evidence_set(db_connection, workspace_id=result.workspace_id)
    freshness = resolve_evidence_set_freshness(
        evidence_set.evidence_set_ref_id,
        workspace_id=result.workspace_id,
        reader=SqlAlchemyEvidenceRepository(db_connection),
    )
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
    )
    boundary_input = _base_input(
        workspace_id=result.workspace_id, context=context, evidence_freshness=freshness
    )

    proof = _evaluator(db_connection).evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.ALLOW
    assert proof.evidence_proof_refs == (str(evidence_set.evidence_set_ref_id.value),)


def test_denies_evidence_invalidated_between_prepare_and_commit(
    db_connection: sa.Connection,
) -> None:
    """Mandatory package-specific attack: Evidence invalidated after
    prepare, proven at the exact commit-time gate 09 section 114
    assigns this check to (BND-014), not merely at BND-013."""
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd014-evidence-invalidated@nonproof.test")
    _grant(
        db_connection,
        workspace_id=result.workspace_id,
        user_id=result.owner_user_id.value,
        authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
    )
    evidence_set = _seed_fresh_evidence_set(db_connection, workspace_id=result.workspace_id)
    evidence_repo = SqlAlchemyEvidenceRepository(db_connection)
    # Evaluated fresh at "prepare" time...
    freshness_at_prepare = resolve_evidence_set_freshness(
        evidence_set.evidence_set_ref_id, workspace_id=result.workspace_id, reader=evidence_repo
    )
    assert freshness_at_prepare.is_fresh
    # ...but invalidated before this commit attempt re-resolves it.
    member = evidence_set.member_evidence_id_and_version_list[0]
    evidence_repo.update_validation_state(
        evidence_id=member.evidence_id,
        workspace_id=result.workspace_id,
        expected_record_version=RecordVersion.initial(),
        new_state=EvidenceValidationState.INVALIDATED,
    )
    freshness_at_commit = resolve_evidence_set_freshness(
        evidence_set.evidence_set_ref_id, workspace_id=result.workspace_id, reader=evidence_repo
    )
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
    )
    boundary_input = _base_input(
        workspace_id=result.workspace_id, context=context, evidence_freshness=freshness_at_commit
    )

    proof = _evaluator(db_connection).evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code.startswith("STALE_EVIDENCE:")
    assert "INVALIDATED" in proof.reason_code


def test_denies_when_the_evidence_set_vanished_before_commit(db_connection: sa.Connection) -> None:
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd014-evidence-vanished@nonproof.test")
    _grant(
        db_connection,
        workspace_id=result.workspace_id,
        user_id=result.owner_user_id.value,
        authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
    )
    phantom_ref = EvidenceSetId(uuid.uuid4())
    freshness = resolve_evidence_set_freshness(
        phantom_ref,
        workspace_id=result.workspace_id,
        reader=SqlAlchemyEvidenceRepository(db_connection),
    )
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
    )
    boundary_input = _base_input(
        workspace_id=result.workspace_id, context=context, evidence_freshness=freshness
    )

    proof = _evaluator(db_connection).evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code == "EVIDENCE_SET_NOT_FOUND"


def test_evidence_freshness_check_runs_before_authority_resolution(
    db_connection: sa.Connection,
) -> None:
    """Novel/adapted attack: prove stale Evidence is caught even when
    authority itself would otherwise ALLOW -- neither check can mask
    the other."""
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd014-evidence-before-authority@nonproof.test")
    # Deliberately no authority grant at all -- if evidence freshness
    # did not run first, this would still DENY, but for the wrong
    # reason; asserting the specific STALE_EVIDENCE code proves ordering.
    evidence_set = _seed_fresh_evidence_set(db_connection, workspace_id=result.workspace_id)
    evidence_repo = SqlAlchemyEvidenceRepository(db_connection)
    member = evidence_set.member_evidence_id_and_version_list[0]
    evidence_repo.update_validation_state(
        evidence_id=member.evidence_id,
        workspace_id=result.workspace_id,
        expected_record_version=RecordVersion.initial(),
        new_state=EvidenceValidationState.UNAVAILABLE,
    )
    freshness = resolve_evidence_set_freshness(
        evidence_set.evidence_set_ref_id, workspace_id=result.workspace_id, reader=evidence_repo
    )
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
    )
    boundary_input = _base_input(
        workspace_id=result.workspace_id, context=context, evidence_freshness=freshness
    )

    proof = _evaluator(db_connection).evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.DENY
    assert proof.reason_code.startswith("STALE_EVIDENCE:")
    assert proof.authority_proof is None


def test_allows_an_operation_with_no_targets_at_all(db_connection: sa.Connection) -> None:
    """Positive control: a creation-style operation with no pre-existing
    target has nothing to check versions for -- not vacuously denied.
    """
    bootstrap = NonProofWorkspaceBootstrap(db_connection, FixedClock(_NOW), _ID_GEN)
    result = bootstrap.seed(owner_email="bnd014-no-targets@nonproof.test")
    _grant(
        db_connection,
        workspace_id=result.workspace_id,
        user_id=result.owner_user_id.value,
        authority_class=AuthorityClass.SESSION_CONTROL_RIGHT,
    )
    context = _context(
        workspace_id=result.workspace_id,
        actor=ActorIdentity(ActorClass.HUMAN_USER, result.owner_user_id),
    )
    boundary_input = _base_input(
        workspace_id=result.workspace_id, context=context, expected_versions={}, current_versions={}
    )

    proof = _evaluator(db_connection).evaluate(boundary_input, context)

    assert proof.result is BoundaryResult.ALLOW
