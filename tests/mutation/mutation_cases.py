"""MUTATIONS: the ten mandatory PKG-31 mutations (14 §46 OBJECTIVE:
"deliberately removes BND-014, trusts cached authority, removes
Workspace check, treats AI recommendation as Decision, enables direct
DB write, treats Event as Command, accepts stale Evidence, enables
INDETERMINATE retry, enables admin fallback and bypasses AI Gateway").

TEST ONLY. Never imported by production code -- same import-graph
guard as every other file under `tests/`.

Every `target_test_nodeids` entry below names a real, pre-existing
test file/function this package did not write (all landed in PKG-01
through PKG-30). This module writes zero new assertions; it only
supplies the ten `setattr` seams and the pre-existing node ids each is
expected to turn red -- see `harness.py`'s own module docstring for
why that is deliberate, not an oversight.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Protocol
from uuid import UUID

from authority.resolver import (
    AuthorityRequest,
    AuthorityResolution,
    AuthorityResolver,
    AuthorityVerdict,
    ResolutionReason,
)
from boundaries.bnd_001_identity import Bnd001IdentityEvaluator, Bnd001Input
from boundaries.bnd_002_workspace import Bnd002Input, Bnd002WorkspaceEvaluator
from boundaries.bnd_014_commit import Bnd014CommitEvaluator, Bnd014Input
from boundaries.bnd_017_failure_indeterminate import (
    Bnd017FailureIndeterminateEvaluator,
    Bnd017Input,
)
from boundaries.types import BoundaryContext, BoundaryId, BoundaryProof, BoundaryResult
from check_provider_sdk_imports import Violation
from command.envelope import CommandEnvelope
from commit.coordinator import CommitOutcome, CommitUnit
from evidence.freshness import EvidenceFreshnessPort, EvidenceMemberFreshness
from harness import MutationCase, MutationPatch
from semantic_types.ids import CommitId, EvidenceId, UserId, WorkspaceId
from semantic_types.versions import ContractVersion, RecordVersion


class _MutationExecutorLike(Protocol):
    def apply(self) -> object: ...


def _forced_allow_proof(
    evaluator_boundary_id: BoundaryId, context: BoundaryContext, reason_code: str
) -> BoundaryProof:
    return BoundaryProof(
        boundary_id=evaluator_boundary_id,
        boundary_version=ContractVersion("1.0"),
        result=BoundaryResult.ALLOW,
        reason_code=reason_code,
        workspace_id=context.workspace_id,
        actor=context.actor,
        input_refs=(),
        authoritative_version_refs=(),
        authority_proof=None,
        evidence_proof_refs=(),
        evaluated_at=context.evaluated_at,
        correlation_id=context.correlation_id,
    )


# ---------------------------------------------------------------------------
# MUT-PKG31-01: BND-014 removed (commit-time boundary forced ALLOW)
# ---------------------------------------------------------------------------


def _mut01_bnd014_always_allows(
    _original: Callable[[Bnd014CommitEvaluator, Bnd014Input, BoundaryContext], BoundaryProof],
) -> Callable[[Bnd014CommitEvaluator, Bnd014Input, BoundaryContext], BoundaryProof]:
    def _evaluate(
        self: Bnd014CommitEvaluator, boundary_input: Bnd014Input, context: BoundaryContext
    ) -> BoundaryProof:
        return _forced_allow_proof(self.boundary_id, context, "MUT_PKG31_01_BND014_DISABLED")

    return _evaluate


MUT_PKG31_01 = MutationCase(
    mutation_id="MUT-PKG31-01",
    invariant="BND-014 evaluates expected/current versions, upstream chain result and "
    "evidence freshness before any commit; removing it must let a stale-version or "
    "already-denied commit through unchecked.",
    expected_boundary="BND_014",
    patch=MutationPatch(
        target_module="boundaries.bnd_014_commit",
        target_qualname="Bnd014CommitEvaluator.evaluate",
        replacement_factory=_mut01_bnd014_always_allows,  # type: ignore[arg-type]
    ),
    target_test_nodeids=(
        "tests/boundaries/test_bnd_014_commit.py::test_denies_a_stale_expected_version",
        "tests/command_commit_event/test_commit.py::test_commit_denies_when_state_version_changed",
    ),
)


# ---------------------------------------------------------------------------
# MUT-PKG31-02: trust cached authority (resolver memoizes first verdict)
# ---------------------------------------------------------------------------


def _mut02_authority_resolver_caches(
    original: Callable[[AuthorityResolver, AuthorityRequest], AuthorityResolution],
) -> Callable[[AuthorityResolver, AuthorityRequest], AuthorityResolution]:
    cache: dict[tuple[UUID, UserId, str, UUID], AuthorityResolution] = {}

    def _resolve(self: AuthorityResolver, request: AuthorityRequest) -> AuthorityResolution:
        key = (
            request.workspace_id.value,
            request.actor.user_id,
            request.scope_type,
            request.scope_id,
        )
        if key in cache:
            return cache[key]
        result = original(self, request)
        cache[key] = result
        return result

    return _resolve


MUT_PKG31_02 = MutationCase(
    mutation_id="MUT-PKG31-02",
    invariant="AuthorityResolver.resolve() never caches -- every call re-reads current "
    "membership/binding state (14 section 16: commit-time resolver reloads current "
    "authoritative state). Caching the first verdict lets a later revocation be invisible "
    "to a second resolution that reuses the stale, still-GRANTED answer.",
    expected_boundary="BND_005",
    patch=MutationPatch(
        target_module="authority.resolver",
        target_qualname="AuthorityResolver.resolve",
        replacement_factory=_mut02_authority_resolver_caches,  # type: ignore[arg-type]
    ),
    target_test_nodeids=(
        "tests/authority/test_resolver.py::test_stale_binding_denied_after_revoke_between_two_resolutions",
    ),
)


# ---------------------------------------------------------------------------
# MUT-PKG31-03: Workspace check removed (BND-002 forced ALLOW)
# ---------------------------------------------------------------------------


def _mut03_bnd002_always_allows(
    _original: Callable[[Bnd002WorkspaceEvaluator, Bnd002Input, BoundaryContext], BoundaryProof],
) -> Callable[[Bnd002WorkspaceEvaluator, Bnd002Input, BoundaryContext], BoundaryProof]:
    def _evaluate(
        self: Bnd002WorkspaceEvaluator, boundary_input: Bnd002Input, context: BoundaryContext
    ) -> BoundaryProof:
        return _forced_allow_proof(self.boundary_id, context, "MUT_PKG31_03_BND002_DISABLED")

    return _evaluate


MUT_PKG31_03 = MutationCase(
    mutation_id="MUT-PKG31-03",
    invariant="BND-002 denies when a request's claimed Workspace does not match the "
    "resolved scope of every object it names; removing it lets a request read/act across "
    "Workspace boundaries.",
    expected_boundary="BND_002",
    patch=MutationPatch(
        target_module="boundaries.bnd_002_workspace",
        target_qualname="Bnd002WorkspaceEvaluator.evaluate",
        replacement_factory=_mut03_bnd002_always_allows,  # type: ignore[arg-type]
    ),
    target_test_nodeids=(
        "tests/boundaries/test_bnd_002_workspace.py::test_denies_cross_workspace_object_set",
        "tests/e2e/test_proof_bundle_paths.py::test_cross_workspace_path_a_challenge_from_another_workspace_is_denied",
    ),
)


# ---------------------------------------------------------------------------
# MUT-PKG31-04: AI recommendation treated as Decision (BND-001 forced ALLOW)
# ---------------------------------------------------------------------------


def _mut04_bnd001_always_allows(
    _original: Callable[[Bnd001IdentityEvaluator, Bnd001Input, BoundaryContext], BoundaryProof],
) -> Callable[[Bnd001IdentityEvaluator, Bnd001Input, BoundaryContext], BoundaryProof]:
    def _evaluate(
        self: Bnd001IdentityEvaluator, boundary_input: Bnd001Input, context: BoundaryContext
    ) -> BoundaryProof:
        return _forced_allow_proof(self.boundary_id, context, "MUT_PKG31_04_BND001_DISABLED")

    return _evaluate


MUT_PKG31_04 = MutationCase(
    mutation_id="MUT-PKG31-04",
    invariant="BND-001 denies an actor class the operation does not accept -- in "
    "particular an AI_PROCESSOR can never pass as the HUMAN_USER a Human Decision "
    "requires. Removing it lets an AI-authored recommendation be recorded as if it were "
    "a Human Decision.",
    expected_boundary="BND_001",
    patch=MutationPatch(
        target_module="boundaries.bnd_001_identity",
        target_qualname="Bnd001IdentityEvaluator.evaluate",
        replacement_factory=_mut04_bnd001_always_allows,  # type: ignore[arg-type]
    ),
    target_test_nodeids=(
        "tests/boundaries/test_bnd_001_identity.py::test_ai_processor_can_never_pass_as_human_user",
        "tests/e2e/test_proof_bundle_paths.py::test_ai_boundary_path_an_ai_actor_is_denied_before_any_decision_is_touched",
    ),
)


# ---------------------------------------------------------------------------
# MUT-PKG31-05: direct DB write enabled (CommitCoordinator skips audit/outbox)
# ---------------------------------------------------------------------------


def _mut05_commit_inner_skips_audit_and_outbox(
    _original: Callable[..., CommitUnit],
) -> Callable[..., CommitUnit]:
    def _commit_inner(
        self: object,
        *,
        envelope: CommandEnvelope,
        proof: BoundaryProof,
        mutation: _MutationExecutorLike,
        occurred_at: datetime,
        commit_id: CommitId,
    ) -> CommitUnit:
        # Applies the canonical mutation directly and fabricates a
        # CommitUnit WITHOUT ever writing commit_units/audit_events/
        # outbox_events rows -- AC-09-002's "one atomic commit unit"
        # bundle, with the audit/outbox/commit-record half silently
        # skipped. This is what "enables direct DB write" means
        # concretely: canonical state changes, nothing governed
        # accompanies it.
        mutation.apply()
        return CommitUnit(
            commit_id=commit_id,
            command_id=envelope.command_id,
            attempt_id=envelope.attempt_id,
            workspace_id=envelope.workspace_scope_ref,
            target_refs=envelope.target_refs,
            relation_refs=(),
            governance_refs=(),
            audit_event_ids=(),
            outbox_ids=(),
            committed_at=occurred_at,
            outcome=CommitOutcome.COMMITTED,
        )

    return _commit_inner


MUT_PKG31_05 = MutationCase(
    mutation_id="MUT-PKG31-05",
    invariant="AC-09-002 (Governed Commit Unit): canonical mutation + audit + durable "
    "outbox entry must be persisted as one atomic bundle. A direct write that applies "
    "the canonical mutation without the audit/outbox half must be detectable by "
    "re-querying the real database for the missing artifacts, not merely by trusting the "
    "CommitUnit object returned to the caller.",
    expected_boundary="N/A (post-BND-014 commit-bundle atomicity, not a boundary evaluator)",
    patch=MutationPatch(
        target_module="commit.coordinator",
        target_qualname="CommitCoordinator._commit_inner",
        replacement_factory=_mut05_commit_inner_skips_audit_and_outbox,  # type: ignore[arg-type]
    ),
    target_test_nodeids=(
        "tests/command_commit_event/test_commit.py::test_commit_succeeds_and_atomically_writes_every_artifact",
    ),
)


# ---------------------------------------------------------------------------
# MUT-PKG31-06: Event treated as Command (CommandEnvelope type guard removed)
# ---------------------------------------------------------------------------


def _mut06_command_envelope_skips_validation(
    _original: Callable[[CommandEnvelope], None],
) -> Callable[[CommandEnvelope], None]:
    def _post_init(self: CommandEnvelope) -> None:
        return None

    return _post_init


MUT_PKG31_06 = MutationCase(
    mutation_id="MUT-PKG31-06",
    invariant="CommandEnvelope.__post_init__ structurally rejects a command_id that is "
    "not a real CommandId (in particular an EventId) -- 09 section 160.3's own defense "
    "against 'replay sends old Event to Command handler'. Removing the check lets an "
    "EventEnvelope's own identity construct a CommandEnvelope.",
    expected_boundary="N/A (semantic-type construction guard, not a boundary evaluator)",
    patch=MutationPatch(
        target_module="command.envelope",
        target_qualname="CommandEnvelope.__post_init__",
        replacement_factory=_mut06_command_envelope_skips_validation,  # type: ignore[arg-type]
    ),
    target_test_nodeids=(
        "tests/command_commit_event/test_command_event_split.py::test_an_event_id_cannot_construct_a_command_envelope",
    ),
)


# ---------------------------------------------------------------------------
# MUT-PKG31-07: stale Evidence accepted (freshness check forced FRESH)
# ---------------------------------------------------------------------------


def _mut07_evidence_member_always_fresh(
    _original: Callable[
        [EvidenceId, RecordVersion, WorkspaceId, EvidenceFreshnessPort], EvidenceMemberFreshness
    ],
) -> Callable[
    [EvidenceId, RecordVersion, WorkspaceId, EvidenceFreshnessPort], EvidenceMemberFreshness
]:
    def _resolve_member(
        evidence_id: EvidenceId,
        expected_content_version: RecordVersion,
        workspace_id: WorkspaceId,
        reader: EvidenceFreshnessPort,
    ) -> EvidenceMemberFreshness:
        return EvidenceMemberFreshness.FRESH

    return _resolve_member


MUT_PKG31_07 = MutationCase(
    mutation_id="MUT-PKG31-07",
    invariant="09 section 114: an Evidence member that is invalidated, superseded, "
    "unavailable, wrong-Workspace, or content-version-changed since capture is stale, "
    "and a commit naming a stale set must fail (BND-014's evidence branch). Forcing every "
    "member FRESH lets a commit proceed on Evidence that no longer holds.",
    expected_boundary="BND_014 (evidence_freshness branch)",
    patch=MutationPatch(
        target_module="evidence.freshness",
        target_qualname="_resolve_member",
        replacement_factory=_mut07_evidence_member_always_fresh,  # type: ignore[arg-type]
    ),
    target_test_nodeids=(
        "tests/evidence/test_freshness.py::test_an_invalidated_member_after_prepare_is_stale",
        "tests/evidence/test_freshness.py::test_a_cross_workspace_member_is_stale",
        "tests/evidence/test_freshness.py::test_a_superseded_member_is_stale",
    ),
)


# ---------------------------------------------------------------------------
# MUT-PKG31-08: INDETERMINATE retry enabled (BND-017 forced ALLOW)
# ---------------------------------------------------------------------------


def _mut08_bnd017_always_allows(
    _original: Callable[
        [Bnd017FailureIndeterminateEvaluator, Bnd017Input, BoundaryContext], BoundaryProof
    ],
) -> Callable[[Bnd017FailureIndeterminateEvaluator, Bnd017Input, BoundaryContext], BoundaryProof]:
    def _evaluate(
        self: Bnd017FailureIndeterminateEvaluator,
        boundary_input: Bnd017Input,
        context: BoundaryContext,
    ) -> BoundaryProof:
        return _forced_allow_proof(self.boundary_id, context, "MUT_PKG31_08_BND017_DISABLED")

    return _evaluate


MUT_PKG31_08 = MutationCase(
    mutation_id="MUT-PKG31-08",
    invariant="BND-017 denies a blind retry while consequence certainty is genuinely "
    "uncertain, and denies any operation on a target another INDETERMINATE record still "
    "blocks. Forcing ALLOW lets a retry proceed on an unproven outcome.",
    expected_boundary="BND_017",
    patch=MutationPatch(
        target_module="boundaries.bnd_017_failure_indeterminate",
        target_qualname="Bnd017FailureIndeterminateEvaluator.evaluate",
        replacement_factory=_mut08_bnd017_always_allows,  # type: ignore[arg-type]
    ),
    target_test_nodeids=(
        "tests/boundaries/test_bnd_017_failure_indeterminate.py::test_uncertain_consequence_denies_blind_retry",
        "tests/boundaries/test_bnd_017_failure_indeterminate.py::test_denies_dependent_operation_while_target_is_blocked",
    ),
)


# ---------------------------------------------------------------------------
# MUT-PKG31-09: admin fallback enabled (resolver grants on membership alone)
# ---------------------------------------------------------------------------


def _mut09_authority_resolver_admin_fallback(
    original: Callable[[AuthorityResolver, AuthorityRequest], AuthorityResolution],
) -> Callable[[AuthorityResolver, AuthorityRequest], AuthorityResolution]:
    def _resolve(self: AuthorityResolver, request: AuthorityRequest) -> AuthorityResolution:
        result = original(self, request)
        if (
            result.verdict is AuthorityVerdict.DENIED
            and result.proof.reason is ResolutionReason.DENIED_NO_MATCHING_BINDING
        ):
            # Mutant "admin fallback": any current member, with no
            # matching HumanAuthorityBinding at all, is granted anyway
            # -- exactly the Membership != Authority / Role != Authority
            # collapse 14's own non-collapse rules forbid.
            return AuthorityResolution(verdict=AuthorityVerdict.GRANTED, proof=result.proof)
        return result

    return _resolve


MUT_PKG31_09 = MutationCase(
    mutation_id="MUT-PKG31-09",
    invariant="AuthorityResolver.resolve() grants only on a current, scope-matching "
    "HumanAuthorityBinding -- current Workspace membership alone (any role, including "
    "Owner) is a precondition, never a substitute (05 AC-05-004). Granting on membership "
    "alone whenever no binding matches is the 'admin fallback' 14 explicitly forbids.",
    expected_boundary="BND_005",
    patch=MutationPatch(
        target_module="authority.resolver",
        target_qualname="AuthorityResolver.resolve",
        replacement_factory=_mut09_authority_resolver_admin_fallback,  # type: ignore[arg-type]
    ),
    target_test_nodeids=(
        "tests/security/test_admin_non_authority.py::test_admin_cannot_create_a_legitimate_decision",
        "tests/authority/test_resolver.py::test_owner_only_is_denied",
    ),
)


# ---------------------------------------------------------------------------
# MUT-PKG31-10: AI Gateway bypassed (provider-SDK import checker disabled)
# ---------------------------------------------------------------------------


def _mut10_provider_sdk_checker_disabled(
    _original: Callable[[tuple[Path, ...] | None], list[Violation]],
) -> Callable[[tuple[Path, ...] | None], list[Violation]]:
    def _check(roots: tuple[Path, ...] | None = None) -> list[Violation]:
        return []

    return _check


MUT_PKG31_10 = MutationCase(
    mutation_id="MUT-PKG31-10",
    invariant="check_provider_sdk_imports.check() rejects any production module outside "
    "packages/ai_gateway/adapters/providers/ that imports a real provider SDK -- the "
    "static half of 'all LLM traffic through the Gateway' (BND-009). Disabling the "
    "checker lets a Gateway-bypassing direct provider call land undetected.",
    expected_boundary="BND_009 (static enforcement half)",
    patch=MutationPatch(
        target_module="check_provider_sdk_imports",
        target_qualname="check",
        replacement_factory=_mut10_provider_sdk_checker_disabled,  # type: ignore[arg-type]
    ),
    target_test_nodeids=(
        "tests/security/test_ai_gateway.py::test_direct_provider_import_outside_gateway_adapter_is_rejected",
    ),
)


MUTATIONS: tuple[MutationCase, ...] = (
    MUT_PKG31_01,
    MUT_PKG31_02,
    MUT_PKG31_03,
    MUT_PKG31_04,
    MUT_PKG31_05,
    MUT_PKG31_06,
    MUT_PKG31_07,
    MUT_PKG31_08,
    MUT_PKG31_09,
    MUT_PKG31_10,
)

__all__ = ["MUTATIONS"]
